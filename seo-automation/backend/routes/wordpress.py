from fastapi import APIRouter, HTTPException
from models.schemas import PublishRequest, BulkPublishRequest, PublishResult
from services.wordpress_service import publish_to_wordpress
from typing import List

router = APIRouter()

@router.post("/publish", response_model=PublishResult)
async def publish_single(req: PublishRequest):
    """Publish a single SEO page to WordPress."""
    if not req.wp_config.wp_url or not req.wp_config.wp_username:
        raise HTTPException(status_code=400, detail="WordPress URL and username are required.")
    return await publish_to_wordpress(req.seo_block, req.wp_config)

@router.post("/publish/bulk", response_model=List[PublishResult])
async def publish_bulk(req: BulkPublishRequest):
    """Publish multiple SEO pages to WordPress."""
    if not req.wp_config.wp_url or not req.wp_config.wp_username:
        raise HTTPException(status_code=400, detail="WordPress URL and username are required.")
    results = []
    for block in req.pages:
        result = await publish_to_wordpress(block, req.wp_config)
        results.append(result)
    return results
