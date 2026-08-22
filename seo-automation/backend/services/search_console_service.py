"""
search_console_service.py — official Google Search Console API integration:
Sitemaps API (tell Google to (re)fetch a sitemap) and URL Inspection API
(check a URL's real indexing status). Both are self-serve, no special Google
approval needed — unlike the Indexing API, which is NOT used here for blog
content since Google restricts it to JobPosting/BroadcastEvent pages.

Reuses the same service-account key file as indexing_service.py (already an
Owner on the Search Console property) — just requested with the
webmasters/searchconsole scope instead of the indexing scope.
"""
import os
import logging
from urllib.parse import quote, urlparse, urlunparse

from config import settings

logger = logging.getLogger(__name__)

_SCOPES = ["https://www.googleapis.com/auth/webmasters"]
_SITEMAPS_ENDPOINT = "https://www.googleapis.com/webmasters/v3/sites/{site}/sitemaps/{feed}"
_INSPECT_ENDPOINT = "https://searchconsole.googleapis.com/v1/urlInspection/index:inspect"

_session = None
_loaded = False


def _get_session():
    global _session, _loaded
    if _loaded:
        return _session
    _loaded = True
    keyfile = settings.GOOGLE_INDEXING_KEY_FILE
    if not keyfile or not os.path.exists(keyfile):
        logger.info("Search Console API: no key file configured — disabled.")
        return None
    try:
        from google.oauth2 import service_account
        from google.auth.transport.requests import AuthorizedSession
        creds = service_account.Credentials.from_service_account_file(keyfile, scopes=_SCOPES)
        _session = AuthorizedSession(creds)
        logger.info("Search Console API: authenticated.")
    except Exception as e:
        logger.error(f"Search Console API auth failed: {e}")
        _session = None
    return _session


def is_configured() -> bool:
    return _get_session() is not None and bool(settings.GSC_SITE_URL)


def _inspection_url(url: str) -> str:
    """Map apex/www so inspection stays under the verified www.zeorbit.com property."""
    site = (settings.GSC_SITE_URL or "").strip()
    if not site.startswith("http") or not url:
        return url
    try:
        su = urlparse(site)
        uu = urlparse(url)

        def root(host: str) -> str:
            h = (host or "").lower()
            return h[4:] if h.startswith("www.") else h

        if su.netloc and uu.netloc and root(su.netloc) == root(uu.netloc) and su.netloc.lower() != uu.netloc.lower():
            return urlunparse((su.scheme or uu.scheme, su.netloc, uu.path, uu.params, uu.query, uu.fragment))
    except Exception:
        pass
    return url


def ping_google_sitemap(sitemap_url: str) -> dict:
    """Public sitemap ping — complements Search Console submit."""
    if not sitemap_url:
        return {"ok": False, "detail": "no sitemap_url"}
    try:
        import httpx
        r = httpx.get("https://www.google.com/ping", params={"sitemap": sitemap_url}, timeout=15)
        return {"ok": r.status_code < 400, "status": r.status_code}
    except Exception as e:
        logger.warning(f"Google sitemap ping failed: {e}")
        return {"ok": False, "detail": str(e)}


def submit_sitemap(sitemap_url: str) -> dict:
    """PUT the sitemap to Search Console's Sitemaps API — an official hint
    for Google to (re)fetch it. Idempotent, safe to call after every publish."""
    session = _get_session()
    site_url = settings.GSC_SITE_URL
    if session is None or not site_url:
        return {"ok": False, "detail": "Search Console not configured"}
    if not sitemap_url:
        return {"ok": False, "detail": "no sitemap_url"}
    try:
        from urllib.parse import quote
        url = _SITEMAPS_ENDPOINT.format(site=quote(site_url, safe=""), feed=quote(sitemap_url, safe=""))
        r = session.put(url, timeout=20)
        ok = r.status_code in (200, 204)
        if not ok:
            logger.warning(f"Sitemap submit {sitemap_url} -> {r.status_code}: {r.text[:200]}")
        ping_google_sitemap(sitemap_url)
        return {"ok": ok, "status": r.status_code, "detail": r.text[:300]}
    except Exception as e:
        logger.error(f"Sitemap submit error for {sitemap_url}: {e}")
        return {"ok": False, "detail": str(e)}


_COVERAGE_TO_STATUS = {
    "submitted and indexed": "indexed",
    "indexed, though blocked by robots.txt": "not_indexed",
    "indexed without content": "indexed",
    "discovered - currently not indexed": "submitted",
    "crawled - currently not indexed": "crawled",
    "url is unknown to google": "not_indexed",
    "page with redirect": "not_indexed",
}


def inspect_url(url: str) -> dict:
    """POST to the URL Inspection API — the official, correct way to check
    real indexing status for a normal page (not the Indexing API)."""
    session = _get_session()
    site_url = settings.GSC_SITE_URL
    if session is None or not site_url:
        return {"ok": False, "detail": "Search Console not configured"}
    try:
        r = session.post(
            _INSPECT_ENDPOINT,
            json={"inspectionUrl": _inspection_url(url), "siteUrl": site_url},
            timeout=20,
        )
        if r.status_code != 200:
            logger.warning(f"URL Inspection {url} -> {r.status_code}: {r.text[:200]}")
            return {"ok": False, "status": r.status_code, "detail": r.text[:300]}
        data = r.json()
        result = data.get("inspectionResult", {})
        index_result = result.get("indexStatusResult", {})
        coverage_state = index_result.get("coverageState", "")
        key = coverage_state.lower().strip()
        status = _COVERAGE_TO_STATUS.get(key)
        if status is None:
            if "crawled" in key:
                status = "crawled"
            elif "discovered" in key:
                status = "submitted"
            elif "indexed" in key and "not indexed" not in key:
                status = "indexed"
            else:
                status = "not_indexed"
        return {
            "ok": True,
            "status": status,
            "coverage_state": coverage_state,
            "verdict": index_result.get("verdict", ""),
            "last_crawl_time": index_result.get("lastCrawlTime", ""),
            "raw": result,
        }
    except Exception as e:
        logger.error(f"URL Inspection error for {url}: {e}")
        return {"ok": False, "detail": str(e)}
