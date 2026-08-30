from fastapi import APIRouter, HTTPException, Query
from services.location_service import get_nearby_cities, LocationNotResolvedError
from typing import List, Optional
from models.schemas import CityInfo
from pathlib import Path
import json

router = APIRouter()

_SD_COUNTY = None
_US_CITIES = None


def _san_diego_county():
    global _SD_COUNTY
    if _SD_COUNTY is None:
        path = Path(__file__).resolve().parents[1] / "data" / "san_diego_county.json"
        _SD_COUNTY = json.loads(path.read_text(encoding="utf-8"))
    return _SD_COUNTY


def _us_cities():
    global _US_CITIES
    if _US_CITIES is None:
        path = Path(__file__).resolve().parents[1] / "data" / "us_cities.json"
        raw = json.loads(path.read_text(encoding="utf-8"))
        # Normalize to "City, ST" strings once
        out = []
        seen = set()
        for row in raw:
            if not isinstance(row, dict):
                continue
            city = (row.get("city") or "").strip()
            state = (row.get("state") or "").strip().upper()
            if not city or not state:
                continue
            label = f"{city}, {state}"
            key = label.lower()
            if key in seen:
                continue
            seen.add(key)
            out.append(label)
        _US_CITIES = out
    return _US_CITIES


@router.get("/counties")
async def list_us_counties(state: str = Query(default="CA")):
    """Counties for a US state — California returns all 58."""
    from services.location_service import list_counties
    rows = list_counties(state)
    return {
        "state": (state or "CA").upper()[:2],
        "counties": [{"name": c["name"], "state": c["state"], "label": f"{c['name']}, {c['state']}"} for c in rows],
        "total": len(rows),
    }


@router.get("/place-catalog")
async def place_catalog(
    base_location: str = Query(default=""),
    county: str = Query(default=""),
    city: str = Query(default=""),
):
    """Dynamic cities / local areas / streets for the selected county."""
    from services.location_service import build_place_catalog
    loc = (county or base_location or "San Diego County, CA").strip()
    return build_place_catalog(base_location=loc, county_name=county or loc, city_name=city)


@router.get("/san-diego-county")
async def san_diego_county_breakdown():
    """County → 18 cities + unincorporated → local areas → streets."""
    return _san_diego_county()


@router.get("/cities")
async def search_cities(
    q: str = Query(default="", description="City name search"),
    limit: int = Query(default=40, ge=1, le=100),
):
    """Search ~30k US cities for the Base city picker."""
    query = (q or "").strip().lower()
    cities = _us_cities()
    if not query:
        # Prefer California + major hubs when the field is empty/focused
        preferred = [c for c in cities if c.endswith(", CA")][:limit]
        if len(preferred) < limit:
            preferred = (preferred + [c for c in cities if c not in preferred])[:limit]
        return {"cities": preferred, "total": len(cities)}
    starts = []
    contains = []
    for c in cities:
        cl = c.lower()
        if cl.startswith(query) or cl.startswith(query.split(",")[0].strip()):
            starts.append(c)
        elif query in cl:
            contains.append(c)
        if len(starts) >= limit:
            break
    merged = starts + [c for c in contains if c not in starts]
    return {"cities": merged[:limit], "total": len(cities)}


@router.get("/nearby", response_model=List[CityInfo])
async def nearby_cities(
    base_location: str = Query(default="San Diego, CA"),
    num_cities: int = Query(default=10, ge=1, le=250)
):
    """Preview of places the generate agent will expand from the base city."""
    from services.location_service import expand_places_from_base
    try:
        cities = await expand_places_from_base(base_location, num_cities)
    except LocationNotResolvedError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return cities
