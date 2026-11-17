"""Free geo lookups: REST Countries, CountriesNow, US county file, Photon (OSM)."""
from __future__ import annotations

from typing import List

import httpx

from services.location_service import (
    _STATE_NAME_TO_CODE, _STATE_CODE_TO_NAME, _US_CITIES, _normalize_state_token,
    list_counties, nearest_county,
)

_CN = "https://countriesnow.space/api/v0.1"
_PHOTON = "https://photon.komoot.io/api/"
_UA = {"User-Agent": "ZeOrbitSEO/1.0 (local-seo)"}

_cache: dict = {}

_US_REGIONS = [
    ("West", ["AK", "AZ", "CA", "CO", "HI", "ID", "MT", "NM", "NV", "OR", "UT", "WA", "WY"]),
    ("Midwest", ["IA", "IL", "IN", "KS", "MI", "MN", "MO", "ND", "NE", "OH", "SD", "WI"]),
    ("South", ["AL", "AR", "DC", "DE", "FL", "GA", "KY", "LA", "MD", "MS", "NC", "OK", "SC", "TN", "TX", "VA", "WV"]),
    ("Northeast", ["CT", "MA", "ME", "NH", "NJ", "NY", "PA", "RI", "VT"]),
]

_CA_COUNTY_GROUPS = [
    ("San Diego & Imperial", ["San Diego County", "Imperial County"]),
    ("Greater Los Angeles", ["Los Angeles County", "Orange County", "Ventura County", "Riverside County", "San Bernardino County"]),
    ("Central Coast", ["Santa Barbara County", "San Luis Obispo County", "Monterey County", "San Benito County", "Santa Cruz County"]),
    ("Bay Area", ["San Francisco County", "San Mateo County", "Santa Clara County", "Alameda County", "Contra Costa County", "Marin County", "Solano County", "Napa County", "Sonoma County"]),
    ("Central Valley", ["Sacramento County", "Yolo County", "San Joaquin County", "Stanislaus County", "Merced County", "Madera County", "Fresno County", "Kings County", "Tulare County", "Kern County"]),
    ("North & Sierra", ["Shasta County", "Tehama County", "Butte County", "Glenn County", "Colusa County", "Sutter County", "Yuba County", "Nevada County", "Placer County", "El Dorado County", "Amador County", "Calaveras County", "Tuolumne County", "Mariposa County", "Alpine County", "Mono County", "Inyo County"]),
    ("Far North", ["Del Norte County", "Siskiyou County", "Modoc County", "Lassen County", "Plumas County", "Sierra County", "Trinity County", "Humboldt County", "Mendocino County", "Lake County"]),
]

_CN = "https://countriesnow.space/api/v0.1"
_PHOTON = "https://photon.komoot.io/api/"
_UA = {"User-Agent": "ZeOrbitSEO/1.0 (local-seo)"}

_cache: dict = {}


def _is_us(country: str) -> bool:
    t = (country or "").strip().lower()
    return t in {"united states", "united states of america", "usa", "us", "america"}


async def _get_json(url: str, *, params=None, json=None, method="GET"):
    async with httpx.AsyncClient(timeout=14.0, headers=_UA, follow_redirects=True) as client:
        if method == "POST":
            r = await client.post(url, json=json or {})
        else:
            r = await client.get(url, params=params or {})
        r.raise_for_status()
        return r.json()


async def list_countries() -> List[dict]:
    return [{"name": "United States", "code": "US"}]


async def list_states(country: str = "United States") -> List[str]:
    grouped = grouped_us_states()
    names = []
    for g in grouped:
        names.extend(g["states"])
    return names


def grouped_us_states() -> List[dict]:
    out = []
    for region, codes in _US_REGIONS:
        states = []
        for code in codes:
            name = _STATE_CODE_TO_NAME.get(code) or next(
                (n.title() for n, c in _STATE_NAME_TO_CODE.items() if c == code), code
            )
            states.append(name)
        out.append({"region": region, "states": states})
    return out


def grouped_counties(state: str) -> List[dict]:
    rows = list_counties(state)
    names = [r["name"] for r in rows]
    code = (_normalize_state_token(state) or "").upper()
    if code == "CA":
        used = set()
        groups = []
        for region, members in _CA_COUNTY_GROUPS:
            present = [n for n in members if n in names]
            for n in present:
                used.add(n)
            if present:
                groups.append({"region": region, "counties": present})
        leftover = [n for n in names if n not in used]
        if leftover:
            groups.append({"region": "Other California", "counties": leftover})
        return groups
    if len(names) <= 15:
        return [{"region": state or "Counties", "counties": names}]
    lats = sorted((r.get("lat") or 0, r["name"]) for r in rows)
    n = len(lats)
    south = [nm for _, nm in lats[: n // 3]]
    central = [nm for _, nm in lats[n // 3: (2 * n) // 3]]
    north = [nm for _, nm in lats[(2 * n) // 3:]]
    south.sort(); central.sort(); north.sort()
    return [
        {"region": "South", "counties": south},
        {"region": "Central", "counties": central},
        {"region": "North", "counties": north},
    ]


async def list_geo_counties(country: str, state: str) -> List[str]:
    country = (country or "United States").strip()
    state = (state or "").strip()
    if _is_us(country) and state:
        return [r["name"] for r in list_counties(state)]
    return []


async def list_geo_cities(country: str, state: str, county: str = "") -> List[str]:
    country = (country or "United States").strip()
    state = (state or "").strip()
    county = (county or "").strip()
    key = f"cities:{country}:{state}:{county}".lower()
    if key in _cache:
        return _cache[key]
    names: List[str] = []
    if not _is_us(country):
        _cache[key] = []
        return []
    code = _normalize_state_token(state) or (state or "").upper()[:2]
    rows = [r for r in _US_CITIES if (r.get("state") or "").upper() == code and (r.get("city") or "").strip()]
    if county:
        want = county.lower().replace(" county", "").strip()
        for r in rows:
            rec = nearest_county(r["lat"], r["lon"], code)
            cname = (rec or {}).get("name") or ""
            if want in cname.lower() or cname.lower().replace(" county", "") == want:
                names.append(r["city"].strip())
    else:
        names = [r["city"].strip() for r in rows]
    names = sorted(set(names))
    _cache[key] = names
    return names


def list_county_local_areas(state: str, county: str, city: str = "") -> dict:
    """Local areas for a US county, grouped by city (catalog + nearby names)."""
    from services.location_service import build_place_catalog
    state = (state or "California").strip()
    county = (county or "").strip()
    city = (city or "").strip()
    if not county:
        return {"groups": [], "areas": []}
    label = county if "," in county else f"{county}, {_normalize_state_token(state) or 'CA'}"
    data = build_place_catalog(base_location=label, county_name=label, city_name=city if city else "")
    groups = []
    flat = []
    seen = set()
    for c in data.get("cities") or []:
        parent = (c.get("name") or "").strip()
        if not parent or parent.lower() == "unincorporated" and city:
            pass
        if city and parent.lower() != city.lower() and parent.lower() != "unincorporated":
            continue
        areas = [a for a in (c.get("local_areas") or []) if a and a.strip()]
        clean = []
        for a in areas:
            k = a.lower()
            if k in seen or k == parent.lower():
                continue
            seen.add(k)
            clean.append(a)
            flat.append({"name": a, "city": parent if parent.lower() != "unincorporated" else county})
        if clean:
            groups.append({"city": parent, "areas": clean})
    return {"groups": groups, "areas": [x["name"] for x in flat], "items": flat}


async def list_local_areas(country: str, state: str, city: str, county: str = "") -> List[str]:
    city = (city or "").strip()
    state = (state or "").strip()
    country = (country or "").strip()
    if not city:
        return []
    key = f"areas:{country}:{state}:{city}".lower()
    if key in _cache:
        return _cache[key]
    names: List[str] = []
    try:
        data = await _get_json(
            _PHOTON,
            params={"q": f"{city}, {state}, {country}", "limit": 30},
        )
        for feat in data.get("features") or []:
            props = feat.get("properties") or {}
            kind = (props.get("type") or "").lower()
            if kind not in {"district", "suburb", "neighbourhood", "neighborhood", "locality", "quarter", "hamlet"}:
                continue
            n = (props.get("name") or "").strip()
            if n and n.lower() != city.lower() and n.lower() not in {x.lower() for x in names}:
                names.append(n)
        if len(names) < 6:
            extra = await _get_json(_PHOTON, params={"q": f"{city} neighborhood", "limit": 20})
            for feat in extra.get("features") or []:
                props = feat.get("properties") or {}
                n = (props.get("name") or "").strip()
                if n and n.lower() != city.lower() and n.lower() not in {x.lower() for x in names}:
                    names.append(n)
    except Exception as e:
        print(f"[Geo] areas: {e}")
    _cache[key] = names[:400]
    return _cache[key]
