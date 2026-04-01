import uuid
from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from models.schemas import GenerateRequest, SEOBlock, BulkGenerateResponse
from services.location_service import get_nearby_cities
from services.content_service import generate_seo_block
from services.export_service import export_json, export_html, export_wordpress
from typing import List

router = APIRouter()

@router.post("/generate", response_model=BulkGenerateResponse)
async def generate_bulk(req: GenerateRequest):
    cities = await get_nearby_cities(req.base_location, req.num_cities)
    if not cities:
        raise HTTPException(status_code=404, detail="No cities found for the given location")

    pages: List[SEOBlock] = []
    for city_info in cities:
        block = await generate_seo_block(req.business_type, city_info.name, city_info.state, req.target_keywords, req.industry)
        pages.append(block)

    return BulkGenerateResponse(
        total=len(pages),
        pages=pages,
        job_id=str(uuid.uuid4())
    )

@router.post("/generate/single", response_model=SEOBlock)
async def generate_single(business_type: str, city: str, state: str = "CA"):
    return await generate_seo_block(business_type, city, state)

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
