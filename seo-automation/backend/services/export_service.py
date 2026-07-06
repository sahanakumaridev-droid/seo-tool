import json
from typing import List
from models.schemas import SEOBlock

def export_json(pages: List[SEOBlock]) -> str:
    return json.dumps([p.model_dump() for p in pages], indent=2)

def export_html(page: SEOBlock) -> str:
    faqs_html = "\n".join([
        f"""  <div class="faq-item">
    <h4>{faq.question}</h4>
    <p>{faq.answer}</p>
  </div>"""
        for faq in page.faqs
    ])
    h2s_html = "\n".join([f"  <h2>{h}</h2>" for h in page.h2s])
    h3s_html = "\n".join([f"  <h3>{h}</h3>" for h in page.h3s])
    schema_json = json.dumps(page.schema_markup, indent=2)
    
    # Get the page URL (you can customize this based on your domain)
    page_url = f"https://yourwebsite.com/{page.slug}"
    
    # Get the featured image URL
    image_url = page.featured_image_url or "https://yourwebsite.com/default-image.jpg"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  
  <!-- Basic SEO Meta Tags -->
  <title>{page.title}</title>
  <meta name="description" content="{page.meta_description}">
  <meta name="keywords" content="{page.keywords.primary}, {', '.join(page.keywords.secondary[:3])}">
  
  <!-- Open Graph Meta Tags (Facebook, WhatsApp, LinkedIn) -->
  <meta property="og:type" content="website">
  <meta property="og:url" content="{page_url}">
  <meta property="og:title" content="{page.title}">
  <meta property="og:description" content="{page.meta_description}">
  <meta property="og:image" content="{image_url}">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta property="og:image:alt" content="{page.business_type} in {page.city}, {page.state}">
  <meta property="og:site_name" content="Your Business Name">
  <meta property="og:locale" content="en_US">
  
  <!-- Twitter Card Meta Tags -->
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:url" content="{page_url}">
  <meta name="twitter:title" content="{page.title}">
  <meta name="twitter:description" content="{page.meta_description}">
  <meta name="twitter:image" content="{image_url}">
  <meta name="twitter:image:alt" content="{page.business_type} in {page.city}, {page.state}">
  <meta name="twitter:site" content="@yourtwitterhandle">
  <meta name="twitter:creator" content="@yourtwitterhandle">
  
  <!-- Additional Meta Tags for Better Sharing -->
  <meta property="article:published_time" content="{page.created_at if hasattr(page, 'created_at') else ''}">
  <meta property="article:author" content="Your Business Name">
  <meta property="article:section" content="{page.business_type}">
  <meta property="article:tag" content="{page.keywords.primary}">
  
  <!-- Canonical URL -->
  <link rel="canonical" href="{page_url}">
  
  <!-- Schema.org JSON-LD -->
  <script type="application/ld+json">
{schema_json}
  </script>
</head>
<body>
  <h1>{page.h1}</h1>
{h2s_html}
{h3s_html}
  <div class="content">
    <p>{page.content.replace(chr(10), '</p><p>')}</p>
  </div>
  <section class="faqs">
    <h2>Frequently Asked Questions</h2>
{faqs_html}
  </section>
  <section class="cta">
    <p>{page.cta}</p>
  </section>
</body>
</html>"""

def export_wordpress(page: SEOBlock) -> dict:
    """WordPress REST API compatible format."""
    content_html = f"<h1>{page.h1}</h1>\n"
    for h2 in page.h2s:
        content_html += f"<h2>{h2}</h2>\n"
    content_html += f"<p>{page.content.replace(chr(10), '</p><p>')}</p>\n"
    content_html += "<h2>FAQs</h2>\n"
    for faq in page.faqs:
        content_html += f"<h4>{faq.question}</h4><p>{faq.answer}</p>\n"
    content_html += f"<p><strong>{page.cta}</strong></p>"

    return {
        "title": page.title,
        "content": content_html,
        "status": "draft",
        "meta": {
            "_yoast_wpseo_title": page.title,
            "_yoast_wpseo_metadesc": page.meta_description,
            "_yoast_wpseo_focuskw": page.keywords.primary,
        },
        "slug": f"{page.business_type.lower().replace(' ', '-')}-{page.city.lower().replace(' ', '-')}",
    }


def generate_social_meta_tags(page: SEOBlock, page_url: str = None) -> str:
    """
    Generate Open Graph and Twitter Card meta tags for social media sharing.
    These tags are FREE - no API needed! Just add them to your page's <head> section.
    
    Args:
        page: SEOBlock with content data
        page_url: Full URL of the page (e.g., "https://yourwebsite.com/plumbing-san-diego")
    
    Returns:
        String of HTML meta tags ready to paste into <head>
    """
    if not page_url:
        page_url = f"https://yourwebsite.com/{page.slug}"
    
    image_url = page.featured_image_url or "https://yourwebsite.com/default-image.jpg"
    
    return f"""<!-- Open Graph Meta Tags (Facebook, WhatsApp, LinkedIn) -->
<meta property="og:type" content="website">
<meta property="og:url" content="{page_url}">
<meta property="og:title" content="{page.title}">
<meta property="og:description" content="{page.meta_description}">
<meta property="og:image" content="{image_url}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{page.business_type} in {page.city}, {page.state}">
<meta property="og:site_name" content="Your Business Name">
<meta property="og:locale" content="en_US">

<!-- Twitter Card Meta Tags -->
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:url" content="{page_url}">
<meta name="twitter:title" content="{page.title}">
<meta name="twitter:description" content="{page.meta_description}">
<meta name="twitter:image" content="{image_url}">
<meta name="twitter:image:alt" content="{page.business_type} in {page.city}, {page.state}">
<meta name="twitter:site" content="@yourtwitterhandle">
<meta name="twitter:creator" content="@yourtwitterhandle">"""
