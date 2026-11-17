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


@router.get("/county-cities")
async def county_cities(state: str = Query(...), county: str = Query(...), limit: int = Query(default=25, ge=1, le=80)):
    from services.location_service import cities_in_county
    rows = cities_in_county(state, county, limit)
    return {"county": county, "state": state, "cities": rows, "total": len(rows)}


@router.get("/us-counties")
async def all_us_counties():
    """Every county in the US dataset, labeled with its state."""
    from services.location_service import _STATE_CODE_TO_NAME, _US_COUNTIES
    rows = []
    for county in _US_COUNTIES:
        code = county.get("state") or ""
        name = county.get("name") or ""
        state_name = _STATE_CODE_TO_NAME.get(code, code)
        rows.append({
            "name": name,
            "state": code,
            "state_name": state_name,
            "label": f"{name}, {state_name}",
        })
    rows.sort(key=lambda row: row["label"])
    return {"country": "United States", "counties": rows, "total": len(rows)}


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


@router.get("/geo/countries")
async def geo_countries():
    from services.geo_places import list_countries
    rows = await list_countries()
    return {"countries": rows, "total": len(rows)}


@router.get("/geo/states")
async def geo_states(country: str = Query(default="United States")):
    from services.geo_places import list_states, grouped_us_states
    rows = await list_states(country)
    return {"country": "United States", "states": rows, "groups": grouped_us_states(), "total": len(rows)}


@router.get("/geo/counties")
async def geo_counties(
    country: str = Query(default="United States"),
    state: str = Query(default="California"),
):
    from services.geo_places import list_geo_counties, grouped_counties
    rows = await list_geo_counties(country, state)
    return {
        "country": "United States",
        "state": state,
        "counties": rows,
        "groups": grouped_counties(state),
        "total": len(rows),
    }


@router.get("/geo/cities")
async def geo_cities(
    country: str = Query(default="United States"),
    state: str = Query(default="California"),
    county: str = Query(default=""),
):
    from services.geo_places import list_geo_cities
    rows = await list_geo_cities(country, state, county)
    return {"country": "United States", "state": state, "county": county, "cities": rows, "total": len(rows)}


@router.get("/geo/areas")
async def geo_areas(
    country: str = Query(default="United States"),
    state: str = Query(default="California"),
    city: str = Query(default=""),
    county: str = Query(default=""),
):
    from services.geo_places import list_county_local_areas, list_local_areas
    if county:
        data = list_county_local_areas(state, county, city)
        extra = []
        if city:
            extra = await list_local_areas(country, state, city, county)
        seen = {a.lower() for a in data.get("areas") or []}
        for n in extra:
            if n.lower() not in seen:
                data.setdefault("items", []).append({"name": n, "city": city})
                data.setdefault("areas", []).append(n)
                seen.add(n.lower())
                # attach to city group
                found = False
                for g in data.get("groups") or []:
                    if (g.get("city") or "").lower() == city.lower():
                        g.setdefault("areas", []).append(n)
                        found = True
                        break
                if not found:
                    data.setdefault("groups", []).append({"city": city, "areas": [n]})
        return {
            "country": "United States",
            "state": state,
            "county": county,
            "city": city,
            "groups": data.get("groups") or [],
            "items": data.get("items") or [],
            "areas": data.get("areas") or [],
            "total": len(data.get("areas") or []),
        }
    rows = await list_local_areas(country, state, city)
    return {"country": "United States", "state": state, "city": city, "areas": rows, "groups": [], "items": [{"name": a, "city": city} for a in rows], "total": len(rows)}


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
