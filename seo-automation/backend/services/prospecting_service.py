"""
prospecting_service.py
Discovers real businesses matching an industry + location using the Google Places API
(Places API v1 Text Search + Place Details) and maps them into lead records.

Requires GOOGLE_PLACES_API_KEY. Returns [] gracefully when the key is missing.
"""
import httpx
from typing import List
from config import settings

_PLACES_SEARCH = "https://places.googleapis.com/v1/places:searchText"


async def discover_businesses(industry: str, location: str, limit: int = 20) -> List[dict]:
    """Find businesses via Google Places Text Search. Returns lead dicts."""
    if not settings.GOOGLE_PLACES_API_KEY:
        print("[Prospecting] GOOGLE_PLACES_API_KEY not set — returning no leads.")
        return []

    query = f"{industry} in {location}".strip()
    # Field mask keeps the response (and cost) small while giving us lead data.
    field_mask = (
        "places.displayName,places.formattedAddress,places.websiteUri,"
        "places.internationalPhoneNumber,places.nationalPhoneNumber,"
        "places.primaryTypeDisplayName"
    )
    leads: List[dict] = []
    try:
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.post(
                _PLACES_SEARCH,
                json={"textQuery": query, "pageSize": min(limit, 20)},
                headers={
                    "Content-Type": "application/json",
                    "X-Goog-Api-Key": settings.GOOGLE_PLACES_API_KEY,
                    "X-Goog-FieldMask": field_mask,
                },
            )
            if resp.status_code != 200:
                print(f"[Prospecting] Places API {resp.status_code}: {resp.text[:200]}")
                return []
            for place in resp.json().get("places", [])[:limit]:
                name = (place.get("displayName") or {}).get("text", "")
                phone = place.get("nationalPhoneNumber") or place.get("internationalPhoneNumber") or ""
                leads.append({
                    "source": "prospecting",
                    "business_name": name,
                    "name": name,
                    "contact_name": "",
                    "email": "",
                    "phone": phone,
                    "website": place.get("websiteUri", "") or "",
                    "industry": industry,
                    "service": (place.get("primaryTypeDisplayName") or {}).get("text", industry),
                    "location": place.get("formattedAddress", location),
                    "budget": "",
                    "message": "",
                    "status": "new",
                })
    except Exception as e:
        print(f"[Prospecting] error: {e}")
    return leads
