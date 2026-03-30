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

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{page.title}</title>
  <meta name="description" content="{page.meta_description}">
  <meta name="keywords" content="{page.keywords.primary}, {', '.join(page.keywords.secondary[:3])}">
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
