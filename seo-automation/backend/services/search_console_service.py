"""
search_console_service.py — Search Console: sitemaps, URL Inspection, Search Analytics.
"""
import logging
from datetime import date, timedelta
from pathlib import Path
from urllib.parse import quote, urlparse, urlunparse

from config import settings, _BACKEND_ROOT

logger = logging.getLogger(__name__)

_SCOPES = ["https://www.googleapis.com/auth/webmasters"]
_SITEMAPS_ENDPOINT = "https://www.googleapis.com/webmasters/v3/sites/{site}/sitemaps/{feed}"
_INSPECT_ENDPOINT = "https://searchconsole.googleapis.com/v1/urlInspection/index:inspect"
_ANALYTICS_ENDPOINT = "https://www.googleapis.com/webmasters/v3/sites/{site}/searchAnalytics/query"
_SITES_ENDPOINT = "https://www.googleapis.com/webmasters/v3/sites"

_session = None
_auth_error = ""


def resolve_key_file() -> str:
    raw = (settings.GOOGLE_INDEXING_KEY_FILE or "").strip()
    if not raw:
        return ""
    candidates = [Path(raw)]
    if not Path(raw).is_absolute():
        candidates.extend([
            _BACKEND_ROOT / raw,
            _BACKEND_ROOT / "secrets" / Path(raw).name,
            Path("/opt/seo-tool/backend") / raw,
        ])
    for p in candidates:
        try:
            if p.is_file():
                return str(p.resolve())
        except OSError:
            continue
    return raw


def _get_session():
    global _session, _auth_error
    if _session is not None:
        return _session
    keyfile = resolve_key_file()
    if not keyfile or not Path(keyfile).is_file():
        _auth_error = f"Key file missing: {keyfile or '(empty GOOGLE_INDEXING_KEY_FILE)'}"
        logger.info("Search Console API: %s", _auth_error)
        return None
    try:
        from google.oauth2 import service_account
        from google.auth.transport.requests import AuthorizedSession
        creds = service_account.Credentials.from_service_account_file(keyfile, scopes=_SCOPES)
        _session = AuthorizedSession(creds)
        _auth_error = ""
        logger.info("Search Console API: authenticated (%s)", keyfile)
    except Exception as e:
        _auth_error = str(e)
        logger.error("Search Console API auth failed: %s", e)
        _session = None
    return _session


def is_configured() -> bool:
    return _get_session() is not None and bool((settings.GSC_SITE_URL or "").strip())


def connection_status() -> dict:
    session = _get_session()
    site = (settings.GSC_SITE_URL or "").strip()
    key = resolve_key_file()
    sites = []
    probe = ""
    if session is not None:
        try:
            r = session.get(_SITES_ENDPOINT, timeout=20)
            if r.status_code == 200:
                sites = [s.get("siteUrl") for s in (r.json().get("siteEntry") or []) if s.get("siteUrl")]
            else:
                probe = f"sites list HTTP {r.status_code}: {(r.text or '')[:180]}"
        except Exception as e:
            probe = str(e)
    listed = True
    if sites and site:
        variants = {site, site.rstrip("/") + "/", site.rstrip("/")}
        listed = any(v in sites for v in variants)
    return {
        "configured": bool(session is not None and site),
        "gsc_site_url": site,
        "key_file": key,
        "key_exists": bool(key and Path(key).is_file()),
        "auth_ok": session is not None,
        "auth_error": _auth_error,
        "sites": sites,
        "property_listed": listed,
        "probe": probe,
        "note": "Search Analytics lags 2–3 days. This is Google Search traffic, not ChatGPT.",
    }


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
    sitemap_url = _inspection_url(sitemap_url)
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


def _analytics_query(site_url: str, body: dict) -> dict:
    session = _get_session()
    if session is None or not site_url:
        return {"ok": False, "detail": "Search Console not configured", "rows": []}
    url = _ANALYTICS_ENDPOINT.format(site=quote(site_url, safe=""))
    try:
        r = session.post(url, json=body, timeout=45)
        if r.status_code != 200:
            return {"ok": False, "detail": f"HTTP {r.status_code}: {(r.text or '')[:300]}", "rows": []}
        data = r.json()
        return {"ok": True, "rows": data.get("rows") or [], "responseAggregationType": data.get("responseAggregationType")}
    except Exception as e:
        return {"ok": False, "detail": str(e), "rows": []}


def fetch_performance(days: int = 28) -> dict:
    """Clicks / impressions / CTR / position for the verified GSC property."""
    days = max(7, min(int(days or 28), 90))
    site = (settings.GSC_SITE_URL or "").strip()
    # GSC Search Analytics is delayed ~2 days.
    end = date.today() - timedelta(days=2)
    start = end - timedelta(days=days - 1)
    start_s, end_s = start.isoformat(), end.isoformat()
    conn = connection_status()
    if not conn.get("configured"):
        return {
            "ok": False,
            "detail": conn.get("auth_error") or "Search Console not configured",
            "connection": conn,
            "start_date": start_s,
            "end_date": end_s,
            "totals": {"clicks": 0, "impressions": 0, "ctr": 0, "position": 0},
            "by_date": [],
            "queries": [],
            "pages": [],
        }

    base_body = {"startDate": start_s, "endDate": end_s, "rowLimit": 250}

    by_date = _analytics_query(site, {**base_body, "dimensions": ["date"]})
    queries = _analytics_query(site, {**base_body, "dimensions": ["query"], "rowLimit": 50})
    pages = _analytics_query(site, {**base_body, "dimensions": ["page"], "rowLimit": 50})

    def rows_dim(result: dict, key: str) -> list:
        out = []
        for row in result.get("rows") or []:
            keys = row.get("keys") or [""]
            out.append({
                key: keys[0],
                "clicks": row.get("clicks") or 0,
                "impressions": row.get("impressions") or 0,
                "ctr": round((row.get("ctr") or 0) * 100, 2),
                "position": round(row.get("position") or 0, 1),
            })
        return out

    date_rows = rows_dim(by_date, "date")
    date_rows.sort(key=lambda r: r["date"])
    clicks = sum(r["clicks"] for r in date_rows)
    imps = sum(r["impressions"] for r in date_rows)
    ctr = round((clicks / imps * 100) if imps else 0, 2)
    pos = round(
        (sum(r["position"] * r["impressions"] for r in date_rows) / imps) if imps else 0,
        1,
    )
    err = next((r.get("detail") for r in (by_date, queries, pages) if not r.get("ok") and r.get("detail")), "")
    return {
        "ok": by_date.get("ok") or queries.get("ok") or pages.get("ok"),
        "detail": err,
        "connection": conn,
        "start_date": start_s,
        "end_date": end_s,
        "days": days,
        "totals": {"clicks": clicks, "impressions": imps, "ctr": ctr, "position": pos},
        "by_date": date_rows,
        "queries": rows_dim(queries, "query"),
        "pages": rows_dim(pages, "page"),
    }
