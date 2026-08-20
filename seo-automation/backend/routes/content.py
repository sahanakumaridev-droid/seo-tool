import uuid
import re
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.schemas import (
    GenerateRequest, SEOBlock, BulkGenerateResponse,
    ArticleRequest, WebsiteAnalysisRequest, WebsiteProfile,
)
from services.location_service import get_nearby_cities, LocationNotResolvedError, merge_extra_locations
from services.content_service import generate_seo_block, generate_articles
from services.website_analysis_service import analyze_website
from services.export_service import export_json, export_html, export_wordpress
from db import get_session, PageRecord
from datetime import datetime, timezone
from typing import List, Optional

router = APIRouter()

def slugify(text: str) -> str:
    return re.sub(r'[^a-z0-9-]+', '-', text.lower()).strip('-')

from services.llm_service import available_providers

@router.get("/llm-providers")
async def llm_providers():
    """Return which AI models are configured so the UI can enable/disable options."""
    return available_providers()


@router.post("/generate", response_model=BulkGenerateResponse)
async def generate_bulk(req: GenerateRequest, session: AsyncSession = Depends(get_session)):
    try:
        cities = await get_nearby_cities(req.base_location, req.num_cities)
        cities = merge_extra_locations(cities, req.extra_locations)
        cities = [c for c in cities if getattr(c, "kind", "city") != "state"]
    except LocationNotResolvedError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not cities:
        raise HTTPException(status_code=404, detail="No cities found for the given location")

    pages: List[SEOBlock] = []
    used_featured: List[str] = []
    # Avoid colliding with images already saved for other locations (featured + body)
    from services.image_service import normalize_image_key, generate_article_images, topic_image_family
    existing_rows = (await session.execute(select(PageRecord))).scalars().all()
    niche_family = topic_image_family(req.business_type)
    for row in existing_rows:
        block0 = row.seo_block if isinstance(row.seo_block, dict) else {}
        row_family = topic_image_family(
            f"{row.business_type or ''} {(block0 or {}).get('business_type') or ''}"
        )
        if niche_family and row_family and niche_family != row_family:
            continue
        url0 = (block0 or {}).get("featured_image_url") or ""
        if url0:
            used_featured.append(url0)
        for im in (block0 or {}).get("in_content_images") or []:
            if isinstance(im, dict) and im.get("url"):
                used_featured.append(im["url"])
            elif hasattr(im, "url") and im.url:
                used_featured.append(im.url)

    for city_info in cities:
        # State chip is for Location Expansion UI; generate for cities + counties only.
        if getattr(city_info, "kind", "city") == "state":
            continue
        exclude = list(used_featured)
        from services.slug_utils import article_slug
        preview_slug = article_slug(req.target_keywords, city_info.name, req.business_type)
        result = await session.execute(select(PageRecord).where(PageRecord.slug == preview_slug))
        existing = result.scalar_one_or_none()
        if existing:
            prev = existing.seo_block if isinstance(existing.seo_block, dict) else {}
            free_urls = []
            if (prev or {}).get("featured_image_url"):
                free_urls.append(prev["featured_image_url"])
            for im in (prev or {}).get("in_content_images") or []:
                u = im.get("url") if isinstance(im, dict) else getattr(im, "url", None)
                if u:
                    free_urls.append(u)
            free_keys = {normalize_image_key(u) for u in free_urls}
            exclude = [u for u in exclude if normalize_image_key(u) not in free_keys]

        block = await generate_seo_block(
            req.business_type,
            city_info.name,
            city_info.state,
            req.target_keywords,
            req.industry,
            use_ai=req.use_ai,
            llm_provider=req.llm_provider,
            exclude_image_urls=exclude,
        )
        # Final uniqueness guard (same as async jobs path)
        if block.featured_image_url:
            taken = {normalize_image_key(u) for u in used_featured}
            key = normalize_image_key(block.featured_image_url)
            if key in taken:
                images = await generate_article_images(
                    f"{req.business_type} {city_info.name}",
                    f"{city_info.name}, {city_info.state}".strip(", "),
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
        slug = (block.slug or preview_slug).strip()
        block.slug = slug
        pages.append(block)
        
        if existing:
            existing.seo_block = block.model_dump()
            existing.slug = slug
            existing.updated_at = datetime.now(timezone.utc)
        else:
            session.add(PageRecord(
                business_type=req.business_type,
                base_location=req.base_location,
                city=city_info.name,
                state=city_info.state,
                slug=slug,
                seo_block=block.model_dump(),
            ))
    
    await session.commit()

    return BulkGenerateResponse(
        total=len(pages),
        pages=pages,
        job_id=str(uuid.uuid4())
    )

@router.post("/analyze-website", response_model=WebsiteProfile)
async def analyze_website_endpoint(req: WebsiteAnalysisRequest):
    """Analyze a website URL: extract services, products, audience, tone, and page inventory."""
    return await analyze_website(req.website_url)


@router.post("/generate-articles", response_model=BulkGenerateResponse)
async def generate_articles_endpoint(req: ArticleRequest, session: AsyncSession = Depends(get_session)):
    """Generate N unique articles from a primary keyword + location, grounded in a website analysis."""
    profile = await analyze_website(req.website_url)
    try:
        pages = await generate_articles(req, profile)
    except LocationNotResolvedError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not pages:
        raise HTTPException(status_code=502, detail="Article generation failed. Check OPENAI_API_KEY.")

    city, _, _ = (req.location.partition(","))
    used_featured: List[str] = []
    from services.image_service import normalize_image_key
    for row in (await session.execute(select(PageRecord))).scalars().all():
        b0 = row.seo_block if isinstance(row.seo_block, dict) else {}
        u0 = (b0 or {}).get("featured_image_url") or ""
        if u0:
            used_featured.append(u0)

    for block in pages:
        # Namespace the slug so keyword-articles don't collide with city-page slugs.
        base_slug = block.slug or slugify(block.title)
        slug = base_slug
        result = await session.execute(select(PageRecord).where(PageRecord.slug == slug))
        existing = result.scalar_one_or_none()
        # Re-pick featured if it collides with another saved page
        feat = block.featured_image_url or ""
        if feat and normalize_image_key(feat) in {normalize_image_key(u) for u in used_featured}:
            from services.image_service import generate_article_images
            imgs = await generate_article_images(
                req.primary_keyword,
                f"{block.city or city.strip()}, {block.state or ''}".strip(", "),
                "",
                count=3,
                angle_title=block.title or "",
                exclude_urls=used_featured,
                industry=getattr(req, "industry", "") or getattr(block, "industry", "") or "",
                niche=req.primary_keyword or "",
            )
            if imgs:
                block.in_content_images = imgs
                block.featured_image_url = imgs[0].url
                feat = imgs[0].url
        if feat:
            used_featured.append(feat)
        if existing:
            existing.seo_block = block.model_dump()
            existing.updated_at = datetime.now(timezone.utc)
        else:
            session.add(PageRecord(
                business_type=req.primary_keyword,
                base_location=req.location,
                city=block.city or city.strip(),
                state=block.state or "",
                slug=slug,
                seo_block=block.model_dump(),
            ))
    await session.commit()

    return BulkGenerateResponse(total=len(pages), pages=pages, job_id=str(uuid.uuid4()))


@router.post("/generate/single", response_model=SEOBlock)
async def generate_single(
    business_type: str,
    city: str,
    state: str = "CA",
    use_ai: bool = False,
    llm_provider: str = None,
):
    return await generate_seo_block(business_type, city, state, use_ai=use_ai, llm_provider=llm_provider)


@router.post("/refresh-images")
async def refresh_images(
    slug: Optional[str] = None,
    only_unrelated: bool = True,
    dedupe: bool = False,
    session: AsyncSession = Depends(get_session),
):
    """Re-assign on-topic featured images for existing blogs without regenerating copy.

    Keeps all page content/titles/FAQs. Replaces featured_image_url + in_content_images only.
    By default only touches pages whose current image looks unrelated (Flickr/picsum/empty).
    Pass dedupe=true to reassign every page so featured photos are unique across the library.
    """
    from services.image_service import generate_article_images, normalize_image_key, topic_image_family
    from collections import defaultdict

    result = await session.execute(select(PageRecord))
    rows = result.scalars().all()
    updated = []
    skipped = []

    def _is_unrelated(url: str) -> bool:
        u = (url or "").lower()
        if not u:
            return True
        if "picsum.photos" in u:
            return True
        if "live.staticflickr.com" in u or "flickr.com" in u:
            return True
        if "placeholder" in u:
            return True
        return False

    # When deduping, process all pages and never reuse a featured URL within a niche family.
    if dedupe and not slug:
        only_unrelated = False

    used_by_family: dict = defaultdict(list)
    if only_unrelated and not slug and not dedupe:
        for row in rows:
            block = row.seo_block if isinstance(row.seo_block, dict) else {}
            current = block.get("featured_image_url") or ""
            if current and not _is_unrelated(current):
                biz = row.business_type or block.get("business_type") or ""
                fam = topic_image_family(f"{biz} {block.get('title') or ''}")
                used_by_family[fam].append(current)

    for row in rows:
        if slug and row.slug != slug:
            continue
        block = row.seo_block if isinstance(row.seo_block, dict) else {}
        current = block.get("featured_image_url") or ""
        if only_unrelated and not _is_unrelated(current) and not slug:
            skipped.append(row.slug)
            continue

        business = row.business_type or block.get("business_type") or ""
        city = row.city or block.get("city") or ""
        state = row.state or block.get("state") or ""
        kw = ""
        try:
            kw = (block.get("keywords") or {}).get("primary") or ""
        except Exception:
            kw = ""
        focus = kw or f"{business} {city}".strip()
        location = f"{city}, {state}".strip(", ")
        family = topic_image_family(
            f"{business} {focus} {block.get('title') or ''} {block.get('industry') or ''}"
        )
        images = await generate_article_images(
            focus, location, "", count=3,
            angle_title=block.get("title") or "",
            exclude_urls=used_by_family[family],
            industry=block.get("industry") or "",
            niche=business,
        )
        if not images:
            skipped.append(row.slug)
            continue

        block = dict(block)
        block["featured_image_url"] = images[0].url
        block["in_content_images"] = [img.model_dump() if hasattr(img, "model_dump") else img for img in images]
        row.seo_block = block
        row.updated_at = datetime.now(timezone.utc)
        # Exclude every assigned photo so the next location cannot reuse any of them
        for img in images:
            if img.url:
                used_by_family[family].append(img.url)
        updated.append({"slug": row.slug, "family": family, "featured_image_url": images[0].url})

    await session.commit()
    unique = len({normalize_image_key(p["featured_image_url"]) for p in updated})
    family_stats = {
        fam: len({normalize_image_key(u) for u in urls})
        for fam, urls in used_by_family.items()
    }
    return {
        "updated": len(updated),
        "skipped": len(skipped),
        "unique_featured_in_batch": unique,
        "unique_per_family": family_stats,
        "pages": updated[:50],
        "note": "Existing blog copy preserved — images only" + (" (deduped by niche)" if dedupe else ""),
    }


@router.post("/export/json")
async def export_as_json(req: GenerateRequest):
    try:
        cities = await get_nearby_cities(req.base_location, req.num_cities)
    except LocationNotResolvedError as e:
        raise HTTPException(status_code=400, detail=str(e))
    pages = [await generate_seo_block(req.business_type, c.name, c.state) for c in cities]
    return JSONResponse(content={"pages": [p.model_dump() for p in pages]})

@router.post("/export/html")
async def export_as_html(business_type: str, city: str, state: str = "CA"):
    block = await generate_seo_block(business_type, city, state)
    html = export_html(block)
    return HTMLResponse(content=html)

@router.post("/export/wordpress")
async def export_as_wordpress(req: GenerateRequest):
    try:
        cities = await get_nearby_cities(req.base_location, req.num_cities)
    except LocationNotResolvedError as e:
        raise HTTPException(status_code=400, detail=str(e))
    pages = [await generate_seo_block(req.business_type, c.name, c.state) for c in cities]
    wp_posts = [export_wordpress(p) for p in pages]
    return {"posts": wp_posts}
