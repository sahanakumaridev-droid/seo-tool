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
    keyword: str = Query(..., min_length=1, description="Keyword to research (required)"),
    location: str = Query(default="US"),
):
    if not (keyword or "").strip():
        from fastapi import HTTPException
        raise HTTPException(status_code=422, detail="Keyword search is required")
    return await _keyword_data_provider.research(keyword.strip(), location)
