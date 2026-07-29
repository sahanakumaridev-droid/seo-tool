"""
seo_indexing.py — status dashboard + refresh endpoint for the free Google
Search automation pipeline (sitemap + Search Console URL Inspection).
Every WordPress publish is tracked here via routes/wordpress.py::_track_and_verify.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db import get_session, PublishedUrlRecord
from services import crawl_check_service, search_console_service
from config import settings
from datetime import datetime, timezone

router = APIRouter()


def _to_dict(rec: PublishedUrlRecord) -> dict:
    return {
        "id": rec.id,
        "url": rec.url,
        "source": rec.source,
        "post_id": rec.post_id,
        "title": rec.title,
        "status": rec.status,
        "http_status": rec.http_status,
        "robots_allowed": rec.robots_allowed,
        "has_noindex": rec.has_noindex,
        "canonical_ok": rec.canonical_ok,
        "coverage_state": rec.coverage_state,
        "error_message": rec.error_message,
        "sitemap_submitted_at": rec.sitemap_submitted_at.isoformat() if rec.sitemap_submitted_at else None,
        "last_inspected_at": rec.last_inspected_at.isoformat() if rec.last_inspected_at else None,
        "created_at": rec.created_at.isoformat() if rec.created_at else None,
        "updated_at": rec.updated_at.isoformat() if rec.updated_at else None,
    }


@router.get("/status")
async def get_status(session: AsyncSession = Depends(get_session)):
    rows = (await session.execute(
        select(PublishedUrlRecord).order_by(PublishedUrlRecord.created_at.desc())
    )).scalars().all()
    return {
        "gsc_configured": search_console_service.is_configured(),
        "urls": [_to_dict(r) for r in rows],
    }


@router.post("/refresh")
async def refresh_status(id: Optional[int] = None, session: AsyncSession = Depends(get_session)):
    """Re-run crawl checks + a fresh Search Console URL Inspection for
    tracked URLs not yet 'indexed' (or a single URL via ?id=). Indexing
    itself happens on Google's own schedule — this just reflects the latest
    real status, it can't force it."""
    stmt = select(PublishedUrlRecord)
    if id is not None:
        stmt = stmt.where(PublishedUrlRecord.id == id)
    else:
        stmt = stmt.where(PublishedUrlRecord.status != "indexed")
    rows = (await session.execute(stmt)).scalars().all()

    updated = []
    for rec in rows:
        check = await crawl_check_service.check_url(rec.url)
        rec.http_status = check["http_status"]
        rec.robots_allowed = check["robots_allowed"]
        rec.has_noindex = check["has_noindex"]
        rec.canonical_ok = check["canonical_ok"]
        if not check["ok"]:
            rec.status = "error"
            rec.error_message = check["error"]
            updated.append(_to_dict(rec))
            continue

        inspect = search_console_service.inspect_url(rec.url)
        if inspect.get("ok"):
            rec.status = inspect["status"]
            rec.coverage_state = inspect.get("coverage_state", "")
            rec.last_inspected_at = datetime.now(timezone.utc)
            rec.error_message = ""
        updated.append(_to_dict(rec))

    await session.commit()
    return {"refreshed": len(updated), "urls": updated}
