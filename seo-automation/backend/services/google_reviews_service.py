"""Live Google Business reviews via Places API (New) Place Details."""
from __future__ import annotations

import time
from typing import Any, Optional

import httpx
from config import settings

_PLACE_ID = "ChIJpd4HFaVZ2YARFUApQxHkD30"
_PLACE_URL = f"https://places.googleapis.com/v1/places/{_PLACE_ID}"
_FIELD_MASK = "id,displayName,rating,userRatingCount,googleMapsUri,reviews"
_CACHE_TTL = 60 * 30  # 30 minutes so Maps count catches up quickly
# Google Maps listing currently shows 41; Places API userRatingCount often lags.
_MAPS_REVIEW_FLOOR = 41

_cache: dict[str, Any] = {"at": 0.0, "payload": None}


def _map_review(item: dict) -> Optional[dict]:
    text = ((item.get("text") or {}).get("text") or "").strip()
    if not text:
        return None
    attr = item.get("authorAttribution") or {}
    rating = float(item.get("rating") or 5)
    return {
        "author": (attr.get("displayName") or "Google user").strip(),
        "when": item.get("relativePublishTimeDescription") or "",
        "rating": rating,
        "avatar": attr.get("photoUri") or "",
        "profileUrl": attr.get("uri") or "",
        "text": text,
    }


async def fetch_google_reviews() -> dict:
    """Return live rating + reviews. Cached. Raises if Places is not configured."""
    now = time.time()
    if _cache["payload"] and now - _cache["at"] < _CACHE_TTL:
        return _cache["payload"]

    key = (settings.GOOGLE_PLACES_API_KEY or "").strip()
    if not key:
        raise RuntimeError("GOOGLE_PLACES_API_KEY is not set")

    async with httpx.AsyncClient(timeout=20) as client:
        resp = await client.get(
            _PLACE_URL,
            headers={
                "X-Goog-Api-Key": key,
                "X-Goog-FieldMask": _FIELD_MASK,
            },
        )
    if resp.status_code != 200:
        raise RuntimeError(f"Places API {resp.status_code}: {resp.text[:240]}")

    data = resp.json()
    reviews = []
    for item in data.get("reviews") or []:
        mapped = _map_review(item)
        if mapped:
            reviews.append(mapped)

    rating = data.get("rating")
    payload = {
        "live": True,
        "name": ((data.get("displayName") or {}).get("text") or "ZeOrbit"),
        "rating": f"{float(rating):.1f}" if rating is not None else "5.0",
        "reviewCount": max(int(data.get("userRatingCount") or 0), _MAPS_REVIEW_FLOOR),
        "reviewsUrl": data.get("googleMapsUri")
        or "https://maps.app.goo.gl/teVefHUc3yycwkcA7",
        "placeId": _PLACE_ID,
        "reviews": reviews,
    }
    _cache["at"] = now
    _cache["payload"] = payload
    return payload
