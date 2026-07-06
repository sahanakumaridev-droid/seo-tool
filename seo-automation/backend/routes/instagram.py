"""
Instagram API Routes
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.instagram_service import instagram_service

router = APIRouter()


class InstagramPostRequest(BaseModel):
    image_url: str
    caption: str


@router.post("/post")
async def post_to_instagram(request: InstagramPostRequest):
    """
    Post image with caption to Instagram Business account.
    
    Requirements:
    - Instagram Business Account
    - INSTAGRAM_ACCESS_TOKEN in .env
    - INSTAGRAM_ACCOUNT_ID in .env
    """
    result = await instagram_service.post_to_instagram(
        image_url=request.image_url,
        caption=request.caption
    )
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message"))
    
    return result


@router.get("/account")
async def get_instagram_account():
    """Get Instagram Business account information"""
    result = await instagram_service.get_account_info()
    
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))
    
    return result


@router.get("/status")
async def instagram_status():
    """Check if Instagram API is configured"""
    import os
    
    has_token = bool(os.getenv("INSTAGRAM_ACCESS_TOKEN"))
    has_account_id = bool(os.getenv("INSTAGRAM_ACCOUNT_ID"))
    
    return {
        "configured": has_token and has_account_id,
        "has_access_token": has_token,
        "has_account_id": has_account_id,
        "message": "Instagram API is configured" if (has_token and has_account_id) else "Instagram API not configured. Add INSTAGRAM_ACCESS_TOKEN and INSTAGRAM_ACCOUNT_ID to .env"
    }
