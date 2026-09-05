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


def assign_canonical_images(images: List["ImageAsset"]) -> tuple:
    """One article → one image set. Featured = first; footer = first distinct non-featured.

    Drops duplicate URLs within the set. Returns (featured_url, footer_url, cleaned_images).
    """
    if not images:
        return "", "", []
    cleaned: List[ImageAsset] = []
    seen: Set[str] = set()
    for im in images:
        raw = (getattr(im, "url", "") or "").strip()
        if not raw:
            continue
        key = normalize_image_key(raw)
        if key and key in seen:
            continue
        if key:
            seen.add(key)
        im.is_featured = len(cleaned) == 0
        cleaned.append(im)
    if not cleaned:
        return "", "", []
    featured = cleaned[0].url or ""
    feat_key = normalize_image_key(featured)
    footer = featured
    for im in cleaned[1:]:
        if im.url and normalize_image_key(im.url) != feat_key:
            footer = im.url
            break
    return featured, footer, cleaned




def topic_image_family(text: str) -> str:
    """Bucket niches so uniqueness is enforced per family (web vs plumbing, etc.)."""
    t = (text or "").lower()
    if any(k in t for k in ("used car", "car dealer", "auto dealer", "automotive", "dealership")):
        return "automotive"
    if any(k in t for k in ("plumb",)):
        return "plumbing"
    if any(k in t for k in ("hvac", "heating", "air condition")):
        return "hvac"
    if any(k in t for k in ("electric",)):
        return "electrician"
    if any(k in t for k in ("dental", "dentist")):
        return "dental"
    # Verticals before "website" so "medical website" is not filed as generic web.
    if any(k in t for k in ("health", "medical", "clinic", "hospital", "doctor", "patient", "primary care")):
        return "healthcare"
    if any(k in t for k in ("law", "legal", "attorney")):
        return "legal"
    if any(k in t for k in ("real estate", "realtor")):
        return "real_estate"
    if any(k in t for k in ("restaurant", "chef", "cafe")):
        return "restaurant"
    if any(k in t for k in ("educat", "school", "learn", "tutor", "university", "college", "student")):
        return "education"
    if any(k in t for k in ("financ", "bank", "fintech", "invest", "account")):
        return "finance"
    if any(k in t for k in ("market", "seo", "advertis", "agency")) and not any(
        k in t for k in ("web", "website", "wordpress", "designer", "wix", "shopify")
    ):
        return "marketing"
    # Software/SaaS separate from web-design so large location batches don't collide
    if any(k in t for k in ("software", "saas", "coding", "engineer", "sotware")) and not any(
        k in t for k in ("web design", "website", "wordpress", "web designer", "wix", "shopify")
    ):
        return "software"
    if any(k in t for k in ("web", "website", "wordpress", "designer", "developer", "wix", "shopify", "squarespace", "webflow")):
        return "web"
    if any(k in t for k in ("clean",)):
        return "cleaning"
    if any(k in t for k in ("roof",)):
        return "roofing"
    if any(k in t for k in ("landscap", "lawn")):
        return "landscaping"
    if any(k in t for k in ("fitness", "gym", "trainer")):
        return "fitness"
    # Require photographer/photography — bare "photo" matches too many false positives.
    if any(k in t for k in ("photographer", "photography", "photo studio")):
        return "photography"
    return "general"


# Blog-only: map the editor's search query to a visual category (platform / topic).
# Example: "how to fix the wix website" → category "wix" → Wix-themed stock photos.
_BLOG_PLATFORM_VISUALS = (
    (r"primary[\s-]?care|physician|pediatric|doctors?|clinic|medical|healthcare|dentist", {
        "category": "healthcare",
        "topic": "doctor clinic patient medical office",
        "modifiers": [
            "doctor with patient",
            "medical clinic reception",
            "physician laptop clinic",
            "healthcare office website",
        ],
        "concept": "Doctor and clinic website for a medical practice",
        "label": "Healthcare",
    }),
    (r"gym|fitness|personal train", {
        "category": "fitness",
        "topic": "gym fitness training",
        "modifiers": [
            "gym training session",
            "fitness studio",
            "personal trainer",
            "workout gym floor",
        ],
        "concept": "Gym and fitness studio",
        "label": "Fitness",
    }),
    ("wix", {
        "category": "wix",
        "topic": "wix website builder editor",
        "modifiers": [
            "wix editor laptop screen",
            "website builder dashboard",
            "drag and drop website editor",
            "small business website on laptop",
        ],
        "concept": "Wix website editor open on a laptop",
        "label": "Wix",
    }),
    ("shopify", {
        "category": "shopify",
        "topic": "shopify store dashboard laptop",
        "modifiers": [
            "shopify admin dashboard",
            "ecommerce store laptop",
            "online store checkout",
            "product page website",
        ],
        "concept": "Shopify store dashboard on a laptop",
        "label": "Shopify",
    }),
    ("squarespace", {
        "category": "squarespace",
        "topic": "squarespace website builder",
        "modifiers": [
            "website template editor",
            "designer laptop mockup",
            "portfolio website screen",
            "website builder dashboard",
        ],
        "concept": "Squarespace-style website builder on a laptop",
        "label": "Squarespace",
    }),
    ("webflow", {
        "category": "webflow",
        "topic": "webflow designer interface",
        "modifiers": [
            "web design tool screen",
            "ui designer laptop",
            "website cms dashboard",
            "responsive website mockup",
        ],
        "concept": "Webflow-style design tool on a laptop",
        "label": "Webflow",
    }),
    ("wordpress", {
        "category": "wordpress",
        "topic": "wordpress dashboard laptop",
        "modifiers": [
            "wordpress admin screen",
            "wordpress theme editor",
            "cms dashboard laptop",
            "blog website on screen",
        ],
        "concept": "WordPress dashboard on a laptop",
        "label": "WordPress",
    }),
    (r"\bwp\b", {
        "category": "wordpress",
        "topic": "wordpress dashboard laptop",
        "modifiers": [
            "wordpress admin screen",
            "cms dashboard laptop",
            "blog website on screen",
            "website editor laptop",
        ],
        "concept": "WordPress dashboard on a laptop",
        "label": "WordPress",
    }),
    ("weebly", {
        "category": "weebly",
        "topic": "website builder editor laptop",
        "modifiers": [
            "website builder dashboard",
            "drag drop website",
            "small business website",
            "laptop website design",
        ],
        "concept": "Website builder editor on a laptop",
        "label": "Weebly",
    }),
    ("godaddy", {
        "category": "godaddy",
        "topic": "website builder hosting dashboard",
        "modifiers": [
            "domain hosting laptop",
            "website builder screen",
            "small business website",
            "web hosting dashboard",
        ],
        "concept": "Website builder and hosting dashboard on a laptop",
        "label": "GoDaddy",
    }),
    ("framer", {
        "category": "framer",
        "topic": "framer website design tool",
        "modifiers": [
            "ui design laptop",
            "website prototype screen",
            "designer workspace",
            "modern website mockup",
        ],
        "concept": "Framer-style website design tool on a laptop",
        "label": "Framer",
    }),
    ("magento", {
        "category": "magento",
        "topic": "ecommerce admin dashboard",
        "modifiers": [
            "online store laptop",
            "ecommerce dashboard",
            "product catalog screen",
            "shopping website",
        ],
        "concept": "Ecommerce admin dashboard on a laptop",
        "label": "Magento",
    }),
    ("bigcommerce", {
        "category": "bigcommerce",
        "topic": "ecommerce store dashboard",
        "modifiers": [
            "online store laptop",
            "ecommerce admin",
            "product page website",
            "shopping cart website",
        ],
        "concept": "Ecommerce store dashboard on a laptop",
        "label": "BigCommerce",
    }),
    (r"\b(301|302|redirect|htaccess)\b", {
        "category": "redirect",
        "topic": "website url redirect browser",
        "modifiers": [
            "browser address bar",
            "developer laptop code",
            "server configuration",
            "http status screen",
        ],
        "concept": "Browser showing a website URL redirect",
        "label": "URL redirects",
    }),
    (r"\b(seo|search console|ranking)\b", {
        "category": "seo",
        "topic": "seo analytics dashboard laptop",
        "modifiers": [
            "search analytics chart",
            "keyword research screen",
            "google analytics laptop",
            "seo dashboard",
        ],
        "concept": "SEO analytics dashboard on a laptop",
        "label": "SEO",
    }),
    (r"\b(mobile app|ios app|android app)\b", {
        "category": "mobile_app",
        "topic": "mobile app development phone",
        "modifiers": [
            "app ui on phone",
            "developer phone laptop",
            "mobile app mockup",
            "smartphone app screen",
        ],
        "concept": "Mobile app UI on a phone next to a laptop",
        "label": "Mobile apps",
    }),
)


_IMAGE_KEYWORD_PHRASES = (
    "used car", "used cars", "real estate", "primary care", "web design",
    "web designer", "website design", "mobile app", "google ads", "search console",
    "air conditioning", "personal trainer", "social media", "landing page",
    "online store", "small business", "custom software", "car dealer",
)

_IMAGE_KEYWORD_STOP = {
    "the", "in", "of", "and", "a", "an", "for", "to", "at", "on", "by", "with",
    "near", "me", "best", "top", "how", "to", "a", "the", "my", "your", "website",
    "site", "page", "pages", "guide", "what", "is", "why",
}


def image_keyword_terms(text: str) -> dict:
    """Parse 1–2 word image keywords the editor types (dentist, used car)."""
    raw = re.sub(r"[-_/]+", " ", (text or "").lower())
    raw = re.sub(r"[^\w\s]", " ", raw)
    raw = re.sub(r"\s+", " ", raw).strip()
    if not raw:
        return {"phrase": "", "words": [], "is_short": False}
    keep2 = {"ai", "rv", "ux", "ui", "hr", "it", "seo", "ppc", "crm"}
    tokens = []
    for w in raw.split():
        if w in _IMAGE_KEYWORD_STOP:
            continue
        if len(w) <= 1:
            continue
        if len(w) == 2 and w not in keep2:
            continue
        tokens.append(w)
    if not tokens:
        tokens = [w for w in raw.split() if w not in _IMAGE_KEYWORD_STOP]
    phrase = ""
    for bg in _IMAGE_KEYWORD_PHRASES:
        if re.search(rf"\b{re.escape(bg)}\b", raw):
            phrase = bg
            break
    if not phrase:
        phrase = " ".join(tokens[:2]) if tokens else raw
    words = phrase.split()
    return {"phrase": phrase.strip(), "words": words, "is_short": len(words) <= 2}


def blog_image_plan(query: str, niche: str = "") -> dict:
    """Blog-only: pick image category from the search query (e.g. Wix from 'fix wix website').

    Returns topic + Unsplash modifiers so featured photos match what the reader searched.
    When multiple platforms appear (e.g. 'wordpress vs squarespace'), use the first one
    mentioned in the query — not the order of the platform list.
    One- and two-word image keywords (dentist, used car) stay as the visual topic.
    """
    blob = f"{query or ''} {niche or ''}".strip().lower()
    kw = image_keyword_terms(query or "")
    if kw["phrase"] and kw["is_short"] and topic_image_family(kw["phrase"]) not in ("web", "software", "general"):
        phrase = kw["phrase"]
        return {
            "category": phrase.replace(" ", "_"),
            "topic": phrase,
            "modifiers": [
                phrase,
                f"{phrase} professional",
                f"{phrase} business",
                f"{kw['words'][0]} workplace" if kw["words"] else phrase,
            ],
            "concept": f"{phrase.title()} related photography",
            "label": phrase.title(),
            "focus": phrase,
        }
    if not blob:
        return {
            "category": "website",
            "topic": "website design laptop",
            "modifiers": [
                "web designer office laptop",
                "website mockup screen",
                "ui design desk",
                "laptop website",
            ],
            "concept": "Website design on a laptop",
            "label": "Website",
            "focus": "website design",
        }
    # Prefer earliest match in the query text (left-to-right).
    best = None  # (start_index, plan)
    for pattern, plan in _BLOG_PLATFORM_VISUALS:
        rx = pattern if pattern.startswith(r"\b") or "\\" in pattern else rf"\b{re.escape(pattern)}\b"
        m = re.search(rx, blob, re.I)
        if m and (best is None or m.start() < best[0]):
            best = (m.start(), plan)
    if best:
        out = dict(best[1])
        out["focus"] = best[1]["category"]
        return out
    # No named platform — use significant words from the query (drop how/to/a/the/fix).
    stop = {
        "how", "to", "a", "an", "the", "my", "your", "for", "and", "or", "of", "in", "on",
        "fix", "repair", "broken", "guide", "what", "is", "why", "when", "do", "i", "with",
        "website", "site", "page", "pages",
    }
    tokens = [t for t in re.findall(r"[a-z0-9]+", blob) if t not in stop and len(t) > 2]
    if not tokens:
        kw2 = image_keyword_terms(blob)
        tokens = kw2["words"] or (blob.split()[:2] if blob else ["website", "design"])
    label = " ".join(tokens[:2]).title() if tokens else "Website"
    topic_bits = tokens[:2] or ["website", "design"]
    short_topic = " ".join(topic_bits)
    if len(topic_bits) <= 2 and topic_image_family(short_topic) not in ("web", "software", "general"):
        return {
            "category": tokens[0] if tokens else "website",
            "topic": short_topic,
            "modifiers": [
                short_topic,
                f"{short_topic} professional",
                f"{topic_bits[0]} workplace",
                f"{short_topic} business",
            ],
            "concept": f"{label} photography",
            "label": label,
            "focus": short_topic,
        }
    topic = short_topic + " website laptop"
    return {
        "category": tokens[0] if tokens else "website",
        "topic": topic,
        "modifiers": [
            f"{topic_bits[0]} website screen" if topic_bits else "website screen",
            "designer laptop mockup",
            "website on laptop",
            "web design desk",
        ],
        "concept": f"{label} website topic on a laptop screen",
        "label": label,
        "focus": " ".join(topic_bits) if topic_bits else "website design",
    }

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


def _title_caption_words(text: str) -> str:
    parts = []
    small = {"in", "for", "of", "and", "a", "the", "to", "on"}
    for i, w in enumerate((text or "").split()):
        low = w.lower()
        if low == "wordpress":
            parts.append("WordPress")
        elif low in {"seo", "ai"}:
            parts.append(low.upper())
        elif i and low in small:
            parts.append(low)
        else:
            parts.append(w[:1].upper() + w[1:] if w else w)
    return " ".join(parts)


def _dedupe_service_phrase(kw: str) -> str:
    """Collapse mashed keywords like 'Contractors wordpress website design Website Redesign'."""
    raw = re.sub(r"\s+", " ", (kw or "").strip())
    if not raw:
        return ""
    low = raw.lower()
    # Prefer a single service intent — never "Website Design … Website Redesign"
    if "website redesign" in low and ("website design" in low or "wordpress" in low):
        # Keep WordPress Website Design (or Website Design); drop Redesign mash
        raw = re.sub(r"\bwebsite\s+redesign\b", "", raw, flags=re.I)
        raw = re.sub(r"\bredesign\b", "", raw, flags=re.I)
        raw = re.sub(r"\s+", " ", raw).strip(" -–,")
        low = raw.lower()
    elif "website redesign" in low:
        # Clean standalone redesign path
        pass
    # Collapse "Design Redesign" leftovers
    raw = re.sub(r"\bdesign\s+redesign\b", "Design", raw, flags=re.I)
    raw = re.sub(r"\bredesign\s+design\b", "Design", raw, flags=re.I)
    tokens = raw.split()
    out = []
    seen_norm = set()
    for w in tokens:
        norm = w.lower()
        if out and out[-1].lower() == norm:
            continue
        if norm in seen_norm and norm in {
            "website", "websites", "design", "designer", "redesign", "wordpress", "web",
        }:
            continue
        out.append(w)
        seen_norm.add(norm)
    return " ".join(out).strip(" -–,")


def natural_place_caption(keyword: str, location: str) -> str:
    """Natural caption: 'Contractors WordPress Website Design in Downtown Chula Vista, CA'."""
    kw = _dedupe_service_phrase(re.sub(r"\s+", " ", (keyword or "").strip()))
    loc = re.sub(r"\s+", " ", (location or "").strip())
    if not loc:
        return _title_caption_words(kw) if kw else "Local services"
    city = loc.split(",")[0].strip()
    if city:
        kw = re.sub(re.escape(city), "", kw, flags=re.I)
        kw = re.sub(r"\s+", " ", kw).strip(" -–,")
        # Also strip trailing state if duplicated in keyword
        for part in loc.split(","):
            part = part.strip()
            if part and len(part) > 1:
                kw = re.sub(rf"\b{re.escape(part)}\b", "", kw, flags=re.I)
        kw = re.sub(r"\s+", " ", kw).strip(" -–,")
    core = _dedupe_service_phrase(kw) or _dedupe_service_phrase(keyword or "Services")
    pretty = _title_caption_words(core) if core else "Services"
    if city and re.search(rf"\bin\s+{re.escape(city)}\b", pretty, re.I):
        return pretty
    return f"{pretty} in {loc}"


def build_image_metadata(
    focus_keyword: str,
    location: str,
    business_name: str,
    idx: int,
    is_featured: bool,
    image_concept_text: str = "",
    industry: str = "",
    photo_alt: str = "",
    slot_hint: str = "",
) -> dict:
    """Generate SEO-friendly filename + alt/title/caption/description for an image.

    Alt text must describe the actual subject (website work / business owner),
    not keyword-stuffed SEO phrases, writing briefs, or tourism landmarks.
    """
    raw_kw = (focus_keyword or "").strip()
    # Never paste editor brief labels into image SEO fields.
    if re.search(r"(?i)working title|search intent:|customer problem:", raw_kw):
        raw_kw = "website design"
    kw = raw_kw or "website design"
    # Prefer a short clean phrase for filenames
    kw_short = re.sub(r"\s+", " ", kw)
    if len(kw_short) > 40:
        kw_short = "website design"
    loc = location.strip()
    city = (loc.split(",")[0] if loc else "").strip()
    biz = business_name.strip()
    filename = f"{_slug(kw_short)}-{_slug(loc) or 'local'}-{idx + 1}.webp"
    real_alt = re.sub(r"\s+", " ", (photo_alt or "").strip())
    if real_alt and not re.search(r"(?i)netflix|facebook|messenger|instagram|tiktok", real_alt):
        phrase = real_alt[:125]
        if city and city.lower() not in phrase.lower():
            phrase = f"{phrase.rstrip('.')} for {city}"
        concept = phrase
    else:
        concept = (image_concept_text or "").strip()
    if concept and not re.search(r"(?i)working title|search intent:", concept):
        # Shorten concept into natural alt text
        alt = re.sub(r"\s+", " ", concept)
        alt = re.sub(r",?\s*related to.*$", "", alt, flags=re.I).strip()
        if len(alt) > 125:
            alt = alt[:122].rstrip() + "…"
        phrase = alt
    else:
        phrase = (
            f"Website design on a laptop{f' for a business in {city}' if city else ''}"
        ).strip()
    by = f" by {biz}" if biz and is_featured else ""
    roles = ("Featured header", "Footer", "In-article")
    role = roles[idx] if 0 <= idx < len(roles) else f"Image {idx + 1}"
    zip_m = re.search(r"\b(\d{5})\b", loc)
    zip_code = zip_m.group(1) if zip_m else ""
    zip_bit = f" {zip_code}" if zip_code else ""
    loc_bit = f" — {city}{zip_bit}" if city else (f" — ZIP {zip_code}" if zip_code else "")
    hint = re.sub(r"\s+", " ", (slot_hint or role).strip())[:48]
    if hint and hint.lower() not in (phrase or "").lower():
        phrase = f"{hint}: {phrase}" if phrase else hint

    alt = f"{phrase}{by}{loc_bit}".strip()
    title = f"{role} · {city or 'article'}{zip_bit}: {hint or phrase}".strip()
    caption = f"{city or 'This article'}{zip_bit} · {role} #{idx + 1}: {hint or phrase}."
    caption = re.sub(r"[\.?]+$", ".", caption)
    caption = re.sub(r"\s+", " ", caption).strip()
    description = (
        f"{role} for {city or 'this article'}{zip_bit}. {phrase.rstrip('.?!')}. "
        "Unique visual for this location and slot."
    )
    return {
        "filename": filename,
        "alt_text": alt[:140],
        "title": title[:120],
        "caption": caption[:160],
        "description": description[:220],
    }


# High-coverage, near-guaranteed-to-return-real-results search terms for the
# common local-service business categories this tool targets. Matched by
# substring against the article's own query so a niche/specific phrase that
# returns zero results on Openverse still resolves to a genuinely on-topic
# photo instead of a random unrelated Flickr hit.
_CATEGORY_FALLBACK_QUERIES = [
    (("medical", "clinic", "health", "doctor", "physician", "primary care"), "doctor with patient"),
    (("gym", "fitness", "personal train"), "gym fitness training"),
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
    (("clean",), "professional cleaning service"),
    (("landscap", "lawn"), "landscaper gardening"),
    (("photograph",), "photographer with camera"),
    (("insurance",), "insurance agent meeting client"),
    (("moving", "mover"), "movers loading truck"),
    (("pest",), "pest control technician"),
    (("paint",), "painter painting wall"),
    (("floor", "carpet"), "flooring installation"),
    (("pet", "vet", "animal"), "veterinarian with pet"),
    (("software", "app development", "custom software", "coding"), "software developer coding"),
    (("construction", "contractor", "remodel", "renovation"), "construction contractor at work"),
    (("market", "advertis", "seo", "digital"), "marketing team meeting"),
    (("web design", "website", "web developer", "web development"), "web designer laptop ui mockup"),
]

# Topic-STRICT curated Unsplash photos only (no generic offices/meetings/abstract art).
# Relevance > uniqueness — every URL must clearly match the niche.
# Skip IDs Unsplash has removed (404) — they break Header/Footer previews.
_DEAD_UNSPLASH_IDS = frozenset({
    "photo-1561070791-0369aee323b7",
    "photo-1586717791821-3f8f48fcfba0",
    "photo-1481487196290-c152efe700ba",
    "photo-1593720216276-0caa6452c8d0",
    "photo-1484417894907-623942c8ee41",
    "photo-1611162616305-c69b3037c7bb",
    "photo-1618477388954-7852f72348ae",
    "photo-1600132806608-235180695415",
    "photo-1587440871875-191322eeaf42",
    "photo-1504384764586-bb4cdc3d78c0",
    # 3D app logos (Netflix / Facebook / Messenger / Instagram) — never use on web pages
    "photo-1611162617474-5b21e879e113",
    "photo-1611162618071-b39a2ec055fb",
    "photo-1611162616475-46b635cb6868",
    "photo-1611162617213-7d7a39e9b1d7",
    "photo-1611162618475-46b635cb6868",
    "photo-1611944212129-2995ae3b5ca3",
    "photo-1618761714954-0b8cd0026356",
    "photo-1481487196290-ab5e5f0d0aa2",
    "photo-1661956602119-0de8e45c0430",
})


def _is_banned_stock_key(key: str) -> bool:
    """Block dead IDs and 3D social-app logo photos (Alexander Shatov series)."""
    k = (key or "").lower()
    if not k:
        return True
    if k in _DEAD_UNSPLASH_IDS:
        return True
    # Whole Unsplash 3D-logo series: photo-161116261…
    if k.startswith("photo-161116261"):
        return True
    return False


def _looks_like_camera_photo(url: str, alt: str = "") -> bool:
    blob = f"{url or ''} {alt or ''}".lower()
    return any(
        x in blob
        for x in ("camera", "dslr", "eos rebel", "canon eos", "nikon d", "photo studio", "tripod")
    )


def stock_url_needs_replace(url: str) -> bool:
    """True if this stored URL is empty, placeholder, or a known-404 Unsplash ID."""
    u = (url or "").strip().lower()
    if not u:
        return True
    if "picsum.photos" in u:
        return True
    if "live.staticflickr.com" in u or "flickr.com" in u:
        return True
    if "placeholder" in u:
        return True
    if any(x in u for x in ("camera", "dslr", "canon", "nikon", "tripod")):
        return True
    return _is_banned_stock_key(normalize_image_key(url))

_WEB_DESIGN_IMAGES = [
    "https://images.unsplash.com/photo-1467232004584-a241de8bcf5d",
    "https://images.unsplash.com/photo-1559028012-481c04fa702d",
    "https://images.unsplash.com/photo-1581291518633-83b4ebd1d83e",
    "https://images.unsplash.com/photo-1507238691740-187a5b1d37b8",
    "https://images.unsplash.com/photo-1547658719-da2b51169166",
    "https://images.unsplash.com/photo-1522542550221-31fd19575a2d",
    "https://images.unsplash.com/photo-1561070791-2526d30994b5",
    "https://images.unsplash.com/photo-1559027615-cd4628902d4a",
    "https://images.unsplash.com/photo-1558655146-9f40138edfeb",
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
    "https://images.unsplash.com/photo-1627398242454-45a1465c2479",
    "https://images.unsplash.com/photo-1633356122544-f134324a6cee",
    "https://images.unsplash.com/photo-1504639725590-34d0984388bd",
    "https://images.unsplash.com/photo-1483058712412-4245e9b90334",
    "https://images.unsplash.com/photo-1496171367470-9ed9a91ea931",
    "https://images.unsplash.com/photo-1555421689-491a97ff2040",
    "https://images.unsplash.com/photo-1516321318423-f06f85e504b3",
    "https://images.unsplash.com/photo-1499951360447-b19be8fe80f5",
    "https://images.unsplash.com/photo-1531403009284-440f080d1e12",
    "https://images.unsplash.com/photo-1553877522-43269d4ea984",
    "https://images.unsplash.com/photo-1519389950473-47ba0277781c",
    "https://images.unsplash.com/photo-1516321497487-e288fb19713f",
    "https://images.unsplash.com/photo-1581091226825-a6a2a5aee158",
    "https://images.unsplash.com/photo-1504384308090-c894fdcc538d",
    "https://images.unsplash.com/photo-1559136555-9303baea8ebd",
    "https://images.unsplash.com/photo-1432888498266-38ffec3eaf0a",
    "https://images.unsplash.com/photo-1460925895917-afdab827c52f",
    "https://images.unsplash.com/photo-1551288049-bebda4e38f71",
    "https://images.unsplash.com/photo-1557804506-669a67965ba0",
    "https://images.unsplash.com/photo-1556761175-b413da4baf72",
    "https://images.unsplash.com/photo-1516321497487-e288fb19713f",
    "https://images.unsplash.com/photo-1454165804606-c3d57bc86b40",
    "https://images.unsplash.com/photo-1522202176988-66273c2fd55f",
    "https://images.unsplash.com/photo-1600880292203-757bb62b4baf",
    "https://images.unsplash.com/photo-1552664730-d307ca884978",
    "https://images.unsplash.com/photo-1542744173-8e7e53415bb0",
    "https://images.unsplash.com/photo-1531482615713-2afd69097998",
    "https://images.unsplash.com/photo-1556155092-490a1ba16284",
    "https://images.unsplash.com/photo-1460925895917-afdab827c52f",
    "https://images.unsplash.com/photo-1551288049-bebda4e38f71",
    "https://images.unsplash.com/photo-1504868584819-f8e8b4b6d7e3",
    "https://images.unsplash.com/photo-1432888498266-38ffec3eaf0a",
    "https://images.unsplash.com/photo-1559136555-9303baea8ebd",
    "https://images.unsplash.com/photo-1504384308090-c894fdcc538d",
    "https://images.unsplash.com/photo-1519389950473-47ba0277781c",
    "https://images.unsplash.com/photo-1496171367470-9ed9a91ea931",
    "https://images.unsplash.com/photo-1483058712412-4245e9b90334",
    "https://images.unsplash.com/photo-1504639725590-34d0984388bd",
    "https://images.unsplash.com/photo-1633356122544-f134324a6cee",
    "https://images.unsplash.com/photo-1627398242454-45a1465c2479",
    "https://images.unsplash.com/photo-1593720213428-28a5b9e94613",
    "https://images.unsplash.com/photo-1571171637578-41bc2dd41cd2",
    "https://images.unsplash.com/photo-1550439062-609e1531270e",
    "https://images.unsplash.com/photo-1542744094-3a31f272c490",
    "https://images.unsplash.com/photo-1517245386807-bb43f82c33c4",
    "https://images.unsplash.com/photo-1522071820081-009f0129c71c",
    "https://images.unsplash.com/photo-1522199755839-a2bacb67c546",
    "https://images.unsplash.com/photo-1551434678-e076c223a692",
    "https://images.unsplash.com/photo-1573164713714-d95e436ab8d6",
    "https://images.unsplash.com/photo-1516321165247-4aa89a48be28",
    "https://images.unsplash.com/photo-1481487196290-ab5e5f0d0aa2",
    "https://images.unsplash.com/photo-1519389950473-47ba0277781c",
    "https://images.unsplash.com/photo-1460925895917-afdab827c52f",
    "https://images.unsplash.com/photo-1553877522-43269d4ea984",
    "https://images.unsplash.com/photo-1556155092-490a1ba16284",
    "https://images.unsplash.com/photo-1454165804606-c3d57bc86b40",
    "https://images.unsplash.com/photo-1542744173-8e7e53415bb0",
    "https://images.unsplash.com/photo-1531482615713-2afd69097998",
    "https://images.unsplash.com/photo-1600880292203-757bb62b4baf",
    "https://images.unsplash.com/photo-1522202176988-66273c2fd55f",
    "https://images.unsplash.com/photo-1552664730-d307ca884978",
    "https://images.unsplash.com/photo-1661956602119-0de8e45c0430",
    "https://images.unsplash.com/photo-1586717791821-3f44a563fa4c",
    "https://images.unsplash.com/photo-1517245386807-bb43f82c33c4",
    "https://images.unsplash.com/photo-1496171367470-9ed9a91ea931",
    "https://images.unsplash.com/photo-1483058712412-4245e9b90334",
    "https://images.unsplash.com/photo-1504384308090-c894fdcc538d",
    "https://images.unsplash.com/photo-1559136555-9303baea8ebd",
    "https://images.unsplash.com/photo-1432888498266-38ffec3eaf0a",
    "https://images.unsplash.com/photo-1556761175-5973dc0f32e7",
    "https://images.unsplash.com/photo-1516321318423-f06f85e504b3",
    "https://images.unsplash.com/photo-1499951360447-b19be8fe80f5",
    "https://images.unsplash.com/photo-1531403009284-440f080d1e12",
    "https://images.unsplash.com/photo-1581091226825-a6a2a5aee158",
    "https://images.unsplash.com/photo-1557804506-669a67965ba0",
    "https://images.unsplash.com/photo-1556761175-b413da4baf72",
    "https://images.unsplash.com/photo-1504868584819-f8e8b4b6d7e3",
    "https://images.unsplash.com/photo-1516321497487-e288fb19713f",
    "https://images.unsplash.com/photo-1460925895917-afdab827c52f",
]

# Dedupe while preserving order; drop logo / dead IDs.
_WEB_DESIGN_IMAGES = [
    u for u in dict.fromkeys(_WEB_DESIGN_IMAGES)
    if not _is_banned_stock_key(normalize_image_key(u))
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

# Clinic / medical — used when Industry = Healthcare (or medical keywords)
_HEALTHCARE_IMAGES = [
    "https://images.unsplash.com/photo-1576091160399-112ba8d25d1d",  # medical clinic
    "https://images.unsplash.com/photo-1576091160550-2173dba999ef",  # doctor at computer
    "https://images.unsplash.com/photo-1584820927498-cfe5211fd8bf",  # doctor
    "https://images.unsplash.com/photo-1631217868264-e5b90bb7e133",  # medical office
    "https://images.unsplash.com/photo-1516549655169-df83a0774514",  # hospital
    "https://images.unsplash.com/photo-1551076805-e1869033e561",  # hospital corridor
    "https://images.unsplash.com/photo-1666214280557-f1b5022eb634",  # clinician laptop
    "https://images.unsplash.com/photo-1579684385127-1ef15d508118",  # clinical care
]

# Back-compat alias used by pool helpers
_WEB_FAMILY_IMAGES = list(_WEB_DESIGN_IMAGES)

_CURATED_TOPIC_IMAGES = {
    "web design": list(_WEB_DESIGN_IMAGES),
    "website design": list(_WEB_DESIGN_IMAGES),
    "website designer": list(_WEB_DESIGN_IMAGES),
    "web development": list(_WEB_DESIGN_IMAGES),
    "wordpress": list(_WEB_DESIGN_IMAGES),
    "wix": list(_WEB_DESIGN_IMAGES),
    "shopify": list(_WEB_DESIGN_IMAGES),
    "squarespace": list(_WEB_DESIGN_IMAGES),
    "webflow": list(_WEB_DESIGN_IMAGES),
    "weebly": list(_WEB_DESIGN_IMAGES),
    "godaddy": list(_WEB_DESIGN_IMAGES),
    "framer": list(_WEB_DESIGN_IMAGES),
    "redirect": list(_WEB_DESIGN_IMAGES),
    "seo": list(_WEB_DESIGN_IMAGES),
    "mobile_app": list(_WEB_DESIGN_IMAGES),
    "mobile app": list(_WEB_DESIGN_IMAGES),
    "software": list(_SOFTWARE_IMAGES),
    "finance": list(_FINANCE_IMAGES),
    "banking": list(_FINANCE_IMAGES),
    "fintech": list(_FINANCE_IMAGES),
    "investment": list(_FINANCE_IMAGES),
    "healthcare": list(_HEALTHCARE_IMAGES),
    "medical": list(_HEALTHCARE_IMAGES),
    "clinic": list(_HEALTHCARE_IMAGES),
    "hospital": list(_HEALTHCARE_IMAGES),
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

# 301 / redirects / URL migration — topic articles must not fall back to generic offices
_REDIRECT_IMAGES = [
    "https://images.unsplash.com/photo-1461749280684-dccba630e2f6",  # code on screen
    "https://images.unsplash.com/photo-1498050108023-c5249f4df085",  # laptop code
    "https://images.unsplash.com/photo-1555066931-4365d14bab8c",  # IDE dark
    "https://images.unsplash.com/photo-1515879218367-8466d910aaa4",  # python/code
    "https://images.unsplash.com/photo-1555949963-aa79dcee981c",  # coding hands
    "https://images.unsplash.com/photo-1544197150-b99a580bb7a2",  # network / server
    "https://images.unsplash.com/photo-1558494949-ef010cbdcc31",  # server rack
    "https://images.unsplash.com/photo-1451187580459-43490279c0fa",  # digital / network globe
]

# Topic-specific search modifiers (generic "storefront" pulls wrong photos for web design).
_TOPIC_MODIFIERS = {
    "web design": ["ui mockup", "designer laptop", "website wireframe", "creative desk"],
    "website": ["ui mockup", "designer laptop", "website wireframe", "creative desk"],
    "web development": ["coding laptop", "developer desk", "html css", "app interface"],
    "wix": ["wix editor screen", "website builder dashboard", "drag drop website", "laptop website design"],
    "shopify": ["shopify dashboard", "ecommerce store laptop", "online store screen", "product page website"],
    "squarespace": ["website template editor", "portfolio website", "designer laptop", "website builder"],
    "webflow": ["web design tool", "ui designer laptop", "cms dashboard", "website mockup"],
    "wordpress": ["wordpress dashboard", "cms admin screen", "theme editor", "blog website"],
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
    "healthcare": ["clinic website", "doctor laptop", "hospital website", "medical office"],
    "medical": ["clinic website", "doctor laptop", "hospital website", "medical office"],
    "clinic": ["medical clinic", "doctor laptop", "hospital reception", "healthcare app"],
    "insurance": ["insurance office", "agent laptop", "policy documents", "insurance website"],
    "redirect": ["browser address bar", "website code", "server configuration", "http status"],
    "301": ["url redirect", "browser address bar", "htaccess file", "developer laptop"],
    "canonical": ["website code", "search console", "url structure", "developer laptop"],
}

# When Business Niche is web/software and Industry is a vertical, search these
# instead of generic UI mockups — e.g. Web Design + Healthcare → clinic website.
_WEB_VERTICAL_MODIFIERS = {
    "medical": ["clinic website", "doctor laptop", "hospital website", "healthcare app"],
    "finance": ["banking website", "finance dashboard", "investment app", "fintech laptop"],
    "legal": ["law firm website", "attorney laptop", "legal office computer", "law website"],
    "real estate": ["real estate website", "property listing laptop", "realtor computer", "home website"],
    "education": ["school website", "student laptop", "university website", "elearning ui"],
    "insurance": ["insurance website", "agent laptop", "policy dashboard", "insurance office"],
    "construction": ["construction contractor", "job site laptop", "blueprint desk", "contractor website"],
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

# Leftover tech niches that are NOT the service we sell (e.g. "software engineer"
# while Industry is Education). Do NOT treat WordPress / web design as stale —
# those are ZeOrbit services; Industry is the client vertical (healthcare, etc.).
_STALE_NICHE_RE = re.compile(
    r"\b(software\s*engineer|sotware|coding|developer|saas)\b",
    re.I,
)
_SERVICE_NICHE_RE = re.compile(
    r"\b(wordpress|web\s*design|website\s*design|website\s*designer|"
    r"landing\s*page|seo|ppc|mobile\s*app|e-?commerce)\b",
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
    # Industry = who we sell to. Niche = what ZeOrbit builds. Never replace
    # "Small Business WordPress Web Design" with "Healthcare".
    if bt and _SERVICE_NICHE_RE.search(bt):
        return bt

    bt_fam = topic_image_family(bt)
    ind_fam = topic_image_family(industry_niche)

    # Already aligned (e.g. niche "tutoring" + Education)
    if bt and bt_fam == ind_fam and bt_fam not in ("general",):
        return bt

    stale = (not bt) or bt_l in _STALE_DEFAULTS or bool(_STALE_NICHE_RE.search(bt))
    if stale or (bt_fam != ind_fam and bt_fam in ("software", "general")):
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
    if re.search(r"\b(301|302|redirect|htaccess|url redirect|canonical)\b", t):
        return list(_REDIRECT_IMAGES)
    # Exact / prefix family first so "finance software engineer" never steals
    # the software pool when the chosen topic is finance (and vice versa).
    fam = topic_image_family(t)
    family_pools = {
        "plumbing": _CURATED_TOPIC_IMAGES.get("plumbing", []),
        "hvac": _CURATED_TOPIC_IMAGES.get("hvac", []),
        "electrician": _CURATED_TOPIC_IMAGES.get("electrician", []),
        "finance": _FINANCE_IMAGES,
        "healthcare": _HEALTHCARE_IMAGES,
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
    if not raw or raw in ("other", "general", "services", "retail",
                          "professional services", "restaurants", "restaurant"):
        # Restaurants/Retail are niches — they must come from Business Niche, not Industry
        return ""
    if raw in ("contractors", "contractor", "construction", "remodel", "renovation"):
        return "construction"
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


def _related_stock_plan(
    focus_keyword: str,
    industry: str,
    location_words: set,
    niche: str = "",
) -> tuple:
    """Build an on-topic Unsplash/Pexels query from keyword + niche + industry.

    Web Design + Healthcare → "medical website" / clinic laptop, not generic UI mockups
    and not a hospital-only override that drops the website angle.
    """
    blob = f"{focus_keyword} {niche} {industry}".lower()
    if re.search(r"\b(301|302|redirect|htaccess|canonical url)\b", blob):
        topic = "website url redirect"
        mods = ["browser address bar", "developer laptop", "server configuration", "http code"]
        return topic, mods, topic

    visual = _resolve_visual_industry(industry)
    niche_clean = _clean_image_query(niche, exclude=location_words)
    kw_clean = (
        _clean_image_query(focus_keyword, exclude=location_words)
        or niche_clean
        or "business"
    )
    fam = topic_image_family(f"{niche} {focus_keyword} {kw_clean}")

    if visual and fam in ("web", "software", "marketing", "general"):
        mods = list(_WEB_VERTICAL_MODIFIERS.get(visual) or [visual, "professional", "laptop", "office"])
        if fam == "web":
            topic = f"{visual} website"
        elif fam == "software":
            topic = f"{visual} software"
            mods = [f"{visual} app", "dashboard", "developer laptop", visual]
        else:
            topic = f"{visual} {kw_clean}".strip()
        return topic, mods, visual

    topic = kw_clean
    modifiers = _IMAGE_QUERY_MODIFIERS
    search_blob = f"{topic} {industry} {focus_keyword} {niche}".lower()
    for key, mods in _TOPIC_MODIFIERS.items():
        if key in topic.lower() or key in search_blob:
            modifiers = mods
            break
    return topic, modifiers, topic


def _with_unsplash_params(url: str) -> str:
    if "images.unsplash.com" in url and "?" not in url:
        return f"{url}?w=1200&h=675&fit=crop&q=80"
    return url


def _all_curated_urls() -> List[str]:
    """Every curated Unsplash URL we ship — used when a niche pool is exhausted."""
    seen: List[str] = []
    keys = set()
    for pool in (_WEB_DESIGN_IMAGES, _SOFTWARE_IMAGES, _FINANCE_IMAGES, _HEALTHCARE_IMAGES, _GENERIC_CURATED):
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
    """Pick an on-topic curated Unsplash photo. Never returns random picsum placeholders.

    Never reuses a URL already in `exclude` — returns "" so callers can fetch a fresh
    Unsplash/Pexels hit instead of repeating the same photo across blog posts.
    """
    exclude_keys = {normalize_image_key(u) for u in (exclude or []) if u}

    def _pick(pool: List[str]) -> str:
        if not pool:
            return ""
        candidates = []
        for u in pool:
            key = normalize_image_key(u)
            if not key or _is_banned_stock_key(key):
                continue
            if key in exclude_keys:
                continue
            candidates.append(u)
        if not candidates:
            return ""
        candidates.sort(
            key=lambda u: hashlib.md5(f"{seed}|{normalize_image_key(u)}".encode("utf-8")).hexdigest()
        )
        return _with_unsplash_params(candidates[0])

    topic_pool = _curated_pool_for_topic(topic)
    fam = topic_image_family(topic)
    if fam == "healthcare":
        topic_pool = list(_HEALTHCARE_IMAGES)
    elif fam in ("dental", "legal", "fitness"):
        pass
    elif fam in ("web", "software", "general") and any(
        w in (topic or "").lower() for w in ("website", "web design", "wordpress", "shopify", "wix", "squarespace", "webflow", "laptop")
    ):
        topic_pool = list(_WEB_DESIGN_IMAGES)
    url = _pick(topic_pool)
    if url:
        return url
    # Expand on-topic before giving up (still honor exclude — never silently reuse).
    expanded = list(dict.fromkeys(list(topic_pool or []) + list(_WEB_DESIGN_IMAGES) + list(_SOFTWARE_IMAGES)))
    url = _pick(expanded)
    if url:
        return url
    return ""


_OFFTOPIC_STOCK_MARKERS = (
    "mountain", "mountains", "forest", "beach", "sunset", "sunrise", "ocean wave",
    "nature landscape", "scenic", "waterfall", "desert dune", "flower field",
    "wildlife", "snowy peak", "national park", "hiking trail", "autumn leaves",
    "hotel", "resort", "skyline", "tourist", "tourism", "boardwalk", "cruise",
    "landmark", "monument", "cathedral exterior", "museum exterior", "airport terminal",
    # ZeOrbit sells websites — reject common Unsplash false positives
    "camera", "dslr", "canon eos", "photo studio", "softbox", "tripod", "photographer",
    "classroom", "students at desk", "lecture hall", "chalkboard", "blackboard",
    "pipe wrench", "plumbing pipe", "restaurant kitchen food", "chef plating",
    "netflix", "facebook messenger", "messenger logo", "instagram logo",
    "tiktok logo", "whatsapp", "youtube logo", "social media icon",
    "app icon 3d", "3d logo",
)


def _stock_result_score(result: dict, query: str) -> int:
    """Score Unsplash/Pexels hits; 0 means reject (off-topic / scenery)."""
    tags = result.get("tags") or []
    tag_txt = " ".join(
        (t.get("title") if isinstance(t, dict) else str(t)) for t in tags
    )
    photo_blob = " ".join([
        str(result.get("alt_description") or result.get("alt") or ""),
        str(result.get("description") or ""),
        str(result.get("title") or ""),
        tag_txt,
    ]).lower()
    blob = f"{photo_blob} {(query or '')}".lower()
    q = (query or "").lower()
    # Never pick consumer-app logos for web-design / local-business pages.
    if any(m in photo_blob for m in (
        "netflix", "facebook", "messenger", "instagram", "tiktok", "whatsapp",
        "snapchat", "youtube logo", "social media icon",
    )) and not any(x in q for x in ("facebook ads", "instagram marketing", "social media marketing")):
        return 0
    wants_photo = any(x in q for x in ("photograph", "photographer", "camera"))
    wants_edu = any(x in q for x in ("school", "classroom", "tutor", "university"))
    # Hard reject camera / classroom stock unless the query explicitly asks for it.
    if not wants_photo and any(m in photo_blob for m in (
        "camera", "dslr", "photo studio", "softbox", "photographer with camera", "canon ",
        "nikon ", "lens cap", "eos rebel",
    )):
        return 0
    if not wants_edu and any(m in photo_blob for m in (
        "classroom", "students sitting", "lecture hall", "school children",
    )):
        return 0
    if any(m in photo_blob for m in _OFFTOPIC_STOCK_MARKERS):
        # Allow only if the PHOTO (not the search query) is clearly on-topic
        if not any(k in photo_blob for k in (
            "website", "laptop", "computer", "code", "design", "ui", "ux",
            "office desk", "developer", "wordpress", "shopify", "mockup", "web design",
            "responsive", "browser", "doctor", "clinic", "hospital", "patient", "medical",
        )):
            return 0
    # Prefer website-related hits only when the search is actually about websites.
    wants_web = any(k in q for k in ("website", "web design", "wordpress", "shopify", "wix", "webflow"))
    web_ok = any(k in blob for k in (
        "website", "web design", "laptop", "computer", "code", "ui", "ux",
        "mockup", "wordpress", "shopify", "browser", "developer", "designer",
    ))
    if wants_web and not web_ok:
        return 0
    web_bonus = 2 if (wants_web and web_ok) else 0
    words = [w for w in re.findall(r"[a-zA-Z]+", (query or "").lower()) if len(w) > 2]
    if not words:
        return 1 + web_bonus
    hits = sum(1 for w in words if w in photo_blob or w in blob)
    if len(words) >= 2 and hits == 0:
        return 0
    if len(words) == 1 and words[0] not in photo_blob and words[0] not in blob:
        return max(0, web_bonus)
    return hits + web_bonus + (2 if hits >= min(2, len(words)) else 0)


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
) -> Tuple[str, str]:
    """Return (url, photographer_alt) from Unsplash/Pexels, or curated URL + empty alt."""
    exclude_keys = {normalize_image_key(u) for u in (exclude or []) if u}
    search = query
    page0 = (_stable_index(f"{seed}|{len(exclude_keys)}", 40) + 1)
    pages = [page0, (page0 % 40) + 1, ((page0 + 7) % 40) + 1, ((page0 + 19) % 40) + 1]
    if settings.UNSPLASH_ACCESS_KEY:
        try:
            async with httpx.AsyncClient(timeout=12) as client:
                for page in pages:
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
                    if resp.status_code != 200:
                        continue
                    results = resp.json().get("results", [])
                    scored = []
                    for r in results:
                        url = (r.get("urls") or {}).get("regular") or (r.get("urls") or {}).get("full") or ""
                        if not url or normalize_image_key(url) in exclude_keys:
                            continue
                        if _is_banned_stock_key(normalize_image_key(url)):
                            continue
                        score = _stock_result_score(r, search)
                        if score <= 0:
                            continue
                        alt = (r.get("alt_description") or r.get("description") or "") or ""
                        scored.append((score, url, alt))
                    if scored:
                        scored.sort(key=lambda x: (-x[0], x[1]))
                        pick = scored[_stable_index(seed, len(scored))]
                        return pick[1], pick[2]
        except Exception as e:
            print(f"[Image] Unsplash search error: {e}")
    if settings.PEXELS_API_KEY:
        try:
            async with httpx.AsyncClient(timeout=12) as client:
                for page in pages:
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
                    if resp.status_code != 200:
                        continue
                    photos = resp.json().get("photos", [])
                    scored = []
                    for p in photos:
                        src = (p.get("src") or {})
                        cand = src.get("original") or src.get("large2x") or src.get("large") or ""
                        if not cand or normalize_image_key(cand) in exclude_keys:
                            continue
                        if _is_banned_stock_key(normalize_image_key(cand)):
                            continue
                        alt = p.get("alt") or ""
                        score = _stock_result_score(
                            {"alt_description": alt, "description": ""},
                            search,
                        )
                        if score <= 0:
                            continue
                        scored.append((score, cand, alt))
                    if scored:
                        scored.sort(key=lambda x: (-x[0], x[1]))
                        pick = scored[_stable_index(seed, len(scored))]
                        return pick[1], pick[2]
        except Exception as e:
            print(f"[Image] Pexels search error: {e}")

    return _curated_image_url(query, seed, exclude=exclude_keys), ""


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
    niche: str = "",
    search_intent: str = "",
    image_concept_text: str = "",
    keyword_index: int = 0,
    content_type: str = "service",
    match_query: str = "",
    audience: str = "",
    image_keyword: str = "",
) -> List[ImageAsset]:
    """Generate 1 featured + (count-1) in-content images with full SEO metadata.

    Photos must match LOCATION + INDUSTRY + SERVICE + PROBLEM + INTENT — never
    tourism/hotel/beach scenery just because a city name appears.

    Blog posts (`content_type=blog`): visuals follow the search query category
    (e.g. Wix for "how to fix the wix website"), not generic WordPress/Shopify.

    `exclude_urls` prevents reusing photos already assigned in the same batch.
    """
    count = max(1, min(count, 3))
    assets: List[ImageAsset] = []
    location_words = {
        w for w in re.findall(r"[a-zA-Z]+", (location or "").lower()) if len(w) > 2
    }
    is_blog = (content_type or "").lower() in ("blog", "post")
    seed_query = (image_keyword or match_query or focus_keyword or niche or industry or "").strip()
    plan = blog_image_plan(seed_query, niche=f"{niche or ''} {industry or ''}")
    topic = plan["topic"]
    modifiers = list(plan["modifiers"] or [])
    fallback_topic = plan["category"]
    visual_fam = topic_image_family(f"{seed_query} {industry or ''} {niche or ''}")
    if visual_fam == "healthcare":
        topic = plan["topic"] if plan.get("category") == "healthcare" else "doctor clinic medical office"
        modifiers = [
            "doctor with patient",
            "medical clinic reception",
            "physician laptop clinic",
            "healthcare office",
        ]
        fallback_topic = "healthcare"
    if image_concept_text and "working title" not in image_concept_text.lower():
        concept_for_meta = image_concept_text
    else:
        concept_for_meta = plan["concept"]
    clean_focus = plan.get("focus") or plan["category"] or focus_keyword or "website design"
    print(
        f"[Image] keyword-plan category={plan['category']} label={plan.get('label')} "
        f"query={seed_query[:80]!r} kind={content_type} family={visual_fam}"
    )

    # Featured must not reuse another page's header. Body/footer only need to be
    # unique *within this article* — excluding the whole library here left later
    # pages with a single image once the pool was exhausted.
    featured_taken: Set[str] = {normalize_image_key(u) for u in (exclude_urls or []) if u}
    used: Set[str] = set()
    if visual_fam == "healthcare":
        web_only_pool = list(dict.fromkeys(list(_HEALTHCARE_IMAGES) + list(_WEB_DESIGN_IMAGES)))
        prefer_hosted = False
    else:
        web_only_pool = list(dict.fromkeys(
            list(_WEB_DESIGN_IMAGES) + list(_SOFTWARE_IMAGES) + list(_GENERIC_CURATED) + list(_all_curated_urls())
        ))
        prefer_hosted = bool(settings.UNSPLASH_ACCESS_KEY or settings.PEXELS_API_KEY)

    for i in range(count):
        pick_exclude: Set[str] = set(used) | featured_taken
        is_featured = i == 0
        modifier = modifiers[i % len(modifiers)]
        query = f"{topic} {modifier}".strip()
        # Location is required in the seed so Austin vs Driftwood never collide.
        seed = (
            f"{topic}|{location}|{'blog-' + (match_query or focus_keyword or '')[:40] if is_blog else 'website-design'}|{i}|{angle_title}|"
            f"{search_intent}|{keyword_index}|{(concept_for_meta or '')[:80]}|"
            f"loc-{(location or '').strip().lower()}|{(audience or '')[:40]}|{(industry or '')[:40]}"
        )
        url = ""
        key = ""
        photo_alt = ""
        if prefer_hosted:
            hosted, hosted_alt = await _hosted_image_url(query, seed=seed, exclude=pick_exclude, location="")
            hkey = normalize_image_key(hosted)
            if hosted and hkey and hkey not in pick_exclude and not _is_banned_stock_key(hkey) and not _looks_like_camera_photo(hosted, hosted_alt):
                url, key, photo_alt = hosted, hkey, hosted_alt
        if not url:
            url = _curated_image_url(
                fallback_topic,
                seed=seed,
                exclude=pick_exclude,
            )
            key = normalize_image_key(url)
            photo_alt = ""
        if (not url or key in pick_exclude) and (settings.UNSPLASH_ACCESS_KEY or settings.PEXELS_API_KEY):
            hosted, hosted_alt = await _hosted_image_url(query, seed=seed, exclude=pick_exclude, location="")
            hkey = normalize_image_key(hosted)
            if hosted and hkey and hkey not in pick_exclude and not _is_banned_stock_key(hkey) and not _looks_like_camera_photo(hosted, hosted_alt):
                url, key, photo_alt = hosted, hkey, hosted_alt
        if key and key in pick_exclude:
            for attempt in range(16):
                alt_seed = f"{seed}|retry|{attempt}|{keyword_index}"
                alt = _curated_image_url(
                    fallback_topic,
                    seed=alt_seed,
                    exclude=pick_exclude,
                )
                alt_key = normalize_image_key(alt)
                if alt_key and alt_key not in pick_exclude:
                    url, key = alt, alt_key
                    photo_alt = ""
                    break
                if settings.UNSPLASH_ACCESS_KEY or settings.PEXELS_API_KEY:
                    hosted, hosted_alt = await _hosted_image_url(
                        f"{topic} {modifiers[(i + attempt) % len(modifiers)]}",
                        seed=alt_seed,
                        exclude=pick_exclude,
                        location="",
                    )
                    hkey = normalize_image_key(hosted)
                    if hosted and hkey and hkey not in pick_exclude and not _is_banned_stock_key(hkey) and not _looks_like_camera_photo(hosted, hosted_alt):
                        url, key, photo_alt = hosted, hkey, hosted_alt
                        break
        # Still colliding — rotate unused website pool first (unique within this article)
        if (not url) or (key and key in pick_exclude):
            picked = False
            for u in web_only_pool:
                uk = normalize_image_key(u)
                if uk and uk not in used and uk not in featured_taken and not _is_banned_stock_key(uk):
                    url, key = _with_unsplash_params(u), uk
                    picked = True
                    break
            if not picked:
                url, key = "", ""
        if not url:
            unused = [
                u for u in web_only_pool
                if normalize_image_key(u) not in used
                and normalize_image_key(u) not in featured_taken
                and not _is_banned_stock_key(normalize_image_key(u))
            ]
            if unused:
                url = _with_unsplash_params(unused[(keyword_index + i) % len(unused)])
                key = normalize_image_key(url)
            else:
                hosted, hosted_alt = await _hosted_image_url(
                    f"{query} workspace {keyword_index}-{i}",
                    seed=f"{seed}|exhausted|{keyword_index}|{i}",
                    exclude=used,
                    location="",
                )
                hkey = normalize_image_key(hosted)
                if hosted and hkey and hkey not in used and not _is_banned_stock_key(hkey) and not _looks_like_camera_photo(hosted, hosted_alt):
                    url, key, photo_alt = hosted, hkey, hosted_alt
                else:
                    # Last resort: any unused curated photo so we still ship 3 images
                    for u in web_only_pool:
                        uk = normalize_image_key(u)
                        if uk and uk not in used and uk not in featured_taken and not _is_banned_stock_key(uk):
                            url, key = _with_unsplash_params(u), uk
                            break
                    if not url:
                        continue
        if key:
            used.add(key)
        if i == 0:
            print(f"[Image] related stock: {query} → {(url or '')[:80]}")
        if url and "picsum.photos" in url:
            url = _curated_image_url("website design", seed=f"{seed}|nopicsum", exclude=used)
            if not url:
                url = _with_unsplash_params(_WEB_DESIGN_IMAGES[(keyword_index + i) % len(_WEB_DESIGN_IMAGES)])
            key = normalize_image_key(url)
            if key:
                used.add(key)
        meta = build_image_metadata(
            clean_focus, location, business_name, len(assets), is_featured=(len(assets) == 0),
            image_concept_text=concept_for_meta if concept_for_meta and "working title" not in (concept_for_meta or "").lower() else "",
            industry="" if is_blog else "",
            photo_alt=photo_alt,
            slot_hint=modifier,
        )
        assets.append(ImageAsset(
            url=url,
            filename=meta["filename"],
            mime_type="image/webp",
            alt_text=meta["alt_text"],
            title=meta["title"],
            caption=meta["caption"],
            description=meta["description"],
            is_featured=(len(assets) == 0),
        ))
    # Drop any empty-URL accidents, then guarantee ≥1 real image
    assets = [a for a in assets if (a.url or "").strip()]
    # Always ship header + footer + body (3). Never leave a page with a single photo.
    pool_for_pad = list(dict.fromkeys(
        list(_WEB_DESIGN_IMAGES) + list(_SOFTWARE_IMAGES) + list(_GENERIC_CURATED) + list(_all_curated_urls())
    ))
    while len(assets) < count:
        next_url = ""
        for u in pool_for_pad:
            uk = normalize_image_key(u)
            if uk and uk not in used and not _is_banned_stock_key(uk):
                next_url = _with_unsplash_params(u)
                used.add(uk)
                break
        if not next_url:
            break
        meta = build_image_metadata(
            clean_focus, location, business_name, len(assets), is_featured=(len(assets) == 0),
            image_concept_text=concept_for_meta if concept_for_meta and "working title" not in (concept_for_meta or "").lower() else "",
            industry="" if is_blog else "",
            photo_alt="",
            slot_hint=modifiers[len(assets) % len(modifiers)],
        )
        assets.append(ImageAsset(
            url=next_url,
            filename=meta["filename"],
            mime_type="image/webp",
            alt_text=meta["alt_text"],
            title=meta["title"],
            caption=meta["caption"],
            description=meta["description"],
            is_featured=(len(assets) == 0),
        ))
    if not assets:
        url = _with_unsplash_params(_WEB_DESIGN_IMAGES[keyword_index % len(_WEB_DESIGN_IMAGES)])
        meta = build_image_metadata("website design", location, business_name, 0, True, image_concept_text="", industry="")
        assets.append(ImageAsset(
            url=url, filename=meta["filename"], mime_type="image/webp",
            alt_text=meta["alt_text"], title=meta["title"], caption=meta["caption"],
            description=meta["description"], is_featured=True,
        ))
        print(f"[Image] forced fallback featured for {location or focus_keyword}")
    return assets


def collect_image_urls_from_seo_block(block: dict) -> List[str]:
    """All image URLs stored on a page/blog SEO block."""
    out: List[str] = []
    if not isinstance(block, dict):
        return out
    for key in ("featured_image_url", "footer_image_url"):
        u = block.get(key) or ""
        if u:
            out.append(u)
    for im in block.get("in_content_images") or []:
        if isinstance(im, dict) and im.get("url"):
            out.append(im["url"])
        elif hasattr(im, "url") and im.url:
            out.append(im.url)
    return out


async def reassign_unique_featured_images(rows: Iterable, used: Optional[List[str]] = None) -> int:
    """Re-pick featured (+ in-content) images so no two pages share the same photo key.

    Mutates row.seo_block in place; caller commits the session. Returns update count.
    """
    used_list: List[str] = list(used or [])
    used_keys: Set[str] = {normalize_image_key(u) for u in used_list if u}
    updated = 0
    # First pass: register unique featured keys already in use (keep first owner)
    owners: dict = {}
    ordered = list(rows)
    for r in ordered:
        b = r.seo_block if isinstance(r.seo_block, dict) else {}
        feat = (b or {}).get("featured_image_url") or ""
        key = normalize_image_key(feat)
        if key and key not in owners:
            owners[key] = r
            used_keys.add(key)
            used_list.append(feat)

    for r in ordered:
        b = r.seo_block if isinstance(r.seo_block, dict) else {}
        if not isinstance(b, dict):
            continue
        feat = b.get("featured_image_url") or ""
        key = normalize_image_key(feat)
        # Keep the first page that claimed this photo; refresh duplicates + missing
        if key and owners.get(key) is r and not stock_url_needs_replace(feat):
            continue
        exclude = list(used_list)
        focus = b.get("focus_keyword") or r.business_type or "website design"
        loc = f"{getattr(r, 'city', '') or ''}, {getattr(r, 'state', '') or ''}".strip(", ")
        industry = b.get("industry") or ""
        imgs = await generate_article_images(
            "website design wordpress shopify" if topic_image_family(str(focus)) in ("web", "general", "software") and not (b.get("image_keyword") or "").strip() else (b.get("image_keyword") or focus),
            loc,
            "ZeOrbit",
            count=3,
            exclude_urls=exclude,
            industry=industry if (b.get("content_type") or "") not in ("blog", "post") else "",
            niche=str(focus),
            search_intent=b.get("search_intent") or "",
            image_concept_text=b.get("image_concept") or "",
            keyword_index=updated,
            content_type=b.get("content_type") or "",
            match_query=(b.get("image_keyword") or "").strip() or str(focus),
            image_keyword=(b.get("image_keyword") or "").strip(),
        )
        if not imgs:
            continue
        feat2, foot2, cleaned = assign_canonical_images(imgs)
        if not feat2:
            continue
        payload = dict(b)
        payload["featured_image_url"] = feat2
        payload["footer_image_url"] = foot2
        payload["in_content_images"] = [
            im.model_dump() if hasattr(im, "model_dump") else im for im in cleaned
        ]
        r.seo_block = payload
        try:
            from sqlalchemy.orm.attributes import flag_modified
            flag_modified(r, "seo_block")
        except Exception:
            pass
        used_list.append(feat2)
        used_keys.add(normalize_image_key(feat2))
        for im in cleaned:
            if getattr(im, "url", None):
                used_list.append(im.url)
        updated += 1
    return updated


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
