from fastapi import APIRouter, HTTPException
from models.schemas import PublishRequest, BulkPublishRequest, PublishResult
from services.wordpress_service import publish_to_wordpress
from services.indexing_service import submit_url
from config import settings
from typing import List
import asyncio

router = APIRouter()


async def _auto_index(result: PublishResult):
    """After a successful publish, ping Google to crawl the new URL (best effort)."""
    try:
        url = getattr(result, "post_url", None)
        if getattr(result, "success", False) and url:
            await asyncio.to_thread(submit_url, url, "URL_UPDATED")
    except Exception:
        pass


def _apply_defaults(wp_config):
    """Fall back to the server-configured WordPress connection (env) when the
    request leaves fields blank. Lets the tool publish to the connected site
    (zeorbit.com) without the password ever living in the browser."""
    if not wp_config.wp_url:
        wp_config.wp_url = settings.WP_URL
    if not wp_config.wp_username:
        wp_config.wp_username = settings.WP_USERNAME
    if not wp_config.wp_app_password:
        wp_config.wp_app_password = settings.WP_APP_PASSWORD
    if not wp_config.seo_plugin:
        wp_config.seo_plugin = settings.WP_SEO_PLUGIN
    return wp_config


@router.post("/publish", response_model=PublishResult)
async def publish_single(req: PublishRequest):
    """Publish a single SEO page to WordPress."""
    _apply_defaults(req.wp_config)
    if not req.wp_config.wp_url or not req.wp_config.wp_username or not req.wp_config.wp_app_password:
        raise HTTPException(status_code=400, detail="WordPress connection not configured.")
    result = await publish_to_wordpress(req.seo_block, req.wp_config)
    await _auto_index(result)
    return result


@router.post("/publish/bulk", response_model=List[PublishResult])
async def publish_bulk(req: BulkPublishRequest):
    """Publish multiple SEO pages to WordPress."""
    _apply_defaults(req.wp_config)
    if not req.wp_config.wp_url or not req.wp_config.wp_username or not req.wp_config.wp_app_password:
        raise HTTPException(status_code=400, detail="WordPress connection not configured.")
    results = []
    for block in req.pages:
        result = await publish_to_wordpress(block, req.wp_config)
        await _auto_index(result)
        results.append(result)
    return results
