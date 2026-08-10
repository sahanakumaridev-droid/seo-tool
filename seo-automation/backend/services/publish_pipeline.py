"""
publish_pipeline.py — post-publish automation for public /p/ pages:
crawl check → sitemap ping (Search Console) → optional paused Ads create.
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from db import PublishedUrlRecord
from models.schemas import GoogleAdsCampaignRequest, SEOBlock
from services import crawl_check_service, search_console_service

logger = logging.getLogger(__name__)


def _sitemap_url() -> str:
    base = (settings.PUBLIC_BASE_URL or "").rstrip("/")
    return f"{base}/sitemap.xml" if base else ""


async def track_public_publish(
    *,
    url: str,
    block: SEOBlock,
    session: AsyncSession,
    source: str = "public_web",
) -> dict[str, Any]:
    """Verify crawlability and notify Search Console for a /p/ URL."""
    out: dict[str, Any] = {
        "url": url,
        "crawl_ok": False,
        "indexing": "skipped",
        "detail": "",
    }
    if not url:
        return out

    try:
        existing = (
            await session.execute(select(PublishedUrlRecord).where(PublishedUrlRecord.url == url))
        ).scalar_one_or_none()
        record = existing or PublishedUrlRecord(url=url, source=source)
        record.title = block.title or ""
        record.status = "published"
        record.error_message = ""
        if not existing:
            session.add(record)
        await session.commit()

        check = await crawl_check_service.check_url(url)
        record.http_status = check.get("http_status")
        record.robots_allowed = check.get("robots_allowed")
        record.has_noindex = check.get("has_noindex")
        record.canonical_ok = check.get("canonical_ok")
        out["crawl_ok"] = bool(check.get("ok"))
        if not check.get("ok"):
            record.status = "error"
            record.error_message = check.get("error") or "crawl check failed"
            out["detail"] = record.error_message
            await session.commit()
            return out

        sitemap = _sitemap_url()
        if sitemap and settings.GSC_SITE_URL and settings.GOOGLE_INDEXING_KEY_FILE:
            search_console_service.submit_sitemap(sitemap)
            inspect = search_console_service.inspect_url(url)
            if inspect.get("ok"):
                record.status = inspect.get("status") or "submitted"
                record.coverage_state = inspect.get("coverage_state", "")
                record.last_inspected_at = datetime.now(timezone.utc)
                out["indexing"] = record.status
            else:
                record.status = "sitemap_submitted"
                record.sitemap_submitted_at = datetime.now(timezone.utc)
                out["indexing"] = "sitemap_submitted"
                out["detail"] = inspect.get("detail") or inspect.get("error") or ""
        elif sitemap:
            record.status = "published_awaiting_gsc"
            out["indexing"] = "awaiting_gsc_setup"
            out["detail"] = "Set GSC_SITE_URL + GOOGLE_INDEXING_KEY_FILE to auto-request indexing."
        else:
            out["indexing"] = "no_public_base"
            out["detail"] = "Set PUBLIC_BASE_URL so /sitemap.xml can be submitted."

        await session.commit()
    except Exception as e:
        logger.error("track_public_publish failed for %s: %s", url, e)
        out["detail"] = str(e)
    return out


async def maybe_auto_create_ads(
    *,
    public_url: str,
    block: SEOBlock,
    daily_budget: float = 25.0,
    enable: Optional[bool] = None,
) -> dict[str, Any]:
    """Optionally create a Search campaign for the published page."""
    if not getattr(settings, "GOOGLE_ADS_AUTO_CREATE_ON_PUBLISH", False):
        return {"skipped": True, "reason": "GOOGLE_ADS_AUTO_CREATE_ON_PUBLISH is off"}

    from services.google_ads_service import create_campaign, suggest_ad_copy
    from models.schemas import GoogleAdsSuggestRequest

    copy = await suggest_ad_copy(
        GoogleAdsSuggestRequest(
            business_name=block.business_type or "Business",
            category=block.business_type or "services",
            city=block.city or "",
        )
    )
    headlines = copy.get("headlines") or []
    descriptions = copy.get("descriptions") or []
    keywords = copy.get("keywords") or []
    if block.keywords and getattr(block.keywords, "primary", None):
        keywords = list(dict.fromkeys([block.keywords.primary, *(block.keywords.secondary or []), *keywords]))[:8]

    name = f"{block.business_type or 'SEO'} - {block.city or 'Local'}"
    auto_enable = bool(getattr(settings, "GOOGLE_ADS_AUTO_ENABLE", False)) if enable is None else bool(enable)
    result = await create_campaign(
        GoogleAdsCampaignRequest(
            campaign_name=name[:100],
            daily_budget=daily_budget,
            final_url=public_url,
            headlines=(headlines or ["Local Pros Near You", "Book Today", "Free Quote"])[:15],
            descriptions=(descriptions or ["Trusted local service. Fast response.", "Get a free quote today."])[:4],
            keywords=(keywords or [block.business_type or "services"])[:8],
            enable=auto_enable,
        )
    )
    return result.model_dump()
