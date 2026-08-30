"""Editorial URLs that belong in post-sitemap.xml (blogs only, not location tests)."""
from __future__ import annotations

import re
from datetime import date
from pathlib import Path
from sqlalchemy import select

from db import PageRecord, PublishedUrlRecord

_TEST_LANDING = re.compile(
    r"^/(?:"
    r"(?:contractors|healthcare|web-design|web-designer|plumbing|software-engineer|"
    r"local-service|website-redesign|education|kitchen-remodel|"
    r"remodeling-contractors|general-contractors)[-/]"
    r"|restaurants?-(?!web-design)"
    r")",
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


def _row_lastmod(row, today: str) -> str:
    ts = getattr(row, "updated_at", None) or getattr(row, "created_at", None)
    if ts:
        try:
            return ts.date().isoformat() if hasattr(ts, "date") else str(ts)[:10]
        except Exception:
            return today
    return today


def _is_blog_block(block: dict) -> bool:
    kind = ((block or {}).get("content_type") or "service").lower()
    return kind in ("blog", "post")


async def _published_url_slugs(session) -> set[str]:
    rows = (await session.execute(select(PublishedUrlRecord))).scalars().all()
    out = set()
    for r in rows:
        url = (r.url or "").strip()
        if not url:
            continue
        path = url.split("://", 1)[-1]
        path = path.split("/", 1)[-1] if "/" in path else ""
        slug = path.strip("/").split("/")[0].lower()
        if slug:
            out.add(slug)
        st = (r.status or "").lower()
        if st in {"error", "deleted"}:
            out.discard(slug)
    return out


async def editorial_page_urls(session, *, site_base: str, limit: int = 4000) -> list[tuple[str, str]]:
    """Menu routes + location/service pages only — never blog posts."""
    base = (site_base or "https://zeorbit.com").rstrip("/")
    today = date.today().isoformat()
    seen: set[str] = set()
    out: list[tuple[str, str]] = []
    live = await _published_url_slugs(session)

    def add(loc: str, lastmod: str = today):
        loc = (loc or "").rstrip("/") or base
        if not loc or loc in seen:
            return
        seen.add(loc)
        out.append((loc, lastmod or today))

    for path in SITE_MENU_PATHS:
        loc = base if path == "/" else f"{base}{path}"
        add(loc, today)

    rows = (await session.execute(select(PageRecord).order_by(PageRecord.updated_at.desc()))).scalars().all()
    for r in rows:
        if len(out) >= limit:
            break
        slug = (r.slug or "").strip("/")
        if not slug:
            continue
        path = f"/{slug}"
        if path in _MENU or slug in {p.strip("/") for p in SITE_MENU_PATHS if p != "/"}:
            continue
        if _TEST_LANDING.search(path) and slug.lower() not in live:
            continue
        block = r.seo_block if isinstance(r.seo_block, dict) else {}
        if _is_blog_block(block):
            continue
        add(f"{base}/{slug}", _row_lastmod(r, today))
    return out


async def editorial_post_urls(session, *, site_base: str, limit: int = 2000) -> list[tuple[str, str]]:
    """Blog/post records only — never location pages or marketing menu URLs."""
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

    live = await _published_url_slugs(session)
    rows = (await session.execute(select(PageRecord).order_by(PageRecord.updated_at.desc()))).scalars().all()
    for r in rows:
        if len(out) >= limit:
            break
        slug = (r.slug or "").strip("/")
        if not slug:
            continue
        if _TEST_LANDING.search(f"/{slug}") and slug.lower() not in live:
            continue
        block = r.seo_block if isinstance(r.seo_block, dict) else {}
        if not _is_blog_block(block):
            continue
        add(f"{base}/{slug}", _row_lastmod(r, today))
    return out


async def sitemap_overview(session, *, site_base: str) -> dict:
    """JSON for the SEO-tool Sitemap screen (not a public XML change)."""
    base = (site_base or "https://zeorbit.com").rstrip("/")

    menu_locs = {base if path == "/" else f"{base}{path}".rstrip("/") for path in SITE_MENU_PATHS}
    pages = []
    loc_pages = []
    for loc, lastmod in await editorial_page_urls(session, site_base=base):
        kind = "menu" if loc.rstrip("/") in menu_locs or loc.rstrip("/") == base else "location"
        item = {"loc": loc, "lastmod": lastmod, "kind": kind, "changefreq": "weekly"}
        pages.append(item)
        if kind == "location":
            loc_pages.append(item)

    rows = (await session.execute(select(PageRecord))).scalars().all()
    by_loc = {f"{base}/{(r.slug or '').strip('/')}": r for r in rows if r.slug}
    for item in loc_pages:
        r = by_loc.get(item["loc"])
        if not r:
            continue
        block = r.seo_block if isinstance(r.seo_block, dict) else {}
        item["city"] = r.city or ""
        item["title"] = (block.get("title") or "") if isinstance(block, dict) else ""

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


def sitemap_index_xml(site_base: str) -> str:
    base = (site_base or "https://zeorbit.com").rstrip("/")
    return (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        f"<sitemap><loc>{_xml_esc(base)}/page-sitemap.xml</loc></sitemap>"
        f"<sitemap><loc>{_xml_esc(base)}/post-sitemap.xml</loc></sitemap>"
        "</sitemapindex>"
    )


def _sitemap_write_dirs() -> list[Path]:
    here = Path(__file__).resolve()
    # SEO_Tool/zeorbit-website/public and live www root
    roots = [
        here.parents[3] / "zeorbit-website" / "public",
        here.parents[3] / "zeorbit-website" / "dist",
        Path("/var/www/zeorbit-website"),
    ]
    return [p for p in roots if p.exists()]


async def persist_live_sitemaps(session, site_base: str = "https://zeorbit.com") -> dict:
    """Write page/post sitemaps to disk so nginx try_files cannot serve empty copies."""
    base = (site_base or "https://zeorbit.com").rstrip("/")
    pages = await editorial_page_urls(session, site_base=base)
    posts = await editorial_post_urls(session, site_base=base)
    files = {
        "sitemap.xml": sitemap_index_xml(base),
        "page-sitemap.xml": urlset_xml(pages, priority="1.0"),
        "post-sitemap.xml": urlset_xml(posts),
    }
    written = []
    for folder in _sitemap_write_dirs():
        for name, body in files.items():
            dest = folder / name
            try:
                dest.write_text(body, encoding="utf-8")
                written.append(str(dest))
            except OSError:
                continue
    return {"ok": True, "page_urls": len(pages), "post_urls": len(posts), "written": written}


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
