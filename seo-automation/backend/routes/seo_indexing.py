"""
seo_indexing.py — production-ready free indexing status.

Priority:
  1. Google Search Console URL Inspection (free official API) when configured
  2. Free crawl checks (HTTP / robots / noindex / canonical) — no Google bill
  3. DEMO_MODE sample rows only when empty + demo enabled + no live data path needed
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db import get_session, PublishedUrlRecord
from services import crawl_check_service, search_console_service
from providers.demo_google import use_demo_fallback, build_demo_index_urls
from datetime import datetime, timezone

router = APIRouter()


class InspectUrlRequest(BaseModel):
    url: str = Field(..., min_length=8, description="Public URL to crawl-check")
    title: str = ""


def _to_dict(rec: PublishedUrlRecord, demo: bool = False) -> dict:
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
        "demo": demo,
    }


def _apply_free_crawl(rec: PublishedUrlRecord, check: dict) -> None:
    """Production free path when GSC isn't configured — honest crawl readiness."""
    rec.http_status = check.get("http_status")
    rec.robots_allowed = check.get("robots_allowed")
    rec.has_noindex = check.get("has_noindex")
    rec.canonical_ok = check.get("canonical_ok")
    rec.last_inspected_at = datetime.now(timezone.utc)
    if not check.get("ok"):
        rec.status = "error"
        rec.error_message = check.get("error") or "Crawl check failed"
        rec.coverage_state = "Not crawl-ready"
        return
    rec.error_message = ""
    # Never claim Google indexed without GSC — report crawl readiness instead.
    if rec.status in ("indexed", "discovered", "not_indexed"):
        pass  # keep prior GSC-ish status if we somehow had it
    else:
        rec.status = "sitemap_added" if rec.status == "sitemap_added" else "published"
    rec.coverage_state = "Crawl-ready (free check) — connect Search Console for live index status"
    if check.get("canonical_ok") is False:
        rec.coverage_state += " · canonical mismatch"


@router.get("/status")
async def get_status(session: AsyncSession = Depends(get_session)):
    rows = (await session.execute(
        select(PublishedUrlRecord).order_by(PublishedUrlRecord.created_at.desc())
    )).scalars().all()

    gsc_configured = search_console_service.is_configured()
    mode = "gsc" if gsc_configured else "crawl"

    if not rows and use_demo_fallback(live_configured=gsc_configured):
        return {
            "gsc_configured": False,
            "demo": True,
            "mode": "demo",
            "urls": build_demo_index_urls(),
        }

    return {
        "gsc_configured": gsc_configured,
        "demo": False,
        "mode": mode,
        "urls": [_to_dict(r) for r in rows],
    }


@router.post("/inspect")
async def inspect_url(req: InspectUrlRequest, session: AsyncSession = Depends(get_session)):
    """Free production inspect: crawl-check a URL and track it. Uses GSC when configured."""
    url = req.url.strip()
    if not url.startswith(("http://", "https://")):
        raise HTTPException(status_code=400, detail="URL must start with http:// or https://")

    gsc_configured = search_console_service.is_configured()
    check = await crawl_check_service.check_url(url)

    existing = (await session.execute(
        select(PublishedUrlRecord).where(PublishedUrlRecord.url == url)
    )).scalar_one_or_none()

    rec = existing or PublishedUrlRecord(
        url=url,
        source="manual",
        post_id="",
        title=req.title.strip() or url,
        status="published",
    )
    if not existing:
        session.add(rec)

    if not check.get("ok"):
        _apply_free_crawl(rec, check)
    elif gsc_configured:
        rec.http_status = check["http_status"]
        rec.robots_allowed = check["robots_allowed"]
        rec.has_noindex = check["has_noindex"]
        rec.canonical_ok = check["canonical_ok"]
        inspect = search_console_service.inspect_url(url)
        if inspect.get("ok"):
            rec.status = inspect["status"]
            rec.coverage_state = inspect.get("coverage_state", "")
            rec.last_inspected_at = datetime.now(timezone.utc)
            rec.error_message = ""
        else:
            _apply_free_crawl(rec, check)
            rec.coverage_state = inspect.get("detail") or rec.coverage_state
    else:
        _apply_free_crawl(rec, check)

    await session.commit()
    await session.refresh(rec)
    return {
        "ok": check.get("ok", False),
        "demo": False,
        "mode": "gsc" if gsc_configured else "crawl",
        "url": _to_dict(rec),
    }


@router.post("/refresh")
async def refresh_status(id: Optional[int] = None, session: AsyncSession = Depends(get_session)):
    """Re-run free crawl checks (+ GSC inspect when configured)."""
    gsc_configured = search_console_service.is_configured()

    rows_all = (await session.execute(select(PublishedUrlRecord))).scalars().all()
    if not rows_all and use_demo_fallback(live_configured=gsc_configured):
        urls = build_demo_index_urls()
        for u in urls:
            if u["status"] == "published":
                u["status"] = "discovered"
                u["coverage_state"] = "Discovered – currently not indexed"
            elif u["status"] == "sitemap_added":
                u["status"] = "discovered"
                u["coverage_state"] = "Discovered – currently not indexed"
            elif u["status"] == "discovered":
                u["status"] = "indexed"
                u["coverage_state"] = "Submitted and indexed"
            u["last_inspected_at"] = datetime.now(timezone.utc).isoformat()
        return {"refreshed": len(urls), "demo": True, "mode": "demo", "urls": urls}

    stmt = select(PublishedUrlRecord)
    if id is not None:
        stmt = stmt.where(PublishedUrlRecord.id == id)
    else:
        stmt = stmt.where(PublishedUrlRecord.status != "indexed")
    rows = (await session.execute(stmt)).scalars().all()

    updated = []
    for rec in rows:
        check = await crawl_check_service.check_url(rec.url)
        if not check.get("ok"):
            _apply_free_crawl(rec, check)
            updated.append(_to_dict(rec))
            continue

        if gsc_configured:
            rec.http_status = check["http_status"]
            rec.robots_allowed = check["robots_allowed"]
            rec.has_noindex = check["has_noindex"]
            rec.canonical_ok = check["canonical_ok"]
            inspect = search_console_service.inspect_url(rec.url)
            if inspect.get("ok"):
                rec.status = inspect["status"]
                rec.coverage_state = inspect.get("coverage_state", "")
                rec.last_inspected_at = datetime.now(timezone.utc)
                rec.error_message = ""
            else:
                _apply_free_crawl(rec, check)
        else:
            _apply_free_crawl(rec, check)
        updated.append(_to_dict(rec))

    await session.commit()
    return {
        "refreshed": len(updated),
        "demo": False,
        "mode": "gsc" if gsc_configured else "crawl",
        "urls": updated,
    }


@router.get("/setup")
async def setup_checklist():
    """What is wired for Google Search discovery of /p/ pages."""
    from config import settings
    import os

    key = settings.GOOGLE_INDEXING_KEY_FILE or ""
    base = (settings.PUBLIC_BASE_URL or "").rstrip("/")
    gsc = search_console_service.is_configured()
    steps = [
        {
            "id": "public_base",
            "label": "Public site URL",
            "done": bool(base),
            "detail": base or "Set PUBLIC_BASE_URL",
        },
        {
            "id": "sitemap",
            "label": "Sitemap live",
            "done": bool(base),
            "detail": f"{base}/sitemap.xml" if base else "Needs PUBLIC_BASE_URL",
            "href": f"{base}/sitemap.xml" if base else None,
        },
        {
            "id": "gsc_property",
            "label": "Search Console property",
            "done": bool(settings.GSC_SITE_URL),
            "detail": settings.GSC_SITE_URL or "Set GSC_SITE_URL (URL-prefix of your /p/ host)",
            "href": "https://search.google.com/search-console",
        },
        {
            "id": "verification",
            "label": "Site verification meta/file",
            "done": bool(settings.GSC_VERIFICATION_META or settings.GSC_VERIFICATION_FILENAME),
            "detail": (
                "Verification token set"
                if (settings.GSC_VERIFICATION_META or settings.GSC_VERIFICATION_FILENAME)
                else "Paste GSC HTML-tag token into GSC_VERIFICATION_META, then restart"
            ),
        },
        {
            "id": "service_account",
            "label": "Service account JSON key",
            "done": bool(key) and os.path.exists(key),
            "detail": key if key else "Run: python3 scripts/setup_gsc.py",
        },
        {
            "id": "api_live",
            "label": "Search Console API connected",
            "done": gsc,
            "detail": "Ready to submit sitemap + inspect URLs" if gsc else "Complete steps above, add SA as Owner in GSC",
        },
    ]
    return {
        "ready": gsc,
        "public_base_url": base,
        "gsc_site_url": settings.GSC_SITE_URL,
        "sitemap_url": f"{base}/sitemap.xml" if base else "",
        "setup_cmd": "python3 scripts/setup_gsc.py",
        "steps": steps,
    }


@router.post("/push-all")
async def push_all_to_google(session: AsyncSession = Depends(get_session)):
    """Bootstrap every published /p/ page into tracking + submit sitemap to GSC."""
    from config import settings
    from db import PageRecord

    base = (settings.PUBLIC_BASE_URL or "").rstrip("/")
    if not base:
        raise HTTPException(status_code=400, detail="Set PUBLIC_BASE_URL first")

    pages = (await session.execute(select(PageRecord))).scalars().all()
    created = 0
    for page in pages:
        url = f"{base}/{page.slug}"
        title = ""
        if isinstance(page.seo_block, dict):
            title = page.seo_block.get("title") or ""
        existing = (
            await session.execute(select(PublishedUrlRecord).where(PublishedUrlRecord.url == url))
        ).scalar_one_or_none()
        if existing:
            if title and not existing.title:
                existing.title = title
            continue
        session.add(
            PublishedUrlRecord(
                url=url,
                source="public_web",
                title=title or page.slug,
                status="published",
            )
        )
        created += 1
    await session.commit()

    sitemap = f"{base}/sitemap.xml"
    sitemap_result = {"ok": False, "detail": "Search Console not configured"}
    gsc = search_console_service.is_configured()
    if gsc:
        sitemap_result = search_console_service.submit_sitemap(sitemap)

    # Crawl-check a sample of newest tracked URLs so the UI isn't empty of status
    rows = (
        await session.execute(
            select(PublishedUrlRecord).order_by(PublishedUrlRecord.created_at.desc()).limit(25)
        )
    ).scalars().all()
    inspected = 0
    for rec in rows:
        check = await crawl_check_service.check_url(rec.url)
        if not check.get("ok"):
            _apply_free_crawl(rec, check)
            continue
        if gsc:
            rec.http_status = check["http_status"]
            rec.robots_allowed = check["robots_allowed"]
            rec.has_noindex = check["has_noindex"]
            rec.canonical_ok = check["canonical_ok"]
            inspect = search_console_service.inspect_url(rec.url)
            if inspect.get("ok"):
                rec.status = inspect["status"]
                rec.coverage_state = inspect.get("coverage_state", "")
                rec.last_inspected_at = datetime.now(timezone.utc)
                rec.error_message = ""
                inspected += 1
            else:
                _apply_free_crawl(rec, check)
                if sitemap_result.get("ok"):
                    rec.status = "sitemap_submitted"
                    rec.sitemap_submitted_at = datetime.now(timezone.utc)
        else:
            _apply_free_crawl(rec, check)
            rec.status = "published_awaiting_gsc"
            rec.coverage_state = "Awaiting Search Console connection"
    await session.commit()

    all_rows = (
        await session.execute(select(PublishedUrlRecord).order_by(PublishedUrlRecord.created_at.desc()))
    ).scalars().all()
    return {
        "ok": True,
        "gsc_configured": gsc,
        "pages_tracked_new": created,
        "sitemap": sitemap_result,
        "sitemap_url": sitemap,
        "inspected": inspected,
        "mode": "gsc" if gsc else "crawl",
        "urls": [_to_dict(r) for r in all_rows[:100]],
        "next": (
            None
            if gsc
            else "Run python3 scripts/setup_gsc.py, verify the property in Search Console, add the service account as Owner."
        ),
    }
