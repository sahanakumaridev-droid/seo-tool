"""Public news feed and signed-in feed management. Does not touch /blogs."""
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from auth import get_current_active_user
from db import NewsArticleRecord, NewsFeedRecord, get_session
from services.news_rss import ensure_default_feeds, sync_enabled, sync_feed

router = APIRouter()


def _article(row: NewsArticleRecord) -> dict:
    published = row.published_at.isoformat() if isinstance(row.published_at, datetime) else ""
    return {
        "id": row.id,
        "title": row.title,
        "summary": row.summary,
        "image_url": row.image_url if (row.image_url or "").startswith("http") else "",
        "author": row.author or "",
        "source_name": row.source_name or "",
        "url": row.url,
        "published_at": published,
    }


def _mix_sources(rows):
    buckets = {}
    order = []
    for row in rows:
        key = (row.source_name or str(row.feed_id)).strip() or str(row.feed_id)
        if key not in buckets:
            buckets[key] = []
            order.append(key)
        buckets[key].append(row)
    mixed = []
    while True:
        progressed = False
        for key in order:
            if buckets[key]:
                mixed.append(buckets[key].pop(0))
                progressed = True
        if not progressed:
            return mixed


@router.get("")
async def list_news(page: int = 1, limit: int = 12, session: AsyncSession = Depends(get_session)):
    await ensure_default_feeds(session)
    page = max(1, page)
    limit = min(24, max(1, limit))
    enabled_ids = select(NewsFeedRecord.id).where(NewsFeedRecord.enabled == True)
    base = select(NewsArticleRecord).where(
        NewsArticleRecord.hidden == False,
        NewsArticleRecord.feed_id.in_(enabled_ids),
    )
    total = (await session.execute(select(func.count()).select_from(base.subquery()))).scalar_one()
    rows = (await session.execute(
        base.order_by(NewsArticleRecord.published_at.desc()).limit(240)
    )).scalars().all()
    mixed = _mix_sources(rows)
    start = (page - 1) * limit
    page_rows = mixed[start:start + limit]
    items = [_article(row) for row in page_rows]
    featured = items[0] if page == 1 and items else None
    rest = items[1:] if featured else items
    return {
        "featured": featured,
        "items": rest,
        "page": page,
        "limit": limit,
        "total": total,
        "has_more": start + limit < len(mixed),
    }


class FeedIn(BaseModel):
    name: str = Field(..., min_length=2, max_length=160)
    url: str = Field(..., min_length=8, max_length=500)
    filter_software: bool = True
    enabled: bool = True


@router.get("/admin/feeds")
async def list_feeds(_user=Depends(get_current_active_user), session: AsyncSession = Depends(get_session)):
    await ensure_default_feeds(session)
    rows = (await session.execute(select(NewsFeedRecord).order_by(NewsFeedRecord.name))).scalars().all()
    return {"feeds": [_feed(row) for row in rows]}


@router.post("/admin/feeds")
async def add_feed(body: FeedIn, _user=Depends(get_current_active_user), session: AsyncSession = Depends(get_session)):
    url = body.url.strip()
    exists = (await session.execute(select(NewsFeedRecord).where(NewsFeedRecord.url == url))).scalar_one_or_none()
    if exists:
        raise HTTPException(status_code=409, detail="That feed is already saved.")
    row = NewsFeedRecord(
        name=body.name.strip(),
        url=url,
        source_name=body.name.strip(),
        enabled=body.enabled,
        filter_software=body.filter_software,
        last_status="waiting",
    )
    session.add(row)
    await session.commit()
    await session.refresh(row)
    return _feed(row)


@router.put("/admin/feeds/{feed_id}")
async def update_feed(feed_id: int, body: FeedIn, _user=Depends(get_current_active_user), session: AsyncSession = Depends(get_session)):
    row = await session.get(NewsFeedRecord, feed_id)
    if not row:
        raise HTTPException(status_code=404, detail="Feed not found.")
    row.name = body.name.strip()
    row.source_name = body.name.strip()
    row.url = body.url.strip()
    row.enabled = body.enabled
    row.filter_software = body.filter_software
    await session.commit()
    return _feed(row)


@router.post("/admin/sync")
async def sync_now(_user=Depends(get_current_active_user), session: AsyncSession = Depends(get_session)):
    return {"results": await sync_enabled(session)}


@router.post("/admin/feeds/{feed_id}/sync")
async def sync_one(feed_id: int, _user=Depends(get_current_active_user), session: AsyncSession = Depends(get_session)):
    row = await session.get(NewsFeedRecord, feed_id)
    if not row:
        raise HTTPException(status_code=404, detail="Feed not found.")
    return await sync_feed(session, row)


@router.post("/admin/articles/{article_id}/hide")
async def hide_article(article_id: int, _user=Depends(get_current_active_user), session: AsyncSession = Depends(get_session)):
    row = await session.get(NewsArticleRecord, article_id)
    if not row:
        raise HTTPException(status_code=404, detail="Article not found.")
    row.hidden = not bool(row.hidden)
    await session.commit()
    return {"id": row.id, "hidden": bool(row.hidden)}


@router.get("/admin/articles")
async def list_admin_articles(_user=Depends(get_current_active_user), session: AsyncSession = Depends(get_session)):
    rows = (await session.execute(
        select(NewsArticleRecord).order_by(NewsArticleRecord.published_at.desc()).limit(40)
    )).scalars().all()
    return {"articles": [{**_article(row), "hidden": bool(row.hidden)} for row in rows]}


def _feed(row: NewsFeedRecord) -> dict:
    return {
        "id": row.id,
        "name": row.name,
        "url": row.url,
        "enabled": bool(row.enabled),
        "filter_software": bool(row.filter_software),
        "last_status": row.last_status or "",
        "last_error": row.last_error or "",
        "last_added": row.last_added or 0,
        "last_synced_at": row.last_synced_at.isoformat() if row.last_synced_at else "",
    }
