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
from services.location_service import get_nearby_cities
from services.content_service import generate_seo_block, generate_articles
from services.website_analysis_service import analyze_website
from services.export_service import export_json, export_html, export_wordpress
from db import get_session, PageRecord
from datetime import datetime, timezone
from typing import List

router = APIRouter()

def slugify(text: str) -> str:
    return re.sub(r'[^a-z0-9-]+', '-', text.lower()).strip('-')

@router.post("/generate", response_model=BulkGenerateResponse)
async def generate_bulk(req: GenerateRequest, session: AsyncSession = Depends(get_session)):
    cities = await get_nearby_cities(req.base_location, req.num_cities)
    if not cities:
        raise HTTPException(status_code=404, detail="No cities found for the given location")

    pages: List[SEOBlock] = []
    for city_info in cities:
        block = await generate_seo_block(
            req.business_type,
            city_info.name,
            city_info.state,
            req.target_keywords,
            req.industry,
            use_ai=req.use_ai,
        )
        pages.append(block)
        
        # Save each page to the database
        slug = slugify(f"{req.business_type}-{city_info.name}")
        result = await session.execute(select(PageRecord).where(PageRecord.slug == slug))
        existing = result.scalar_one_or_none()
        
        if existing:
            existing.seo_block = block.model_dump()
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
    pages = await generate_articles(req, profile)
    if not pages:
        raise HTTPException(status_code=502, detail="Article generation failed. Check OPENAI_API_KEY.")

    city, _, _ = (req.location.partition(","))
    for block in pages:
        # Namespace the slug so keyword-articles don't collide with city-page slugs.
        base_slug = block.slug or slugify(block.title)
        slug = base_slug
        result = await session.execute(select(PageRecord).where(PageRecord.slug == slug))
        existing = result.scalar_one_or_none()
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
):
    return await generate_seo_block(business_type, city, state, use_ai=use_ai)

@router.post("/export/json")
async def export_as_json(req: GenerateRequest):
    cities = await get_nearby_cities(req.base_location, req.num_cities)
    pages = [await generate_seo_block(req.business_type, c.name, c.state) for c in cities]
    return JSONResponse(content={"pages": [p.model_dump() for p in pages]})

@router.post("/export/html")
async def export_as_html(business_type: str, city: str, state: str = "CA"):
    block = await generate_seo_block(business_type, city, state)
    html = export_html(block)
    return HTMLResponse(content=html)

@router.post("/export/wordpress")
async def export_as_wordpress(req: GenerateRequest):
    cities = await get_nearby_cities(req.base_location, req.num_cities)
    pages = [await generate_seo_block(req.business_type, c.name, c.state) for c in cities]
    wp_posts = [export_wordpress(p) for p in pages]
    return {"posts": wp_posts}
