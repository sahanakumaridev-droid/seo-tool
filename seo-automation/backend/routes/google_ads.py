from fastapi import APIRouter
from models.schemas import GoogleAdsCampaignRequest, GoogleAdsCampaignResult
from services.google_ads_service import create_campaign, is_configured

router = APIRouter()


@router.get("/status")
async def get_status():
    return {"configured": is_configured()}


@router.post("/create-campaign", response_model=GoogleAdsCampaignResult)
async def create_campaign_route(req: GoogleAdsCampaignRequest):
    return await create_campaign(req)
