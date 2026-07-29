"""
public_page_service.py — renders a saved SEOBlock as a public BLOG article
(served at /p/{slug}) styled to match the ZeOrbit brand site: black utility bar
with email + socials, elegant serif display headlines, outlined pill badges,
inline SVG logo. Self-contained; opens instantly in any browser.
"""
import html
import json
import re
from models.schemas import SEOBlock
from services.wordpress_service import _build_content_html
from config import settings

EMAIL = "info@zeorbit.com"
PHONE = "+16197249517"
PHONE_DISPLAY = "+1 (619) 724-9517"
WEBSITE = "https://zeorbit.com"
ADDRESS = "4231 Balboa Avenue, Suite 1340, San Diego, CA 92117"
OTHER_OFFICES = ["1860 Greenfield Dr, El Cajon, CA 92021, USA", "3938 Red Maple Drive, Los Angeles, CA 90071"]

# Mirrors the live zeorbit.com footer columns.
_FOOTER_OFFER_LINKS = [
    ("WordPress & Web Builder Solutions", f"{WEBSITE}/wordpress-web-builder-solutions/"),
    ("Web Hosting & Domain", f"{WEBSITE}/web-hosting-and-domain-services/"),
    ("Ecommerce Store Management", f"{WEBSITE}/ecommerce-store-management/"),
    ("Web Research & Data Processing", f"{WEBSITE}/web-research-data-processing/"),
    ("AI Consulting Strategy & Dev", f"{WEBSITE}/ai-consulting-strategy-development/"),
    ("AI Agent Copilot Development", f"{WEBSITE}/ai-copilot-for-sales/"),
    ("ML-Powered Development", f"{WEBSITE}/machine-learning-development-services/"),
    ("API Integrations Solution", f"{WEBSITE}/api-integration-services/"),
    ("Area's We Serve", f"{WEBSITE}/locations/"),
]
_FOOTER_SPECIAL_LINKS = [
    ("Website Designing", f"{WEBSITE}/web-development/"),
    ("Mobile Apps", f"{WEBSITE}/app-development/"),
    ("SEO & PPC Tactics", f"{WEBSITE}/seo-development/"),
    ("Mobile Apps Timeline", f"{WEBSITE}/app-development-timeline-duration-for-designing-developing-and-launching-your-app/"),
    ("Logo & Animation Design", f"{WEBSITE}/graphic-logo-design/"),
    ("Portfolios", f"{WEBSITE}/portfolio/"),
    ("Let's Talk", f"{WEBSITE}/contact/"),
    ("Blogs", f"{WEBSITE}/blog/"),
    ("Privacy & Policy", f"{WEBSITE}/privacy-policy/"),
]

# Social links (brand)
_FB_PATH = "M9.1 23.7v-8H6.6v-3.7h2.5v-1.6c0-4.1 1.8-6 5.9-6 .4 0 1 0 1.5.1v3.3h-1.4c-1.1 0-1.7.6-1.7 1.7V12h3.4l-.6 3.7h-2.8v8A12 12 0 1 0 9.1 23.7Z"
_X_PATH = "M18.2 2.2h3.3l-7.2 8.3 8.5 11.3h-6.7l-5.2-6.8-6 6.8H1.7l7.7-8.8L1.3 2.2h6.8l4.7 6.2 5.4-6.2Z"
_LI_PATH = "M20.4 20.5h-3.6v-5.6c0-1.3 0-3-1.8-3s-2.1 1.4-2.1 2.9v5.7H9.4V9h3.4v1.6c.5-.9 1.6-1.9 3.4-1.9 3.6 0 4.3 2.4 4.3 5.5v6.3ZM5.3 7.4a2.1 2.1 0 1 1 0-4.1 2.1 2.1 0 0 1 0 4.1ZM7.1 20.5H3.6V9h3.5v11.5ZM22.2 0H1.8C.8 0 0 .8 0 1.7v20.5C0 23.2.8 24 1.8 24h20.4c1 0 1.8-.8 1.8-1.7V1.7C24 .8 23.2 0 22.2 0Z"
_IG_PATH = "M12 2.2c3.2 0 3.6 0 4.9.1 3.2.1 4.8 1.7 4.9 4.9.1 1.3.1 1.6.1 4.8s0 3.6-.1 4.8c-.1 3.2-1.7 4.8-4.9 4.9-1.3.1-1.6.1-4.9.1s-3.6 0-4.8-.1c-3.3-.1-4.8-1.7-4.9-4.9C2.2 15.6 2.2 15.2 2.2 12s0-3.6.1-4.8C2.4 4 4 2.4 7.2 2.3 8.4 2.2 8.8 2.2 12 2.2Zm0-2.2C8.7 0 8.3 0 7.1.1 2.7.3.3 2.7.1 7.1 0 8.3 0 8.7 0 12s0 3.7.1 4.9c.2 4.4 2.6 6.8 7 7 1.2.1 1.6.1 4.9.1s3.7 0 4.9-.1c4.4-.2 6.8-2.6 7-7 .1-1.2.1-1.6.1-4.9s0-3.7-.1-4.9c-.2-4.4-2.6-6.8-7-7C15.7 0 15.3 0 12 0Zm0 5.8a6.2 6.2 0 1 0 0 12.4 6.2 6.2 0 0 0 0-12.4ZM12 16a4 4 0 1 1 0-8 4 4 0 0 1 0 8Zm6.4-11.8a1.4 1.4 0 1 0 0 2.9 1.4 1.4 0 0 0 0-2.9Z"
_YT_PATH = "M23.5 6.2a3 3 0 0 0-2.1-2.1C19.5 3.5 12 3.5 12 3.5s-7.5 0-9.4.5A3 3 0 0 0 .5 6.2C0 8.1 0 12 0 12s0 3.9.5 5.8a3 3 0 0 0 2.1 2.1c1.9.6 9.4.6 9.4.6s7.5 0 9.4-.5a3 3 0 0 0 2.1-2.1C24 15.9 24 12 24 12s0-3.9-.5-5.8ZM9.5 15.6V8.4l6.3 3.6-6.3 3.6Z"
_PIN_PATH = "M12.017 0C5.396 0 .029 5.367.029 11.987c0 5.079 3.158 9.417 7.618 11.162-.105-.949-.199-2.403.041-3.439.219-.937 1.406-5.957 1.406-5.957s-.359-.72-.359-1.781c0-1.663.967-2.911 2.171-2.911 1.023 0 1.518.769 1.518 1.688 0 1.029-.653 2.567-.992 3.992-.285 1.193.6 2.165 1.777 2.165 2.133 0 3.772-2.249 3.772-5.495 0-2.873-2.064-4.882-5.012-4.882-3.414 0-5.418 2.561-5.418 5.207 0 1.031.397 2.138.893 2.738.099.12.112.225.083.345-.09.375-.293 1.199-.334 1.363-.053.225-.172.271-.4.165-1.495-.69-2.436-2.878-2.436-4.646 0-3.776 2.748-7.246 7.92-7.246 4.158 0 7.392 2.967 7.392 6.923 0 4.135-2.607 7.462-6.233 7.462-1.214 0-2.354-.629-2.746-1.378l-.748 2.845c-.271 1.043-1.002 2.353-1.492 3.153 1.125.345 2.319.535 3.554.535 6.607 0 11.985-5.365 11.985-11.987C23.97 5.39 18.592.026 11.985.026L12.017 0z"
_APPLE_PATH = "M16.365 1.43c0 1.14-.493 2.27-1.177 3.08-.744.9-1.99 1.57-2.987 1.57-.12 0-.23-.02-.3-.03-.01-.06-.04-.22-.04-.39 0-1.15.572-2.27 1.206-2.98.804-.94 2.142-1.64 3.248-1.68.03.13.05.28.05.43zm4.565 15.71c-.03.07-.463 1.58-1.518 3.12-.945 1.34-1.94 2.71-3.43 2.71-1.517 0-1.9-.88-3.63-.88-1.698 0-2.302.91-3.67.91-1.377 0-2.332-1.26-3.428-2.8-1.287-1.82-2.323-4.63-2.323-7.28 0-4.28 2.797-6.55 5.552-6.55 1.448 0 2.675.95 3.6.95.865 0 2.222-1.01 3.902-1.01.613 0 2.886.06 4.374 2.19-.13.09-2.383 1.39-2.383 4.26 0 3.4 3.984 4.55 4.024 4.55l.001.01z"

_SOCIALS = [
    (f"https://facebook.com/zeorbit", _FB_PATH, "#1877F2"),
    (f"https://twitter.com/orbit_ze", _X_PATH, "#000000"),
    (f"https://linkedin.com/company/zeorbit", _LI_PATH, "#0A66C2"),
    (f"https://instagram.com/zeorbit", _IG_PATH, "#C6288E"),
    (f"https://youtube.com/@zeorbit", _YT_PATH, "#FF0000"),
]

# Icon-only "Find us on" row (below-footer credit strip) — brand-colored circles.
_MAP_ICONS = [
    ("Apple Maps", "https://maps.apple.com/?q=ZeOrbit", "#3A3A3C", _APPLE_PATH),
    ("Google", "https://g.page/r/zeorbit", "#4285F4", None),
    ("Yelp", "https://yelp.com/biz/zeorbit", "#D32323", None),
    ("Instagram", "https://instagram.com/zeorbit", "#C6288E", _IG_PATH),
    ("LinkedIn", "https://linkedin.com/company/zeorbit", "#0A66C2", _LI_PATH),
    ("Facebook", "https://facebook.com/zeorbit", "#1877F2", _FB_PATH),
    ("X", "https://twitter.com/orbit_ze", "#000000", _X_PATH),
    ("YouTube", "https://youtube.com/@zeorbit", "#FF0000", _YT_PATH),
    ("Pinterest", "https://pinterest.com/zeorbit", "#E60023", _PIN_PATH),
]


def _social_bar() -> str:
    icons = "".join(
        f'<a href="{url}" target="_blank" rel="noreferrer" aria-label="social">'
        f'<svg width="15" height="15" viewBox="0 0 24 24" fill="#fff"><path d="{d}"/></svg></a>'
        for url, d, _c in _SOCIALS
    )
    return (f'<div class="topbar">'
            f'<div class="topbar-l">'
            f'<a class="mail" href="mailto:{EMAIL}">✉ {EMAIL}</a>'
            f'<a class="mail tel" href="tel:{PHONE}">✆ {PHONE_DISPLAY}</a>'
            f'</div>'
            f'<div class="socials">{icons}</div></div>')


def _gtm_snippets() -> tuple[str, str]:
    """Return (head, body) Google Tag Manager snippets, or ('','') when no
    container ID is configured. Built as plain strings (not f-strings) so the
    GTM code's many braces don't need escaping."""
    gid = (settings.GTM_CONTAINER_ID or "").strip()
    if not gid:
        return "", ""
    head = (
        "<!-- Google Tag Manager -->\n"
        "<script>(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':"
        "new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],"
        "j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;"
        "j.src='https://www.googletagmanager.com/gtm.js?id='+i+dl;"
        "f.parentNode.insertBefore(j,f);})(window,document,'script','dataLayer','"
        + gid + "');</script>\n<!-- End Google Tag Manager -->"
    )
    body = (
        "<!-- Google Tag Manager (noscript) --><noscript>"
        '<iframe src="https://www.googletagmanager.com/ns.html?id=' + gid + '"'
        ' height="0" width="0" style="display:none;visibility:hidden"></iframe>'
        "</noscript><!-- End Google Tag Manager (noscript) -->"
    )
    return head, body


def _adsense_head_snippet() -> str:
    """AdSense auto-ads loader for <head>, or '' when no client id is set."""
    client = (settings.ADSENSE_CLIENT_ID or "").strip()
    if not client:
        return ""
    return (
        '<script async src="https://pagead2.googlesyndication.com/pagead/js/'
        'adsbygoogle.js?client=' + client + '"\n'
        ' crossorigin="anonymous"></script>\n'
        '<script>(adsbygoogle = window.adsbygoogle || []).push({\n'
        '  google_ad_client: "' + client + '",\n'
        '  enable_page_level_ads: true\n'
        '});</script>'
    )


def _adsense_in_article_unit() -> str:
    """A single in-article ad unit, or '' when no client id is set."""
    client = (settings.ADSENSE_CLIENT_ID or "").strip()
    if not client:
        return ""
    slot_attr = f' data-ad-slot="{settings.ADSENSE_SLOT_ID}"' if settings.ADSENSE_SLOT_ID else ""
    return (
        '<div class="ad-slot">'
        f'<ins class="adsbygoogle" style="display:block; text-align:center;" '
        f'data-ad-client="{client}"{slot_attr} data-ad-format="fluid" '
        'data-ad-layout="in-article"></ins>'
        '<script>(adsbygoogle = window.adsbygoogle || []).push({});</script>'
        '</div>'
    )


def _footer() -> str:
    icons = "".join(
        f'<a href="{url}" target="_blank" rel="noreferrer" aria-label="social" style="background:{c}">'
        f'<svg width="13" height="13" viewBox="0 0 24 24" fill="#fff"><path d="{d}"/></svg></a>'
        for url, d, c in _SOCIALS
    )
    offer_links = "".join(f'<li><a href="{url}" target="_blank" rel="noreferrer">{label}</a></li>' for label, url in _FOOTER_OFFER_LINKS)
    special_links = "".join(f'<li><a href="{url}" target="_blank" rel="noreferrer">{label}</a></li>' for label, url in _FOOTER_SPECIAL_LINKS)
    offices = "".join(f'<div>{o}</div>' for o in OTHER_OFFICES)

    return f"""<footer>
    {_below_footer()}
    <div class="foot-main">
      <div class="foot-col foot-brand">
        <a class="brand" href="{WEBSITE}" target="_blank" rel="noreferrer"><img src="/static/zeorbit-logo.png" alt="ZeOrbit" /></a>
        <p>ZeOrbit is a creative multi-award-winning web design firm in San Diego, California, serving clients
        nationwide. We've made a reputation for creating customized user-friendly websites and apps.</p>
        <div class="foot-socials">{icons}</div>
        <div class="dmca-badge"><span>DMCA</span><span>PROTECTED</span></div>
      </div>
      <div class="foot-col">
        <div class="foot-h">What We Offer</div>
        <ul>{offer_links}</ul>
      </div>
      <div class="foot-col">
        <div class="foot-h">Special Links</div>
        <ul>{special_links}</ul>
      </div>
      <div class="foot-col">
        <div class="foot-h">Contact</div>
        <div class="foot-contact-block">
          <div class="foot-address">{ADDRESS}</div>
          <a href="tel:{PHONE}">☎ {PHONE_DISPLAY}</a>
          <a href="mailto:{EMAIL}">✉ {EMAIL}</a>
        </div>
        <div class="foot-h" style="margin-top:22px;">Other Office Locations</div>
        <div class="foot-address">{offices}</div>
      </div>
    </div>
    <div class="foot-bottom">
      <span>Copyright © 2026 ZeOrbit . All Rights Reserved.</span>
      <div class="disclaimer-h">Disclaimer</div>
      <p>All images and content are the property of their respective owners. All referenced content is sourced from its original creators.</p>
    </div>
  </footer>"""


def _below_footer() -> str:
    map_icons = "".join(
        (
            f'<a href="{url}" target="_blank" rel="noreferrer" aria-label="{label}" style="background:{color}" title="{label}">'
            + (f'<svg width="17" height="17" viewBox="0 0 24 24" fill="#fff"><path d="{path}"/></svg>' if path else label[0])
            + '</a>'
        )
        for label, url, color, path in _MAP_ICONS
    )
    return f"""<div class="map-section">
    <div class="map-h">Find Us on Google Map, Apple Map &amp; Social Media</div>
    <div class="map-icons">{map_icons}</div>
  </div>"""


def _esc(s: str) -> str:
    return html.escape(s or "", quote=True)


def _read_time(block: SEOBlock) -> int:
    text = " ".join([block.content or "", " ".join(block.h2s or []),
                     " ".join(f"{f.question} {f.answer}" for f in (block.faqs or []))])
    return max(1, round(len(re.findall(r"\w+", text)) / 200))


def render_public_html(block: SEOBlock, public_url: str = "") -> str:
    body = _build_content_html(block)
    headings = re.findall(r"<h2>(.*?)</h2>", body)
    toc = []
    for i, h in enumerate(headings):
        hid = f"sec-{i}"
        body = body.replace(f"<h2>{h}</h2>", f'<h2 id="{hid}">{h}</h2>', 1)
        toc.append((hid, h))
    toc_html = ""
    if len(toc) >= 2:
        lis = "".join(f'<li><a href="#{hid}">{h}</a></li>' for hid, h in toc)
        toc_html = f'<nav class="toc"><div class="toc-title">In this article</div><ol>{lis}</ol></nav>'

    title = _esc(block.title or block.h1 or f"{block.business_type} in {block.city}")
    desc = _esc(block.meta_description or "")
    h1 = _esc(block.h1 or title)
    featured = block.featured_image_url or ""
    location = _esc(f"{block.city}, {block.state}".strip(", "))
    biz = _esc(block.business_type or "")
    mins = _read_time(block)
    og_img = f'<meta property="og:image" content="{_esc(featured)}" />' if featured else ""
    canonical_tag = f'<link rel="canonical" href="{_esc(public_url)}" />' if public_url else ""
    hero = f'<div class="hero-wrap"><img src="{_esc(featured)}" alt="{h1}" /></div>' if featured else ""
    quick = f'<aside class="quick"><div class="quick-l">Quick answer</div><p>{desc}</p></aside>' if desc else ""
    gtm_head, gtm_body = _gtm_snippets()
    adsense_head = _adsense_head_snippet()
    ad_unit = _adsense_in_article_unit()

    return f"""<!doctype html>
<html lang="en">
<head>
{gtm_head}
{adsense_head}
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>{title}</title>
<meta name="description" content="{desc}" />
<meta property="og:type" content="article" />
<meta property="og:title" content="{title}" />
<meta property="og:description" content="{desc}" />
{og_img}
{canonical_tag}
<meta name="robots" content="index,follow" />
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Playfair+Display:wght@600;700;800;900&family=Newsreader:opsz,wght@6..72,400;6..72,500;6..72,600&display=swap" rel="stylesheet" />
<style>
  :root {{
    --brand:#2563EB; --brand-dark:#1D4ED8; --navy:#0E1A44;
    --ink:#0B1220; --body:#2A2A2A; --muted:#5B6676; --faint:#8A94A6;
    --line:#E6E3DD; --bg:#FFFFFF; --soft:#F7F5F1;
    --sans:'Inter',-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
    --serif:'Newsreader',Georgia,serif;
    --display:'Playfair Display',Georgia,'Times New Roman',serif;
  }}
  * {{ box-sizing:border-box; }}
  html {{ scroll-behavior:smooth; }}
  body {{ margin:0; background:var(--bg); color:var(--body); font-family:var(--serif); font-size:19px; line-height:1.85; -webkit-font-smoothing:antialiased; }}

  /* Black utility bar */
  .topbar {{ display:flex; align-items:center; justify-content:space-between; background:#0A0A0A; color:#fff; padding:9px 30px; font-family:var(--sans); }}
  .topbar-l {{ display:flex; align-items:center; gap:20px; flex-wrap:wrap; }}
  .topbar .mail {{ color:#fff; text-decoration:none; font-size:13px; opacity:.9; }}
  .topbar .mail:hover {{ opacity:1; }}
  .topbar .tel {{ font-weight:600; }}
  .topbar .socials {{ display:flex; gap:14px; align-items:center; }}
  .topbar .socials a {{ display:inline-flex; opacity:.85; transition:opacity .15s; }}
  .topbar .socials a:hover {{ opacity:1; }}

  /* Header */
  .nav {{ position:sticky; top:0; z-index:10; display:flex; align-items:center; justify-content:space-between; gap:20px;
          padding:16px 30px; background:rgba(255,255,255,0.95); backdrop-filter:blur(10px); border-bottom:1px solid var(--line); }}
  .brand {{ display:flex; align-items:center; gap:11px; text-decoration:none; }}
  .brand img {{ height:30px; width:auto; display:block; }}
  .nav .cta {{ font-family:var(--sans); font-size:13px; font-weight:600; color:#fff; background:var(--navy); padding:11px 20px; border-radius:2px; text-decoration:none; text-transform:uppercase; letter-spacing:.05em; flex-shrink:0; }}
  .progress {{ position:fixed; top:0; left:0; height:3px; width:0; background:var(--brand); z-index:20; }}

  article {{ max-width:740px; margin:0 auto; padding:52px 22px 40px; }}
  .eyebrow {{ display:inline-block; font-family:var(--sans); font-size:12px; font-weight:600; text-transform:uppercase; letter-spacing:.14em; color:var(--ink); border:1.5px solid var(--ink); padding:9px 22px; border-radius:999px; margin-bottom:26px; }}
  h1 {{ font-family:var(--display); font-size:clamp(34px,6vw,56px); line-height:1.08; font-weight:800; letter-spacing:-0.01em; color:var(--ink); margin:0 0 24px; }}
  .byline {{ display:flex; align-items:center; gap:12px; font-family:var(--sans); margin:0 0 32px; }}
  .byline .who {{ font-size:14px; font-weight:600; color:var(--ink); }}
  .byline .sub {{ font-size:13px; color:var(--faint); }}
  /* Full-bleed hero — spans the full viewport width, sits above the
     constrained article column rather than inside it. */
  .hero-wrap {{ width:100%; max-height:min(60vh, 560px); overflow:hidden; position:relative; background:var(--soft); }}
  .hero-wrap img {{ width:100%; height:100%; min-height:280px; object-fit:cover; display:block; }}
  .hero-wrap::after {{ content:''; position:absolute; inset:0; background:linear-gradient(180deg, rgba(0,0,0,0) 55%, rgba(0,0,0,0.30) 100%); }}

  .quick {{ background:var(--soft); border-left:4px solid var(--navy); border-radius:4px; padding:18px 22px; margin:0 0 32px; }}
  .quick-l {{ font-family:var(--sans); font-size:11px; font-weight:700; text-transform:uppercase; letter-spacing:.1em; color:var(--navy); margin-bottom:6px; }}
  .quick p {{ margin:0; font-size:19px; color:var(--ink); }}

  .toc {{ border-top:2px solid var(--ink); border-bottom:2px solid var(--ink); padding:20px 4px; margin:0 0 38px; }}
  .toc-title {{ font-family:var(--sans); font-size:12px; font-weight:700; text-transform:uppercase; letter-spacing:.1em; color:var(--muted); margin-bottom:12px; }}
  .toc ol {{ margin:0; padding-left:20px; columns:2; column-gap:32px; }} .toc li {{ margin:8px 0; }}
  .toc a {{ font-family:var(--sans); font-size:15px; color:var(--body); text-decoration:none; }}
  .toc a:hover {{ color:var(--brand); }}

  p {{ margin:0 0 26px; color:var(--body); }}
  .seo-intro {{ font-size:22px; line-height:1.75; color:#1B2536; }}
  h2 {{ font-family:var(--display); font-size:33px; font-weight:700; letter-spacing:-0.01em; color:var(--ink); margin:52px 0 16px; scroll-margin-top:90px; }}
  h3 {{ font-family:var(--sans); font-size:20px; font-weight:700; color:var(--ink); margin:32px 0 10px; }}
  ul,ol {{ margin:0 0 26px; padding-left:24px; }} li {{ margin:10px 0; }}
  a {{ color:var(--brand); text-underline-offset:2px; }}
  figure {{ margin:34px 0; }} figure img {{ width:100%; border-radius:6px; }}
  figure figcaption {{ font-family:var(--sans); font-size:12.5px; color:var(--faint); text-align:center; margin-top:9px; }}

  /* Trust badges — short benefit statements as a pill row, not bare headings */
  .trust-badges {{ display:flex; flex-wrap:wrap; gap:10px; margin:0 0 40px; }}
  .trust-badge {{ display:inline-flex; align-items:center; gap:8px; padding:10px 16px; border-radius:999px;
    background:var(--soft); border:1px solid var(--line); font-family:var(--sans); font-size:13.5px;
    font-weight:600; color:var(--navy); }}
  .trust-badge svg {{ color:var(--brand); flex-shrink:0; }}

  .faq-section {{ margin-top:14px; }}
  .faq-item {{ border-bottom:1px solid var(--line); padding:6px 2px; margin:0; background:transparent; }}
  .faq-item summary {{
    display:flex; align-items:center; justify-content:space-between; gap:16px;
    padding:18px 2px; margin:0; font-size:19px; font-family:var(--display); font-weight:700;
    color:var(--ink); cursor:pointer; list-style:none; user-select:none;
  }}
  .faq-item summary::-webkit-details-marker {{ display:none; }}
  .faq-item summary::after {{
    content:''; flex-shrink:0; width:11px; height:11px; margin-right:6px;
    border-right:2px solid var(--muted); border-bottom:2px solid var(--muted);
    transform:rotate(45deg); transition:transform .2s ease; margin-top:-4px;
  }}
  .faq-item[open] summary::after {{ transform:rotate(-135deg); margin-top:2px; }}
  .faq-item summary:hover {{ color:var(--brand); }}
  .faq-item p {{ margin:0 0 22px; font-size:18px; color:var(--muted); }}

  /* Pull quote — the CTA line, styled light so it doesn't compete with the
     real conversion box (.contact-card) further down the page. */
  .pull-quote {{ margin:52px 0 0; padding:8px 0 8px 26px; border-left:4px solid var(--brand); }}
  .pull-quote p {{ font-family:var(--display); font-size:24px; font-weight:700; line-height:1.4; margin:0; color:var(--ink); }}

  .contact-card {{ margin:52px 0 0; padding:40px 32px; background:var(--navy); color:#fff; border-radius:6px; text-align:center; scroll-margin-top:90px; }}
  .contact-card .cc-l {{ font-family:var(--display); font-size:26px; font-weight:800; margin-bottom:8px; color:#fff; }}
  .contact-card p {{ font-family:var(--sans); font-size:15px; color:rgba(255,255,255,0.8); margin:0 auto 24px; max-width:440px; }}
  .cc-actions {{ display:flex; gap:14px; justify-content:center; flex-wrap:wrap; }}
  .cc-btn {{ font-family:var(--sans); font-size:15px; font-weight:700; text-decoration:none; padding:14px 26px; border-radius:3px; background:#fff; color:var(--navy); letter-spacing:.02em; border:none; cursor:pointer; }}
  .cc-btn.ghost {{ background:transparent; color:#fff; border:1.5px solid rgba(255,255,255,0.5); }}
  .cc-btn:hover {{ opacity:.92; }}

  /* Lead-capture dialog, opened by the "Get a Free Quote" button */
  .lead-dialog {{ border:none; border-radius:8px; padding:32px; width:min(90vw, 380px); box-shadow:0 20px 60px rgba(0,0,0,0.25); }}
  .lead-dialog::backdrop {{ background:rgba(15,23,42,0.55); }}
  .ld-close {{ position:absolute; top:14px; right:14px; width:28px; height:28px; border:none; border-radius:50%; background:var(--soft);
    color:var(--muted); font-size:14px; cursor:pointer; display:flex; align-items:center; justify-content:center; }}
  .ld-close:hover {{ background:var(--line); }}
  .ld-title {{ font-family:var(--display); font-size:21px; font-weight:800; color:var(--ink); margin:0 0 8px; }}
  .ld-sub {{ font-family:var(--sans); font-size:13.5px; color:var(--muted); margin:0 0 20px; }}
  .cc-form {{ display:flex; flex-direction:column; gap:10px; }}
  .cc-form input {{ font-family:var(--sans); font-size:14px; padding:11px 12px; border-radius:4px; border:1px solid var(--line);
    background:#fff; color:var(--ink); width:100%; box-sizing:border-box; }}
  .cc-form input:focus {{ outline:none; border-color:var(--brand); }}
  .cc-form .cc-btn {{ background:var(--brand); color:#fff; padding:12px 18px; font-size:14px; }}
  .cc-form-msg {{ font-family:var(--sans); font-size:13.5px; color:var(--ink); margin-top:14px; display:none; text-align:center; }}
  .cc-form-msg.show {{ display:block; }}

  .bio {{ display:flex; gap:16px; align-items:flex-start; margin:44px 0 0; padding:24px; background:var(--soft); border-radius:6px; }}
  .bio .name {{ font-family:var(--sans); font-weight:700; font-size:15px; color:var(--ink); }}
  .bio .txt {{ font-family:var(--sans); font-size:13.5px; color:var(--muted); margin-top:5px; line-height:1.6; }}

  footer {{ border-top:1px solid var(--line); margin-top:22px; background:var(--bg); color:var(--body); font-family:var(--sans); }}
  .foot-main {{ padding:48px 30px 28px; display:grid; grid-template-columns:1.9fr 0.85fr 0.85fr 1fr; gap:32px; align-items:start; }}
  .foot-col img {{ height:40px; width:auto; display:block; margin-bottom:14px; }}
  .foot-brand p {{ font-size:13.5px; line-height:1.75; color:var(--muted); margin:0 0 16px; }}
  .foot-socials {{ display:flex; gap:9px; margin-bottom:16px; }}
  .foot-socials a {{ width:29px; height:29px; border-radius:50%;
    display:inline-flex; align-items:center; justify-content:center; transition:transform .15s; }}
  .foot-socials a:hover {{ transform:translateY(-2px); }}
  .dmca-badge {{ display:inline-flex; border-radius:3px; overflow:hidden; font-family:var(--sans); font-size:10px; font-weight:800; letter-spacing:.03em; }}
  .dmca-badge span:first-child {{ background:#3BA9C9; color:#fff; padding:4px 7px; }}
  .dmca-badge span:last-child {{ background:#111; color:#fff; padding:4px 7px; }}
  .foot-h {{ font-family:var(--display); font-size:19px; font-weight:800; color:var(--navy); margin-bottom:16px; }}
  .foot-col ul {{ list-style:none; margin:0; padding:0; display:flex; flex-direction:column; gap:11px; }}
  .foot-col ul li {{ position:relative; padding-left:14px; }}
  .foot-col ul li::before {{ content:''; position:absolute; left:0; top:9px; width:5px; height:5px; border-radius:50%; background:var(--navy); }}
  .foot-col ul a {{ font-family:var(--serif); font-size:15px; color:var(--body); text-decoration:none; }}
  .foot-col ul a:hover {{ color:var(--brand); }}
  .foot-contact-block {{ display:flex; flex-direction:column; gap:9px; margin-bottom:6px; }}
  .foot-contact-block a {{ font-family:var(--serif); font-size:15px; color:var(--body); text-decoration:none; }}
  .foot-contact-block a:hover {{ color:var(--brand); }}
  .foot-address {{ font-family:var(--serif); font-size:14.5px; color:var(--muted); line-height:1.6; }}
  .foot-bottom {{ padding:22px 30px; border-top:1px solid var(--line); text-align:center; font-size:13px; color:var(--faint); }}
  .disclaimer-h {{ font-family:var(--display); font-size:17px; font-weight:800; color:var(--ink); margin:20px 0 8px; }}
  .foot-bottom p {{ margin:0; font-size:11.5px; max-width:640px; margin-left:auto; margin-right:auto; }}
  @media (max-width:800px) {{ .foot-main {{ grid-template-columns:1fr 1fr; }} }}
  @media (max-width:500px) {{ .foot-main {{ grid-template-columns:1fr; }} }}

  /* "Find us on" map/social row (below footer) */
  .map-section {{ background:var(--bg); border-top:1px solid var(--line); padding:28px 30px 36px; text-align:center; }}
  .map-h {{ font-family:var(--display); font-size:17px; font-weight:700; color:var(--ink); margin-bottom:18px; }}
  .map-icons {{ display:flex; justify-content:center; gap:12px; flex-wrap:wrap; }}
  .map-icons a {{ width:42px; height:42px; border-radius:50%; display:flex; align-items:center; justify-content:center;
    color:#fff; font-family:var(--sans); font-weight:800; font-size:15px; text-decoration:none; transition:transform .15s; }}
  .map-icons a:hover {{ transform:translateY(-2px); }}

  .ad-slot {{ margin:8px 0 38px; min-height:0; overflow:hidden; }}

  @media (max-width:600px) {{ body {{ font-size:18px; }} article {{ padding:34px 18px 30px; }} .topbar {{ padding:8px 16px; }} .topbar .mail {{ font-size:12px; }} .toc ol {{ columns:1; }} }}
</style>
</head>
<body>
{gtm_body}
  <div class="progress" id="pb"></div>
  {_social_bar()}
  <div class="nav">
    <a class="brand" href="{WEBSITE}" target="_blank" rel="noreferrer"><img src="/static/zeorbit-logo.png" alt="ZeOrbit" /></a>
    <a class="cta" href="tel:{PHONE}">✆ {PHONE_DISPLAY}</a>
  </div>

  {hero}

  <article>
    {f'<span class="eyebrow">{location}</span>' if location else ''}
    <h1>{h1}</h1>
    <div class="byline">
      <div>
        <div class="who">{biz or 'ZeOrbit'} Editorial Team</div>
        <div class="sub">{mins} min read · Local guide</div>
      </div>
    </div>
    {quick}
    {toc_html}
    {ad_unit}
    {body}
    <div class="contact-card" id="contact">
      <div class="cc-l">Ready to get started?</div>
      <p>Speak with our team for a free, no-obligation consultation on your {biz.lower() or 'project'}.</p>
      <div class="cc-actions">
        <a class="cc-btn" href="tel:{PHONE}">✆ {PHONE_DISPLAY}</a>
        <button type="button" class="cc-btn ghost" id="ccOpenDialog">Get a Free Quote</button>
      </div>
    </div>

    <dialog class="lead-dialog" id="leadDialog">
      <button type="button" class="ld-close" id="ccCloseDialog" aria-label="Close">✕</button>
      <div class="ld-title">Get a Free Quote</div>
      <p class="ld-sub">Leave your email and phone number — our team will reach out shortly.</p>
      <form class="cc-form" id="ccLeadForm">
        <input type="email" name="email" placeholder="Your email" required />
        <input type="tel" name="phone" placeholder="Phone number" required />
        <button type="submit" class="cc-btn">Send</button>
      </form>
      <div class="cc-form-msg" id="ccLeadMsg"></div>
    </dialog>
    <div class="bio">
      <div>
        <div class="name">{biz or 'ZeOrbit'} Editorial Team</div>
        <div class="txt">Local {biz.lower() or 'service'} specialists serving {location or 'your area'}. Published and maintained by ZeOrbit — a U.S.-based web design, software &amp; SEO company.</div>
      </div>
    </div>
  </article>

  {_footer()}

  <script>
    var pb=document.getElementById('pb');
    addEventListener('scroll',function(){{
      var h=document.documentElement, max=h.scrollHeight-h.clientHeight;
      pb.style.width=(max>0?(h.scrollTop/max*100):0)+'%';
    }});

    var leadDialog=document.getElementById('leadDialog');
    var ccOpenBtn=document.getElementById('ccOpenDialog');
    var ccCloseBtn=document.getElementById('ccCloseDialog');
    var ccForm=document.getElementById('ccLeadForm');
    if(leadDialog && ccOpenBtn){{
      ccOpenBtn.addEventListener('click', function(){{ leadDialog.showModal(); }});
      ccCloseBtn.addEventListener('click', function(){{ leadDialog.close(); }});
      leadDialog.addEventListener('click', function(e){{ if(e.target===leadDialog) leadDialog.close(); }});
    }}
    if(ccForm){{
      ccForm.addEventListener('submit', function(e){{
        e.preventDefault();
        var btn=ccForm.querySelector('button');
        btn.disabled=true; btn.textContent='Sending…';
        fetch('/api/leads/', {{
          method:'POST',
          headers:{{'Content-Type':'application/json'}},
          body:JSON.stringify({{
            source:'public_page',
            email: ccForm.email.value.trim(),
            phone: ccForm.phone.value.trim(),
            website: {json.dumps(WEBSITE)},
            location: {json.dumps(location)},
            service: {json.dumps(biz)},
            message: 'Lead captured from public SEO page: ' + window.location.href
          }})
        }}).then(function(r){{ if(!r.ok) throw new Error('bad status'); return r.json(); }})
          .then(function(){{
            ccForm.style.display='none';
            var msg=document.getElementById('ccLeadMsg');
            msg.textContent="Thanks! We'll be in touch shortly.";
            msg.classList.add('show');
          }})
          .catch(function(){{
            btn.disabled=false; btn.textContent='Send';
            var msg=document.getElementById('ccLeadMsg');
            msg.textContent='Something went wrong — please call us instead.';
            msg.classList.add('show');
          }});
      }});
    }}
  </script>
</body>
</html>"""
