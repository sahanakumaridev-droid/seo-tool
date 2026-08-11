from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from db import get_session, PageRecord, PublishedUrlRecord
from services.content_service import generate_seo_block
from models.schemas import SEOBlock
from config import settings
from datetime import datetime, timezone
from typing import List
import re

router = APIRouter()

def slugify(text: str) -> str:
    return re.sub(r'[^a-z0-9-]+', '-', text.lower()).strip('-')


def _public_base(request: Request) -> str:
    """Base URL for public /p/{slug} links (config override, else request origin)."""
    if settings.PUBLIC_BASE_URL:
        return settings.PUBLIC_BASE_URL.rstrip("/")
    return str(request.base_url).rstrip("/")


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
        public_url = f"{base}/p/{r.slug}"
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

    slug = block.slug or slugify(f"{block.business_type}-{block.city}-{block.state}")
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

    public_url = f"{_public_base(request)}/p/{slug}"
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
        slug = block.slug or slugify(f"{block.business_type}-{block.city}-{block.state}")
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
        public_url = f"{base}/p/{slug}"
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
            "url": f"/p/{r.slug}",
            "public_url": f"{base}/p/{r.slug}",
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
            posts.append({
                "id": f"wp-{u.id}",
                "source": u.source or "wordpress",
                "title": (u.title or u.url).strip(),
                "excerpt": "Published live SEO article.",
                "category": "Published",
                "slug": "",
                "url": u.url,
                "public_url": u.url,
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
            "public_url": f"{base}/p/{r.slug}",
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
