from fastapi import APIRouter
from fastapi.responses import JSONResponse
from services.google_reviews_service import fetch_google_reviews

router = APIRouter()


@router.get("")
async def google_reviews():
    """Public live Google reviews for the ZeOrbit website."""
    try:
        return await fetch_google_reviews()
    except Exception as exc:
        return JSONResponse(
            status_code=503,
            content={"live": False, "detail": str(exc)[:240]},
        )
