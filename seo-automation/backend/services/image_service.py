"""
image_service.py
Fetches relevant images from Unsplash/Pexels (free) or generates via DALL-E 3.
Converts to WebP, generates full SEO metadata (filename, alt, title, caption,
description), and uploads to the WordPress media library.
"""
import base64
import hashlib
import io
import re
import httpx
from typing import Optional, Tuple, List, Set, Iterable
from config import settings
from models.schemas import ImageAsset


def normalize_image_key(url: str) -> str:
    """Canonical key so ?w=1200, /full vs /regular, and Unsplash variants compare equal."""
    if not url:
        return ""
    base = url.split("?")[0].strip().rstrip("/")
    # Unsplash photo id is stable across size/quality URL variants
    m = re.search(r"(photo-[a-zA-Z0-9_-]+)", base)
    if m:
        return m.group(1).lower()
    # Pexels: .../photos/12345/... → photos/12345
    m = re.search(r"/photos/(\d+)", base)
    if m:
        return f"pexels-{m.group(1)}"
    return base.lower()




def topic_image_family(text: str) -> str:
    """Bucket niches so uniqueness is enforced per family (web vs plumbing, etc.)."""
    t = (text or "").lower()
    if any(k in t for k in ("plumb",)):
        return "plumbing"
    if any(k in t for k in ("hvac", "heating", "air condition")):
        return "hvac"
    if any(k in t for k in ("electric",)):
        return "electrician"
    if any(k in t for k in ("financ", "bank", "fintech", "invest", "account")):
        return "finance"
    if any(k in t for k in ("market", "seo", "advertis", "agency")) and not any(
        k in t for k in ("web", "website", "wordpress", "designer")
    ):
        return "marketing"
    # Software/SaaS separate from web-design so large location batches don't collide
    if any(k in t for k in ("software", "saas", "coding", "engineer", "sotware")) and not any(
        k in t for k in ("web design", "website", "wordpress", "web designer")
    ):
        return "software"
    if any(k in t for k in ("web", "website", "wordpress", "designer", "developer")):
        return "web"
    if any(k in t for k in ("dental", "dentist")):
        return "dental"
    if any(k in t for k in ("real estate", "realtor")):
        return "real_estate"
    if any(k in t for k in ("law", "legal", "attorney")):
        return "legal"
    if any(k in t for k in ("restaurant", "chef", "cafe")):
        return "restaurant"
    if any(k in t for k in ("clean",)):
        return "cleaning"
    if any(k in t for k in ("roof",)):
        return "roofing"
    if any(k in t for k in ("landscap", "lawn")):
        return "landscaping"
    if any(k in t for k in ("fitness", "gym", "trainer")):
        return "fitness"
    if any(k in t for k in ("photo",)):
        return "photography"
    if any(k in t for k in ("educat", "school", "learn", "tutor", "university", "college", "student")):
        return "education"
    return "general"

def _stable_index(seed: str, modulo: int) -> int:
    if modulo <= 0:
        return 0
    digest = hashlib.md5((seed or "seo").encode("utf-8")).hexdigest()
    return int(digest[:8], 16) % modulo


async def fetch_unsplash_image(query: str) -> Optional[Tuple[bytes, str]]:
    """Fetch a relevant image from Unsplash. Returns (image_bytes, filename)."""
    if not settings.UNSPLASH_ACCESS_KEY:
        return None
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(
                "https://api.unsplash.com/photos/random",
                params={"query": query, "orientation": "landscape", "w": 1280, "h": 720},
                headers={"Authorization": f"Client-ID {settings.UNSPLASH_ACCESS_KEY}"},
            )
            if resp.status_code != 200:
                return None
            data = resp.json()
            img_url = data["urls"]["regular"]
            img_resp = await client.get(img_url)
            if img_resp.status_code == 200:
                filename = f"{query.replace(' ', '-')[:40]}.jpg"
                return img_resp.content, filename
    except Exception as e:
        print(f"[Image] Unsplash error: {e}")
    return None


async def fetch_pexels_image(query: str) -> Optional[Tuple[bytes, str]]:
    """Fetch a relevant image from Pexels. Returns (image_bytes, filename)."""
    if not settings.PEXELS_API_KEY:
        return None
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(
                "https://api.pexels.com/v1/search",
                params={"query": query, "per_page": 1, "orientation": "landscape"},
                headers={"Authorization": settings.PEXELS_API_KEY},
            )
            if resp.status_code != 200:
                return None
            data = resp.json()
            photos = data.get("photos", [])
            if not photos:
                return None
            img_url = photos[0]["src"]["large2x"]
            img_resp = await client.get(img_url)
            if img_resp.status_code == 200:
                filename = f"{query.replace(' ', '-')[:40]}.jpg"
                return img_resp.content, filename
    except Exception as e:
        print(f"[Image] Pexels error: {e}")
    return None


async def generate_dalle_image(prompt: str) -> Optional[Tuple[bytes, str]]:
    """Generate an image using DALL-E 3. Returns (image_bytes, filename)."""
    if not settings.OPENAI_API_KEY:
        return None
    try:
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        response = await client.images.generate(
            model="dall-e-3",
            prompt=f"Professional business photo for: {prompt}. Clean, modern, no text overlays.",
            size="1792x1024",
            quality="standard",
            n=1,
            response_format="b64_json",
        )
        img_data = base64.b64decode(response.data[0].b64_json)
        filename = f"ai-{prompt.replace(' ', '-')[:30]}.png"
        return img_data, filename
    except Exception as e:
        print(f"[Image] DALL-E error: {e}")
    return None


async def get_image_for_content(business_type: str, city: str) -> Optional[Tuple[bytes, str]]:
    """Try Unsplash → Pexels → DALL-E in order."""
    query = f"{business_type} {city} professional"

    result = await fetch_unsplash_image(query)
    if result:
        return result

    result = await fetch_pexels_image(query)
    if result:
        return result

    result = await generate_dalle_image(f"{business_type} services in {city}")
    return result


# ══════════════════════════════════════════════════════════════════
#  WebP conversion + SEO metadata + multi-image generation
# ══════════════════════════════════════════════════════════════════

def _slug(text: str, max_len: int = 60) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", (text or "").lower()).strip("-")
    return s[:max_len].strip("-")


def convert_to_webp(image_bytes: bytes, quality: int = 82) -> Optional[bytes]:
    """Convert arbitrary image bytes to WebP. Returns None on failure (caller falls back to original)."""
    try:
        from PIL import Image
        img = Image.open(io.BytesIO(image_bytes))
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        out = io.BytesIO()
        img.save(out, format="WEBP", quality=quality, method=4)
        return out.getvalue()
    except Exception as e:
        print(f"[Image] WebP conversion failed: {e}")
        return None


async def fetch_image_bytes(url: str) -> Optional[bytes]:
    """Download image bytes from a hosted URL."""
    if not url or url.startswith("data:"):
        return None
    try:
        async with httpx.AsyncClient(timeout=25) as client:
            resp = await client.get(url, follow_redirects=True)
            if resp.status_code == 200:
                return resp.content
    except Exception as e:
        print(f"[Image] fetch bytes error: {e}")
    return None


def build_image_metadata(
    focus_keyword: str,
    location: str,
    business_name: str,
    idx: int,
    is_featured: bool,
) -> dict:
    """Generate SEO-friendly filename + alt/title/caption/description for an image."""
    kw = focus_keyword.strip() or "business"
    loc = location.strip()
    biz = business_name.strip()
    filename = f"{_slug(kw)}-{_slug(loc) or 'local'}-{idx + 1}.webp"
    where = f" in {loc}" if loc else ""
    by = f" by {biz}" if biz else ""

    if is_featured:
        alt = f"{kw.title()}{where}{by}"
        title = f"{kw.title()}{where}"
        caption = f"Professional {kw.lower()}{where}."
    else:
        alt = f"{kw.title()} services{where} — detail {idx + 1}"
        title = f"{kw.title()} — {loc or 'Overview'}"
        caption = f"{kw.title()}{where}{by}."
    description = f"Image illustrating {kw.lower()}{where}{by}. Optimized for SEO and web performance (WebP)."
    return {
        "filename": filename,
        "alt_text": alt,
        "title": title,
        "caption": caption,
        "description": description,
    }


# High-coverage, near-guaranteed-to-return-real-results search terms for the
# common local-service business categories this tool targets. Matched by
# substring against the article's own query so a niche/specific phrase that
# returns zero results on Openverse still resolves to a genuinely on-topic
# photo instead of a random unrelated Flickr hit.
_CATEGORY_FALLBACK_QUERIES = [
    (("web design", "website", "web developer", "web development"), "web designer laptop ui mockup"),
    (("plumb",), "plumber repairing pipe"),
    (("hvac", "heating", "air condition"), "hvac technician repair"),
    (("roof",), "roofer working on roof"),
    (("electric",), "electrician at work"),
    (("law", "attorney", "legal"), "lawyer in office"),
    (("dental", "dentist"), "dentist with patient"),
    (("real estate", "realtor"), "real estate agent house"),
    (("restaurant", "cafe", "food"), "restaurant chef kitchen"),
    (("salon", "hair", "beauty", "spa"), "hair salon stylist"),
    (("auto", "car repair", "mechanic"), "mechanic repairing car"),
    (("account", "bookkeep", "tax"), "accountant office desk"),
    (("financ", "bank", "fintech", "invest", "wealth"), "finance banking investment desk"),
    (("gym", "fitness", "personal train"), "gym fitness training"),
    (("clean",), "professional cleaning service"),
    (("landscap", "lawn"), "landscaper gardening"),
    (("market", "advertis", "seo", "digital"), "marketing team meeting"),
    (("photograph",), "photographer with camera"),
    (("insurance",), "insurance agent meeting client"),
    (("moving", "mover"), "movers loading truck"),
    (("pest",), "pest control technician"),
    (("paint",), "painter painting wall"),
    (("floor", "carpet"), "flooring installation"),
    (("pet", "vet", "animal"), "veterinarian with pet"),
    (("medical", "clinic", "health", "doctor"), "doctor with patient"),
    (("software", "app development", "custom software", "coding"), "software developer coding"),
    (("construction", "contractor", "remodel", "renovation"), "construction contractor at work"),
]

# Topic-STRICT curated Unsplash photos only (no generic offices/meetings/abstract art).
# Relevance > uniqueness — every URL must clearly match the niche.
_WEB_DESIGN_IMAGES = [
    "https://images.unsplash.com/photo-1467232004584-a241de8bcf5d",
    "https://images.unsplash.com/photo-1559028012-481c04fa702d",
    "https://images.unsplash.com/photo-1581291518633-83b4ebd1d83e",
    "https://images.unsplash.com/photo-1507238691740-187a5b1d37b8",
    "https://images.unsplash.com/photo-1547658719-da2b51169166",
    "https://images.unsplash.com/photo-1522542550221-31fd19575a2d",
    "https://images.unsplash.com/photo-1561070791-2526d30994b5",
    "https://images.unsplash.com/photo-1561070791-0369aee323b7",
    "https://images.unsplash.com/photo-1586717791821-3f8f48fcfba0",
    "https://images.unsplash.com/photo-1559027615-cd4628902d4a",
    "https://images.unsplash.com/photo-1558655146-9f40138edfeb",
    "https://images.unsplash.com/photo-1481487196290-c152efe700ba",
    "https://images.unsplash.com/photo-1512941937669-90a1b58e7e9c",
    "https://images.unsplash.com/photo-1551650975-87deedd944c3",
    "https://images.unsplash.com/photo-1498050108023-c5249f4df085",
    "https://images.unsplash.com/photo-1517694712202-14dd9538aa97",
    "https://images.unsplash.com/photo-1461749280684-dccba630e2f6",
    "https://images.unsplash.com/photo-1486312338219-ce68d2c6f44d",
    "https://images.unsplash.com/photo-1488590528505-98d2b5aba04b",
    "https://images.unsplash.com/photo-1555066931-4365d14bab8c",
    "https://images.unsplash.com/photo-1587620962725-abab7fe55159",
    "https://images.unsplash.com/photo-1531297484001-80022131f5a1",
    "https://images.unsplash.com/photo-1542831371-29b0f74f9713",
    "https://images.unsplash.com/photo-1555949963-aa79dcee981c",
    "https://images.unsplash.com/photo-1555949963-ff9fe0c870eb",
    "https://images.unsplash.com/photo-1515879218367-8466d910aaa4",
    "https://images.unsplash.com/photo-1550439062-609e1531270e",
    "https://images.unsplash.com/photo-1605379399642-870262d3d051",
    "https://images.unsplash.com/photo-1571171637578-41bc2dd41cd2",
    "https://images.unsplash.com/photo-1593720213428-28a5b9e94613",
    "https://images.unsplash.com/photo-1593720216276-0caa6452c8d0",
    "https://images.unsplash.com/photo-1627398242454-45a1465c2479",
    "https://images.unsplash.com/photo-1633356122544-f134324a6cee",
    "https://images.unsplash.com/photo-1504639725590-34d0984388bd",
    "https://images.unsplash.com/photo-1484417894907-623942c8ee41",
    "https://images.unsplash.com/photo-1483058712412-4245e9b90334",
    "https://images.unsplash.com/photo-1496171367470-9ed9a91ea931",
    "https://images.unsplash.com/photo-1611162617474-5b21e879e113",
    "https://images.unsplash.com/photo-1611162616305-c69b3037c7bb",
    "https://images.unsplash.com/photo-1611162618071-b39a2ec055fb",
    "https://images.unsplash.com/photo-1618477388954-7852f72348ae",
    "https://images.unsplash.com/photo-1618761714954-0b8cd0026356",
    "https://images.unsplash.com/photo-1555421689-491a97ff2040",
    "https://images.unsplash.com/photo-1516321318423-f06f85e504b3",
    "https://images.unsplash.com/photo-1499951360447-b19be8fe80f5",
    "https://images.unsplash.com/photo-1531403009284-440f080d1e12",
    "https://images.unsplash.com/photo-1600132806608-235180695415",
    "https://images.unsplash.com/photo-1587440871875-191322eeaf42",
    "https://images.unsplash.com/photo-1553877522-43269d4ea984",
    "https://images.unsplash.com/photo-1519389950473-47ba0277781c",
    "https://images.unsplash.com/photo-1516321497487-e288fb19713f",
    "https://images.unsplash.com/photo-1581091226825-a6a2a5aee158",
    "https://images.unsplash.com/photo-1504384308090-c894fdcc538d",
    "https://images.unsplash.com/photo-1504384764586-bb4cdc3d78c0",
    "https://images.unsplash.com/photo-1559136555-9303baea8ebd",
    "https://images.unsplash.com/photo-1432888498266-38ffec3eaf0a",
    "https://images.unsplash.com/photo-1460925895917-afdab827c52f",
    "https://images.unsplash.com/photo-1551288049-bebda4e38f71",
    "https://images.unsplash.com/photo-1557804506-669a67965ba0",
    "https://images.unsplash.com/photo-1556761175-b413da4baf72",
]

_SOFTWARE_IMAGES = [
    "https://images.unsplash.com/photo-1498050108023-c5249f4df085",
    "https://images.unsplash.com/photo-1461749280684-dccba630e2f6",
    "https://images.unsplash.com/photo-1488590528505-98d2b5aba04b",
    "https://images.unsplash.com/photo-1517694712202-14dd9538aa97",
    "https://images.unsplash.com/photo-1555066931-4365d14bab8c",
    "https://images.unsplash.com/photo-1587620962725-abab7fe55159",
    "https://images.unsplash.com/photo-1542831371-29b0f74f9713",
    "https://images.unsplash.com/photo-1555949963-aa79dcee981c",
    "https://images.unsplash.com/photo-1515879218367-8466d910aaa4",
    "https://images.unsplash.com/photo-1605379399642-870262d3d051",
    "https://images.unsplash.com/photo-1512941937669-90a1b58e7e9c",
    "https://images.unsplash.com/photo-1551650975-87deedd944c3",
]

# Banking / investing / fintech — used when Industry = Finance (or finance keywords)
_FINANCE_IMAGES = [
    "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3",  # stock charts
    "https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f",  # trading desk
    "https://images.unsplash.com/photo-1559526324-4b87b5e36e44",  # coins / finance
    "https://images.unsplash.com/photo-1579621970563-ebec7560ff3e",  # piggy bank / savings
    "https://images.unsplash.com/photo-1563986768609-322da13575f3",  # mobile banking
    "https://images.unsplash.com/photo-1454165804606-c3d57bc86b40",  # finance desk documents
    "https://images.unsplash.com/photo-1554224155-6726b3ff858f",  # calculator / accounting
    "https://images.unsplash.com/photo-1460925895917-afdab827c52f",  # analytics dashboard
    "https://images.unsplash.com/photo-1551288049-bebda4e38f71",  # charts on screen
    "https://images.unsplash.com/photo-1553729459-efe14ef6055d",  # money / wealth
    "https://images.unsplash.com/photo-1633158829585-23ba8f7c8caf",  # fintech phone
    "https://images.unsplash.com/photo-1642543492481-44e81e3914a7",  # crypto / finance UI
]

# Back-compat alias used by pool helpers
_WEB_FAMILY_IMAGES = list(_WEB_DESIGN_IMAGES)

_CURATED_TOPIC_IMAGES = {
    "web design": list(_WEB_DESIGN_IMAGES),
    "website design": list(_WEB_DESIGN_IMAGES),
    "website designer": list(_WEB_DESIGN_IMAGES),
    "web development": list(_WEB_DESIGN_IMAGES),
    "wordpress": list(_WEB_DESIGN_IMAGES),
    "software": list(_SOFTWARE_IMAGES),
    "finance": list(_FINANCE_IMAGES),
    "banking": list(_FINANCE_IMAGES),
    "fintech": list(_FINANCE_IMAGES),
    "investment": list(_FINANCE_IMAGES),
    "plumbing": [
        "https://images.unsplash.com/photo-1607472586893-edb57bdc0e39",  # plumber tools
        "https://images.unsplash.com/photo-1581244277943-fe4a9c777189",  # plumbing work
        "https://images.unsplash.com/photo-1585704032915-c3400ca199e7",  # pipes
        "https://images.unsplash.com/photo-1504328345606-18bbc8c9d7d1",  # pipe wrench
        "https://images.unsplash.com/photo-1558618666-fcd25c85cd64",  # plumbing pipes
    ],
    "electrician": [
        "https://images.unsplash.com/photo-1621905251189-08b45d6a269e",
        "https://images.unsplash.com/photo-1473341304170-971dccb5ac1e",
        "https://images.unsplash.com/photo-1621905252507-b35492cc74b4",
    ],
    "hvac": [
        "https://images.unsplash.com/photo-1581244277943-fe4a9c777189",
        "https://images.unsplash.com/photo-1607472586893-edb57bdc0e39",
        "https://images.unsplash.com/photo-1585704032915-c3400ca199e7",
    ],
    "marketing": [
        "https://images.unsplash.com/photo-1460925895917-afdab827c52f",  # analytics dashboard
        "https://images.unsplash.com/photo-1432888498266-38ffec3eaf0a",  # SEO / search
        "https://images.unsplash.com/photo-1551288049-bebda4e38f71",  # charts
        "https://images.unsplash.com/photo-1504868584819-f8e8b4b6d7e3",  # data viz
        "https://images.unsplash.com/photo-1557804506-669a67965ba0",  # marketing meeting
        "https://images.unsplash.com/photo-1552664730-d307ca884978",  # team workshop
        "https://images.unsplash.com/photo-1553877522-43269d4ea984",  # strategy
        "https://images.unsplash.com/photo-1542744173-8e7e53415bb0",  # business planning
    ],
    "seo": [
        "https://images.unsplash.com/photo-1460925895917-afdab827c52f",
        "https://images.unsplash.com/photo-1432888498266-38ffec3eaf0a",
        "https://images.unsplash.com/photo-1551288049-bebda4e38f71",
        "https://images.unsplash.com/photo-1504868584819-f8e8b4b6d7e3",
    ],
    "dental": [
        "https://images.unsplash.com/photo-1588776814546-1ffcf47267a5",
        "https://images.unsplash.com/photo-1606811841689-23dfddce3e95",
        "https://images.unsplash.com/photo-1629909613654-28e377c37b09",
    ],
    "real estate": [
        "https://images.unsplash.com/photo-1560518883-ce09059eeffa",
        "https://images.unsplash.com/photo-1582407947304-fd86f028f716",
        "https://images.unsplash.com/photo-1560184897-ae75f418493e",
        "https://images.unsplash.com/photo-1564013799919-ab600027ffc6",
    ],
    "legal": [
        "https://images.unsplash.com/photo-1589829545856-d10d557cf95f",
        "https://images.unsplash.com/photo-1505664194779-8beaceb93744",
        "https://images.unsplash.com/photo-1450101499163-c8848c66ca85",
    ],
    "restaurant": [
        "https://images.unsplash.com/photo-1414235077428-338989a2e8c0",
        "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4",
        "https://images.unsplash.com/photo-1552566626-52f8b828add9",
        "https://images.unsplash.com/photo-1577219491135-ce391730fb2c",
        "https://images.unsplash.com/photo-1559339352-11d035aa65de",
        "https://images.unsplash.com/photo-1514933651103-005eec06c04b",
        "https://images.unsplash.com/photo-1466978913421-dad2ebd01d17",
        "https://images.unsplash.com/photo-1550966871-3ed3cdb5ed0c",
        "https://images.unsplash.com/photo-1555396273-367ea4eb4db5",
        "https://images.unsplash.com/photo-1424847653812-1a7eed4a17cb",
        "https://images.unsplash.com/photo-1600891964599-f61ba0e24092",
        "https://images.unsplash.com/photo-1504674900247-0877df9cc836",
        "https://images.unsplash.com/photo-1476224203421-9ac39bcb3327",
        "https://images.unsplash.com/photo-1482049016688-2d3e1b311543",
        "https://images.unsplash.com/photo-1565299624946-b28f40a0ae38",
        "https://images.unsplash.com/photo-1540189549336-e6e99c3679fe",
        "https://images.unsplash.com/photo-1567620905732-2d1ec7ab7445",
        "https://images.unsplash.com/photo-1565958011703-44f9829df7b2",
        "https://images.unsplash.com/photo-1478144592103-25e218a04891",
    ],
    "restaurants": [
        "https://images.unsplash.com/photo-1414235077428-338989a2e8c0",
        "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4",
        "https://images.unsplash.com/photo-1552566626-52f8b828add9",
        "https://images.unsplash.com/photo-1577219491135-ce391730fb2c",
        "https://images.unsplash.com/photo-1559339352-11d035aa65de",
        "https://images.unsplash.com/photo-1514933651103-005eec06c04b",
        "https://images.unsplash.com/photo-1466978913421-dad2ebd01d17",
        "https://images.unsplash.com/photo-1550966871-3ed3cdb5ed0c",
        "https://images.unsplash.com/photo-1555396273-367ea4eb4db5",
        "https://images.unsplash.com/photo-1424847653812-1a7eed4a17cb",
        "https://images.unsplash.com/photo-1600891964599-f61ba0e24092",
        "https://images.unsplash.com/photo-1504674900247-0877df9cc836",
        "https://images.unsplash.com/photo-1476224203421-9ac39bcb3327",
        "https://images.unsplash.com/photo-1482049016688-2d3e1b311543",
        "https://images.unsplash.com/photo-1565299624946-b28f40a0ae38",
        "https://images.unsplash.com/photo-1540189549336-e6e99c3679fe",
        "https://images.unsplash.com/photo-1567620905732-2d1ec7ab7445",
        "https://images.unsplash.com/photo-1565958011703-44f9829df7b2",
        "https://images.unsplash.com/photo-1478144592103-25e218a04891",
    ],
    "cleaning": [
        "https://images.unsplash.com/photo-1581578731548-c64695cc6952",
        "https://images.unsplash.com/photo-1563453392212-326f5e854473",
        "https://images.unsplash.com/photo-1628177142898-93e36e4e3a50",
    ],
    "roofing": [
        "https://images.unsplash.com/photo-1632778149955-e80f8ceca2e8",
        "https://images.unsplash.com/photo-1503387762-592deb58ef4e",
        "https://images.unsplash.com/photo-1541888946425-d81bb19240f5",
    ],
    "landscaping": [
        "https://images.unsplash.com/photo-1558904541-efa843a96f01",
        "https://images.unsplash.com/photo-1416879595882-3373a0480b5b",
        "https://images.unsplash.com/photo-1585320806297-9794b3e4eeae",
    ],
    "fitness": [
        "https://images.unsplash.com/photo-1534438327276-14e5300c3a48",
        "https://images.unsplash.com/photo-1571019614242-c5c5dee9f50b",
        "https://images.unsplash.com/photo-1517836357463-d25dfeac3438",
    ],
    "photography": [
        "https://images.unsplash.com/photo-1452587925148-ce544e77e70d",
        "https://images.unsplash.com/photo-1471341971476-ae15ff5dd4ea",
        "https://images.unsplash.com/photo-1502920917128-1aa500764cbd",
    ],
    "education": [
        "https://images.unsplash.com/photo-1509062522246-3755977927d7",  # classroom
        "https://images.unsplash.com/photo-1503676260728-1c00da094a0b",  # students learning
        "https://images.unsplash.com/photo-1427504494785-3a9ca7044f45",  # library study
        "https://images.unsplash.com/photo-1523050854058-8df90110c9f1",  # graduation
        "https://images.unsplash.com/photo-1524178232363-1fb2b075b655",  # lecture hall
        "https://images.unsplash.com/photo-1580582932707-520aed937b7b",  # school hallway
        "https://images.unsplash.com/photo-1497633762265-9d179a990aa6",  # books education
        "https://images.unsplash.com/photo-1481627834876-b7833e8f5570",  # library books
        "https://images.unsplash.com/photo-1522202176988-66273c2fd55f",  # study group
        "https://images.unsplash.com/photo-1571260899304-425eee4c7efc",  # kids classroom
        "https://images.unsplash.com/photo-1588072432836-e10032774350",  # teacher board
        "https://images.unsplash.com/photo-1607237138185-eedd9c632b0b",  # university campus
        "https://images.unsplash.com/photo-1516321318423-f06f85e504b3",  # online learning
        "https://images.unsplash.com/photo-1434030216411-0b793f4b4173",  # studying notebook
        "https://images.unsplash.com/photo-14565130808af520-2711bfdbc72a",  # reading / study
    ],
}

_GENERIC_CURATED = [
    # Only used when niche is unknown — keep professional, not random
    "https://images.unsplash.com/photo-1454165804606-c3d57bc86b40",
    "https://images.unsplash.com/photo-1507679799987-c73779587ccf",
    "https://images.unsplash.com/photo-1522202176988-66273c2fd55f",
    "https://images.unsplash.com/photo-1553877522-43269d4ea984",
]

# Topic-specific search modifiers (generic "storefront" pulls wrong photos for web design).
_TOPIC_MODIFIERS = {
    "web design": ["ui mockup", "designer laptop", "website wireframe", "creative desk"],
    "website": ["ui mockup", "designer laptop", "website wireframe", "creative desk"],
    "web development": ["coding laptop", "developer desk", "html css", "app interface"],
    "software": ["coding screen", "developer team", "laptop code", "tech workspace"],
    "finance": ["stock charts", "banking desk", "investment meeting", "financial dashboard"],
    "banking": ["bank office", "mobile banking", "financial advisor", "wealth planning"],
    "fintech": ["fintech app", "payment dashboard", "digital banking", "finance charts"],
    "plumbing": ["pipe repair", "plumber tools", "bathroom fixture", "water heater"],
    "marketing": ["analytics dashboard", "team meeting", "strategy board", "laptop charts"],
    "seo": ["search analytics", "laptop seo", "keyword research", "dashboard"],
    "legal": ["law office", "legal documents", "courthouse", "attorney desk"],
    "real estate": ["modern home", "house keys", "real estate agent", "property exterior"],
    "restaurant": ["restaurant interior", "chef plating food", "dining table", "kitchen service"],
    "restaurants": ["restaurant interior", "chef plating food", "dining table", "kitchen service"],
    "cafe": ["cafe interior", "barista coffee", "bistro dining", "food plating"],
    "education": ["classroom students", "teacher whiteboard", "university campus", "library study"],
    "school": ["classroom students", "school hallway", "graduation ceremony", "students learning"],
    "tutoring": ["tutor student desk", "homework help", "study session", "learning books"],
}

# Audience industries that may bias stock photos — whitelist ONLY (never pass through
# raw dropdown values like "Restaurants" / "Retail", which used to override niche).
_VISUAL_INDUSTRIES = {
    "finance": "finance",
    "banking": "finance",
    "fintech": "finance",
    "accounting": "finance",
    "legal": "legal",
    "law": "legal",
    "real estate": "real estate",
    "education": "education",
    "healthcare": "medical",
    "health": "medical",
    "insurance": "insurance",
}

# Niche families where a strong audience industry (Finance, Legal, …) may override
# stock photos — not Restaurants/Retail, which must follow Business Niche.
_INDUSTRY_OVERRIDE_NICHES = frozenset({"software", "web", "marketing", "general"})

_IMAGE_TYPO_FIXES = {
    "sotware": "software",
    "softwar": "software",
    "pulmbing": "plumbing",
    "plumbin": "plumbing",
    "electrition": "electrician",
    "resturant": "restaurant",
    "restuarant": "restaurant",
}

# Industry / Audience → campaign niche when user picks a vertical but leaves a
# leftover Business Niche (e.g. Industry=Education, niche still "software engineer").
_INDUSTRY_NICHE_MAP = {
    "education": "Education",
    "finance": "Finance",
    "banking": "Finance",
    "restaurants": "Restaurant",
    "restaurant": "Restaurant",
    "legal": "Legal",
    "law": "Legal",
    "real estate": "Real Estate",
    "healthcare": "Healthcare",
    "health": "Healthcare",
    "insurance": "Insurance",
    "retail": "Retail",
}

# Niches that are treated as stale leftovers when a strong Industry is selected.
_STALE_NICHE_RE = re.compile(
    r"\b(software|sotware|engineer|coding|developer|saas|web\s*design|wordpress)\b",
    re.I,
)
_STALE_DEFAULTS = frozenset({
    "", "web design", "website design", "business", "services", "local services",
})


def resolve_campaign_niche(business_type: str, industry: str = "") -> str:
    """Pick the niche that content + images must follow.

    Users often change only Industry / Audience (Education, Finance, Restaurants)
    while Business Niche still holds an old value like "software engineer".
    Strong industries win over stale tech/default niches.
    """
    bt = (business_type or "").strip()
    # typo fixes for niche words
    for typo, fixed in _IMAGE_TYPO_FIXES.items():
        bt = re.sub(rf"\b{re.escape(typo)}\b", fixed, bt, flags=re.I)
    ind_raw = (industry or "").strip().lower()
    industry_niche = _INDUSTRY_NICHE_MAP.get(ind_raw)
    if not industry_niche and ind_raw:
        for key, mapped in _INDUSTRY_NICHE_MAP.items():
            if key in ind_raw or (len(ind_raw) >= 4 and ind_raw in key):
                industry_niche = mapped
                break

    if not industry_niche:
        return bt or "Local Services"

    bt_l = bt.lower().strip()
    bt_fam = topic_image_family(bt)
    ind_fam = topic_image_family(industry_niche)

    # Already aligned (e.g. niche "tutoring" + Education)
    if bt and bt_fam == ind_fam and bt_fam not in ("general",):
        return bt

    stale = (not bt) or bt_l in _STALE_DEFAULTS or bool(_STALE_NICHE_RE.search(bt))
    if stale or (bt_fam != ind_fam and bt_fam in ("software", "web", "marketing", "general")):
        return industry_niche

    return bt or industry_niche


def _category_fallback_query(text: str) -> str:
    t = (text or "").lower()
    for keys, fallback_query in _CATEGORY_FALLBACK_QUERIES:
        if any(k in t for k in keys):
            return fallback_query
    return "professional business team meeting"


def _curated_pool_for_topic(text: str) -> List[str]:
    t = (text or "").lower().strip()
    # Exact / prefix family first so "finance software engineer" never steals
    # the software pool when the chosen topic is finance (and vice versa).
    fam = topic_image_family(t)
    family_pools = {
        "plumbing": _CURATED_TOPIC_IMAGES.get("plumbing", []),
        "hvac": _CURATED_TOPIC_IMAGES.get("hvac", []),
        "electrician": _CURATED_TOPIC_IMAGES.get("electrician", []),
        "finance": _FINANCE_IMAGES,
        "marketing": _CURATED_TOPIC_IMAGES.get("marketing", []),
        "software": _SOFTWARE_IMAGES,
        "web": _WEB_DESIGN_IMAGES,
        "dental": _CURATED_TOPIC_IMAGES.get("dental", []),
        "real_estate": _CURATED_TOPIC_IMAGES.get("real estate", []),
        "legal": _CURATED_TOPIC_IMAGES.get("legal", []),
        "restaurant": _CURATED_TOPIC_IMAGES.get("restaurant", []),
        "cleaning": _CURATED_TOPIC_IMAGES.get("cleaning", []),
        "roofing": _CURATED_TOPIC_IMAGES.get("roofing", []),
        "landscaping": _CURATED_TOPIC_IMAGES.get("landscaping", []),
        "fitness": _CURATED_TOPIC_IMAGES.get("fitness", []),
        "photography": _CURATED_TOPIC_IMAGES.get("photography", []),
        "education": _CURATED_TOPIC_IMAGES.get("education", _GENERIC_CURATED),
    }
    if fam in family_pools and family_pools[fam]:
        return list(dict.fromkeys(family_pools[fam]))
    # Longest / most specific keys first
    for key in sorted(_CURATED_TOPIC_IMAGES.keys(), key=len, reverse=True):
        if key in t:
            return list(dict.fromkeys(_CURATED_TOPIC_IMAGES[key]))
    for keys, _ in _CATEGORY_FALLBACK_QUERIES:
        if any(k in t for k in keys):
            if any(k.startswith("web") or "website" in k for k in keys):
                return list(dict.fromkeys(_WEB_DESIGN_IMAGES))
            if any("plumb" in k for k in keys):
                return list(dict.fromkeys(_CURATED_TOPIC_IMAGES["plumbing"]))
            if any("restaurant" in k or "cafe" in k or "food" in k for k in keys):
                return list(dict.fromkeys(_CURATED_TOPIC_IMAGES["restaurant"]))
            if any("financ" in k or "bank" in k or "fintech" in k for k in keys):
                return list(dict.fromkeys(_FINANCE_IMAGES))
            if any("software" in k or "coding" in k for k in keys):
                return list(dict.fromkeys(_SOFTWARE_IMAGES))
            if any("market" in k or "seo" in k or "digital" in k for k in keys):
                return list(dict.fromkeys(_CURATED_TOPIC_IMAGES["marketing"]))
            break
    return list(dict.fromkeys(_GENERIC_CURATED))


def _resolve_visual_industry(industry: str) -> str:
    """Map Industry / Audience to a visual topic key. Whitelist only — never raw."""
    raw = (industry or "").strip().lower()
    if not raw or raw in ("other", "general", "contractors", "services", "retail",
                          "professional services", "restaurants", "restaurant"):
        # Restaurants/Retail are niches — they must come from Business Niche, not Industry
        return ""
    if raw in _VISUAL_INDUSTRIES:
        return _VISUAL_INDUSTRIES[raw]
    for key, mapped in _VISUAL_INDUSTRIES.items():
        if key in raw or raw in key:
            return mapped
    return ""


def _pick_image_topic(niche_topic: str, focus_keyword: str, industry: str = "") -> tuple:
    """Resolve visuals from niche + industry (Education wins over leftover software niche)."""
    resolved = resolve_campaign_niche(
        niche_topic or focus_keyword or "business",
        industry,
    )
    topic = _clean_image_query(resolved) or resolved.lower().strip() or "business"
    return topic, topic


def _with_unsplash_params(url: str) -> str:
    if "images.unsplash.com" in url and "?" not in url:
        return f"{url}?w=1200&h=675&fit=crop&q=80"
    return url


def _all_curated_urls() -> List[str]:
    """Every curated Unsplash URL we ship — used when a niche pool is exhausted."""
    seen: List[str] = []
    keys = set()
    for pool in (_WEB_DESIGN_IMAGES, _SOFTWARE_IMAGES, _FINANCE_IMAGES, _GENERIC_CURATED):
        for u in pool:
            k = normalize_image_key(u)
            if k and k not in keys:
                keys.add(k)
                seen.append(u)
    for urls in _CURATED_TOPIC_IMAGES.values():
        for u in urls:
            k = normalize_image_key(u)
            if k and k not in keys:
                keys.add(k)
                seen.append(u)
    return seen


def _curated_image_url(
    topic: str,
    seed: str,
    exclude: Optional[Iterable[str]] = None,
) -> str:
    """Pick an unused photo. Niche pool first, then any curated URL, then a unique fallback."""
    exclude_keys = {normalize_image_key(u) for u in (exclude or []) if u}

    def _pick(pool: List[str]) -> str:
        unused = [u for u in pool if normalize_image_key(u) not in exclude_keys]
        if not unused:
            return ""
        unused.sort(key=lambda u: hashlib.md5(f"{seed}|{normalize_image_key(u)}".encode("utf-8")).hexdigest())
        return _with_unsplash_params(unused[0])

    url = _pick(_curated_pool_for_topic(topic))
    if url:
        return url
    url = _pick(_all_curated_urls())
    if url:
        return url
    digest = hashlib.md5((seed or "seo").encode("utf-8")).hexdigest()[:16]
    return f"https://picsum.photos/seed/{digest}/1200/675"


def _openverse_relevance(result: dict, topic_words: List[str]) -> int:
    """Score how on-topic an Openverse hit is; 0 = reject."""
    if not topic_words:
        return 0
    blob = " ".join([
        str(result.get("title") or ""),
        str(result.get("description") or ""),
        " ".join(result.get("tags") or []) if isinstance(result.get("tags"), list) else str(result.get("tags") or ""),
    ]).lower()
    hits = sum(1 for w in topic_words if w in blob)
    # Require at least one strong topic word; reject tourist/random Flickr noise.
    return hits


async def _hosted_image_url(
    query: str,
    seed: str,
    exclude: Optional[Iterable[str]] = None,
    location: str = "",
) -> str:
    """Return an on-topic hosted image URL unique to this seed/location."""
    exclude_keys = {normalize_image_key(u) for u in (exclude or []) if u}
    place = " ".join(re.findall(r"[a-zA-Z]+", (location or "").lower())[:3])
    search = f"{query} {place}".strip() if place else query
    page = (_stable_index(seed, 20) + 1)
    if settings.UNSPLASH_ACCESS_KEY:
        try:
            async with httpx.AsyncClient(timeout=12) as client:
                resp = await client.get(
                    "https://api.unsplash.com/search/photos",
                    params={
                        "query": search,
                        "per_page": 30,
                        "orientation": "landscape",
                        "page": page,
                    },
                    headers={"Authorization": f"Client-ID {settings.UNSPLASH_ACCESS_KEY}"},
                )
                if resp.status_code == 200:
                    results = resp.json().get("results", [])
                    fresh = [
                        r for r in results
                        if normalize_image_key(r.get("urls", {}).get("regular") or "") not in exclude_keys
                    ]
                    if fresh:
                        pick = fresh[_stable_index(seed, len(fresh))]
                        return pick["urls"].get("regular") or pick["urls"].get("full") or ""
        except Exception as e:
            print(f"[Image] Unsplash search error: {e}")
    if settings.PEXELS_API_KEY:
        try:
            async with httpx.AsyncClient(timeout=12) as client:
                resp = await client.get(
                    "https://api.pexels.com/v1/search",
                    params={
                        "query": search,
                        "per_page": 30,
                        "orientation": "landscape",
                        "page": page,
                    },
                    headers={"Authorization": settings.PEXELS_API_KEY},
                )
                if resp.status_code == 200:
                    photos = resp.json().get("photos", [])
                    fresh = []
                    for p in photos:
                        src = (p.get("src") or {})
                        cand = src.get("original") or src.get("large2x") or src.get("large") or ""
                        if normalize_image_key(cand) not in exclude_keys:
                            fresh.append(p)
                    if fresh:
                        pick = fresh[_stable_index(seed, len(fresh))]
                        src = pick.get("src") or {}
                        return src.get("original") or src.get("large2x") or src.get("large")
        except Exception as e:
            print(f"[Image] Pexels search error: {e}")

    return _curated_image_url(query, seed, exclude=exclude_keys)


# Default modifiers — topic-specific only (never generic office/meeting).
_IMAGE_QUERY_MODIFIERS = ["ui mockup", "designer laptop", "website wireframe", "code on screen"]

# Marketing/filler words that make a great blog H1 but a terrible image-search
# query — stripping them (and dropping the city, which stock libraries almost
# never tag by specific town) is what actually gets Openverse a real match
# instead of falling through to the random picsum.photos placeholder.
_IMAGE_QUERY_STOPWORDS = {
    "the", "in", "of", "and", "a", "an", "for", "to", "at", "on", "by", "with",
    "near", "me", "best", "top", "affordable", "proven", "trusted", "licensed",
    "guide", "complete", "services", "service", "your", "you", "we", "our",
    "call", "free", "estimate", "quote", "rates", "fast", "turnaround",
    "options", "mistakes", "avoid", "how", "much", "does", "cost", "why",
    "chooses", "company", "1", "licensed", "experts", "trusted", "local",
    "businesses", "business", "results", "get", "today", "consultation",
}


def _clean_image_query(text: str, max_words: int = 3, exclude: Optional[set] = None) -> str:
    """Reduce a blog title/keyword to a short, stock-photo-searchable topic.

    `exclude` additionally strips any words pulled from the article's own
    location — keywords are built as "{business type} {city}" (see
    keyword_service.py), so the city rides along inside focus_keyword itself
    and a generic English stopword list alone won't catch it.
    """
    skip = _IMAGE_QUERY_STOPWORDS | (exclude or set())
    words = []
    for w in re.findall(r"[a-zA-Z]+", (text or "").lower()):
        w = _IMAGE_TYPO_FIXES.get(w, w)
        if w not in skip and len(w) > 2:
            words.append(w)
    return " ".join(words[:max_words])


async def generate_article_images(
    focus_keyword: str,
    location: str,
    business_name: str = "",
    count: int = 3,
    angle_title: str = "",
    exclude_urls: Optional[Iterable[str]] = None,
    industry: str = "",
) -> List[ImageAsset]:
    """Generate 1 featured + (count-1) in-content images with full SEO metadata.

    Business niche (focus_keyword) owns the visual topic. Industry / Audience only
    overrides for Finance/Legal-style audiences when the niche is a vague tech title.

    `exclude_urls` prevents reusing featured photos already assigned to other pages
    in the same generate/refresh batch (and within this article).
    """
    count = max(1, min(count, 3))
    assets: List[ImageAsset] = []
    location_words = {
        w for w in re.findall(r"[a-zA-Z]+", (location or "").lower()) if len(w) > 2
    }
    niche_topic = (
        _clean_image_query(focus_keyword, exclude=location_words)
        or _clean_image_query(angle_title, exclude=location_words)
        or "business"
    )
    topic, topic_blob = _pick_image_topic(niche_topic, focus_keyword, industry)

    modifiers = _IMAGE_QUERY_MODIFIERS
    topic_l = topic.lower()
    search_blob = f"{topic_l} {industry} {focus_keyword}".lower()
    for key, mods in _TOPIC_MODIFIERS.items():
        if key in topic_l or key in search_blob:
            modifiers = mods
            break

    used: Set[str] = {normalize_image_key(u) for u in (exclude_urls or []) if u}
    # Prefer curated pool when we know the niche — keeps photos on-topic and unique
    # across locations (Unsplash often returns the same popular hit).
    prefer_curated = topic_image_family(topic_blob) not in ("general",)

    for i in range(count):
        is_featured = i == 0
        modifier = modifiers[i % len(modifiers)]
        query = f"{topic} {modifier}".strip()
        seed = f"{topic}|{location}|{focus_keyword}|{i}|{angle_title}|{industry}"
        url = ""
        if prefer_curated:
            url = _curated_image_url(topic_blob, seed=seed, exclude=used)
            key = normalize_image_key(url)
            if key and key in used:
                url = ""
        if not url:
            url = await _hosted_image_url(query, seed=seed, exclude=used, location=location)
        key = normalize_image_key(url)
        # Hard uniqueness: if we still collided, force another curated pick with a new seed
        if key and key in used:
            for attempt in range(12):
                alt = _curated_image_url(
                    topic_blob,
                    seed=f"{seed}|retry|{attempt}",
                    exclude=used,
                )
                alt_key = normalize_image_key(alt)
                if alt_key and alt_key not in used:
                    url, key = alt, alt_key
                    break
            if key in used:
                url = await _hosted_image_url(
                    query, seed=f"{seed}|retry-host", exclude=used, location=location,
                )
                key = normalize_image_key(url)
        if key:
            used.add(key)
        meta = build_image_metadata(focus_keyword, location, business_name, i, is_featured)
        assets.append(ImageAsset(
            url=url,
            filename=meta["filename"],
            mime_type="image/webp",
            alt_text=meta["alt_text"],
            title=meta["title"],
            caption=meta["caption"],
            description=meta["description"],
            is_featured=is_featured,
        ))
    return assets


def _content_type_for(filename: str) -> str:
    if filename.endswith(".webp"):
        return "image/webp"
    if filename.endswith(".png"):
        return "image/png"
    return "image/jpeg"


async def upload_image_to_wordpress(
    image_bytes: bytes,
    filename: str,
    wp_url: str,
    wp_username: str,
    wp_app_password: str,
    alt_text: str = "",
    title: str = "",
    caption: str = "",
    description: str = "",
    convert_webp: bool = True,
) -> Optional[dict]:
    """Upload image to WordPress media library with full SEO metadata.

    Converts to WebP when requested (and the filename targets .webp); falls back
    to the original bytes if conversion fails.
    """
    # WebP conversion.
    if convert_webp and filename.endswith(".webp"):
        webp = convert_to_webp(image_bytes)
        if webp:
            image_bytes = webp
        else:
            filename = re.sub(r"\.webp$", ".jpg", filename)  # fall back to jpg

    credentials = base64.b64encode(f"{wp_username}:{wp_app_password}".encode()).decode()
    headers = {
        "Authorization": f"Basic {credentials}",
        "Content-Disposition": f'attachment; filename="{filename}"',
        "Content-Type": _content_type_for(filename),
    }
    media_api = wp_url.rstrip("/") + "/wp-json/wp/v2/media"
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(media_api, content=image_bytes, headers=headers)
            if resp.status_code in (200, 201):
                data = resp.json()
                media_id = data.get("id")
                # Set full SEO metadata on the media item.
                meta_payload = {}
                if alt_text:
                    meta_payload["alt_text"] = alt_text
                if title:
                    meta_payload["title"] = title
                if caption:
                    meta_payload["caption"] = caption
                if description:
                    meta_payload["description"] = description
                if meta_payload and media_id:
                    await client.post(
                        f"{media_api}/{media_id}",
                        json=meta_payload,
                        headers={
                            "Authorization": f"Basic {credentials}",
                            "Content-Type": "application/json",
                        },
                    )
                return {"id": media_id, "url": data.get("source_url", "")}
    except Exception as e:
        print(f"[Image] WP upload error: {e}")
    return None
