"""
location_service.py
Nationwide (USA) nearby-city lookup.

Geocodes a base location by matching a bundled free US cities dataset
(data/us_cities.json, ~30k cities) — no API key required. Falls back to
OpenCage geocoding (free tier) and finally a small San Diego seed list.
"""
import os
import json
import math
import httpx
from typing import List, Optional, Tuple
from models.schemas import CityInfo
from config import settings

# ── Bundled dataset ─────────────────────────────────────────────
_DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "us_cities.json")
_US_CITIES: List[dict] = []
try:
    with open(_DATA_PATH, encoding="utf-8") as _f:
        _US_CITIES = json.load(_f)
except Exception as _e:  # pragma: no cover
    print(f"[Location] Could not load us_cities.json: {_e}")

_STATE_NAME_TO_CODE = {
    "alabama": "AL", "alaska": "AK", "arizona": "AZ", "arkansas": "AR", "california": "CA",
    "colorado": "CO", "connecticut": "CT", "delaware": "DE", "florida": "FL", "georgia": "GA",
    "hawaii": "HI", "idaho": "ID", "illinois": "IL", "indiana": "IN", "iowa": "IA",
    "kansas": "KS", "kentucky": "KY", "louisiana": "LA", "maine": "ME", "maryland": "MD",
    "massachusetts": "MA", "michigan": "MI", "minnesota": "MN", "mississippi": "MS",
    "missouri": "MO", "montana": "MT", "nebraska": "NE", "nevada": "NV", "new hampshire": "NH",
    "new jersey": "NJ", "new mexico": "NM", "new york": "NY", "north carolina": "NC",
    "north dakota": "ND", "ohio": "OH", "oklahoma": "OK", "oregon": "OR", "pennsylvania": "PA",
    "rhode island": "RI", "south carolina": "SC", "south dakota": "SD", "tennessee": "TN",
    "texas": "TX", "utah": "UT", "vermont": "VT", "virginia": "VA", "washington": "WA",
    "west virginia": "WV", "wisconsin": "WI", "wyoming": "WY", "district of columbia": "DC",
}

# Ultimate fallback if the dataset is missing and geocoding fails.
_DEFAULT_LATLON = (32.7157, -117.1611)  # San Diego, CA


def haversine(lat1, lon1, lat2, lon2) -> float:
    R = 3958.8  # miles
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    return R * 2 * math.asin(math.sqrt(a))


def _parse_location(base_location: str) -> Tuple[str, Optional[str]]:
    """'Austin, TX' -> ('austin', 'TX'); 'Austin, Texas' -> ('austin','TX'); 'Austin' -> ('austin', None)."""
    parts = [p.strip() for p in base_location.split(",") if p.strip()]
    city = parts[0].lower() if parts else base_location.strip().lower()
    state = None
    if len(parts) >= 2:
        raw = parts[1].strip()
        state = raw.upper() if len(raw) == 2 else _STATE_NAME_TO_CODE.get(raw.lower())
    return city, state


def _geocode_from_dataset(base_location: str) -> Optional[dict]:
    """Find the base city record in the bundled dataset."""
    city, state = _parse_location(base_location)
    matches = [c for c in _US_CITIES if c["city"].lower() == city and (not state or c["state"] == state)]
    if not matches and not state:
        # loose contains-match as a last resort
        matches = [c for c in _US_CITIES if c["city"].lower() == city]
    return matches[0] if matches else None


async def _geocode_opencage(base_location: str) -> Optional[Tuple[float, float]]:
    if not settings.OPENCAGE_API_KEY:
        return None
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                "https://api.opencagedata.com/geocode/v1/json",
                params={"q": base_location, "key": settings.OPENCAGE_API_KEY, "limit": 1, "countrycode": "us"},
            )
            data = resp.json()
            if data.get("results"):
                geo = data["results"][0]["geometry"]
                return geo["lat"], geo["lng"]
    except Exception:
        pass
    return None


async def get_nearby_cities(base_location: str, num_cities: int = 10) -> List[CityInfo]:
    """Return the N nearest US cities to the base location (nationwide)."""
    base_city_rec = _geocode_from_dataset(base_location)
    if base_city_rec:
        base_lat, base_lon = base_city_rec["lat"], base_city_rec["lon"]
    else:
        latlon = await _geocode_opencage(base_location)
        base_lat, base_lon = latlon if latlon else _DEFAULT_LATLON

    if not _US_CITIES:
        # Dataset unavailable — return just the base location so callers still work.
        city, state = _parse_location(base_location)
        return [CityInfo(name=city.title(), state=state or "", country="USA",
                         latitude=base_lat, longitude=base_lon)]

    scored = []
    seen = set()
    for c in _US_CITIES:
        key = (c["city"].lower(), c["state"])
        if key in seen:
            continue
        seen.add(key)
        dist = haversine(base_lat, base_lon, c["lat"], c["lon"])
        scored.append((dist, c))
    scored.sort(key=lambda x: x[0])

    result = []
    for _, c in scored[:num_cities]:
        result.append(CityInfo(
            name=c["city"], state=c["state"], country="USA",
            latitude=c["lat"], longitude=c["lon"],
        ))
    return result
