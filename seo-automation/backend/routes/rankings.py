from fastapi import APIRouter, Query

from models.schemas import RankingResult
from providers.mock_rank_data import MockRankProvider

router = APIRouter()
_provider = MockRankProvider()


@router.get("", response_model=RankingResult)
async def get_rankings(
    business_type: str = Query(..., example="Web Design"),
    base_location: str = Query(..., example="San Diego, CA"),
    website: str = Query(default="", example="example.com"),
):
    return await _provider.track(business_type, base_location, website)
