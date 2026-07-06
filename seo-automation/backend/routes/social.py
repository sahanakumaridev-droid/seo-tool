from fastapi import APIRouter, HTTPException
from models.schemas import SocialPostRequest, SocialPostResult
from services.social_service import share_to_social
from typing import List

router = APIRouter()

@router.post("/share", response_model=List[SocialPostResult])
async def share_post(req: SocialPostRequest):
    """Share a published post to selected social media platforms."""
    if not req.platforms:
        raise HTTPException(status_code=400, detail="At least one platform required")
    results = await share_to_social(req)
    return results

@router.get("/platforms")
async def get_platforms():
    """Return configured social platforms status."""
    from config import settings
    return {
        "facebook": bool(settings.FACEBOOK_ACCESS_TOKEN and settings.FACEBOOK_PAGE_ID),
        "twitter": bool(settings.TWITTER_API_KEY and settings.TWITTER_ACCESS_TOKEN),
        "linkedin": bool(settings.LINKEDIN_ACCESS_TOKEN and settings.LINKEDIN_PERSON_URN),
        "instagram": bool(settings.INSTAGRAM_ACCESS_TOKEN and settings.INSTAGRAM_ACCOUNT_ID),
        "pinterest": bool(settings.PINTEREST_ACCESS_TOKEN and settings.PINTEREST_BOARD_ID),
        "threads": bool(settings.THREADS_ACCESS_TOKEN and settings.THREADS_USER_ID),
        "gbp": bool(settings.GBP_ACCESS_TOKEN and settings.GBP_ACCOUNT_ID and settings.GBP_LOCATION_ID),
    }
