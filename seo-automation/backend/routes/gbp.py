from fastapi import APIRouter
from models.schemas import GBPPostRequest, GBPPostResult
from services.social_service import post_gbp_update, gbp_configured

router = APIRouter()


@router.get("/status")
async def get_status():
    return {"configured": gbp_configured()}


@router.post("/post", response_model=GBPPostResult)
async def create_post(req: GBPPostRequest):
    return await post_gbp_update(req)
