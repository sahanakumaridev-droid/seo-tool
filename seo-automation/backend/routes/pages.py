from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from db import get_session, PageRecord, PublishedUrlRecord
from services.content_service import generate_seo_block
from services.slug_utils import article_slug
from models.schemas import SEOBlock
from config import settings
from datetime import datetime, timezone
from typing import List, Optional
from urllib.parse import urlparse
import re

router = APIRouter()

LIVE_SITE = "https://zeorbit.com"


def slugify(text: str) -> str:
    return re.sub(r'[^a-z0-9-]+', '-', text.lower()).strip('-')


def _block_slug(block: SEOBlock) -> str:
    if (block.slug or "").strip():
        return block.slug.strip()
    kws = []
    if getattr(block, "focus_keyword", None):
        kws.append(block.focus_keyword)
    if block.keywords:
        if block.keywords.primary:
            kws.append(block.keywords.primary)
        kws.extend(block.keywords.secondary or [])
    return article_slug(kws, block.city or "", block.business_type or "") or slugify(
        f"{block.business_type}-{block.city}-{block.state}"
    )


def _is_tool_host(url_or_host: str) -> bool:
    h = (url_or_host or "").lower()
    return "nip.io" in h or "://seo." in h


def _reader_base(request: Optional[Request] = None) -> str:
    """Live ZeOrbit site — published blogs must open here, not on the SEO host."""
    marketing = (getattr(settings, "MARKETING_SITE_URL", None) or "").strip().rstrip("/")
    if marketing:
        return marketing
    if settings.PUBLIC_BASE_URL:
        base = settings.PUBLIC_BASE_URL.rstrip("/")
        if not _is_tool_host(base):
            return base
    if request is not None:
        origin = str(request.base_url).rstrip("/")
        if origin and not _is_tool_host(origin) and "127.0.0.1" not in origin and "localhost" not in origin:
            return origin
    return LIVE_SITE


def _public_base(request: Request) -> str:
    """Reader-facing base for /p/{slug} links (always the live website)."""
    return _reader_base(request)


def _rewrite_reader_url(url: str, slug: str = "") -> str:
    """Map SEO-tool / nip.io URLs onto the live website."""
    base = _reader_base()
    if slug:
        return f"{base}/{slug.lstrip('/')}"
    raw = (url or "").strip()
    if not raw:
        return f"{base}/blog"
    if raw.startswith("/p/"):
        return f"{base}/{raw[3:].split('?')[0]}"
    try:
        parsed = urlparse(raw if "://" in raw else f"https://{raw}")
    except Exception:
        return f"{base}/blog"
    path = parsed.path or "/"
    host = (parsed.hostname or "").lower()
    if path.startswith("/p/"):
        return f"{base}/{path[3:].rstrip('/')}"
    if "nip.io" in host or host.startswith("seo."):
        return f"{base}/blog"
    return raw


def _ads_ready_url(url: str) -> bool:
    """Google Ads requires a public domain with a real TLD (not localhost/IP)."""
    try:
        from urllib.parse import urlparse
        import re
        host = (urlparse(url if "://" in url else f"https://{url}").hostname or "").strip()
        if not host or host in {"localhost"} or host.replace(".", "").isdigit():
            return False
        if re.match(r"^(127\.|10\.|192\.168\.|0\.)", host):
            return False
        return bool(re.match(r"^[a-z0-9-]+(\.[a-z0-9-]+)*\.[a-z]{2,}$", host, re.I))
    except Exception:
        return False


@router.get("/landing-pages", response_model=dict)
async def list_landing_pages_for_ads(
    request: Request,
    skip: int = 0,
    limit: int = 50,
    session: AsyncSession = Depends(get_session),
):
    """
    Published SEO landing pages ready to use as Google Ads final URLs.
    Prefer WordPress live URLs and /p/{slug} pages with a public PUBLIC_BASE_URL.
    """
    base = _public_base(request)
    limit = max(1, min(limit, 100))
    skip = max(0, skip)

    pages = []
    page_result = await session.execute(
        select(PageRecord).order_by(PageRecord.created_at.desc()).limit(200)
    )
    for r in page_result.scalars().all():
        block = r.seo_block if isinstance(r.seo_block, dict) else {}
        title = (block.get("title") or block.get("h1") or r.business_type or "Untitled").strip()
        public_url = f"{base}/{r.slug}"
        keywords = []
        kw = block.get("keywords") or {}
        if isinstance(kw, dict):
            if kw.get("primary"):
                keywords.append(kw["primary"])
            keywords.extend([x for x in (kw.get("secondary") or []) if x][:6])
        pages.append({
            "id": f"page-{r.id}",
            "source": "seo",
            "title": title,
            "slug": r.slug,
            "public_url": public_url,
            "business_type": r.business_type or block.get("business_type") or "",
            "city": r.city or "",
            "state": r.state or "",
            "keywords": keywords,
            "ads_ready": _ads_ready_url(public_url),
            "published_at": (r.updated_at or r.created_at).isoformat() if (r.updated_at or r.created_at) else None,
        })

    try:
        wp_result = await session.execute(
            select(PublishedUrlRecord)
            .where(PublishedUrlRecord.status != "error")
            .order_by(PublishedUrlRecord.created_at.desc())
            .limit(100)
        )
        for u in wp_result.scalars().all():
            if not u.url:
                continue
            pages.append({
                "id": f"wp-{u.id}",
                "source": "wordpress",
                "title": (u.title or u.url).strip(),
                "slug": "",
                "public_url": u.url,
                "business_type": "",
                "city": "",
                "state": "",
                "keywords": [],
                "ads_ready": _ads_ready_url(u.url),
                "published_at": u.created_at.isoformat() if u.created_at else None,
            })
    except Exception:
        pass

    ready = [p for p in pages if p.get("ads_ready")]
    not_ready = [p for p in pages if not p.get("ads_ready")]
    ready.sort(key=lambda p: p.get("published_at") or "", reverse=True)
    not_ready.sort(key=lambda p: p.get("published_at") or "", reverse=True)
    ordered = ready + not_ready
    total = len(ordered)
    return {
        "pages": ordered[skip: skip + limit],
        "total": total,
        "public_base_url": base,
        "ads_ready_count": len(ready),
    }


@router.post("/publish-web", response_model=dict)
async def publish_to_web(
    block: SEOBlock,
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    """Save an already-generated page and expose it at a public /p/{slug} URL.
    Also runs crawl/indexing tracking and optional paused Ads auto-create."""
    from services.publish_pipeline import track_public_publish, maybe_auto_create_ads

    slug = _block_slug(block)
    block.slug = slug

    result = await session.execute(select(PageRecord).where(PageRecord.slug == slug))
    existing = result.scalar_one_or_none()
    if existing:
        existing.seo_block = block.model_dump()
        existing.updated_at = datetime.now(timezone.utc)
    else:
        session.add(PageRecord(
            business_type=block.business_type,
            base_location=f"{block.city}, {block.state}",
            city=block.city,
            state=block.state or "",
            slug=slug,
            seo_block=block.model_dump(),
        ))
    await session.commit()

    public_url = f"{_public_base(request)}/{slug}"
    indexing = await track_public_publish(url=public_url, block=block, session=session)
    ads = await maybe_auto_create_ads(public_url=public_url, block=block)

    return {
        "slug": slug,
        "public_url": public_url,
        "published": True,
        "indexing": indexing,
        "ads": ads,
        "automation": {
            "ads_auto_create": bool(settings.GOOGLE_ADS_AUTO_CREATE_ON_PUBLISH),
            "ads_auto_enable": bool(settings.GOOGLE_ADS_AUTO_ENABLE),
        },
    }


@router.post("/publish-web/bulk", response_model=dict)
async def publish_to_web_bulk(
    blocks: List[SEOBlock],
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    """Publish many generated pages to public /p/{slug} URLs in one call."""
    from services.publish_pipeline import track_public_publish, maybe_auto_create_ads

    base = _public_base(request)
    published = []
    for block in blocks:
        slug = _block_slug(block)
        block.slug = slug
        result = await session.execute(select(PageRecord).where(PageRecord.slug == slug))
        existing = result.scalar_one_or_none()
        if existing:
            existing.seo_block = block.model_dump()
            existing.updated_at = datetime.now(timezone.utc)
        else:
            session.add(PageRecord(
                business_type=block.business_type,
                base_location=f"{block.city}, {block.state}",
                city=block.city, state=block.state or "", slug=slug,
                seo_block=block.model_dump(),
            ))
        public_url = f"{base}/{slug}"
        indexing = await track_public_publish(url=public_url, block=block, session=session)
        ads = await maybe_auto_create_ads(public_url=public_url, block=block)
        published.append({
            "slug": slug, "city": block.city, "state": block.state,
            "title": block.title, "public_url": public_url,
            "indexing": indexing, "ads": ads,
        })
    await session.commit()
    return {
        "published": published,
        "count": len(published),
        "automation": {
            "ads_auto_create": bool(settings.GOOGLE_ADS_AUTO_CREATE_ON_PUBLISH),
            "ads_auto_enable": bool(settings.GOOGLE_ADS_AUTO_ENABLE),
        },
    }

@router.post("/save", response_model=dict)
async def save_page(
    business_type: str,
    city: str,
    state: str = "CA",
    session: AsyncSession = Depends(get_session),
):
    block = await generate_seo_block(business_type, city, state)
    slug = slugify(f"{business_type}-{city}")

    # Upsert: update if slug exists, insert otherwise
    result = await session.execute(select(PageRecord).where(PageRecord.slug == slug))
    existing = result.scalar_one_or_none()

    if existing:
        existing.seo_block = block.model_dump()
        existing.updated_at = datetime.now(timezone.utc)
    else:
        session.add(PageRecord(
            business_type=business_type,
            base_location=f"{city}, {state}",
            city=city,
            state=state,
            slug=slug,
            seo_block=block.model_dump(),
        ))

    await session.commit()
    return {"slug": slug, "saved": True}

@router.get("/blog", response_model=dict)
async def list_blog_posts(
    request: Request,
    skip: int = 0,
    limit: int = 24,
    session: AsyncSession = Depends(get_session),
):
    """
    Public blog feed for the marketing site.
    Lists SEO content published to this app (/p/{slug}) plus tracked live WordPress URLs.
    """
    base = _public_base(request)
    limit = max(1, min(limit, 100))
    skip = max(0, skip)

    page_result = await session.execute(
        select(PageRecord).order_by(PageRecord.created_at.desc()).offset(0).limit(200)
    )
    page_rows = page_result.scalars().all()
    page_slugs = {r.slug for r in page_rows if r.slug}

    posts = []
    for r in page_rows:
        block = r.seo_block if isinstance(r.seo_block, dict) else {}
        title = (block.get("title") or block.get("h1") or r.business_type or "Untitled").strip()
        excerpt = (
            block.get("meta_description")
            or block.get("intro")
            or ""
        ).strip()
        if len(excerpt) > 220:
            excerpt = excerpt[:217].rstrip() + "…"
        category = (block.get("industry") or r.business_type or "SEO").strip()
        posts.append({
            "id": f"page-{r.id}",
            "source": "web",
            "title": title,
            "excerpt": excerpt,
            "category": category,
            "slug": r.slug,
            "url": f"/{r.slug}",
            "public_url": f"{base}/{r.slug}",
            "city": r.city,
            "state": r.state,
            "featured_image_url": block.get("featured_image_url") or None,
            "published_at": (r.updated_at or r.created_at).isoformat() if (r.updated_at or r.created_at) else None,
        })

    try:
        wp_result = await session.execute(
            select(PublishedUrlRecord)
            .where(PublishedUrlRecord.status != "error")
            .order_by(PublishedUrlRecord.created_at.desc())
            .limit(100)
        )
        for u in wp_result.scalars().all():
            if not u.url:
                continue
            parsed = urlparse(u.url if "://" in u.url else f"https://{u.url}")
            path = (parsed.path or "").rstrip("/")
            if path.startswith("/p/"):
                slug = path.rsplit("/", 1)[-1]
                if slug in page_slugs:
                    continue
                live = _rewrite_reader_url(u.url, slug)
                rel = f"/{slug}"
            else:
                live = _rewrite_reader_url(u.url)
                rel = live
            posts.append({
                "id": f"wp-{u.id}",
                "source": u.source or "wordpress",
                "title": (u.title or u.url).strip(),
                "excerpt": "Published live SEO article.",
                "category": "Published",
                "slug": "",
                "url": rel,
                "public_url": live,
                "city": "",
                "state": "",
                "featured_image_url": None,
                "published_at": u.created_at.isoformat() if u.created_at else None,
            })
    except Exception:
        # Table may be empty / unavailable in some local setups — pages feed still works.
        pass

    posts.sort(key=lambda p: p.get("published_at") or "", reverse=True)
    total = len(posts)
    slice_posts = posts[skip: skip + limit]

    return {
        "posts": slice_posts,
        "total": total,
        "skip": skip,
        "limit": limit,
    }


@router.get("/", response_model=List[dict])
async def list_pages(
    request: Request,
    skip: int = 0,
    limit: int = 20,
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(
        select(PageRecord).offset(skip).limit(limit).order_by(PageRecord.created_at.desc())
    )
    rows = result.scalars().all()
    base = _public_base(request)
    return [
        {
            "id": r.id,
            "business_type": r.business_type,
            "base_location": r.base_location,
            "city": r.city,
            "state": r.state,
            "slug": r.slug,
            "seo_block": r.seo_block,
            "public_url": f"{base}/{r.slug}",
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in rows
    ]

@router.get("/{slug}", response_model=dict)
async def get_page(slug: str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(PageRecord).where(PageRecord.slug == slug))
    row = result.scalar_one_or_none()
    if not row:
        raise HTTPException(status_code=404, detail="Page not found")
    return {
        "id": row.id,
        "business_type": row.business_type,
        "city": row.city,
        "state": row.state,
        "slug": row.slug,
        "seo_block": row.seo_block,
        "created_at": row.created_at.isoformat() if row.created_at else None,
    }

@router.delete("/{slug}")
async def delete_page(slug: str, session: AsyncSession = Depends(get_session)):
    result = await session.execute(delete(PageRecord).where(PageRecord.slug == slug))
    await session.commit()
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Page not found")
    return {"deleted": True}
