"""
wordpress_service.py
Auto-publishes SEO pages to WordPress via REST API.
Supports RankMath, All in One SEO (AIOSEO), and Yoast SEO meta fields.
Features: featured image upload, categories, tags, scheduled publishing, duplicate detection.
"""
import base64
import json
import httpx
from typing import Optional
from models.schemas import SEOBlock, WordPressConfig, PublishResult
from services.image_service import (
    get_image_for_content, upload_image_to_wordpress,
    fetch_image_bytes,
)


def _figure_html(img) -> str:
    """Render an in-content image as a semantic <figure> with caption."""
    return (
        f'<figure class="wp-block-image">'
        f'<img src="{img.url}" alt="{img.alt_text}" title="{img.title}" loading="lazy" />'
        f'<figcaption>{img.caption}</figcaption>'
        f'</figure>'
    )


def _build_content_html(block: SEOBlock) -> str:
    """Build full WordPress-ready HTML content from SEOBlock."""
    parts = []

    if block.intro:
        parts.append(f'<p class="seo-intro">{block.intro}</p>')

    # In-content images (non-featured) are distributed across the H2 sections.
    in_content_imgs = [img for img in (block.in_content_images or []) if not img.is_featured]
    img_positions = {}
    if in_content_imgs and block.h2s:
        step = max(1, len(block.h2s) // (len(in_content_imgs) + 1))
        for n, img in enumerate(in_content_imgs):
            img_positions[min((n + 1) * step, len(block.h2s) - 1)] = img

    body_paragraphs = [p.strip() for p in block.content.split('\n\n') if p.strip()]

    for i, h2 in enumerate(block.h2s):
        parts.append(f'<h2>{h2}</h2>')
        if i in img_positions:
            parts.append(_figure_html(img_positions[i]))
        if i < len(body_paragraphs):
            para = body_paragraphs[i]
            if '•' in para or para.strip().startswith('1.'):
                lines = para.split('\n')
                html_lines = []
                in_list = False
                for line in lines:
                    line = line.strip()
                    if line.startswith('•') or (len(line) > 2 and line[0].isdigit() and line[1] == '.'):
                        if not in_list:
                            html_lines.append('<ul>')
                            in_list = True
                        item = line.lstrip('•').lstrip('0123456789.').strip()
                        html_lines.append(f'<li>{item}</li>')
                    else:
                        if in_list:
                            html_lines.append('</ul>')
                            in_list = False
                        if line:
                            html_lines.append(f'<p>{line}</p>')
                if in_list:
                    html_lines.append('</ul>')
                parts.append('\n'.join(html_lines))
            else:
                parts.append(f'<p>{para}</p>')

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


async def _check_duplicate(slug: str, wp_api_base: str, headers: dict) -> Optional[int]:
    """Check if a post with this slug already exists. Returns post_id if found."""
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(
                f"{wp_api_base}/posts",
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
    wp_api = f"{wp_api_base}/posts"

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
                    alt_text = f"{block.business_type} services in {block.city}"
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
    existing_id = await _check_duplicate(slug, wp_api_base, headers)

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
