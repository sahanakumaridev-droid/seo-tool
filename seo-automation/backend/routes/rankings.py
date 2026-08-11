from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from config import settings
from db import get_session, PageRecord
from models.schemas import RankingResult
from providers.mock_rank_data import MockRankProvider

router = APIRouter()
_provider = MockRankProvider()


def _public_base(request: Request) -> str:
    if settings.PUBLIC_BASE_URL:
        return settings.PUBLIC_BASE_URL.rstrip("/")
    return str(request.base_url).rstrip("/")


@router.get("", response_model=RankingResult)
async def get_rankings(
    request: Request,
    business_type: str = Query(default="", examples=["Web Design"]),
    base_location: str = Query(default="", examples=["San Diego, CA"]),
    website: str = Query(default="", description="Ignored — rankings use published /p/ SEO pages"),
    session: AsyncSession = Depends(get_session),
):
    """
    Rank tracking for keywords on published SEO blog/service pages.
    URLs always point at /p/{slug} (or live WP URLs on the page), never the
    onboarding website homepage.
    """
    result = await session.execute(
        select(PageRecord).order_by(PageRecord.created_at.desc()).limit(300)
    )
    pages = result.scalars().all()
    return await _provider.track(
        business_type=business_type or "",
        location=base_location or "",
        website="",  # deliberately unused
        pages=pages,
        public_base=_public_base(request),
    )
