"""Publish SEO pages to a connected Shopify blog."""
from typing import List

from fastapi import APIRouter, HTTPException
from models.schemas import SEOBlock
from services.shopify_service import publish_article

router = APIRouter()


@router.post("/publish")
async def publish_single(block: SEOBlock):
    try:
        return await publish_article(block)
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/publish/bulk")
async def publish_bulk(pages: List[SEOBlock]):
    results = []
    for block in pages:
        try:
            results.append(await publish_article(block))
        except RuntimeError as exc:
            results.append({"city": block.city or "", "success": False, "post_url": None, "error": str(exc)})
    if results and not any(item.get("success") for item in results):
        raise HTTPException(status_code=400, detail=results[0].get("error") or "Shopify publish failed.")
    return {"published": results, "count": sum(1 for item in results if item.get("success"))}
