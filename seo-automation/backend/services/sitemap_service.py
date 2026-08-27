"""Editorial URLs that belong in post-sitemap.xml (blogs only, not location tests)."""
from __future__ import annotations

import re
from datetime import date
from urllib.parse import urlparse

from sqlalchemy import select

from db import PageRecord, PublishedUrlRecord

_TEST_LANDING = re.compile(
    r"^/(contractors|healthcare|web-design|plumbing|software-engineer|"
    r"local-service|website-redesign|education)[-/]",
    re.I,
)
SITE_MENU_PATHS = (
    "/",
    "/website-designing",
    "/mobile-apps",
    "/seo-ppc",
    "/custom-software",
    "/portfolio",
    "/contact",
    "/blog",
    "/areas",
    "/privacy-policy",
)

_MENU = {p.rstrip("/") or "/" for p in SITE_MENU_PATHS} | {"", "/"}


def _xml_esc(url: str) -> str:
    return (
        (url or "")
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


async def editorial_post_urls(session, *, site_base: str, limit: int = 2000) -> list[tuple[str, str]]:
    """Return (loc, lastmod) for published blog/post pages on the live site."""
    base = (site_base or "https://zeorbit.com").rstrip("/")
    today = date.today().isoformat()
    seen: set[str] = set()
    out: list[tuple[str, str]] = []

    def add(loc: str, lastmod: str = today):
        loc = (loc or "").rstrip("/")
        if not loc or loc in seen:
            return
        seen.add(loc)
        out.append((loc, lastmod or today))

    rows = (await session.execute(select(PageRecord).order_by(PageRecord.updated_at.desc()))).scalars().all()
    for r in rows:
        if len(out) >= limit:
            break
        slug = (r.slug or "").strip("/")
        if not slug:
            continue
        block = r.seo_block if isinstance(r.seo_block, dict) else {}
        kind = (block.get("content_type") or "service").lower()
        if kind not in ("blog", "post"):
            continue
        lastmod = today
        ts = r.updated_at or r.created_at
        if ts:
            try:
                lastmod = ts.date().isoformat() if hasattr(ts, "date") else str(ts)[:10]
            except Exception:
                lastmod = today
        add(f"{base}/{slug}", lastmod)

    try:
        tracked = (
            await session.execute(
                select(PublishedUrlRecord)
                .where(PublishedUrlRecord.status != "error")
                .order_by(PublishedUrlRecord.created_at.desc())
                .limit(400)
            )
        ).scalars().all()
    except Exception:
        tracked = []

    page_slugs = {r.slug for r in rows if r.slug}
    for u in tracked:
        if len(out) >= limit:
            break
        raw = (u.url or "").strip()
        if not raw:
            continue
        parsed = urlparse(raw if "://" in raw else f"https://{raw}")
        host = (parsed.hostname or "").lower()
        if "nip.io" in host or host.startswith("seo."):
            continue
        path = (parsed.path or "").rstrip("/") or "/"
        if _TEST_LANDING.search(path):
            continue
        if path.startswith("/p/"):
            slug = path.rsplit("/", 1)[-1]
            if slug in page_slugs:
                continue
            if _TEST_LANDING.search(f"/{slug}"):
                continue
            add(f"{base}/{slug}")
            continue
        if host and "zeorbit.com" not in host:
            continue
        if path in _MENU:
            continue
        add(raw if "://" in raw else f"{base}{path}")

    return out


async def sitemap_overview(session, *, site_base: str) -> dict:
    """JSON for the SEO-tool Sitemap screen (not a public XML change)."""
    from datetime import date

    base = (site_base or "https://zeorbit.com").rstrip("/")
    today = date.today().isoformat()

    pages = []
    for path in SITE_MENU_PATHS:
        loc = base if path == "/" else f"{base}{path}"
        pages.append({"loc": loc, "lastmod": today, "kind": "menu", "changefreq": "weekly"})

    loc_pages = []
    rows = (await session.execute(select(PageRecord).order_by(PageRecord.updated_at.desc()))).scalars().all()
    for r in rows:
        slug = (r.slug or "").strip("/")
        if not slug:
            continue
        block = r.seo_block if isinstance(r.seo_block, dict) else {}
        kind = (block.get("content_type") or "service").lower()
        if kind in ("blog", "post"):
            continue
        lastmod = today
        ts = r.updated_at or r.created_at
        if ts:
            try:
                lastmod = ts.date().isoformat() if hasattr(ts, "date") else str(ts)[:10]
            except Exception:
                lastmod = today
        loc_pages.append({
            "loc": f"{base}/{slug}",
            "lastmod": lastmod,
            "kind": "location",
            "city": r.city or "",
            "title": (block.get("title") or "") if isinstance(block, dict) else "",
            "changefreq": "weekly",
        })

    posts = []
    for loc, lastmod in await editorial_post_urls(session, site_base=base):
        posts.append({"loc": loc, "lastmod": lastmod, "kind": "post", "changefreq": "weekly"})

    return {
        "base": base,
        "index_url": f"{base}/sitemap.xml",
        "page_sitemap_url": f"{base}/page-sitemap.xml",
        "post_sitemap_url": f"{base}/post-sitemap.xml",
        "index": [
            {"loc": f"{base}/page-sitemap.xml", "kind": "index"},
            {"loc": f"{base}/post-sitemap.xml", "kind": "index"},
        ],
        "pages": pages,
        "location_pages": loc_pages,
        "posts": posts,
        "counts": {
            "pages": len(pages),
            "location_pages": len(loc_pages),
            "posts": len(posts),
        },
    }


def urlset_xml(entries: list[tuple[str, str]], *, changefreq: str = "weekly", priority: str = "0.8") -> str:
    parts = []
    for loc, lastmod in entries:
        parts.append(
            f"<url><loc>{_xml_esc(loc)}</loc><lastmod>{lastmod}</lastmod>"
            f"<changefreq>{changefreq}</changefreq><priority>{priority}</priority></url>"
        )
    return (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        + "".join(parts)
        + "</urlset>"
    )
