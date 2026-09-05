"""Block duplicate blog/page publishes (same slug, title, or keyword+city)."""
import re
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db import PageRecord


def _norm(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", (text or "").lower())


def _block_dict(row: PageRecord) -> dict:
    b = row.seo_block
    return b if isinstance(b, dict) else {}


def row_matches_post(row: PageRecord, *, slug: str, city: str, keyword: str, title: str) -> Optional[str]:
    if (row.slug or "").strip() == (slug or "").strip():
        return "slug"
    block = _block_dict(row)
    city_a = (row.city or "").strip().lower()
    city_b = (city or "").strip().lower()
    kw_a = (block.get("focus_keyword") or row.business_type or "").strip().lower()
    kw_b = (keyword or "").strip().lower()
    if city_a and city_b and city_a == city_b and kw_a and kw_b and kw_a == kw_b:
        return "keyword_city"
    t_a = _norm(block.get("title") or "")
    t_b = _norm(title)
    if t_a and t_b and t_a == t_b:
        return "title"
    return None


async def find_duplicate_page(
    session: AsyncSession,
    *,
    slug: str,
    city: str = "",
    keyword: str = "",
    title: str = "",
    exclude_slug: str = "",
) -> Optional[PageRecord]:
    rows = (await session.execute(select(PageRecord))).scalars().all()
    for row in rows:
        if exclude_slug and (row.slug or "") == exclude_slug:
            continue
        reason = row_matches_post(row, slug=slug, city=city, keyword=keyword, title=title)
        if reason:
            return row
    return None
