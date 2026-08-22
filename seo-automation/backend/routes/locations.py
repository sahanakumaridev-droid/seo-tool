from fastapi import APIRouter, HTTPException, Query
from services.location_service import get_nearby_cities, LocationNotResolvedError
from typing import List
from models.schemas import CityInfo
from pathlib import Path
import json

router = APIRouter()

_SD_COUNTY = None


def _san_diego_county():
    global _SD_COUNTY
    if _SD_COUNTY is None:
        path = Path(__file__).resolve().parents[1] / "data" / "san_diego_county.json"
        _SD_COUNTY = json.loads(path.read_text(encoding="utf-8"))
    return _SD_COUNTY


@router.get("/san-diego-county")
async def san_diego_county_breakdown():
    """County → 18 cities + unincorporated → local areas → streets."""
    return _san_diego_county()


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
