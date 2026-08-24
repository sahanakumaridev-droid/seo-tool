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


def _city_info(name: str, state: str, lat: float, lon: float, kind: str = "city") -> CityInfo:
    return CityInfo(
        name=name, state=state, country="USA",
        latitude=lat, longitude=lon, kind=kind,
    )


_STATE_ABBR = re.compile(r"^[A-Za-z]{2}$")


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
            if i + 1 < len(tokens) and _STATE_ABBR.fullmatch(tokens[i + 1]):
                out.append(f"{name}, {tokens[i + 1].upper()}")
                i += 2
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
    """Parse a typed or dropdown location like 'Coronado, CA' into CityInfo."""
    raw = (text or "").strip()
    if not raw:
        return None
    if "," in raw:
        name, rest = [p.strip() for p in raw.split(",", 1)]
        # Only treat the remainder as a state if it is a 2-letter code.
        # Otherwise this was a bulk list stuffed into one field.
        if _STATE_ABBR.fullmatch(rest):
            state = rest.upper()
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
    return _city_info(name, state or "", 0.0, 0.0, "city")


def flatten_extra_locations(extra_labels: Optional[List[str]], default_state: str = "") -> List[CityInfo]:
    """Expand chips / pasted lists into one CityInfo per place."""
    out: List[CityInfo] = []
    seen = set()
    for label in extra_labels or []:
        for part in split_location_labels(label):
            info = city_from_label(part, default_state=default_state)
            if not info:
                continue
            key = (info.name.lower(), (info.state or "").lower())
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
    """Build the page list: chips first, then nearby fill up to num_cities.

    - Chips alone under the drag count → fill with nearby cities so Generate 50
      still yields ~50 pages when the user only pinned a few communities.
    - Chips alone at/above the drag count → chips are the full list.
    - No chips → nearby expansion from the base city.
    """
    default_state = ""
    if base_location and "," in base_location:
        maybe = base_location.split(",")[-1].strip()
        if _STATE_ABBR.fullmatch(maybe):
            default_state = maybe.upper()
    extras = flatten_extra_locations(extra_labels, default_state=default_state)
    num = max(1, min(int(num_cities or 1), 100))
    loc = (base_location or "").strip()

    if extras and len(extras) >= num:
        return extras[:num]

    nearby: List[CityInfo] = []
    if loc:
        nearby = await get_nearby_cities(loc, num)
        nearby = [c for c in nearby if getattr(c, "kind", "city") != "state"]
    elif extras:
        # No base city — expand from the first chip
        seed = f"{extras[0].name}, {extras[0].state}".strip(", ")
        if seed.strip(", "):
            nearby = await get_nearby_cities(seed, num)
            nearby = [c for c in nearby if getattr(c, "kind", "city") != "state"]

    if extras:
        return merge_extra_locations(nearby, extra_labels)[:num]
    return nearby[:num]


def merge_extra_locations(cities: List[CityInfo], extra_labels: Optional[List[str]]) -> List[CityInfo]:
    """Prepend manually added locations without duplicating nearby results."""
    out: List[CityInfo] = []
    seen = set()
    extras = flatten_extra_locations(extra_labels)
    for info in extras:
        key = (info.name.lower(), (info.state or "").lower())
        if key in seen:
            continue
        seen.add(key)
        out.append(info)
    for city in cities or []:
        key = (city.name.lower(), (city.state or "").lower())
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
    num_cities = max(1, min(int(num_cities or 10), 100))

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
