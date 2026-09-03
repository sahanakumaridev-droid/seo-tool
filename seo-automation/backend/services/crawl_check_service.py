"""
crawl_check_service.py — verifies a freshly published URL is actually
crawlable by Google BEFORE it's handed off to the sitemap/Search Console
pipeline. Pure HTTP checks, no Google API calls, no credentials needed.
"""
import re
import logging
import urllib.robotparser
from urllib.parse import urlparse

import httpx

logger = logging.getLogger(__name__)

_NOINDEX_RE = re.compile(r'<meta[^>]+name=["\']robots["\'][^>]*content=["\']([^"\']*)["\']', re.IGNORECASE)
_CANONICAL_RE = re.compile(r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\']([^"\']+)["\']', re.IGNORECASE)


async def check_url(url: str) -> dict:
    """Returns:
    {
      "ok": bool,                # overall pass/fail — False blocks the pipeline
      "http_status": int|None,
      "robots_allowed": bool|None,
      "has_noindex": bool,
      "canonical_ok": bool,
      "canonical_url": str,
      "error": str,              # human-readable reason when ok=False
    }
    """
    if url and "://" not in url:
        url = "https://" + url.lstrip("/")
    parsed = urlparse(url)
    result = {
        "ok": False, "http_status": None, "robots_allowed": None,
        "has_noindex": False, "canonical_ok": False, "canonical_url": "", "error": "",
    }

    try:
        async with httpx.AsyncClient(timeout=20, follow_redirects=True) as client:
            resp = await client.get(url)
    except Exception as e:
        result["error"] = f"Could not fetch URL: {e}"
        return result

    result["http_status"] = resp.status_code
    if resp.status_code != 200:
        result["error"] = f"URL returned HTTP {resp.status_code}, expected 200"
        return result

    html = resp.text
    robots_tag = (resp.headers.get("x-robots-tag") or "").lower()
    if "noindex" in robots_tag:
        result["has_noindex"] = True
        result["error"] = "Response has X-Robots-Tag: noindex"
        return result
    if "us-only" in html.lower() and "available in the united states" in html.lower():
        result["has_noindex"] = True
        result["error"] = "URL served the US-only interstitial instead of the real page"
        return result

    # robots.txt — is this path allowed for Googlebot?
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(robots_url)
        rp = urllib.robotparser.RobotFileParser()
        rp.parse((r.text if r.status_code == 200 else "").splitlines())
        result["robots_allowed"] = rp.can_fetch("Googlebot", url)
    except Exception as e:
        logger.warning(f"robots.txt check failed for {url}: {e}")
        result["robots_allowed"] = True  # absence/failure to fetch = not blocked, per robots.txt spec

    if result["robots_allowed"] is False:
        result["error"] = "URL is disallowed by robots.txt for Googlebot"
        return result

    # noindex
    m = _NOINDEX_RE.search(html)
    if m and "noindex" in m.group(1).lower():
        result["has_noindex"] = True
        result["error"] = "Page has a noindex meta tag"
        return result

    # canonical
    m = _CANONICAL_RE.search(html)
    canonical = m.group(1).strip() if m else ""
    result["canonical_url"] = canonical
    result["canonical_ok"] = bool(canonical) and canonical.rstrip("/") == url.rstrip("/")

    result["ok"] = True
    return result
