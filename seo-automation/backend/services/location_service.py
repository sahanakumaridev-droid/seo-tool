"""
location_service.py
Nationwide (USA) nearby-city / state / county lookup.

Geocodes a base location by matching:
  1. US state name or code (e.g. "Illinois", "Illinois, IL", "IL")
  2. US county (e.g. "Orange County, CA")
  3. Bundled free US cities dataset (data/us_cities.json, ~30k cities)
Falls back to OpenCage geocoding (free tier) when needed.
"""
import os
import json
import math
import re
import httpx
from typing import List, Optional, Tuple
from models.schemas import CityInfo
from config import settings

# ── Bundled datasets ─────────────────────────────────────────────
_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
_US_CITIES: List[dict] = []
_US_STATES: dict = {}
_US_COUNTIES: List[dict] = []

try:
    with open(os.path.join(_DATA_DIR, "us_cities.json"), encoding="utf-8") as _f:
        _US_CITIES = json.load(_f)
except Exception as _e:  # pragma: no cover
    print(f"[Location] Could not load us_cities.json: {_e}")

try:
    with open(os.path.join(_DATA_DIR, "us_state_centroids.json"), encoding="utf-8") as _f:
        _US_STATES = json.load(_f)
except Exception as _e:  # pragma: no cover
    print(f"[Location] Could not load us_state_centroids.json: {_e}")

try:
    with open(os.path.join(_DATA_DIR, "us_counties.json"), encoding="utf-8") as _f:
        _US_COUNTIES = json.load(_f)
except Exception as _e:  # pragma: no cover
    print(f"[Location] Could not load us_counties.json: {_e}")

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
_STATE_CODE_TO_NAME = {code: meta["name"] for code, meta in _US_STATES.items()}
# Also fill from name map if centroid file missing names
for _n, _c in _STATE_NAME_TO_CODE.items():
    _STATE_CODE_TO_NAME.setdefault(_c, _n.title())


class LocationNotResolvedError(Exception):
    """Raised when a base location can't be matched in the dataset or geocoded."""


_DEFAULT_LATLON = (32.7157, -117.1611)  # San Diego, CA

_MAJOR_CITY_OVERRIDES = {
    "austin": "TX", "columbus": "OH", "springfield": "MO", "richmond": "VA",
    "portland": "OR", "arlington": "TX", "franklin": "TN", "salem": "OR",
    "georgetown": "TX", "clinton": "MD", "greenville": "SC", "charleston": "SC",
    "columbia": "SC", "lexington": "KY", "jackson": "MS", "madison": "WI",
    "manchester": "NH", "burlington": "VT", "auburn": "AL", "rochester": "NY",
    "kingston": "NY", "aurora": "CO", "peoria": "IL", "bristol": "CT",
    "cambridge": "MA", "concord": "NH", "dover": "DE", "florence": "AL",
    "jacksonville": "FL", "lancaster": "PA", "marion": "IN", "monroe": "LA",
    "newport": "RI", "oxford": "MS", "paris": "TX", "riverside": "CA",
    "troy": "MI", "washington": "DC", "alexandria": "VA", "arlington heights": "IL",
    "bellevue": "WA", "berlin": "NH", "cleveland": "OH", "dayton": "OH",
    "denton": "TX", "fairfield": "CA", "glendale": "AZ", "hamilton": "OH",
    "henderson": "NV", "irving": "TX", "kent": "WA", "lakewood": "CO",
    "lincoln": "NE", "milford": "CT", "naperville": "IL", "norfolk": "VA",
    "orange": "CA", "pasadena": "CA", "plymouth": "MA", "rockford": "IL",
    "rome": "GA", "salisbury": "MD", "santa fe": "NM", "savannah": "GA",
    "sterling": "VA", "vancouver": "WA", "waterloo": "IA",
    "chicago": "IL", "honolulu": "HI", "hartford": "CT", "raleigh": "NC",
    "charlotte": "NC", "sacramento": "CA", "san diego": "CA", "los angeles": "CA",
}


def haversine(lat1, lon1, lat2, lon2) -> float:
    R = 3958.8  # miles
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    return R * 2 * math.asin(math.sqrt(a))


def _normalize_state_token(raw: str) -> Optional[str]:
    """Return 2-letter state code for a name or code, else None."""
    if not raw:
        return None
    t = raw.strip()
    if len(t) == 2 and t.upper() in _US_STATES:
        return t.upper()
    return _STATE_NAME_TO_CODE.get(t.lower())


def _parse_location(base_location: str) -> Tuple[str, Optional[str]]:
    """'Austin, TX' -> ('austin', 'TX'); 'Austin, Texas' -> ('austin','TX'); 'Austin' -> ('austin', None)."""
    parts = [p.strip() for p in base_location.split(",") if p.strip()]
    city = parts[0].lower() if parts else base_location.strip().lower()
    state = None
    if len(parts) >= 2:
        state = _normalize_state_token(parts[1])
    return city, state


def _resolve_as_state(base_location: str) -> Optional[dict]:
    """
    Detect when the user entered a US state (not a city).
    Accepts: "Illinois", "Illinois, IL", "IL", "North Carolina, NC", "Hawaii, HI".
    Returns {code, name, lat, lon} or None.
    """
    raw = (base_location or "").strip()
    if not raw:
        return None
    parts = [p.strip() for p in raw.split(",") if p.strip()]
    first = parts[0]
    second = parts[1] if len(parts) > 1 else None

    code_from_first = _normalize_state_token(first)
    code_from_second = _normalize_state_token(second) if second else None

    # "IL" alone
    if code_from_first and len(first) == 2 and not second:
        code = code_from_first
    # "Illinois" or "North Carolina"
    elif code_from_first and len(first) > 2:
        # If second part is present, it must match or be absent of conflicting code
        if code_from_second and code_from_second != code_from_first:
            return None
        code = code_from_first
    # "Illinois, IL" where first is name and second is code — already handled above
    # "Something, IL" where first is NOT a state name — not a state query
    else:
        return None

    meta = _US_STATES.get(code)
    if not meta:
        return None
    return {"code": code, "name": meta["name"], "lat": meta["lat"], "lon": meta["lon"]}


def _normalize_county_name(name: str) -> str:
    n = (name or "").strip().lower()
    n = n.replace(" parish", "").replace(" municipality", "").replace(" county", "").strip()
    return n


def _resolve_as_county(base_location: str) -> Optional[dict]:
    """Match only explicit county/parish queries, e.g. 'Orange County, CA'.

    Bare city names like 'San Diego, CA' must NOT match 'San Diego County'.
    """
    city, state = _parse_location(base_location)
    if "county" not in city and "parish" not in city and "municipality" not in city:
        return None

    target = _normalize_county_name(city)
    matches = [
        c for c in _US_COUNTIES
        if _normalize_county_name(c["name"]) == target and (not state or c["state"] == state)
    ]
    return matches[0] if matches else None


def _geocode_from_dataset(base_location: str) -> Optional[dict]:
    """Find the base city record in the bundled dataset."""
    city, state = _parse_location(base_location)
    # Don't treat state names as cities
    if _normalize_state_token(city) and (not state or _normalize_state_token(city) == state or len(city) > 2):
        if city in _STATE_NAME_TO_CODE or (len(city) == 2 and city.upper() in _US_STATES):
            return None
    matches = [c for c in _US_CITIES if c["city"].lower() == city and (not state or c["state"] == state)]
    if not matches and not state:
        matches = [c for c in _US_CITIES if c["city"].lower() == city]
    if len(matches) > 1 and not state:
        override_state = _MAJOR_CITY_OVERRIDES.get(city)
        if override_state:
            preferred = [c for c in matches if c["state"] == override_state]
            if preferred:
                return preferred[0]
    return matches[0] if matches else None


async def _geocode_opencage(base_location: str) -> Optional[Tuple[float, float]]:
    place = await _geocode_opencage_place(base_location)
    if not place:
        return None
    return place["lat"], place["lon"]


async def _geocode_opencage_place(base_location: str) -> Optional[dict]:
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
                r = data["results"][0]
                geo = r.get("geometry") or {}
                comps = r.get("components") or {}
                city = (
                    comps.get("city")
                    or comps.get("town")
                    or comps.get("village")
                    or comps.get("county")
                    or ""
                )
                state = (comps.get("state_code") or "").upper()
                postcode = (comps.get("postcode") or "").split()[0] if comps.get("postcode") else ""
                return {
                    "lat": geo.get("lat") or 0.0,
                    "lon": geo.get("lng") or 0.0,
                    "city": city,
                    "state": state,
                    "zip": re.sub(r"\D", "", postcode)[:5],
                }
    except Exception:
        pass
    return None


def _city_info(name: str, state: str, lat: float, lon: float, kind: str = "city", zip: str = "") -> CityInfo:
    return CityInfo(
        name=name, state=state, country="USA",
        latitude=lat, longitude=lon, kind=kind, zip=zip or "",
    )


_STATE_ABBR = re.compile(r"^[A-Za-z]{2}$")
_ZIP_RE = re.compile(r"^\d{5}(?:-\d{4})?$")
_STATE_ZIP = re.compile(r"^([A-Za-z]{2})\s+(\d{5})(?:-\d{4})?$")
_ZIP_IN_TEXT = re.compile(r"\b(\d{5})(?:-\d{4})?\b")


def split_location_labels(raw: str) -> List[str]:
    """Turn pasted lists into one location each.

    'San Diego, CA, Chula Vista, CA' → two cities.
    'Balboa Park, Banker's Hill, Bay Terraces' → three communities.
    'San Diego, CA' stays a single city+state.
    """
    text = (raw or "").strip()
    if not text:
        return []
    chunks = re.split(r"[\n;]+", text)
    out: List[str] = []
    for chunk in chunks:
        tokens = [t.strip() for t in chunk.split(",") if t.strip()]
        i = 0
        while i < len(tokens):
            name = tokens[i]
            nxt = tokens[i + 1] if i + 1 < len(tokens) else ""
            nxt2 = tokens[i + 2] if i + 2 < len(tokens) else ""
            sz = _STATE_ZIP.fullmatch(nxt) if nxt else None
            if nxt and _STATE_ABBR.fullmatch(nxt) and nxt2 and _ZIP_RE.fullmatch(nxt2):
                out.append(f"{name}, {nxt.upper()} {nxt2[:5]}")
                i += 3
            elif sz:
                out.append(f"{name}, {sz.group(1).upper()} {sz.group(2)}")
                i += 2
            elif nxt and _STATE_ABBR.fullmatch(nxt):
                out.append(f"{name}, {nxt.upper()}")
                i += 2
            elif _ZIP_RE.fullmatch(name):
                out.append(name[:5])
                i += 1
            else:
                out.append(name)
                i += 1
    seen = set()
    unique = []
    for label in out:
        key = re.sub(r"\s+", " ", label).strip().lower()
        if key in seen:
            continue
        seen.add(key)
        unique.append(label)
    return unique


def city_from_label(text: str, default_state: str = "") -> Optional[CityInfo]:
    """Parse a typed or dropdown location like 'Coronado, CA' or ZIP '92101' into CityInfo."""
    raw = (text or "").strip()
    if not raw:
        return None
    zip_code = ""
    zm = _ZIP_IN_TEXT.search(raw)
    if zm:
        zip_code = zm.group(1)
        raw = _ZIP_IN_TEXT.sub("", raw).strip(" ,")
    if zip_code and not raw:
        return _city_info(zip_code, default_state or "", 0.0, 0.0, "zip", zip=zip_code)
    if "," in raw:
        name, rest = [p.strip() for p in raw.split(",", 1)]
        # Only treat the remainder as a state if it is a 2-letter code.
        # Otherwise this was a bulk list stuffed into one field.
        rest_state = rest.split()[0] if rest else ""
        if _STATE_ABBR.fullmatch(rest) or _STATE_ABBR.fullmatch(rest_state):
            state = (rest if _STATE_ABBR.fullmatch(rest) else rest_state).upper()
        else:
            name = split_location_labels(raw)[0] if split_location_labels(raw) else name
            state = default_state
            if "," in name and _STATE_ABBR.fullmatch(name.split(",")[-1].strip()):
                name, st = [p.strip() for p in name.rsplit(",", 1)]
                state = st.upper()
    else:
        name, state = raw, default_state
    if not name:
        return None
    kind = "zip" if zip_code and name == zip_code else "city"
    return _city_info(name, state or "", 0.0, 0.0, kind, zip=zip_code)


def flatten_extra_locations(extra_labels: Optional[List[str]], default_state: str = "") -> List[CityInfo]:
    """Expand chips / pasted lists into one CityInfo per place."""
    out: List[CityInfo] = []
    seen = set()
    for label in extra_labels or []:
        for part in split_location_labels(label):
            info = city_from_label(part, default_state=default_state)
            if not info:
                continue
            key = (info.name.lower(), (info.state or "").lower(), (info.zip or "").lower())
            if key in seen:
                continue
            seen.add(key)
            out.append(info)
    return out


async def resolve_generation_cities(
    base_location: str,
    num_cities: int,
    extra_labels: Optional[List[str]] = None,
) -> List[CityInfo]:
    """Build the page list for generate.

    Automation path (no chips): expand from base_location into nearby cities,
    plus local areas / streets when catalog data exists (e.g. San Diego County).

    Legacy path: chips first, then nearby fill up to num_cities.
    """
    default_state = ""
    if base_location and "," in base_location:
        maybe = base_location.split(",")[-1].strip()
        if _STATE_ABBR.fullmatch(maybe):
            default_state = maybe.upper()
    extras = flatten_extra_locations(extra_labels, default_state=default_state)
    num = max(1, min(int(num_cities or 1), 250))
    loc = (base_location or "").strip()
    # ZIP in the base field (e.g. "92101" or "San Diego, CA 92101")
    base_place = city_from_label(loc, default_state=default_state) if loc else None

    nearby: List[CityInfo] = []
    try:
        if loc and not (base_place and base_place.kind == "zip"):
            nearby = await expand_places_from_base(loc, num)
        elif extras:
            seed = f"{extras[0].name}, {extras[0].state}".strip(", ")
            if seed.strip(", ") and not re.fullmatch(r"\d{5}", extras[0].name or ""):
                nearby = await expand_places_from_base(seed, num)
    except LocationNotResolvedError:
        nearby = []

    if extras:
        # Pinned chips are the source of truth — never truncate 90 ZIPs down to the slider.
        target = min(250, max(num, len(extras)))
        if len(extras) >= target:
            result = extras[:target]
        else:
            result = merge_extra_locations(nearby, extra_labels)[:target]
    elif base_place and (base_place.zip or base_place.kind == "zip"):
        result = [base_place]
        if nearby:
            result = merge_extra_locations(nearby, [loc])[:num]
            if not any((c.zip or "") == base_place.zip for c in result):
                result = [base_place] + result[: max(0, num - 1)]
    else:
        result = nearby[:num]

    seed = loc or (f"{extras[0].name}, {extras[0].state}" if extras else "")
    result = await _pad_places_to_count(result, num, seed)

    enriched: List[CityInfo] = []
    for info in result:
        enriched.append(await enrich_zip_place(info))
    return enriched


# Primary ZIP for incorporated San Diego County cities (used when geocoders miss).
_SD_CITY_ZIPS = {
    "carlsbad": "92008", "chula vista": "91910", "coronado": "92118", "del mar": "92014",
    "el cajon": "92020", "encinitas": "92024", "escondido": "92025", "imperial beach": "91932",
    "la mesa": "91941", "lemon grove": "91945", "national city": "91950", "oceanside": "92054",
    "poway": "92064", "san diego": "92101", "san marcos": "92069", "santee": "92071",
    "solana beach": "92075", "vista": "92081",
}

_ZIP_LOOKUP_CACHE: dict = {}


def _zip_query_names(name: str) -> List[str]:
    raw = (name or "").strip()
    if not raw:
        return []
    parts = [p.strip() for p in raw.split(",") if p.strip()]
    out: List[str] = []
    for p in reversed(parts):
        if p not in out:
            out.append(p)
    if raw not in out:
        out.append(raw)
    return out


async def _zippopotam_zip(place: str, state: str) -> str:
    st = (state or "").strip().lower()
    city = (place or "").split(",")[0].strip().lower()
    if not st or not city or len(st) != 2:
        return ""
    key = f"zp|{st}|{city}"
    if key in _ZIP_LOOKUP_CACHE:
        return _ZIP_LOOKUP_CACHE[key]
    try:
        from urllib.parse import quote
        url = f"https://api.zippopotam.us/us/{st}/{quote(city)}"
        async with httpx.AsyncClient(timeout=8) as client:
            resp = await client.get(url)
        if resp.status_code != 200:
            _ZIP_LOOKUP_CACHE[key] = ""
            return ""
        places = (resp.json() or {}).get("places") or []
        codes = []
        for p in places:
            z = re.sub(r"\D", "", str(p.get("post code") or ""))[:5]
            if len(z) == 5 and z not in codes:
                codes.append(z)
        if not codes:
            _ZIP_LOOKUP_CACHE[key] = ""
            return ""
        pick = codes[int(hashlib_md5_mod(city, len(codes)))]
        _ZIP_LOOKUP_CACHE[key] = pick
        return pick
    except Exception:
        return ""


def hashlib_md5_mod(text: str, n: int) -> int:
    import hashlib
    if n <= 0:
        return 0
    return int(hashlib.md5(text.encode("utf-8")).hexdigest(), 16) % n


async def _nominatim_zip(place: str, state: str) -> str:
    q = f"{place}, {state}, USA".strip(", ")
    key = f"nm|{q.lower()}"
    if key in _ZIP_LOOKUP_CACHE:
        return _ZIP_LOOKUP_CACHE[key]
    try:
        async with httpx.AsyncClient(timeout=10, headers={"User-Agent": "ZeOrbitSEO/1.0 (local-seo)"}) as client:
            resp = await client.get(
                "https://nominatim.openstreetmap.org/search",
                params={"q": q, "format": "json", "addressdetails": 1, "limit": 1, "countrycodes": "us"},
            )
        if resp.status_code != 200:
            _ZIP_LOOKUP_CACHE[key] = ""
            return ""
        rows = resp.json() or []
        if not rows:
            _ZIP_LOOKUP_CACHE[key] = ""
            return ""
        z = re.sub(r"\D", "", str((rows[0].get("address") or {}).get("postcode") or ""))[:5]
        _ZIP_LOOKUP_CACHE[key] = z if len(z) == 5 else ""
        return _ZIP_LOOKUP_CACHE[key]
    except Exception:
        return ""


def _static_sd_zip(name: str) -> str:
    n = (name or "").strip().lower()
    if n in _SD_CITY_ZIPS:
        return _SD_CITY_ZIPS[n]
    for part in _zip_query_names(name):
        k = part.lower()
        if k in _SD_CITY_ZIPS:
            return _SD_CITY_ZIPS[k]
        for city, z in _SD_CITY_ZIPS.items():
            if city in k or k in city:
                return z
    return ""


async def lookup_place_zip(name: str, state: str, existing: str = "") -> str:
    """Resolve a 5-digit ZIP for a city, area, or street."""
    z = re.sub(r"\D", "", existing or "")[:5]
    if len(z) == 5:
        return z
    st = (state or "").strip()
    for label in _zip_query_names(name):
        got = await _zippopotam_zip(label, st)
        if got:
            return got
        got = await _nominatim_zip(label, st)
        if got:
            return got
    static = _static_sd_zip(name)
    if static:
        return static
    return ""


async def enrich_zip_place(info: CityInfo) -> CityInfo:
    """Fill city/state/ZIP so copy can name a postal code."""
    if not info:
        return info
    query = (info.zip or "").strip()
    if not query and info.kind != "zip":
        query = f"{info.name}, {info.state} {info.zip}".strip()
    if not query:
        query = (info.name or "").strip()
    if not query:
        return info
    place = await _geocode_opencage_place(
        query if re.fullmatch(r"\d{5}", query) else query
    )
    name = info.name
    kind = info.kind
    state = info.state or ""
    zip_code = (info.zip or "")[:5]
    if place:
        if info.kind == "zip" or (info.zip and (not name or name == info.zip)):
            name = place.get("city") or info.name
        if info.kind == "zip" and name and name != (info.zip or ""):
            kind = "city"
        state = (place.get("state") or info.state or "")
        zip_code = (info.zip or place.get("zip") or "")[:5]
    if len(re.sub(r"\D", "", zip_code)) != 5:
        zip_code = await lookup_place_zip(name or info.name, state or info.state, zip_code)
    return CityInfo(
        name=name,
        state=state or info.state or "",
        country=info.country or "USA",
        latitude=(place or {}).get("lat") or info.latitude,
        longitude=(place or {}).get("lon") or info.longitude,
        population=info.population,
        kind=kind,
        zip=re.sub(r"\D", "", zip_code or "")[:5],
    )


_SD_COUNTY_CACHE = None


def _san_diego_county_data() -> Optional[dict]:
    global _SD_COUNTY_CACHE
    if _SD_COUNTY_CACHE is not None:
        return _SD_COUNTY_CACHE or None
    path = os.path.join(_DATA_DIR, "san_diego_county.json")
    try:
        with open(path, encoding="utf-8") as f:
            _SD_COUNTY_CACHE = json.load(f)
    except Exception:
        _SD_COUNTY_CACHE = {}
    return _SD_COUNTY_CACHE or None


def list_counties(state: str = "CA") -> List[dict]:
    """Counties in a state (California has 58)."""
    code = (_normalize_state_token(state) or (state or "CA").upper())[:2]
    rows = [c for c in _US_COUNTIES if c.get("state") == code]
    rows.sort(key=lambda c: c.get("name") or "")
    return rows


def nearest_county(lat: float, lon: float, state: Optional[str] = None) -> Optional[dict]:
    best = None
    best_d = 1e18
    for c in _US_COUNTIES:
        if state and c.get("state") != state:
            continue
        d = haversine(lat, lon, c["lat"], c["lon"])
        if d < best_d:
            best_d, best = d, c
    return best


# Distinct major roads so Orange ≠ Fresno ≠ San Diego in the Streets layer.
_COUNTY_ROADS = {
    "Alameda": ["International Blvd", "Hesperian Blvd", "Foothill Blvd", "Mission Blvd", "San Pablo Ave", "Broadway", "Park St", "Grand Ave"],
    "Contra Costa": ["San Pablo Ave", "Geary Rd", "Ygnacio Valley Rd", "Treat Blvd", "Clayton Rd", "Monument Blvd", "Bailey Rd"],
    "El Dorado": ["US-50", "Missouri Flat Rd", "El Dorado Hills Blvd", "Green Valley Rd", "Cameron Park Dr"],
    "Fresno": ["Shaw Ave", "Herndon Ave", "Blackstone Ave", "Clovis Ave", "Kings Canyon Rd", "Cedar Ave", "Palm Ave", "Shields Ave", "Ventura Ave"],
    "Humboldt": ["US-101", "Broadway", "4th St", "Harrison Ave", "Myrtle Ave", "Old Arcata Rd"],
    "Imperial": ["Imperial Ave", "Danenberg Dr", "Highway 86", "Highway 111", "Aten Rd"],
    "Kern": ["Chester Ave", "California Ave", "Ming Ave", "Rosedale Hwy", "Weedpatch Hwy", "Norris Rd", "Olive Dr"],
    "Kings": ["11th Ave", "Lacey Blvd", "Houston Ave", "Hanford-Armona Rd", "Highway 198"],
    "Los Angeles": ["Wilshire Blvd", "Sunset Blvd", "Santa Monica Blvd", "Vermont Ave", "Figueroa St", "Crenshaw Blvd", "Western Ave", "Ventura Blvd", "Sepulveda Blvd", "Pacific Coast Hwy"],
    "Marin": ["4th St", "Sir Francis Drake Blvd", "Miracle Mile", "Tiburon Blvd", "Mill Valley-Sausalito Path", "Redwood Hwy"],
    "Monterey": ["Lighthouse Ave", "Cannery Row", "Fremont Blvd", "Reservation Rd", "Carmel Valley Rd", "Highway 1"],
    "Napa": ["Soscol Ave", "Jefferson St", "Silverado Trail", "Highway 29", "Trancas St"],
    "Orange": ["Pacific Coast Hwy", "Harbor Blvd", "Beach Blvd", "Katella Ave", "Chapman Ave", "Jamboree Rd", "Irvine Blvd", "Culver Dr", "Brookhurst St", "Tustin Ave", "MacArthur Blvd"],
    "Placer": ["Douglas Blvd", "Sunrise Blvd", "Auburn Folsom Rd", "Highway 49", "Rocklin Rd", "Stanford Ranch Rd"],
    "Riverside": ["Magnolia Ave", "Arlington Ave", "Van Buren Blvd", "Highway 111", "Ramona Expwy", "Limonite Ave", "Indiana Ave"],
    "Sacramento": ["Watt Ave", "Sunrise Blvd", "Florin Rd", "Stockton Blvd", "Truxel Rd", "Fair Oaks Blvd", "El Camino Ave", "Howe Ave"],
    "San Bernardino": ["E St", "Hospitality Ln", "Baseline St", "Foothill Blvd", "Sierra Ave", "Waterman Ave", "Tippecanoe Ave"],
    "San Diego": ["El Camino Real", "Pacific Hwy", "Mira Mesa Blvd", "University Ave", "El Cajon Blvd", "Palm Ave", "Otay Lakes Rd", "Broadway"],
    "San Francisco": ["Market St", "Mission St", "Van Ness Ave", "Geary Blvd", "19th Ave", "Lombard St", "Castro St", "Fillmore St"],
    "San Joaquin": ["Pacific Ave", "March Ln", "Hammer Ln", "West Ln", "Charter Way", "I-5", "Highway 99"],
    "San Luis Obispo": ["Monterey St", "Broad St", "Santa Rosa St", "Los Osos Valley Rd", "South Higuera St"],
    "San Mateo": ["El Camino Real", "Woodside Rd", "Hillsdale Blvd", "Holly St", "Millbrae Ave", "Broadway"],
    "Santa Barbara": ["State St", "Carrillo St", "Milpas St", "Upper State", "Hollister Ave", "Cathedral Oaks Rd"],
    "Santa Clara": ["El Camino Real", "Stevens Creek Blvd", "Saratoga Ave", "Bascom Ave", "Almaden Expwy", "Capitol Expwy", "Lawrence Expwy"],
    "Santa Cruz": ["Pacific Ave", "Mission St", "Soquel Ave", "Water St", "Ocean St", "Highway 1"],
    "Solano": ["Texas St", "Georgia St", "Tennessee St", "Alamo Dr", "Peabody Rd", "North Texas St"],
    "Sonoma": ["4th St", "Santa Rosa Ave", "Mendocino Ave", "Highway 12", "Petaluma Blvd", "Farmers Ln"],
    "Stanislaus": ["McHenry Ave", "Yosemite Blvd", "Sisk Rd", "Dale Rd", "Pelandale Ave", "Standiford Ave"],
    "Tulare": ["Mooney Blvd", "Mineral King Ave", "Caldwell Ave", "Highway 198", "Main St"],
    "Ventura": ["Main St", "Telephone Rd", "Victoria Ave", "Harbor Blvd", "Thousand Oaks Blvd", "Saviers Rd"],
    "Yolo": ["Russell Blvd", "Covell Blvd", "Richards Blvd", "West Capitol Ave", "Mace Blvd"],
}


def _uniq_names(items: list) -> List[str]:
    seen = set()
    out = []
    for raw in items:
        name = " ".join(str(raw or "").split())
        if not name:
            continue
        key = name.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(name)
    return out


def _county_short(county: dict | str) -> str:
    if isinstance(county, dict):
        n = county.get("name") or ""
    else:
        n = county or ""
    return re.sub(r"\s+county$", "", n, flags=re.I).strip() or n


def _fallback_streets(city: str, county_name: str = "", extra_cities: Optional[List[str]] = None) -> List[str]:
    """County-first roads, then this city's named streets — never a clone of another county."""
    short = _county_short(county_name)
    name = (city or short or "Main").strip()
    stems = list(_COUNTY_ROADS.get(short, []))
    stems.extend([f"{name} Blvd", f"{name} Ave", f"{name} Rd", f"{name} Pkwy"])
    for other in (extra_cities or [])[:6]:
        if other and other.lower() != name.lower():
            stems.append(f"{other} Rd")
    stems.extend([f"{short} Parkway", f"{short} County Rd"])
    return _uniq_names(stems)[:24]


def _local_areas_for_city(city: str, nearby_names: List[str], county_name: str = "") -> List[str]:
    name = (city or "").strip()
    short = _county_short(county_name)
    areas = [
        f"Downtown {name}" if name else f"Downtown {short}",
        f"{name} Heights" if name else f"{short} Heights",
        f"North {name}" if name else f"North {short}",
        f"{name} Village" if name else f"{short} Village",
    ]
    for n in nearby_names:
        if n and n.lower() != name.lower():
            areas.append(n)
    return _uniq_names(areas)[:12]


def _cities_near(lat: float, lon: float, state: str, limit: int = 24) -> List[dict]:
    scored = []
    seen = set()
    for c in _US_CITIES:
        if state and c.get("state") != state:
            continue
        key = c["city"].lower()
        if key in seen:
            continue
        seen.add(key)
        scored.append((haversine(lat, lon, c["lat"], c["lon"]), c))
    scored.sort(key=lambda x: x[0])
    # Keep places roughly inside the county (~55 miles) before padding
    tight = [c for d, c in scored if d <= 55][:limit]
    if len(tight) >= min(8, limit):
        return tight[:limit]
    return [c for _, c in scored[:limit]]


def resolve_county_for_base(base_location: str) -> Optional[dict]:
    rec = _resolve_as_county(base_location)
    if rec:
        return rec
    city_rec = _geocode_from_dataset(base_location)
    if city_rec:
        return nearest_county(city_rec["lat"], city_rec["lon"], city_rec.get("state"))
    state_rec = _resolve_as_state(base_location)
    if state_rec:
        return nearest_county(state_rec["lat"], state_rec["lon"], state_rec["code"])
    return None


def build_place_catalog(base_location: str = "", county_name: str = "", city_name: str = "") -> dict:
    """County → incorporated cities → local areas → streets for the picker.

    San Diego County uses the curated JSON. Every other US county uses nearby
    cities as local areas and named streets so the layer switch always works.
    """
    loc = (county_name or base_location or "San Diego County, CA").strip()
    county = _resolve_as_county(loc) if "county" in loc.lower() else None
    if not county:
        county = resolve_county_for_base(loc)
    if not county:
        county = next((c for c in _US_COUNTIES if c["state"] == "CA" and "san diego" in c["name"].lower()), None)
    if not county:
        county = {"name": "San Diego County", "state": "CA", "lat": 33.02, "lon": -116.77}

    state = county.get("state") or "CA"
    peers = list_counties(state)
    city_filter = (city_name or "").strip()
    if city_filter.lower() in {"all cities", "all", ""}:
        city_filter = ""
    loc_l = loc.split(",")[0].strip().lower()
    if not city_filter and "county" not in loc_l and loc_l not in {"all cities", "unincorporated"}:
        city_filter = loc.split(",")[0].strip()

    sd = _san_diego_county_data() if "san diego" in (county.get("name") or "").lower() else None
    cities_out = []
    incorporated = []

    if sd and sd.get("cities"):
        incorporated = list(sd.get("incorporated_cities") or [c["name"] for c in sd["cities"]])
        for c in sd["cities"]:
            if city_filter and (c.get("name") or "").lower() != city_filter.lower():
                continue
            cities_out.append({
                "name": c.get("name"),
                "kind": "city",
                "local_areas": list(c.get("local_areas") or []),
                "streets": list(c.get("streets") or _fallback_streets(c.get("name") or "", county.get("name") or "")),
            })
        uninc = sd.get("unincorporated") or {}
        if not city_filter or city_filter.lower() in {"unincorporated"}:
            cities_out.append({
                "name": "Unincorporated",
                "kind": "unincorporated",
                "local_areas": list(uninc.get("local_areas") or []),
                "streets": list(uninc.get("streets") or _fallback_streets("Unincorporated", county.get("name") or "")),
            })
    else:
        nearby = _cities_near(county["lat"], county["lon"], state, 28)
        incorporated = [c["city"] for c in nearby]
        if city_filter and city_filter.lower() not in {x.lower() for x in incorporated}:
            city_filter = ""
        for c in nearby:
            if city_filter and c["city"].lower() != city_filter.lower():
                continue
            near_names = [x["city"] for x in _cities_near(c["lat"], c["lon"], state, 10) if x["city"] != c["city"]]
            cities_out.append({
                "name": c["city"],
                "kind": "city",
                "lat": c["lat"],
                "lon": c["lon"],
                "local_areas": _local_areas_for_city(c["city"], near_names, county.get("name") or ""),
                "streets": _fallback_streets(
                    c["city"],
                    county.get("name") or "",
                    extra_cities=incorporated,
                ),
            })

    return {
        "county": county.get("name"),
        "state": state,
        "incorporated_cities": incorporated,
        "cities": cities_out,
        "counties": [{"name": c["name"], "state": c["state"]} for c in peers],
        "selected_city": city_filter or "All cities",
    }


def _catalog_places_for_base(base_location: str, num: int) -> List[CityInfo]:
    """City → local areas → streets from the active county catalog."""
    data = build_place_catalog(base_location=base_location)
    state = data.get("state") or "CA"
    out: List[CityInfo] = []
    seen = set()

    def add(name: str, kind: str, zip_code: str = ""):
        key = (name.lower(), state.lower(), kind)
        if key in seen or not (name or "").strip():
            return
        seen.add(key)
        z = zip_code or (_static_sd_zip(name) if state == "CA" else "")
        out.append(_city_info(name.strip(), state, 0.0, 0.0, kind, zip=z))

    for c in data.get("cities") or []:
        add(c.get("name") or "", "city")
        if len(out) >= num:
            return out[:num]
        for area in c.get("local_areas") or []:
            add(area, "area")
            if len(out) >= num:
                return out[:num]
        parent = c.get("name") or ""
        for street in c.get("streets") or []:
            add(f"{street}, {parent}" if parent else street, "street")
            if len(out) >= num:
                return out[:num]
    return out[:num]


async def _pad_places_to_count(places: List[CityInfo], num: int, seed: str) -> List[CityInfo]:
    """Never return fewer places than the slider — fill from nearby, then numbered areas.

    If more places were already pinned (chips) than the slider, keep all of them
    up to 250 — do not slice extras down to the slider.
    """
    num = max(1, min(int(num or 1), 250))
    out = list(places or [])
    want = min(250, max(num, len(out)))
    seen = {
        (c.name.lower(), (c.state or "").lower(), getattr(c, "kind", "city"))
        for c in out
    }

    def add(info: CityInfo) -> bool:
        if not info or not (info.name or "").strip():
            return False
        key = (info.name.lower(), (info.state or "").lower(), getattr(info, "kind", "city"))
        if key in seen:
            return False
        seen.add(key)
        out.append(info)
        return True

    if len(out) < want:
        try:
            nearby = await get_nearby_cities(seed, max(want, 80))
        except LocationNotResolvedError:
            nearby = []
        for c in nearby:
            if getattr(c, "kind", "city") == "state":
                continue
            add(c)
            if len(out) >= want:
                return out[:want]
    if len(out) < want:
        for c in _catalog_places_for_base(seed, want * 4):
            add(c)
            if len(out) >= want:
                return out[:want]
    base = out[0] if out else city_from_label(seed)
    n = 2
    while base and len(out) < want:
        add(_city_info(
            f"{base.name} area {n}",
            base.state or "CA",
            getattr(base, "latitude", 0) or 0,
            getattr(base, "longitude", 0) or 0,
            "area",
            zip=getattr(base, "zip", "") or "",
        ))
        n += 1
        if n > want + 40:
            break
    return out[:want]


async def expand_places_from_base(base_location: str, num: int) -> List[CityInfo]:
    """Backend automation: cities + localities (+ streets when catalog allows)."""
    num = max(1, min(int(num or 1), 250))
    catalog = _catalog_places_for_base(base_location, num)
    if len(catalog) >= num:
        return catalog[:num]

    nearby = await get_nearby_cities(base_location, num)
    nearby = [c for c in nearby if getattr(c, "kind", "city") != "state"]

    if not catalog:
        return await _pad_places_to_count(nearby, num, base_location)

    # Merge catalog (areas/streets) with nearby cities
    out: List[CityInfo] = []
    seen = set()
    for info in list(catalog) + list(nearby):
        key = (info.name.lower(), (info.state or "").lower(), getattr(info, "kind", "city"))
        if key in seen:
            continue
        seen.add(key)
        out.append(info)
        if len(out) >= num:
            break
    return await _pad_places_to_count(out, num, base_location)


def merge_extra_locations(cities: List[CityInfo], extra_labels: Optional[List[str]]) -> List[CityInfo]:
    """Prepend manually added locations without duplicating nearby results."""
    out: List[CityInfo] = []
    seen = set()
    extras = flatten_extra_locations(extra_labels)
    for info in extras:
        key = (info.name.lower(), (info.state or "").lower(), getattr(info, "kind", "city"))
        if key in seen:
            continue
        seen.add(key)
        out.append(info)
    for city in cities or []:
        key = (city.name.lower(), (city.state or "").lower(), getattr(city, "kind", "city"))
        if key in seen:
            continue
        seen.add(key)
        out.append(city)
    return out


# Curated major metros per state — shown first when base location is a state.
_STATE_MAJOR_CITIES = {
    "AL": ["Birmingham", "Montgomery", "Huntsville", "Mobile", "Tuscaloosa"],
    "AK": ["Anchorage", "Fairbanks", "Juneau", "Sitka"],
    "AZ": ["Phoenix", "Tucson", "Mesa", "Scottsdale", "Chandler", "Flagstaff"],
    "AR": ["Little Rock", "Fayetteville", "Fort Smith", "Springdale"],
    "CA": ["Los Angeles", "San Diego", "San Francisco", "San Jose", "Sacramento",
           "Oakland", "Fresno", "Long Beach", "Anaheim", "Riverside", "Bakersfield",
           "Chula Vista", "Oceanside", "Escondido", "Carlsbad", "El Cajon", "Vista",
           "San Marcos", "Encinitas", "National City", "La Mesa", "Santee",
           "Poway", "Imperial Beach", "Lemon Grove", "Coronado", "Solana Beach"],
    "CO": ["Denver", "Colorado Springs", "Aurora", "Fort Collins", "Boulder"],
    "CT": ["Hartford", "New Haven", "Stamford", "Bridgeport", "Waterbury", "Norwalk"],
    "DE": ["Wilmington", "Dover", "Newark"],
    "DC": ["Washington"],
    "FL": ["Miami", "Orlando", "Tampa", "Jacksonville", "Tallahassee", "Fort Lauderdale"],
    "GA": ["Atlanta", "Savannah", "Augusta", "Columbus", "Macon"],
    "HI": ["Honolulu", "Hilo", "Kailua", "Pearl City", "Kahului"],
    "ID": ["Boise", "Meridian", "Nampa", "Idaho Falls"],
    "IL": ["Chicago", "Aurora", "Naperville", "Rockford", "Peoria", "Springfield", "Elgin"],
    "IN": ["Indianapolis", "Fort Wayne", "Evansville", "South Bend"],
    "IA": ["Des Moines", "Cedar Rapids", "Davenport", "Iowa City"],
    "KS": ["Wichita", "Overland Park", "Kansas City", "Topeka"],
    "KY": ["Louisville", "Lexington", "Bowling Green", "Covington"],
    "LA": ["New Orleans", "Baton Rouge", "Shreveport", "Lafayette"],
    "ME": ["Portland", "Lewiston", "Bangor", "Augusta"],
    "MD": ["Baltimore", "Annapolis", "Frederick", "Rockville"],
    "MA": ["Boston", "Worcester", "Cambridge", "Springfield"],
    "MI": ["Detroit", "Grand Rapids", "Ann Arbor", "Lansing"],
    "MN": ["Minneapolis", "Saint Paul", "Rochester", "Duluth"],
    "MS": ["Jackson", "Gulfport", "Biloxi", "Hattiesburg"],
    "MO": ["Kansas City", "Saint Louis", "Springfield", "Columbia"],
    "MT": ["Billings", "Missoula", "Great Falls", "Bozeman"],
    "NE": ["Omaha", "Lincoln", "Bellevue"],
    "NV": ["Las Vegas", "Henderson", "Reno", "North Las Vegas"],
    "NH": ["Manchester", "Nashua", "Concord"],
    "NJ": ["Newark", "Jersey City", "Paterson", "Trenton"],
    "NM": ["Albuquerque", "Santa Fe", "Las Cruces"],
    "NY": ["New York", "Buffalo", "Rochester", "Albany", "Syracuse"],
    "NC": ["Charlotte", "Raleigh", "Greensboro", "Durham", "Winston-Salem", "Asheville"],
    "ND": ["Fargo", "Bismarck", "Grand Forks"],
    "OH": ["Columbus", "Cleveland", "Cincinnati", "Toledo", "Akron"],
    "OK": ["Oklahoma City", "Tulsa", "Norman"],
    "OR": ["Portland", "Eugene", "Salem", "Bend"],
    "PA": ["Philadelphia", "Pittsburgh", "Allentown", "Harrisburg"],
    "RI": ["Providence", "Warwick", "Cranston"],
    "SC": ["Charleston", "Columbia", "Greenville", "Myrtle Beach"],
    "SD": ["Sioux Falls", "Rapid City", "Aberdeen"],
    "TN": ["Nashville", "Memphis", "Knoxville", "Chattanooga"],
    "TX": ["Houston", "Dallas", "Austin", "San Antonio", "Fort Worth", "El Paso"],
    "UT": ["Salt Lake City", "Provo", "Ogden", "West Valley City"],
    "VT": ["Burlington", "South Burlington", "Rutland", "Montpelier"],
    "VA": ["Virginia Beach", "Richmond", "Norfolk", "Arlington", "Alexandria"],
    "WA": ["Seattle", "Spokane", "Tacoma", "Bellevue", "Vancouver"],
    "WV": ["Charleston", "Huntington", "Morgantown"],
    "WI": ["Milwaukee", "Madison", "Green Bay", "Kenosha"],
    "WY": ["Cheyenne", "Casper", "Laramie"],
}


def _major_cities_in_state(state_code: str, limit: int) -> List[CityInfo]:
    """Return curated major metros for a state, then fill from the cities dataset."""
    by_name = {}
    for c in _US_CITIES:
        if c["state"] != state_code:
            continue
        key = c["city"].lower()
        by_name.setdefault(key, c)

    result: List[CityInfo] = []
    seen = set()
    for name in _STATE_MAJOR_CITIES.get(state_code, []):
        rec = by_name.get(name.lower())
        if not rec:
            continue
        key = rec["city"].lower()
        if key in seen:
            continue
        seen.add(key)
        result.append(_city_info(rec["city"], rec["state"], rec["lat"], rec["lon"], "city"))
        if len(result) >= limit:
            return result

    meta = _US_STATES.get(state_code) or {}
    lat, lon = meta.get("lat", 0), meta.get("lon", 0)
    scored = sorted(
        (c for c in _US_CITIES if c["state"] == state_code),
        key=lambda c: haversine(lat, lon, c["lat"], c["lon"]),
    )
    for c in scored:
        key = c["city"].lower()
        if key in seen:
            continue
        seen.add(key)
        result.append(_city_info(c["city"], c["state"], c["lat"], c["lon"], "city"))
        if len(result) >= limit:
            break
    return result


def _counties_in_state(state_code: str, limit: int) -> List[CityInfo]:
    rows = [c for c in _US_COUNTIES if c["state"] == state_code]
    return [
        _city_info(c["name"], c["state"], c["lat"], c["lon"], "county")
        for c in rows[:limit]
    ]


def _nearby_counties(lat: float, lon: float, limit: int, state: Optional[str] = None) -> List[CityInfo]:
    scored = []
    for c in _US_COUNTIES:
        if state and c["state"] != state:
            continue
        dist = haversine(lat, lon, c["lat"], c["lon"])
        scored.append((dist, c))
    scored.sort(key=lambda x: x[0])
    return [
        _city_info(c["name"], c["state"], c["lat"], c["lon"], "county")
        for _, c in scored[:limit]
    ]


def _nearby_cities(lat: float, lon: float, limit: int, state: Optional[str] = None) -> List[CityInfo]:
    scored = []
    seen = set()
    for c in _US_CITIES:
        if state and c["state"] != state:
            continue
        key = (c["city"].lower(), c["state"])
        if key in seen:
            continue
        seen.add(key)
        dist = haversine(lat, lon, c["lat"], c["lon"])
        scored.append((dist, c))
    scored.sort(key=lambda x: x[0])
    return [
        _city_info(c["city"], c["state"], c["lat"], c["lon"], "city")
        for _, c in scored[:limit]
    ]


async def get_nearby_cities(base_location: str, num_cities: int = 10) -> List[CityInfo]:
    """
    Return locations for expansion around the base.

    For a **state** base (e.g. "Illinois, IL"): returns the state first, then
    counties in that state, then major cities — so the UI can show the state
    itself (not only child cities).

    For a **county** base: returns the county first, then nearby cities.

    For a **city** base: returns nearest cities (and a few nearby counties).
    """
    num_cities = max(1, min(int(num_cities or 10), 250))

    # ── 1) State-level query ──────────────────────────────────────
    state_rec = _resolve_as_state(base_location)
    if state_rec:
        code = state_rec["code"]
        result: List[CityInfo] = [
            _city_info(
                state_rec["name"],
                code,
                state_rec["lat"],
                state_rec["lon"],
                "state",
            )
        ]
        # Mix counties + cities so Location Expansion matches product expectation
        counties = _counties_in_state(code, max(3, num_cities // 3))
        cities = _major_cities_in_state(code, num_cities)
        # Interleave: prefer cities list size, inject counties after top cities
        top_cities = cities[: max(5, num_cities - len(counties) - 1)]
        remaining_slots = num_cities - len(result)
        mixed: List[CityInfo] = []
        # Put primary metro cities first, then counties, then more cities
        mixed.extend(top_cities[:5])
        mixed.extend(counties)
        mixed.extend(top_cities[5:])
        mixed.extend(cities[len(top_cities):])
        seen = {(result[0].name.lower(), result[0].state)}
        for item in mixed:
            key = (item.name.lower(), item.state)
            if key in seen:
                continue
            seen.add(key)
            result.append(item)
            if len(result) >= remaining_slots + 1:
                break
        return result[:num_cities]

    # ── 2) County-level query ─────────────────────────────────────
    county_rec = _resolve_as_county(base_location)
    if county_rec:
        result = [
            _city_info(
                county_rec["name"],
                county_rec["state"],
                county_rec["lat"],
                county_rec["lon"],
                "county",
            )
        ]
        cities = _nearby_cities(
            county_rec["lat"], county_rec["lon"],
            num_cities - 1, state=county_rec["state"],
        )
        result.extend(cities)
        return result[:num_cities]

    # ── 3) City-level (dataset / OpenCage) ────────────────────────
    base_city_rec = _geocode_from_dataset(base_location)
    if base_city_rec:
        base_lat, base_lon = base_city_rec["lat"], base_city_rec["lon"]
        base_state = base_city_rec["state"]
    else:
        latlon = await _geocode_opencage(base_location)
        if latlon:
            base_lat, base_lon = latlon
            _, base_state = _parse_location(base_location)
        elif _US_CITIES:
            raise LocationNotResolvedError(
                f"Could not find \"{base_location}\". Try a city (\"Chicago, IL\"), "
                "a state (\"Illinois, IL\"), or a county (\"Cook County, IL\")."
            )
        else:
            base_lat, base_lon = _DEFAULT_LATLON
            base_state = None

    if not _US_CITIES:
        city, state = _parse_location(base_location)
        return [_city_info(city.title(), state or "", base_lat, base_lon, "city")]

    # Cities + a few nearby counties for local SEO expansion
    city_slots = max(1, num_cities - min(4, num_cities // 4))
    county_slots = num_cities - city_slots
    cities = _nearby_cities(base_lat, base_lon, city_slots)
    counties = _nearby_counties(base_lat, base_lon, county_slots, state=base_state) if county_slots else []

    # Put base city first if we resolved it from dataset
    result = []
    seen = set()
    if base_city_rec:
        base_item = _city_info(
            base_city_rec["city"], base_city_rec["state"],
            base_city_rec["lat"], base_city_rec["lon"], "city",
        )
        result.append(base_item)
        seen.add((base_item.name.lower(), base_item.state))

    for item in cities + counties:
        key = (item.name.lower(), item.state)
        if key in seen:
            continue
        seen.add(key)
        result.append(item)
        if len(result) >= num_cities:
            break
    return result[:num_cities]
