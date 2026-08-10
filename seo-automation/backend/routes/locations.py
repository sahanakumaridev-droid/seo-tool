from fastapi import APIRouter, HTTPException, Query
from services.location_service import get_nearby_cities, LocationNotResolvedError
from typing import List
from models.schemas import CityInfo

router = APIRouter()

@router.get("/nearby", response_model=List[CityInfo])
async def nearby_cities(
    base_location: str = Query(default="San Diego, CA"),
    num_cities: int = Query(default=10, ge=1, le=100)
):
    try:
        cities = await get_nearby_cities(base_location, num_cities)
    except LocationNotResolvedError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return cities
