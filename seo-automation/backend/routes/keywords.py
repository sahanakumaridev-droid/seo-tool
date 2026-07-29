from fastapi import APIRouter, Query
from services.keyword_service import generate_keywords
from models.schemas import KeywordSet, KeywordResearchResult
from providers.mock_keyword_data import MockKeywordDataProvider

router = APIRouter()
_keyword_data_provider = MockKeywordDataProvider()

@router.get("/generate", response_model=KeywordSet)
async def get_keywords(
    business_type: str = Query(...),
    city: str = Query(...),
    state: str = Query(default="CA")
):
    return await generate_keywords(business_type, city, state)

@router.get("/research", response_model=KeywordResearchResult)
async def research_keywords(
    keyword: str = Query(...),
    location: str = Query(default="US"),
):
    return await _keyword_data_provider.research(keyword, location)
