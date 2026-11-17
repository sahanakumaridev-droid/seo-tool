"""
Build a B2B prospect list from public business listings.

Google business fields (name, address, phone, website, category, rating,
review count, Maps URL) come from the official Places API. A publicly
listed email and social profile links are read from the business's own
website when that site allows it. Rows are campaign-ready only when both
a public email and a phone number are present.
"""
import asyncio
import ipaddress
import json
import re
import socket
from typing import Dict, List, Optional
from urllib.parse import quote, urljoin, urlparse
from urllib.robotparser import RobotFileParser

import httpx

from config import settings

_PLACES_SEARCH = "https://places.googleapis.com/v1/places:searchText"
_FIELD_MASK = (
    "places.id,places.displayName,places.formattedAddress,places.addressComponents,"
    "places.websiteUri,places.internationalPhoneNumber,places.nationalPhoneNumber,"
    "places.primaryTypeDisplayName,places.rating,places.userRatingCount,places.googleMapsUri"
)
_UA = "ZeOrbitProspectBot/1.0 (public business contact lookup; +https://zeorbit.com)"
_EMAIL_RE = re.compile(r"[A-Z0-9._%+\-]+@[A-Z0-9.\-]+\.[A-Z]{2,}", re.I)
_HREF_RE = re.compile(r"""href=["']([^"'#]+)["']""", re.I)
_ZIP_RE = re.compile(r"\b(\d{5})(?:-\d{4})?\b")
_STATE_ZIP_RE = re.compile(r",\s*([A-Z]{2})\s+(\d{5})(?:-\d{4})?\b")
_SKIP_EMAIL_HOSTS = (
    "example.com", "example.org", "sentry.io", "wixpress.com", "godaddy.com",
    "schema.org", "googleapis.com", "gstatic.com", "cloudflare.com",
    "wordpress.com", "squarespace.com", "email.com", "domain.com",
)
_SKIP_LOCAL = ("noreply", "no-reply", "donotreply", "privacy", "abuse", "postmaster", "webmaster")
_PREFERRED_LOCAL = ("info", "contact", "hello", "office", "sales", "admin", "support", "inquir", "team")
_SOCIAL_HOSTS = {
    "facebook.com": "facebook",
    "instagram.com": "instagram",
    "linkedin.com": "linkedin",
    "twitter.com": "twitter",
    "x.com": "x",
    "youtube.com": "youtube",
    "tiktok.com": "tiktok",
}
_SHARE_HINTS = ("sharer", "share?", "intent/tweet", "shareArticle", "/share")


def split_address(formatted: str, components: Optional[list]) -> Dict[str, str]:
    city = state = zip_code = ""
    for part in components or []:
        types = part.get("types") or []
        if "locality" in types and not city:
            city = part.get("longText") or part.get("shortText") or ""
        elif "postal_town" in types and not city:
            city = part.get("longText") or ""
        elif "administrative_area_level_1" in types and not state:
            state = part.get("shortText") or part.get("longText") or ""
        elif "postal_code" in types and not zip_code:
            zip_code = part.get("longText") or part.get("shortText") or ""
    if not zip_code:
        found = _ZIP_RE.search(formatted or "")
        if found:
            zip_code = found.group(1)
    if not state:
        found = _STATE_ZIP_RE.search(formatted or "")
        if found:
            state = found.group(1)
            zip_code = zip_code or found.group(2)
    if not city and formatted:
        bits = [b.strip() for b in formatted.split(",")]
        if len(bits) >= 2:
            city = bits[-2]
    return {"city": city, "state": state, "zip_code": zip_code}


def _host(url: str) -> str:
    host = (urlparse(url).hostname or "").lower()
    return host[4:] if host.startswith("www.") else host


def _public_http_url(url: str) -> bool:
    parsed = urlparse(url or "")
    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        return False
    host = parsed.hostname.lower()
    if host in {"localhost", "127.0.0.1", "0.0.0.0"} or host.endswith(".local"):
        return False
    try:
        literal = ipaddress.ip_address(host)
    except ValueError:
        literal = None
    if literal is not None:
        return not (literal.is_private or literal.is_loopback or literal.is_link_local or literal.is_reserved)
    try:
        infos = socket.getaddrinfo(host, None)
    except socket.gaierror:
        return False
    for info in infos:
        try:
            ip = ipaddress.ip_address(info[4][0])
        except ValueError:
            return False
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved:
            return False
    return True


def pick_email(html: str, website: str) -> str:
    found = []
    for match in _EMAIL_RE.findall(html or ""):
        email = match.strip(".").lower()
        local, _, host = email.partition("@")
        if not host or any(local.startswith(skip) for skip in _SKIP_LOCAL):
            continue
        if any(host == blocked or host.endswith("." + blocked) for blocked in _SKIP_EMAIL_HOSTS):
            continue
        if host.endswith((".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg")):
            continue
        found.append(email)
    if not found:
        return ""
    site_host = _host(website)
    on_site = [email for email in found if site_host and email.endswith("@" + site_host)]
    pool = on_site or []
    if not pool:
        return ""

    def rank(email: str) -> tuple:
        local = email.split("@", 1)[0]
        preferred = 0 if any(local.startswith(p) for p in _PREFERRED_LOCAL) else 1
        return (preferred, len(local), email)

    unique = list(dict.fromkeys(pool))
    unique.sort(key=rank)
    return unique[0]


def pick_socials(html: str, page_url: str) -> Dict[str, str]:
    found: Dict[str, str] = {}
    for href in _HREF_RE.findall(html or ""):
        absolute = urljoin(page_url, href.strip())
        lowered = absolute.lower()
        if any(hint in lowered for hint in _SHARE_HINTS):
            continue
        host = _host(absolute)
        for domain, label in _SOCIAL_HOSTS.items():
            if label in found:
                continue
            if host == domain or host.endswith("." + domain):
                found[label] = absolute.split("?")[0][:300]
    return found


def _contact_links(html: str, page_url: str) -> List[str]:
    links = []
    page_host = _host(page_url)
    for href in _HREF_RE.findall(html or ""):
        absolute = urljoin(page_url, href.strip())
        if _host(absolute) != page_host:
            continue
        path = urlparse(absolute).path.lower()
        if any(token in path for token in ("/contact", "/about", "/reach")):
            links.append(absolute.split("#")[0])
    return list(dict.fromkeys(links))[:1]


async def _allowed(client: httpx.AsyncClient, url: str, cache: Dict[str, RobotFileParser]) -> bool:
    parsed = urlparse(url)
    origin = f"{parsed.scheme}://{parsed.netloc}"
    parser = cache.get(origin)
    if parser is None:
        parser = RobotFileParser()
        cache[origin] = parser
        try:
            resp = await client.get(f"{origin}/robots.txt", timeout=6)
            if resp.status_code < 400:
                parser.parse(resp.text.splitlines())
            else:
                parser.parse([])
        except Exception:
            parser.parse([])
    try:
        return parser.can_fetch(_UA, url)
    except Exception:
        return True


async def _fetch_html(client: httpx.AsyncClient, url: str, cache: Dict[str, RobotFileParser]) -> str:
    if not _public_http_url(url):
        return ""
    if not await _allowed(client, url, cache):
        return ""
    try:
        resp = await client.get(
            url,
            timeout=8,
            follow_redirects=True,
            headers={"User-Agent": _UA, "Accept": "text/html"},
        )
    except Exception:
        return ""
    if resp.status_code >= 400:
        return ""
    ctype = (resp.headers.get("content-type") or "").lower()
    if "html" not in ctype and "text" not in ctype:
        return ""
    final = str(resp.url)
    if not _public_http_url(final):
        return ""
    return resp.text[:400_000]


async def enrich_website(client: httpx.AsyncClient, website: str, cache: Dict[str, RobotFileParser]) -> Dict[str, object]:
    if not website or not _public_http_url(website):
        return {"email": "", "socials": {}}
    home = await _fetch_html(client, website, cache)
    if not home:
        return {"email": "", "socials": {}}
    email = pick_email(home, website)
    socials = pick_socials(home, website)
    if not email:
        for link in _contact_links(home, website):
            page = await _fetch_html(client, link, cache)
            if not page:
                continue
            email = pick_email(page, website)
            for label, href in pick_socials(page, link).items():
                socials.setdefault(label, href)
            if email:
                break
    return {"email": email, "socials": socials}


def _place_to_row(place: dict, industry: str, query: str) -> dict:
    name = (place.get("displayName") or {}).get("text", "") or ""
    address = place.get("formattedAddress") or ""
    parts = split_address(address, place.get("addressComponents"))
    phone = place.get("nationalPhoneNumber") or place.get("internationalPhoneNumber") or ""
    website = place.get("websiteUri") or ""
    place_id = place.get("id") or ""
    maps_url = place.get("googleMapsUri") or ""
    if not maps_url and place_id:
        maps_url = f"https://www.google.com/maps/search/?api=1&query={name}&query_place_id={place_id}"
    category = (place.get("primaryTypeDisplayName") or {}).get("text") or industry
    rating = place.get("rating")
    reviews = place.get("userRatingCount")
    return {
        "place_id": place_id,
        "business_name": name,
        "website": website,
        "category": category,
        "address": address,
        "city": parts["city"],
        "state": parts["state"],
        "zip_code": parts["zip_code"],
        "phone": phone,
        "email": "",
        "maps_url": maps_url,
        "rating": float(rating) if isinstance(rating, (int, float)) else None,
        "review_count": int(reviews) if isinstance(reviews, int) else None,
        "socials": {},
        "query": query,
    }


async def _google_rows(client: httpx.AsyncClient, industry: str, location: str, query: str, page_size: int) -> List[dict]:
    resp = await client.post(
        _PLACES_SEARCH,
        json={"textQuery": query, "pageSize": page_size},
        headers={
            "Content-Type": "application/json",
            "X-Goog-Api-Key": settings.GOOGLE_PLACES_API_KEY,
            "X-Goog-FieldMask": _FIELD_MASK,
        },
    )
    if resp.status_code != 200:
        detail = resp.text[:180].replace("\n", " ")
        raise RuntimeError(f"Google Places returned {resp.status_code}. {detail}")
    places = (resp.json() or {}).get("places") or []
    return [_place_to_row(place, industry, query) for place in places[:page_size]]


def _nominatim_row(item: dict, industry: str, location: str, query: str) -> Optional[dict]:
    extra = item.get("extratags") or {}
    addr = item.get("address") or {}
    name = (item.get("name") or "").strip()
    if not name:
        return None
    phone = extra.get("phone") or extra.get("contact:phone") or ""
    website = extra.get("website") or extra.get("contact:website") or extra.get("url") or ""
    if website and not str(website).startswith(("http://", "https://")):
        website = "https://" + str(website)
    email = (extra.get("email") or extra.get("contact:email") or "").strip().lower()
    city = addr.get("city") or addr.get("town") or addr.get("village") or location.split(",")[0].strip()
    state = addr.get("state") or ""
    zip_code = addr.get("postcode") or ""
    line = " ".join(part for part in (addr.get("house_number"), addr.get("road")) if part).strip()
    region = " ".join(part for part in (state, zip_code) if part).strip()
    address = ", ".join(part for part in (line, city, region) if part) or (item.get("display_name") or "")
    category = str(item.get("type") or industry).replace("_", " ")
    place_id = f"osm:{item.get('osm_type') or 'node'}:{item.get('osm_id')}"
    maps_query = quote(f"{name}, {address}" if address else name)
    return {
        "place_id": place_id,
        "business_name": name,
        "website": website,
        "category": category,
        "address": address[:300],
        "city": city,
        "state": state,
        "zip_code": zip_code,
        "phone": phone,
        "email": email,
        "maps_url": f"https://www.google.com/maps/search/?api=1&query={maps_query}",
        "rating": None,
        "review_count": None,
        "socials": {},
        "query": query,
    }


async def _osm_rows(client: httpx.AsyncClient, industry: str, location: str, query: str, page_size: int) -> List[dict]:
    headers = {"User-Agent": _UA, "Accept": "application/json"}
    geo = await client.get(
        "https://nominatim.openstreetmap.org/search",
        params={"q": location, "format": "jsonv2", "limit": 1},
        headers=headers,
        timeout=20,
    )
    if geo.status_code != 200 or not geo.json():
        raise RuntimeError(f"Could not find {location} on the free map.")
    south, north, west, east = geo.json()[0]["boundingbox"]
    await asyncio.sleep(1.1)
    found = await client.get(
        "https://nominatim.openstreetmap.org/search",
        params={
            "q": industry,
            "format": "jsonv2",
            "addressdetails": 1,
            "extratags": 1,
            "limit": min(40, max(page_size * 5, page_size)),
            "viewbox": f"{west},{north},{east},{south}",
            "bounded": 1,
        },
        headers=headers,
        timeout=20,
    )
    if found.status_code != 200:
        raise RuntimeError("The free map search is busy. Wait a minute and try again.")
    rows = []
    seen = set()
    for item in found.json() or []:
        row = _nominatim_row(item, industry, location, query)
        if not row:
            continue
        key = row["business_name"].lower()
        if key in seen:
            continue
        seen.add(key)
        rows.append(row)
    rows.sort(key=lambda row: (0 if row["phone"] and row["website"] else 1 if row["phone"] else 2, row["business_name"].lower()))
    rows = rows[:page_size]
    if not rows:
        raise RuntimeError(f"No public {industry} listings were found around {location}.")
    return rows


async def search_prospects(industry: str, location: str, limit: int = 10) -> List[dict]:
    query = f"{industry.strip()} in {location.strip()}".strip()
    page_size = max(1, min(int(limit or 10), 20))
    use_google = bool((settings.GOOGLE_PLACES_API_KEY or "").strip())
    async with httpx.AsyncClient(timeout=45) as client:
        if use_google:
            rows = await _google_rows(client, industry.strip(), location.strip(), query, page_size)
        else:
            rows = await _osm_rows(client, industry.strip(), location.strip(), query, page_size)
        cache: Dict[str, RobotFileParser] = {}
        sem = asyncio.Semaphore(4)

        async def _enrich(row: dict) -> dict:
            listed_email = (row.get("email") or "").strip()
            async with sem:
                extra = await enrich_website(client, row.get("website") or "", cache)
            row["email"] = extra["email"] or listed_email
            row["socials"] = extra["socials"]
            row["ready"] = bool(row["email"] and row["phone"])
            return row

        return list(await asyncio.gather(*[_enrich(row) for row in rows]))


def socials_json(value) -> str:
    if isinstance(value, str):
        return value[:2000]
    try:
        return json.dumps(value or {})[:2000]
    except TypeError:
        return "{}"
