from fastapi import APIRouter, HTTPException, BackgroundTasks
import asyncio
from models.schemas import BulkGenerateResponse, GenerateRequest, BulkPublishRequest
from services.job_service import create_job, get_job, run_bulk_job, cleanup_old_jobs
from services.content_service import generate_seo_block
from services.wordpress_service import publish_to_wordpress
from services.location_service import get_nearby_cities, LocationNotResolvedError, merge_extra_locations

router = APIRouter()


@router.post("/generate")
async def start_bulk_generate_job(req: GenerateRequest, background_tasks: BackgroundTasks):
    """Start an async bulk content generation job. Returns job_id for polling."""
    try:
        cities = await get_nearby_cities(req.base_location, req.num_cities)
        cities = merge_extra_locations(cities, req.extra_locations)
        cities = [c for c in cities if getattr(c, "kind", "city") != "state"]
    except LocationNotResolvedError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not cities:
        raise HTTPException(status_code=400, detail="No cities found for location")

    job_id = create_job(total=len(cities))
    cleanup_old_jobs()

    used_featured: list = []
    used_lock = asyncio.Lock()

    # Seed exclude list from already-published pages in this niche
    try:
        from db import AsyncSessionLocal, PageRecord
        from sqlalchemy import select
        from services.image_service import topic_image_family
        niche = topic_image_family(req.business_type)
        async with AsyncSessionLocal() as session:
            rows = (await session.execute(select(PageRecord))).scalars().all()
            for row in rows:
                block0 = row.seo_block if isinstance(row.seo_block, dict) else {}
                fam = topic_image_family(f"{row.business_type or ''} {(block0 or {}).get('business_type') or ''}")
                if niche and fam and niche != fam:
                    continue
                if (block0 or {}).get("featured_image_url"):
                    used_featured.append(block0["featured_image_url"])
                for im in (block0 or {}).get("in_content_images") or []:
                    u = im.get("url") if isinstance(im, dict) else None
                    if u:
                        used_featured.append(u)
    except Exception as e:
        print(f"[Jobs] could not seed used images: {e}")

    async def generate_task(city_info):
        name = city_info.name if hasattr(city_info, "name") else city_info["name"]
        state = city_info.state if hasattr(city_info, "state") else city_info["state"]
        async with used_lock:
            exclude = list(used_featured)
        block = await generate_seo_block(
            business_type=req.business_type,
            city=name,
            state=state,
            target_keywords=req.target_keywords,
            industry=req.industry,
            use_ai=req.use_ai,
            llm_provider=req.llm_provider,
            exclude_image_urls=exclude,
        )
        async with used_lock:
            # Re-check under lock in case another task claimed the same URL first
            if block.featured_image_url:
                from services.image_service import normalize_image_key, generate_article_images
                taken = {normalize_image_key(u) for u in used_featured}
                key = normalize_image_key(block.featured_image_url)
                if key in taken:
                    images = await generate_article_images(
                        f"{req.business_type} {name}",
                        f"{name}, {state}".strip(", "),
                        "",
                        count=3,
                        exclude_urls=used_featured,
                        industry=req.industry or "",
                        niche=req.business_type or "",
                    )
                    if images:
                        block.in_content_images = images
                        block.featured_image_url = images[0].url
                if block.featured_image_url:
                    used_featured.append(block.featured_image_url)
                for im in block.in_content_images or []:
                    if im.url:
                        used_featured.append(im.url)
        return block.model_dump()

    background_tasks.add_task(
        run_bulk_job,
        job_id=job_id,
        items=cities,
        task_fn=generate_task,
        concurrency=3,
        retry_count=2,
    )

    return {"job_id": job_id, "total": len(cities), "status": "started"}


@router.post("/publish")
async def start_bulk_publish_job(req: BulkPublishRequest, background_tasks: BackgroundTasks):
    """Start an async bulk WordPress publish job. Returns job_id for polling."""
    job_id = create_job(total=len(req.pages))
    cleanup_old_jobs()

    async def publish_task(block_data):
        from models.schemas import SEOBlock
        block = SEOBlock(**block_data) if isinstance(block_data, dict) else block_data
        result = await publish_to_wordpress(block, req.wp_config)
        return result.model_dump()

    background_tasks.add_task(
        run_bulk_job,
        job_id=job_id,
        items=[p.model_dump() for p in req.pages],
        task_fn=publish_task,
        concurrency=2,
        retry_count=2,
    )

    return {"job_id": job_id, "total": len(req.pages), "status": "started"}


@router.get("/{job_id}")
async def get_job_status(job_id: str):
    """Poll job status and results."""
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job
