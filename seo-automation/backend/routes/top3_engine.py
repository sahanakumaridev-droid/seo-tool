from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from urllib.parse import quote

from config import settings
from services.top3_engine import run_top3_engine
from services import crawl_check_service, search_console_service

router = APIRouter()


class Top3Request(BaseModel):
    website: str = Field(..., examples=["https://zeorbit.com"])
    keyword: str = Field(..., examples=["best web designer in San Diego"])


class GscInspectRequest(BaseModel):
    url: str = Field(..., examples=["https://zeorbit.com/web-designer-near-me"])


@router.post("/analyze")
async def analyze_top3(payload: Top3Request):
    try:
        return await run_top3_engine(payload.website, payload.keyword)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Top 3 analysis failed: {e}")


@router.post("/gsc-inspect")
async def gsc_inspect(payload: GscInspectRequest):
    """Official Google Search Console URL Inspection — is this URL live in Google's index?"""
    url = (payload.url or "").strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url.lstrip("/")
    crawl = await crawl_check_service.check_url(url)
    gsc_ok = search_console_service.is_configured()
    inspect = search_console_service.inspect_url(url) if gsc_ok else {
        "ok": False,
        "detail": "Search Console API is not connected. Open the Google inspect link below, or finish GSC setup on Search Indexing.",
    }
    indexed = bool(inspect.get("ok") and inspect.get("status") == "indexed")
    from urllib.parse import urlparse as _up
    host = (_up(url).hostname or "").lower()
    if host.startswith("www."):
        host = host[4:]
    resource = f"sc-domain:{host}" if host else (settings.GSC_SITE_URL or "")
    # Do not append &id= — Google returns 404 on that inspect deep-link.
    inspect_link = (
        "https://search.google.com/search-console/inspect"
        f"?resource_id={quote(resource, safe='')}"
    )
    return {
        "url": url,
        "gsc_configured": gsc_ok,
        "live_in_google": indexed if inspect.get("ok") else None,
        "coverage_state": inspect.get("coverage_state") or "",
        "verdict": inspect.get("verdict") or "",
        "last_crawl_time": inspect.get("last_crawl_time") or "",
        "gsc_status": inspect.get("status") or "",
        "gsc_ok": bool(inspect.get("ok")),
        "gsc_detail": inspect.get("detail") or "",
        "http_live": bool(crawl.get("ok")),
        "http_status": crawl.get("http_status"),
        "robots_allowed": crawl.get("robots_allowed"),
        "has_noindex": crawl.get("has_noindex"),
        "canonical_ok": crawl.get("canonical_ok"),
        "crawl_error": crawl.get("error") or "",
        "inspect_link": inspect_link,
        "howto": (
            "Open URL inspection, paste the full page URL into Google's box, then Request indexing if needed. "
            "Indexed means Google knows the page — not Top 3 or AI Mode."
        ),
    }
