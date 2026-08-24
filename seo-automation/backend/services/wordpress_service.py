"""
wordpress_service.py
Auto-publishes SEO pages to WordPress via REST API.
Supports RankMath, All in One SEO (AIOSEO), and Yoast SEO meta fields.
Features: featured image upload, categories, tags, scheduled publishing, duplicate detection.
"""
import base64
import json
import re
import httpx
from typing import Optional
from models.schemas import SEOBlock, WordPressConfig, PublishResult
from services.image_service import (
    get_image_for_content, upload_image_to_wordpress,
    fetch_image_bytes, natural_place_caption,
)


_INSTRUCTION_LEAK_MARKERS = (
    "focus each page on the specific",
    "make every page feel unique",
    "custom content requirements",
    "honor every point",
    "avoid generic or repetitive",
    "keep the content simple, credible",
    "show how zeorbit can help with seo-",
    "these should be treated only as ai",
    "never appear as visible content",
)


def _looks_like_instruction_leak(text: str) -> bool:
    t = (text or "").strip().lower()
    if not t:
        return False
    return any(m in t for m in _INSTRUCTION_LEAK_MARKERS)


def _clean_caption(caption: str, fallback_alt: str = "") -> str:
    """Title-case / dedupe mashed keyword captions at render time."""
    raw = (caption or "").strip().rstrip(".")
    if not raw or _looks_like_instruction_leak(raw):
        raw = (fallback_alt or "").strip()
    if not raw:
        return ""
    # Drop trailing "— detail N"
    raw = re.sub(r"\s*[—-]\s*detail\s*\d+\s*$", "", raw, flags=re.I).strip()
    # Collapse duplicate adjacent phrases ("design Website Redesign")
    words = raw.split()
    cleaned = []
    prev_l = ""
    for w in words:
        wl = w.lower()
        if wl == prev_l:
            continue
        # Skip if this word already appeared in the last 3 tokens (mash)
        recent = {x.lower() for x in cleaned[-3:]}
        if wl in recent and wl in {"website", "design", "wordpress", "redesign"}:
            # allow WordPress once; skip second "website"/"design" mash
            if wl in {"website", "design"} and any(
                x.lower() in {"website", "design", "redesign"} for x in cleaned
            ):
                continue
        cleaned.append(w)
        prev_l = wl
    phrase = " ".join(cleaned).strip(" ,.-")
    if not phrase:
        return ""
    # Prefer natural_place_caption when location-like " in City" is present
    if re.search(r"\bin\s+\w+", phrase, re.I):
        m = re.search(r"^(.*?)\s+in\s+(.+)$", phrase, re.I)
        if m:
            phrase = natural_place_caption(m.group(1), m.group(2))
    # Title-ish casing for brands
    parts = []
    for i, w in enumerate(phrase.split()):
        low = w.lower()
        if low == "wordpress":
            parts.append("WordPress")
        elif low in {"seo", "ai"}:
            parts.append(low.upper())
        elif i and low in {"in", "for", "of", "and", "a", "the", "to", "on"}:
            parts.append(low)
        else:
            # Preserve contractions without forcing mid-word caps (don't → Don't)
            if "'" in w or "’" in w:
                parts.append(w[:1].upper() + w[1:].lower() if w else w)
            else:
                parts.append(w[:1].upper() + w[1:] if w else w)
    out = " ".join(parts).rstrip(" .?!") + "."
    return out


def _para_to_html(para: str) -> str:
    para = (para or "").strip()
    if not para or _looks_like_instruction_leak(para):
        return ""
    # Never render leftover markdown headings as body copy
    if re.match(r"^#{1,6}\s+", para):
        return ""
    if "•" in para or para.strip().startswith("1."):
        lines = para.split("\n")
        html_lines = []
        in_list = False
        for line in lines:
            line = line.strip()
            if not line or _looks_like_instruction_leak(line):
                continue
            if re.match(r"^#{1,6}\s+", line):
                continue
            if line.startswith("•") or (len(line) > 2 and line[0].isdigit() and line[1] == "."):
                if not in_list:
                    html_lines.append("<ul>")
                    in_list = True
                item = line.lstrip("•").lstrip("0123456789.").strip()
                html_lines.append(f"<li>{item}</li>")
            else:
                if in_list:
                    html_lines.append("</ul>")
                    in_list = False
                html_lines.append(f"<p>{line}</p>")
        if in_list:
            html_lines.append("</ul>")
        return "\n".join(html_lines)
    # Multi-paragraph blob under one H2
    chunks = [p.strip() for p in re.split(r"\n{2,}", para) if p.strip()]
    out = []
    for chunk in chunks:
        if _looks_like_instruction_leak(chunk) or re.match(r"^#{1,6}\s+", chunk):
            continue
        out.append(f"<p>{chunk}</p>")
    return "\n".join(out)


def _sections_aligned_to_h2s(content: str, h2s: list) -> list[str]:
    """Map body copy onto each H2. Handles ## markdown sections correctly."""
    heads = [str(h).strip() for h in (h2s or []) if str(h).strip()]
    text = (content or "").strip()
    if not heads:
        return []

    mapped: dict[str, str] = {}
    if re.search(r"(?m)^##\s+", text):
        parts = re.split(r"(?m)^##\s+", text)
        for part in parts[1:]:
            nl = part.find("\n")
            if nl == -1:
                heading, body = part.strip(), ""
            else:
                heading, body = part[:nl].strip(), part[nl:].strip()
            body = re.sub(r"(?m)^#{1,6}\s+.+$", "", body).strip()
            body = "\n\n".join(
                p for p in re.split(r"\n{2,}", body)
                if p.strip() and not _looks_like_instruction_leak(p)
            )
            if heading:
                mapped[heading.lower()] = body

        out = []
        used_keys = set()
        for h in heads:
            key = h.lower()
            body = mapped.get(key, "")
            if not body:
                for k, v in mapped.items():
                    if k in used_keys:
                        continue
                    if key in k or k in key:
                        body = v
                        used_keys.add(k)
                        break
            else:
                used_keys.add(key)
            out.append(body)
        # Fill empty slots from unused markdown bodies
        unused = [v for k, v in mapped.items() if k not in used_keys and v]
        ui = 0
        for i, body in enumerate(out):
            if not body and ui < len(unused):
                out[i] = unused[ui]
                ui += 1
        return out

    paras = [
        p.strip()
        for p in re.split(r"\n{2,}", text)
        if p.strip()
        and not re.match(r"^#{1,6}\s+", p.strip())
        and not _looks_like_instruction_leak(p)
    ]
    n = len(heads)
    chunks: list[str] = [""] * n
    idx = 0
    for i in range(n):
        remaining_h = n - i
        remaining_p = len(paras) - idx
        if remaining_p <= 0:
            break
        take = remaining_p if i == n - 1 else max(1, remaining_p // remaining_h)
        chunks[i] = "\n\n".join(paras[idx: idx + take])
        idx += take
    return chunks


def _fallback_section_copy(h2: str) -> str:
    h = (h2 or "This topic").strip()
    return (
        f"{h} matters when someone lands on your site and needs a clear answer fast. "
        f"ZeOrbit builds WordPress pages that explain the offer in plain language, "
        f"show proof, and make the next step obvious — contact, call, or book — "
        f"without stuffing keywords or repeating the same template on every page."
    )


def _figure_html(img) -> str:
    """Render an in-content image as a semantic <figure> with caption."""
    url = img.url if hasattr(img, "url") else (img or {}).get("url", "")
    alt = img.alt_text if hasattr(img, "alt_text") else (img or {}).get("alt_text", "")
    title = img.title if hasattr(img, "title") else (img or {}).get("title", "")
    caption = img.caption if hasattr(img, "caption") else (img or {}).get("caption", "")
    if not url:
        return ""
    # Prefer stable https Unsplash/Pexels URLs; skip obviously broken blanks
    cap = _clean_caption(caption, fallback_alt=alt)
    alt_clean = _clean_caption(alt, fallback_alt=title).rstrip(".")
    title_clean = _clean_caption(title, fallback_alt=alt_clean).rstrip(".")
    fig = (
        f'<figure class="wp-block-image">'
        f'<img src="{url}" alt="{alt_clean}" title="{title_clean}" loading="lazy" '
        f'onerror="this.closest(\'figure\').style.display=\'none\'" />'
    )
    if cap:
        fig += f"<figcaption>{cap}</figcaption>"
    fig += "</figure>"
    return fig


def _img_url(img) -> str:
    if not img:
        return ""
    if hasattr(img, "url"):
        return (img.url or "").split("?")[0]
    if isinstance(img, dict):
        return (img.get("url") or "").split("?")[0]
    return ""


def _img_is_featured(img) -> bool:
    if hasattr(img, "is_featured"):
        return bool(img.is_featured)
    if isinstance(img, dict):
        return bool(img.get("is_featured"))
    return False


def _build_content_html(block: SEOBlock) -> str:
    """Build full WordPress-ready HTML content from SEOBlock."""
    parts = []

    if block.intro:
        parts.append(f'<p class="seo-intro">{block.intro}</p>')

    # In-content images only — never re-show the hero/featured photo in the body.
    featured_key = (block.featured_image_url or "").split("?")[0]
    in_content_imgs = []
    seen = {featured_key} if featured_key else set()
    for img in (block.in_content_images or []):
        if _img_is_featured(img):
            continue
        key = _img_url(img)
        if not key or key in seen:
            continue
        seen.add(key)
        in_content_imgs.append(img)

    img_positions = {}
    if in_content_imgs and block.h2s:
        step = max(1, len(block.h2s) // (len(in_content_imgs) + 1))
        for n, img in enumerate(in_content_imgs):
            # Spread images across distinct H2 slots (avoid overwriting the same index).
            pos = min((n + 1) * step, len(block.h2s) - 1)
            while pos in img_positions and pos < len(block.h2s) - 1:
                pos += 1
            if pos not in img_positions:
                img_positions[pos] = img

    section_bodies = _sections_aligned_to_h2s(block.content or "", block.h2s or [])

    # One mid-article CALL NOW + one near the end — not after every section
    call_btn = (
        '<div class="call-now-wrap">'
        '<a class="call-now-btn" href="tel:6197249517">CALL NOW : 619-724-9517</a>'
        '</div>'
    )
    n_h2 = len(block.h2s or [])
    mid_cta_at = max(1, (n_h2 // 2) - 1) if n_h2 >= 3 else -1

    for i, h2 in enumerate(block.h2s or []):
        parts.append(f'<h2>{h2}</h2>')
        if i in img_positions:
            fig = _figure_html(img_positions[i])
            if fig:
                parts.append(fig)
        body = section_bodies[i] if i < len(section_bodies) else ""
        html = _para_to_html(body) if body else ""
        plain = re.sub(r"<[^>]+>", " ", html or "")
        plain = re.sub(r"\s+", " ", plain).strip()
        if not html or len(plain.split()) < 25:
            extra = _para_to_html(_fallback_section_copy(h2))
            html = f"{html}\n{extra}".strip() if html else extra
        if html:
            parts.append(html)
        if i == mid_cta_at:
            parts.append(call_btn)

    if n_h2 >= 2:
        parts.append(call_btn)

    if block.h3s:
        # These are short trust/benefit statements ("Fast Turnaround for
        # {city} Clients", "Transparent Pricing — No Hidden Fees"), not
        # headings with their own body copy — render as a badge row instead
        # of bare <h3> tags with nothing under them.
        check_icon = (
            '<svg width="14" height="14" viewBox="0 0 24 24" fill="none">'
            '<path d="M20 6L9 17l-5-5" stroke="currentColor" stroke-width="2.5" '
            'stroke-linecap="round" stroke-linejoin="round"/></svg>'
        )
        badges = "".join(
            f'<span class="trust-badge">{check_icon}<span>{h3}</span></span>'
            for h3 in block.h3s[:4]
        )
        parts.append(
            '<section class="trust-section" aria-label="Why choose us">'
            '<div class="trust-kicker">Why businesses choose us</div>'
            f'<div class="trust-badges">{badges}</div>'
            '</section>'
        )

    if block.faqs:
        parts.append('<section class="faq-wrap" aria-labelledby="faq-heading">')
        parts.append('<h2 id="faq-heading">Frequently Asked Questions</h2>')
        parts.append('<p class="faq-lead">Clear answers to the questions local buyers ask most.</p>')
        parts.append('<div class="faq-section" itemscope itemtype="https://schema.org/FAQPage">')
        for i, faq in enumerate(block.faqs):
            parts.append(
                f'<details class="faq-item"{" open" if i == 0 else ""} '
                f'itemscope itemprop="mainEntity" itemtype="https://schema.org/Question">'
                f'<summary itemprop="name">{faq.question}</summary>'
                f'<div itemscope itemprop="acceptedAnswer" itemtype="https://schema.org/Answer">'
                f'<p itemprop="text">{faq.answer}</p>'
                f'</div></details>'
            )
        parts.append('</div></section>')

    # Soft end-note only — primary conversion lives in the contact band below.
    if block.cta:
        parts.append(f'<p class="end-note">{block.cta}</p>')

    schema = block.schema_markup
    if schema:
        for key, val in schema.items():
            parts.append(
                f'<script type="application/ld+json">\n{json.dumps(val, indent=2)}\n</script>'
            )

    return '\n'.join(parts)


def _build_seo_meta(block: SEOBlock, plugin: str) -> dict:
    """Build SEO plugin meta fields for RankMath, AIOSEO, or Yoast."""
    focus_kw = block.keywords.primary
    secondary_kws = ', '.join(block.keywords.secondary[:5])

    if plugin == "rankmath":
        return {
            "rank_math_title": block.title,
            "rank_math_description": block.meta_description,
            "rank_math_focus_keyword": focus_kw,
            "rank_math_secondary_focus_keyword": secondary_kws,
            "rank_math_robots": ["index", "follow"],
            "rank_math_canonical_url": "",
            "rank_math_og_title": block.title,
            "rank_math_og_description": block.meta_description,
        }
    elif plugin == "aioseo":
        return {
            "_aioseo_title": block.title,
            "_aioseo_description": block.meta_description,
            "_aioseo_keywords": focus_kw,
            "_aioseo_og_title": block.title,
            "_aioseo_og_description": block.meta_description,
        }
    else:  # yoast
        return {
            "_yoast_wpseo_title": block.title,
            "_yoast_wpseo_metadesc": block.meta_description,
            "_yoast_wpseo_focuskw": focus_kw,
            "_yoast_wpseo_opengraph-title": block.title,
            "_yoast_wpseo_opengraph-description": block.meta_description,
        }


async def _check_duplicate(slug: str, wp_api_base: str, headers: dict, resource: str = "posts") -> Optional[int]:
    """Check if a post/page with this slug already exists. Returns id if found."""
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(
                f"{wp_api_base}/{resource}",
                params={"slug": slug, "status": "any"},
                headers=headers,
            )
            if resp.status_code == 200:
                posts = resp.json()
                if posts:
                    return posts[0].get("id")
    except Exception:
        pass
    return None


# In-process cache so repeated publishes don't re-look-up/re-create the same
# category on every call. Keyed by (wp_api_base, category name, lowercased).
_category_cache: dict[tuple[str, str], int] = {}


async def _find_or_create_category(name: str, wp_api_base: str, headers: dict) -> Optional[int]:
    """Find a WordPress category by name, creating it if it doesn't exist yet."""
    cache_key = (wp_api_base, name.strip().lower())
    if cache_key in _category_cache:
        return _category_cache[cache_key]
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(f"{wp_api_base}/categories", params={"search": name}, headers=headers)
            if resp.status_code == 200:
                for cat in resp.json():
                    if cat.get("name", "").strip().lower() == name.strip().lower():
                        _category_cache[cache_key] = cat["id"]
                        return cat["id"]
            create_resp = await client.post(f"{wp_api_base}/categories", json={"name": name}, headers=headers)
            if create_resp.status_code in (200, 201):
                cat_id = create_resp.json().get("id")
                if cat_id:
                    _category_cache[cache_key] = cat_id
                    return cat_id
    except Exception as e:
        print(f"[WP] Category lookup/create failed for '{name}': {e}")
    return None


async def publish_to_wordpress(
    block: SEOBlock,
    config: WordPressConfig,
) -> PublishResult:
    """Publish a single SEOBlock to WordPress via REST API."""
    credentials = base64.b64encode(
        f"{config.wp_username}:{config.wp_app_password}".encode()
    ).decode()
    headers = {
        "Authorization": f"Basic {credentials}",
        "Content-Type": "application/json",
    }

    content_html = _build_content_html(block)
    seo_meta = _build_seo_meta(block, config.seo_plugin)

    slug = block.slug or f"{block.business_type.lower().replace(' ', '-')}-{block.city.lower().replace(' ', '-')}"
    wp_api_base = config.wp_url.rstrip('/') + "/wp-json/wp/v2"
    is_wp_page = (block.content_type or "service") not in ("blog", "post")
    resource = "pages" if is_wp_page else "posts"
    wp_api = f"{wp_api_base}/{resource}"

    # ── Featured image ──────────────────────────────────────────
    featured_media_id = None
    featured_image_url = None
    if config.fetch_image:
        try:
            # Prefer the article's generated featured ImageAsset (WebP + full metadata).
            featured_asset = next(
                (img for img in (block.in_content_images or []) if img.is_featured), None
            )
            if featured_asset and featured_asset.url:
                img_bytes = await fetch_image_bytes(featured_asset.url)
                if img_bytes:
                    media = await upload_image_to_wordpress(
                        img_bytes, featured_asset.filename,
                        config.wp_url, config.wp_username, config.wp_app_password,
                        alt_text=featured_asset.alt_text,
                        title=featured_asset.title,
                        caption=featured_asset.caption,
                        description=featured_asset.description,
                    )
                    if media:
                        featured_media_id = media["id"]
                        featured_image_url = media["url"]

            # Fall back to the legacy business-type image fetch (city pages).
            if not featured_media_id:
                img_result = await get_image_for_content(block.business_type, block.city)
                if img_result:
                    img_bytes, img_filename = img_result
                    alt_text = f"{block.business_type} in {block.city}"
                    media = await upload_image_to_wordpress(
                        img_bytes, img_filename,
                        config.wp_url, config.wp_username, config.wp_app_password,
                        alt_text=alt_text,
                    )
                    if media:
                        featured_media_id = media["id"]
                        featured_image_url = media["url"]
        except Exception as e:
            print(f"[WP] Image upload failed for {block.city}: {e}")

    # ── Check for duplicate ──────────────────────────────────────
    existing_id = await _check_duplicate(slug, wp_api_base, headers, resource=resource)

    # ── Build post data ──────────────────────────────────────────
    post_data: dict = {
        "title": block.title,
        "content": content_html,
        "slug": slug,
        "meta": seo_meta,
        "excerpt": block.meta_description,
    }

    # Categories and tags — explicit category_ids always win; otherwise
    # auto-resolve a category from content_type (service page vs. blog post)
    # so pillar pages and supporting posts land in separate categories.
    category_ids = list(config.category_ids)
    if not category_ids:
        category_name = "Blog" if block.content_type == "blog" else f"{block.business_type} Services"
        resolved_id = await _find_or_create_category(category_name, wp_api_base, headers)
        if resolved_id:
            category_ids = [resolved_id]
    if category_ids:
        post_data["categories"] = category_ids
    if config.tag_ids:
        post_data["tags"] = config.tag_ids

    # Featured image
    if featured_media_id:
        post_data["featured_media"] = featured_media_id

    # Scheduling vs immediate publish
    if config.scheduled_at:
        post_data["status"] = "future"
        post_data["date"] = config.scheduled_at
    else:
        post_data["status"] = config.status

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            if existing_id:
                # Update existing post
                resp = await client.post(
                    f"{wp_api}/{existing_id}",
                    json=post_data,
                    headers=headers,
                )
            else:
                resp = await client.post(wp_api, json=post_data, headers=headers)

        if resp.status_code in (200, 201):
            data = resp.json()
            return PublishResult(
                city=block.city,
                success=True,
                post_id=data.get("id"),
                post_url=data.get("link"),
                featured_image_id=featured_media_id,
            )
        else:
            return PublishResult(
                city=block.city,
                success=False,
                error=f"WP API error {resp.status_code}: {resp.text[:200]}",
            )
    except Exception as e:
        return PublishResult(
            city=block.city,
            success=False,
            error=str(e),
        )
