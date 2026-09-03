import logging
import httpx
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.schemas import PublishRequest, BulkPublishRequest, PublishResult, SEOBlock
from services.wordpress_service import publish_to_wordpress
from services import crawl_check_service, search_console_service
from config import settings
from db import get_session, PublishedUrlRecord
from typing import List
from datetime import datetime, timezone

router = APIRouter()
logger = logging.getLogger(__name__)


def _require_zip_for_location_page(block: SEOBlock):
    if (getattr(block, "content_type", "service") or "service") in ("blog", "post"):
        return
    if not (getattr(block, "city", "") or "").strip():
        return
    from services.zeorbit_local_seo import copy_has_zip, digits_zip
    faq_blob = ""
    if getattr(block, "faqs", None):
        for faq in block.faqs:
            faq_blob += f" {getattr(faq, 'question', '') or ''} {getattr(faq, 'answer', '') or ''}"
    if not digits_zip(getattr(block, "zip", "") or "") or not copy_has_zip(faq_blob, getattr(block, "zip", "") or ""):
        raise HTTPException(
            status_code=400,
            detail=f"ZIP is mandatory in FAQ answers. '{block.city}' must include a hyperlinked 5-digit ZIP in an FAQ.",
        )


async def _track_and_verify(result: PublishResult, block: SEOBlock, session: AsyncSession):
    """After a successful publish: verify the URL is actually crawlable, then
    hand it to the compliant Google Search Console pipeline (sitemap +
    URL Inspection) — never the Indexing API, which Google restricts to
    JobPosting/BroadcastEvent pages, not ordinary blog posts."""
    url = getattr(result, "post_url", None)
    if not getattr(result, "success", False) or not url:
        return
    try:
        existing = (await session.execute(
            select(PublishedUrlRecord).where(PublishedUrlRecord.url == url)
        )).scalar_one_or_none()
        record = existing or PublishedUrlRecord(url=url, source="wordpress")
        record.title = block.title or ""
        record.post_id = str(getattr(result, "post_id", "") or "")
        record.status = "published"
        record.error_message = ""
        if not existing:
            session.add(record)
        await session.commit()

        check = await crawl_check_service.check_url(url)
        record.http_status = check["http_status"]
        record.robots_allowed = check["robots_allowed"]
        record.has_noindex = check["has_noindex"]
        record.canonical_ok = check["canonical_ok"]
        if not check["ok"]:
            record.status = "error"
            record.error_message = check["error"]
            await session.commit()
            return

        is_post = (getattr(block, "content_type", "") or "") in ("blog", "post")
        sitemap_url = settings.WP_SITEMAP_URL
        extra_sm = (settings.WP_POST_SITEMAP_URL if is_post else settings.WP_PAGE_SITEMAP_URL) or ""
        # Never submit a post to page-sitemap or a page to post-sitemap.
        sitemaps = [u for u in (sitemap_url, extra_sm) if u]
        in_sitemap = False
        for sitemap_url in sitemaps:
            try:
                async with httpx.AsyncClient(timeout=15) as client:
                    r = await client.get(sitemap_url)
                if r.status_code == 200 and url in r.text:
                    in_sitemap = True
            except Exception as e:
                logger.warning(f"Sitemap fetch failed for {sitemap_url}: {e}")
            search_console_service.submit_sitemap(sitemap_url)
        if in_sitemap:
            record.status = "sitemap_added"
            record.sitemap_submitted_at = datetime.now(timezone.utc)

        if is_post:
            try:
                from services import indexnow_service
                if getattr(settings, "INDEXNOW_ENABLED", True) and indexnow_service.is_configured():
                    indexnow_service.submit_urls([url])
                extra = (settings.WP_POST_SITEMAP_URL or settings.WP_SITEMAP_URL or "").strip()
                if extra:
                    indexnow_service.ping_bing_sitemap(extra)
            except Exception as e:
                logger.warning("IndexNow after WordPress publish failed: %s", e)

        inspect = search_console_service.inspect_url(url)
        if inspect.get("ok"):
            record.status = inspect["status"]
            record.coverage_state = inspect.get("coverage_state", "")
            record.last_inspected_at = datetime.now(timezone.utc)
        await session.commit()
    except Exception as e:
        logger.error(f"Publish tracking failed for {url}: {e}")


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
async def publish_single(req: PublishRequest, session: AsyncSession = Depends(get_session)):
    """Publish a single SEO page to WordPress."""
    _apply_defaults(req.wp_config)
    if not req.wp_config.wp_url or not req.wp_config.wp_username or not req.wp_config.wp_app_password:
        raise HTTPException(status_code=400, detail="WordPress connection not configured.")
    _require_zip_for_location_page(req.seo_block)
    result = await publish_to_wordpress(req.seo_block, req.wp_config)
    await _track_and_verify(result, req.seo_block, session)
    return result


@router.post("/publish/bulk", response_model=List[PublishResult])
async def publish_bulk(req: BulkPublishRequest, session: AsyncSession = Depends(get_session)):
    """Publish multiple SEO pages to WordPress."""
    _apply_defaults(req.wp_config)
    if not req.wp_config.wp_url or not req.wp_config.wp_username or not req.wp_config.wp_app_password:
        raise HTTPException(status_code=400, detail="WordPress connection not configured.")
    results = []
    for block in req.pages:
        _require_zip_for_location_page(block)
        result = await publish_to_wordpress(block, req.wp_config)
        await _track_and_verify(result, block, session)
        results.append(result)
    return results
