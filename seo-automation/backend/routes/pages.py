from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from db import get_session, PageRecord
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


@router.post("/publish-web", response_model=dict)
async def publish_to_web(
    block: SEOBlock,
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    """Save an already-generated page and expose it at a public /p/{slug} URL."""
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

    return {"slug": slug, "public_url": f"{_public_base(request)}/p/{slug}", "published": True}


@router.post("/publish-web/bulk", response_model=dict)
async def publish_to_web_bulk(
    blocks: List[SEOBlock],
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    """Publish many generated pages to public /p/{slug} URLs in one call."""
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
        published.append({"slug": slug, "city": block.city, "state": block.state,
                          "title": block.title, "public_url": f"{base}/p/{slug}"})
    await session.commit()
    return {"published": published, "count": len(published)}

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

@router.get("/", response_model=List[dict])
async def list_pages(
    skip: int = 0,
    limit: int = 20,
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(
        select(PageRecord).offset(skip).limit(limit).order_by(PageRecord.created_at.desc())
    )
    rows = result.scalars().all()
    return [
        {
            "id": r.id,
            "business_type": r.business_type,
            "base_location": r.base_location,
            "city": r.city,
            "state": r.state,
            "slug": r.slug,
            "seo_block": r.seo_block,
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
