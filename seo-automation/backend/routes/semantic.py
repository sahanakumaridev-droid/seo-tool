"""
semantic.py — Semantic search and AI-powered analysis endpoints
Includes competitor analysis, content recommendations, and embeddings
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from services.semantic_service import get_semantic_service, SemanticSearchService
from services.advanced_ai_service import get_advanced_ai_service, AdvancedAIService
from auth import get_current_active_user, User
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


class SemanticSearchRequest(BaseModel):
    query: str
    business_type: str
    top_k: int = 5


class CompetitorAnalysisRequest(BaseModel):
    competitor_url: str
    business_type: str
    city: str


class SEORecommendationRequest(BaseModel):
    content: str
    target_keywords: List[str]
    business_type: str


class ContentVariantRequest(BaseModel):
    content: str
    num_variants: int = 3
    tone: str = "professional"


@router.post("/search")
async def semantic_search(
    req: SemanticSearchRequest,
    current_user: User = Depends(get_current_active_user),
    semantic_service: SemanticSearchService = Depends(get_semantic_service)
):
    """Find similar content using semantic search."""
    try:
        results = await semantic_service.find_similar_content(
            req.query,
            req.business_type,
            req.top_k
        )
        return {"results": results}
    except Exception as e:
        logger.error(f"Semantic search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/competitor-analysis")
async def analyze_competitor(
    req: CompetitorAnalysisRequest,
    current_user: User = Depends(get_current_active_user),
    ai_service: AdvancedAIService = Depends(get_advanced_ai_service)
):
    """AI-powered competitor analysis."""
    try:
        analysis = await ai_service.analyze_competitor_strategy(
            req.competitor_url,
            req.business_type,
            req.city
        )
        return analysis
    except Exception as e:
        logger.error(f"Competitor analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/seo-recommendations")
async def get_seo_recommendations(
    req: SEORecommendationRequest,
    current_user: User = Depends(get_current_active_user),
    ai_service: AdvancedAIService = Depends(get_advanced_ai_service)
):
    """Get AI-powered SEO recommendations."""
    try:
        recommendations = await ai_service.generate_seo_recommendations(
            req.content,
            req.target_keywords,
            req.business_type
        )
        return recommendations
    except Exception as e:
        logger.error(f"SEO recommendations failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/content-variants")
async def generate_variants(
    req: ContentVariantRequest,
    current_user: User = Depends(get_current_active_user),
    ai_service: AdvancedAIService = Depends(get_advanced_ai_service)
):
    """Generate multiple content variants."""
    try:
        variants = await ai_service.generate_content_variants(
            req.content,
            req.num_variants,
            req.tone
        )
        return {"variants": variants}
    except Exception as e:
        logger.error(f"Content variant generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/embed")
async def embed_text(
    text: str,
    current_user: User = Depends(get_current_active_user),
    semantic_service: SemanticSearchService = Depends(get_semantic_service)
):
    """Generate embedding for text."""
    try:
        embedding = await semantic_service.embed_text(text)
        return {"embedding": embedding, "dimension": len(embedding)}
    except Exception as e:
        logger.error(f"Embedding generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
