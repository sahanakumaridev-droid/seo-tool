"""
image_service.py
Fetches relevant images from Unsplash/Pexels (free) or generates via DALL-E 3.
Converts to WebP, generates full SEO metadata (filename, alt, title, caption,
description), and uploads to the WordPress media library.
"""
import base64
import io
import re
import httpx
from typing import Optional, Tuple, List
from config import settings
from models.schemas import ImageAsset


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


async def _hosted_image_url(query: str, seed: str) -> str:
    """Return a hosted image URL for preview. Prefers Unsplash/Pexels; falls back to picsum seed."""
    # Reuse the fetch helpers only to discover a URL is not exposed by them (they return bytes),
    # so hit the search APIs directly for a URL when keys exist.
    if settings.UNSPLASH_ACCESS_KEY:
        try:
            async with httpx.AsyncClient(timeout=12) as client:
                resp = await client.get(
                    "https://api.unsplash.com/search/photos",
                    params={"query": query, "per_page": 5, "orientation": "landscape"},
                    headers={"Authorization": f"Client-ID {settings.UNSPLASH_ACCESS_KEY}"},
                )
                if resp.status_code == 200:
                    results = resp.json().get("results", [])
                    if results:
                        pick = results[abs(hash(seed)) % len(results)]
                        return pick["urls"]["regular"]
        except Exception as e:
            print(f"[Image] Unsplash search error: {e}")
    if settings.PEXELS_API_KEY:
        try:
            async with httpx.AsyncClient(timeout=12) as client:
                resp = await client.get(
                    "https://api.pexels.com/v1/search",
                    params={"query": query, "per_page": 5, "orientation": "landscape"},
                    headers={"Authorization": settings.PEXELS_API_KEY},
                )
                if resp.status_code == 200:
                    photos = resp.json().get("photos", [])
                    if photos:
                        pick = photos[abs(hash(seed)) % len(photos)]
                        return pick["src"]["large2x"]
        except Exception as e:
            print(f"[Image] Pexels search error: {e}")
    # Deterministic, always-available fallback so previews still render.
    return f"https://picsum.photos/seed/{_slug(seed) or 'seo'}/1200/675"


async def generate_article_images(
    focus_keyword: str,
    location: str,
    business_name: str = "",
    count: int = 3,
) -> List[ImageAsset]:
    """Generate 1 featured + (count-1) in-content images with full SEO metadata.

    Each ImageAsset carries a hosted preview `url` plus WebP filename and
    alt/title/caption/description. WebP byte-conversion happens at WP upload time.
    """
    count = max(1, min(count, 3))
    assets: List[ImageAsset] = []
    base_query = f"{focus_keyword} {location}".strip()
    angle_terms = ["professional", "team at work", "detail closeup"]

    for i in range(count):
        is_featured = i == 0
        query = f"{base_query} {angle_terms[i % len(angle_terms)]}".strip()
        url = await _hosted_image_url(query, seed=f"{base_query}-{i}")
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
