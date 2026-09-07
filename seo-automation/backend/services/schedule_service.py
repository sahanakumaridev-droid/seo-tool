"""Publish pages/posts that were saved with a future scheduled_at."""
from __future__ import annotations

import logging
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db import PageRecord

logger = logging.getLogger(__name__)
LIVE_SITE = "https://zeorbit.com"


def _parse_when(value: str | None) -> datetime | None:
    raw = (value or "").strip()
    if not raw:
        return None
    try:
        if raw.endswith("Z"):
            raw = raw[:-1] + "+00:00"
        dt = datetime.fromisoformat(raw)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except ValueError:
        return None


async def publish_due_pages(session: AsyncSession) -> int:
    from services.publish_pipeline import track_public_publish, maybe_auto_create_ads
    from models.schemas import SEOBlock

    now = datetime.now(timezone.utc)
    rows = (await session.execute(select(PageRecord))).scalars().all()
    published = 0
    for row in rows:
        block_data = row.seo_block if isinstance(row.seo_block, dict) else {}
        if (block_data.get("publish_status") or "").lower() != "scheduled":
            continue
        when = _parse_when(block_data.get("scheduled_at"))
        if not when or when > now:
            continue
        try:
            block = SEOBlock(**{k: v for k, v in block_data.items() if k != "publish_status"})
        except Exception:
            logger.exception("Scheduled page %s failed to parse", row.slug)
            continue
        public_url = f"{LIVE_SITE}/{row.slug}"
        try:
            await track_public_publish(url=public_url, block=block, session=session)
            await maybe_auto_create_ads(public_url=public_url, block=block)
        except Exception:
            logger.exception("Scheduled publish failed for %s", row.slug)
            continue
        block_data["publish_status"] = "live"
        block_data.pop("scheduled_at", None)
        row.seo_block = block_data
        published += 1
        logger.info("Scheduled page went live: /%s", row.slug)
    if published:
        await session.commit()
        try:
            from services.sitemap_service import persist_live_sitemaps
            await persist_live_sitemaps(session, site_base=LIVE_SITE)
        except Exception:
            logger.exception("Sitemap update after scheduled publish failed")
    return published
