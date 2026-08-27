"""IndexNow — notify Bing, Yandex, and partners of new/updated URLs (free)."""
from __future__ import annotations

import logging
from urllib.parse import urlparse

from config import settings

logger = logging.getLogger(__name__)

_ENDPOINT = "https://api.indexnow.org/indexnow"
_BING_SITEMAP_PING = "https://www.bing.com/ping"


def is_configured() -> bool:
    return bool((getattr(settings, "INDEXNOW_KEY", "") or "").strip())


def host_key() -> str:
    return (getattr(settings, "INDEXNOW_KEY", "") or "").strip()


def submit_urls(urls: list[str]) -> dict:
    key = host_key()
    cleaned = [u.strip() for u in urls if (u or "").strip().startswith("http")]
    if not key or not cleaned:
        return {"ok": False, "detail": "missing key or urls"}
    host = urlparse(cleaned[0]).hostname or "zeorbit.com"
    key_location = f"https://{host}/{key}.txt"
    payload = {
        "host": host,
        "key": key,
        "keyLocation": key_location,
        "urlList": cleaned[:10_000],
    }
    try:
        import httpx
        r = httpx.post(_ENDPOINT, json=payload, timeout=20)
        ok = r.status_code in (200, 202)
        if not ok:
            logger.warning("IndexNow %s -> %s %s", cleaned[0], r.status_code, r.text[:200])
        return {"ok": ok, "status": r.status_code, "detail": (r.text or "")[:200]}
    except Exception as e:
        logger.warning("IndexNow failed: %s", e)
        return {"ok": False, "detail": str(e)}


def ping_bing_sitemap(sitemap_url: str) -> dict:
    if not sitemap_url:
        return {"ok": False, "detail": "no sitemap"}
    try:
        import httpx
        r = httpx.get(_BING_SITEMAP_PING, params={"sitemap": sitemap_url}, timeout=15)
        return {"ok": r.status_code < 400, "status": r.status_code}
    except Exception as e:
        logger.warning("Bing sitemap ping failed: %s", e)
        return {"ok": False, "detail": str(e)}
