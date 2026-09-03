from fastapi import APIRouter, HTTPException, BackgroundTasks
import asyncio
from models.schemas import BulkGenerateResponse, GenerateRequest, BulkPublishRequest, CityInfo
from services.job_service import create_job, get_job, run_bulk_job, cleanup_old_jobs
from services.content_service import generate_seo_block, generate_seo_block_until_floor
from services.wordpress_service import publish_to_wordpress
from services.location_service import get_nearby_cities, LocationNotResolvedError, resolve_generation_cities

router = APIRouter()


@router.post("/generate")
async def start_bulk_generate_job(req: GenerateRequest, background_tasks: BackgroundTasks):
    """Start an async bulk content generation job. Returns job_id for polling."""
    from routes.content import ensure_brief_for_generate, _places_for_generate
    req = await ensure_brief_for_generate(req)
    cities = await _places_for_generate(req)

    job_id = create_job(total=len(cities))
    cleanup_old_jobs()

    used_featured: list = []
    existing_bodies: list = []
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
                # Blog/posts reuse website stock across niches — seed every image
                if req.content_kind != "post":
                    if niche and fam and niche != fam:
                        continue
                if (block0 or {}).get("featured_image_url"):
                    used_featured.append(block0["featured_image_url"])
                for im in (block0 or {}).get("in_content_images") or []:
                    u = im.get("url") if isinstance(im, dict) else None
                    if u:
                        used_featured.append(u)
                body0 = f"{(block0 or {}).get('intro') or ''}\n{(block0 or {}).get('content') or ''}".strip()
                if body0:
                    existing_bodies.append(body0)
    except Exception as e:
        print(f"[Jobs] could not seed used images: {e}")

    indexed = [{"i": i, "city": c} for i, c in enumerate(cities)]

    async def generate_task(item):
        city_info = item["city"]
        keyword_index = item["i"]
        name = city_info.name if hasattr(city_info, "name") else city_info["name"]
        state = city_info.state if hasattr(city_info, "state") else city_info["state"]
        zip_code = city_info.zip if hasattr(city_info, "zip") else (city_info.get("zip") if isinstance(city_info, dict) else "")
        async with used_lock:
            exclude = list(used_featured)
            bodies_snapshot = list(existing_bodies)
        try:
            block, extra_attempts = await generate_seo_block_until_floor(
                business_type=req.business_type,
                city=name,
                state=state,
                target_keywords=req.target_keywords,
                industry=req.industry,
                use_ai=req.use_ai,
                llm_provider=req.llm_provider,
                exclude_image_urls=exclude,
                custom_requirements=req.custom_requirements,
                content_kind=req.content_kind,
                audience=req.audience,
                keyword_index=keyword_index,
                existing_bodies=bodies_snapshot,
                zip=zip_code or "",
                image_keyword=getattr(req, "image_keyword", "") or "",
            )
        except Exception as e:
            print(f"[Jobs] {name} failed ({e}); writing a fallback page so none are skipped")
            try:
                block = await generate_seo_block(
                    req.business_type,
                    name,
                    state,
                    req.target_keywords,
                    req.industry,
                    use_ai=False,
                    llm_provider=None,
                    exclude_image_urls=exclude,
                    custom_requirements=req.custom_requirements,
                    content_kind=req.content_kind,
                    audience=req.audience,
                    keyword_index=keyword_index,
                    zip=zip_code or "",
                    image_keyword=getattr(req, "image_keyword", "") or "",
                )
            except Exception as e2:
                print(f"[Jobs] fallback also failed for {name}: {e2}")
                raise
            extra_attempts = 0
        if extra_attempts:
            print(
                f"[Jobs] {name} scored below 90% — generated again "
                f"({extra_attempts} extra pass(es))"
            )
        try:
            async with used_lock:
                # Re-check under lock in case another task claimed the same URL first
                if block.featured_image_url:
                    from services.image_service import normalize_image_key, generate_article_images
                    taken = {normalize_image_key(u) for u in used_featured}
                    key = normalize_image_key(block.featured_image_url)
                    if key in taken:
                        images = await generate_article_images(
                            f"{req.target_keywords[0] if req.target_keywords else req.business_type} {name}",
                            f"{name}, {state} {zip_code}".strip(),
                            "ZeOrbit",
                            count=3,
                            exclude_urls=used_featured,
                            industry="" if req.content_kind == "post" else (req.industry or ""),
                            niche=req.business_type or "",
                            search_intent=getattr(block, "search_intent", "") or "",
                            image_concept_text=getattr(block, "image_concept", "") or "",
                            keyword_index=keyword_index,
                            content_type="blog" if req.content_kind == "post" else "service",
                            match_query=(getattr(req, "image_keyword", "") or "").strip() or (req.target_keywords[0] if req.target_keywords else req.business_type) or "",
                            audience=req.audience or "",
                            image_keyword=(getattr(req, "image_keyword", "") or "").strip(),
                        )
                        if images:
                            from services.image_service import assign_canonical_images
                            feat, foot, cleaned = assign_canonical_images(images)
                            if feat:
                                block.in_content_images = cleaned
                                block.featured_image_url = feat
                                block.footer_image_url = foot
                            else:
                                print(f"[Image] uniqueness regen empty for {name}; keeping prior featured")
                    if block.featured_image_url:
                        used_featured.append(block.featured_image_url)
                existing_bodies.append(f"{block.intro or ''}\n{block.content or ''}")
        except Exception as e:
            print(f"[Jobs] image uniqueness for {name} failed ({e}); keeping page")
        dumped = block.model_dump()
        # Draft only — persist to PageRecord when the user clicks Publish to ZeOrbit.
        return dumped

    background_tasks.add_task(
        run_bulk_job,
        job_id=job_id,
        items=indexed,
        task_fn=generate_task,
        concurrency=4,
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
