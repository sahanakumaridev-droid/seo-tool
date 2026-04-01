"""
wordpress_service.py
Auto-publishes SEO pages to WordPress via REST API.
Supports RankMath, All in One SEO (AIOSEO), and Yoast SEO meta fields.
Image spec: 1280x720 WebP (16:9)
"""
import base64
import json
import httpx
from typing import Optional
from models.schemas import SEOBlock, WordPressConfig, PublishResult


def _build_content_html(block: SEOBlock) -> str:
    """Build full WordPress-ready HTML content from SEOBlock."""
    parts = []

    # Intro paragraph (AI-citation optimized — direct, clear, no fluff)
    if block.intro:
        parts.append(f'<p class="seo-intro">{block.intro}</p>')

    # H2 sections with body content split across them
    body_paragraphs = [p.strip() for p in block.content.split('\n\n') if p.strip()]

    for i, h2 in enumerate(block.h2s):
        parts.append(f'<h2>{h2}</h2>')
        if i < len(body_paragraphs):
            # Convert bullet lines to <ul>
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

    # H3 sub-sections
    if block.h3s:
        for h3 in block.h3s[:2]:
            parts.append(f'<h3>{h3}</h3>')

    # FAQs section (structured for AI extraction)
    if block.faqs:
        parts.append('<h2>Frequently Asked Questions</h2>')
        parts.append('<div class="faq-section" itemscope itemtype="https://schema.org/FAQPage">')
        for faq in block.faqs:
            parts.append(
                f'<div class="faq-item" itemscope itemprop="mainEntity" itemtype="https://schema.org/Question">'
                f'<h3 itemprop="name">{faq.question}</h3>'
                f'<div itemscope itemprop="acceptedAnswer" itemtype="https://schema.org/Answer">'
                f'<p itemprop="text">{faq.answer}</p>'
                f'</div></div>'
            )
        parts.append('</div>')

    # CTA
    parts.append(f'<div class="cta-section"><p><strong>{block.cta}</strong></p></div>')

    # JSON-LD schema (both LocalBusiness + FAQPage)
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

    post_data = {
        "title": block.title,
        "content": content_html,
        "status": config.status,
        "slug": slug,
        "meta": seo_meta,
        "excerpt": block.meta_description,
    }

    wp_api = config.wp_url.rstrip('/') + "/wp-json/wp/v2/posts"

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(wp_api, json=post_data, headers=headers)

        if resp.status_code in (200, 201):
            data = resp.json()
            return PublishResult(
                city=block.city,
                success=True,
                post_id=data.get("id"),
                post_url=data.get("link"),
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
