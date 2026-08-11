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

# Real ZeOrbit profile URLs — single source of truth, reused by both lists below.
_URL_FACEBOOK = "https://www.facebook.com/zeorbit.web.designers.mobileapp.developers"
_URL_X = "https://twitter.com/orbit_ze"
_URL_LINKEDIN = "https://www.linkedin.com/company/zeorbit/"
_URL_INSTAGRAM = "https://www.instagram.com/zeorbit/"
_URL_YOUTUBE = "https://www.youtube.com/@ZeOrbit-Firm/"
_URL_PINTEREST = "https://www.pinterest.com/zeorbitsd/"
_URL_APPLE_MAPS = "https://maps.apple/p/VA-_LREgJ5PzDV"
_URL_GOOGLE_MAPS = "https://maps.app.goo.gl/teVefHUc3yycwkcA7"
_URL_YELP = "https://www.yelp.com/biz/zeorbit-san-diego-2"

# (url, svg_path, brand_color) — official brand colors
_SOCIALS = [
    (_URL_FACEBOOK, _FB_PATH, "#1877F2"),
    (_URL_X, _X_PATH, "#000000"),
    (_URL_LINKEDIN, _LI_PATH, "#0A66C2"),
    (_URL_INSTAGRAM, _IG_PATH, "#E1306C"),
    (_URL_YOUTUBE, _YT_PATH, "#FF0000"),
    (_URL_PINTEREST, _PIN_PATH, "#E60023"),
]

# Icon-only "Find us on" row (below-footer credit strip) — brand-colored circles.
_MAP_ICONS = [
    ("Apple Maps", _URL_APPLE_MAPS, "#3A3A3C", _APPLE_PATH),
    ("Google", _URL_GOOGLE_MAPS, "#4285F4", None),
    ("Yelp", _URL_YELP, "#D32323", None),
    ("Instagram", _URL_INSTAGRAM, "#C6288E", _IG_PATH),
    ("LinkedIn", _URL_LINKEDIN, "#0A66C2", _LI_PATH),
    ("Facebook", _URL_FACEBOOK, "#1877F2", _FB_PATH),
    ("X", _URL_X, "#000000", _X_PATH),
    ("YouTube", _URL_YOUTUBE, "#FF0000", _YT_PATH),
    ("Pinterest", _URL_PINTEREST, "#E60023", _PIN_PATH),
]


def _social_bar() -> str:
    # Brand-colored circles + white glyphs (X stays black circle so it reads on the bar)
    icons = "".join(
        f'<a class="tb-social" href="{url}" target="_blank" rel="noreferrer" aria-label="social" '
        f'style="background:{c}">'
        f'<svg width="13" height="13" viewBox="0 0 24 24" fill="#fff"><path d="{d}"/></svg></a>'
        for url, d, c in _SOCIALS
    )
    return (f'<div class="topbar">'
            f'<div class="topbar-l">'
            f'<a class="mail" href="mailto:{EMAIL}">✉ {EMAIL}</a>'
            f'<a class="mail tel" href="tel:{PHONE}">✆ {PHONE_DISPLAY}</a>'
            f'</div>'
            f'<div class="socials">{icons}</div></div>')


def _share_bar(public_url: str, title: str, image_url: str = "") -> str:
    """Share row below the article — same networks as the topbar, posting this page URL."""
    from urllib.parse import quote

    url = (public_url or "").strip()
    if not url or "example.com" in url.lower():
        return ""
    t = (title or "").strip()
    u = quote(url, safe="")
    qt = quote(t, safe="")
    media = quote(image_url, safe="") if image_url else ""
    pin = (
        f"https://pinterest.com/pin/create/button/?url={u}&description={qt}"
        + (f"&media={media}" if media else "")
    )
    # Official brand colors (filled circles, white glyphs)
    items = [
        ("Share on Facebook", f"https://www.facebook.com/sharer/sharer.php?u={u}&quote={qt}", _FB_PATH, "#1877F2", None),
        ("Share on X", f"https://twitter.com/intent/tweet?url={u}&text={qt}", _X_PATH, "#000000", None),
        ("Share on LinkedIn", f"https://www.linkedin.com/sharing/share-offsite/?url={u}", _LI_PATH, "#0A66C2", None),
        ("Share on Instagram", _URL_INSTAGRAM, _IG_PATH, None, "linear-gradient(45deg,#f09433 0%,#e6683c 25%,#dc2743 50%,#cc2366 75%,#bc1888 100%)"),
        ("Share on YouTube", _URL_YOUTUBE, _YT_PATH, "#FF0000", None),
        ("Share on Pinterest", pin, _PIN_PATH, "#E60023", None),
        (
            "Share by email",
            f"mailto:?subject={quote('I wanted to share this article with you', safe='')}&body={u}",
            "M20 4H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 4l-8 5-8-5V6l8 5 8-5v2z",
            "#EA4335",
            None,
        ),
    ]
    buttons = []
    for label, href, path, solid, gradient in items:
        bg = f"background:{gradient};" if gradient else f"background:{solid};"
        buttons.append(
            f'<a class="share-btn" href="{href}" target="_blank" rel="noopener noreferrer" '
            f'aria-label="{label}" title="{label}" style="{bg}">'
            f'<svg width="18" height="18" viewBox="0 0 24 24" fill="#fff"><path d="{path}"/></svg></a>'
        )
    return (
        f'<div class="share-bar" aria-label="Share this article">'
        f'<div class="share-label">Share</div>'
        f'<div class="share-icons">{"".join(buttons)}</div></div>'
    )

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
    """Premium multi-section footer: CTA → trust → nav grid → legal bar."""
    socials = "".join(
        f'<a class="ft-social" href="{url}" target="_blank" rel="noreferrer" aria-label="social" '
        f'style="background:{c};border-color:{c};color:#fff">'
        f'<svg width="14" height="14" viewBox="0 0 24 24" fill="#fff"><path d="{d}"/></svg></a>'
        for url, d, c in _SOCIALS
    )

    # Reuse existing ZeOrbit destinations — remapped into clearer nav groups.
    services = [
        ("Web Design", f"{WEBSITE}/web-development/"),
        ("SEO Services", f"{WEBSITE}/seo-development/"),
        ("Mobile Apps", f"{WEBSITE}/app-development/"),
        ("WordPress Solutions", f"{WEBSITE}/wordpress-web-builder-solutions/"),
        ("Ecommerce Stores", f"{WEBSITE}/ecommerce-store-management/"),
        ("AI Consulting", f"{WEBSITE}/ai-consulting-strategy-development/"),
    ]
    resources = [
        ("Blog", f"{WEBSITE}/blog/"),
        ("Portfolio", f"{WEBSITE}/portfolio/"),
        ("Locations", f"{WEBSITE}/locations/"),
        ("App Timeline Guide", f"{WEBSITE}/app-development-timeline-duration-for-designing-developing-and-launching-your-app/"),
        ("Hosting & Domains", f"{WEBSITE}/web-hosting-and-domain-services/"),
    ]
    company = [
        ("About ZeOrbit", WEBSITE),
        ("Contact", f"{WEBSITE}/contact/"),
        ("Privacy Policy", f"{WEBSITE}/privacy-policy/"),
        ("Terms of Service", f"{WEBSITE}/privacy-policy/"),
    ]

    def _links(items):
        return "".join(
            f'<li><a href="{url}" target="_blank" rel="noreferrer">{label}</a></li>'
            for label, url in items
        )

    return f"""
  <section class="prefoot" aria-label="Get started">
    <div class="ft-shell prefoot-inner">
      <div class="prefoot-copy">
        <p class="prefoot-kicker">Next step</p>
        <h2 class="prefoot-h">Want a clearer plan for your site?</h2>
        <p class="prefoot-p">Talk with ZeOrbit about web design, SEO, and local visibility — no pressure, just a practical next step.</p>
      </div>
      <div class="prefoot-actions">
        <a class="call-now-btn" href="tel:6197249517">CALL NOW : 619-724-9517</a>
        <button type="button" class="prefoot-btn prefoot-btn-ghost" id="ccOpenDialogFooter">Get a Free Quote</button>
      </div>
    </div>
  </section>

  <footer class="site-footer">
    <div class="ft-shell">
      <div class="ft-trust" aria-label="What we help with">
        <span class="ft-trust-label">Trusted by businesses looking to improve</span>
        <ul class="ft-trust-list">
          <li>SEO</li>
          <li>Performance</li>
          <li>Web Design</li>
          <li>Digital Growth</li>
        </ul>
      </div>

      <div class="ft-grid">
        <div class="ft-brand">
          <a class="ft-logo" href="{WEBSITE}" target="_blank" rel="noreferrer">
            <img src="/static/zeorbit-logo.png" alt="ZeOrbit" />
          </a>
          <p class="ft-brand-p">Helping businesses improve their visibility, websites, and digital growth with smarter SEO tools and strategies.</p>
          <div class="ft-socials">{socials}</div>
          <div class="ft-contact-mini">
            <a href="tel:{PHONE}">{PHONE_DISPLAY}</a>
            <a href="mailto:{EMAIL}">{EMAIL}</a>
            <span>{ADDRESS}</span>
          </div>
        </div>

        <details class="ft-col" open>
          <summary class="ft-h">Services</summary>
          <ul>{_links(services)}</ul>
        </details>

        <details class="ft-col" open>
          <summary class="ft-h">Resources</summary>
          <ul>{_links(resources)}</ul>
        </details>

        <details class="ft-col" open>
          <summary class="ft-h">Company</summary>
          <ul>{_links(company)}</ul>
        </details>
      </div>
    </div>

    <div class="ft-bottom">
      <div class="ft-shell ft-bottom-inner">
        <div class="ft-copy">© 2026 ZeOrbit. All rights reserved.</div>
        <nav class="ft-legal" aria-label="Legal">
          <a href="{WEBSITE}/privacy-policy/" target="_blank" rel="noreferrer">Privacy Policy</a>
          <a href="{WEBSITE}/privacy-policy/" target="_blank" rel="noreferrer">Terms of Service</a>
          <a href="{WEBSITE}/privacy-policy/" target="_blank" rel="noreferrer">Cookie Policy</a>
        </nav>
      </div>
      <div class="ft-shell ft-disclaimer">
        <p>All images and content are the property of their respective owners. All referenced content is sourced from its original creators.</p>
      </div>
    </div>
  </footer>"""


def _below_footer() -> str:
    """Deprecated strip — kept as no-op so older call sites remain safe."""
    return ""


def _esc(s: str) -> str:
    return html.escape(s or "", quote=True)


def _read_time(block: SEOBlock) -> int:
    text = " ".join([block.content or "", " ".join(block.h2s or []),
                     " ".join(f"{f.question} {f.answer}" for f in (block.faqs or []))])
    return max(1, round(len(re.findall(r"\w+", text)) / 200))


def _short_nav_label(text: str) -> str:
    """Short in-page nav label — never truncated with ellipsis."""
    t = re.sub(r"<[^>]+>", "", text or "").strip()
    t = re.sub(r"\s+", " ", t)
    lower = t.lower()
    if "cost" in lower or "price" in lower or "pricing" in lower:
        return "Pricing"
    if "benefit" in lower:
        return "Benefits"
    if "worth" in lower:
        return "Worth It"
    if "best" in lower:
        return "Best Fit"
    if "how long" in lower or "timeline" in lower or "take" in lower:
        return "Timeline"
    if "process" in lower or "how we" in lower:
        return "Process"
    if "faq" in lower or "frequently" in lower:
        return "FAQ"
    if "customer" in lower or "lead" in lower or "get more" in lower:
        return "Customers"
    if "what does" in lower or "what is" in lower or "do in" in lower:
        return "Services"
    if "why" in lower or "choose" in lower:
        return "Why Us"
    t = re.sub(
        r"^(what are|what makes|what is|how much does|how long does|how do|is|are|why|when)\s+",
        "",
        t,
        flags=re.I,
    )
    t = re.sub(r"^(the|a|an)\s+", "", t, flags=re.I).strip(" ?|")
    if " in " in t.lower():
        t = re.split(r"\s+in\s+", t, maxsplit=1, flags=re.I)[0].strip()
    # Keep at most two short words — no ellipsis
    words = [w for w in re.findall(r"[A-Za-z0-9]+", t) if w]
    if not words:
        return "Section"
    return " ".join(words[:2])


def render_public_html(block: SEOBlock, public_url: str = "") -> str:
    body = _build_content_html(block)
    # Old generated schema used example.com — rewrite to the real public page URL.
    if public_url:
        body = re.sub(
            r"https?://(?:www\.)?example\.(?:com|org)[^\s\"'<>]*",
            public_url,
            body,
            flags=re.I,
        )
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

    # Center nav stays on this page — never send users to WordPress/zeorbit.com.
    mid_links = [('<a href="#overview">Overview</a>')]
    content_secs = [(hid, h) for hid, h in toc if "frequently asked" not in h.lower()]
    for hid, h in content_secs[:3]:
        mid_links.append(f'<a href="#{hid}">{_esc(_short_nav_label(h))}</a>')
    if block.faqs:
        mid_links.append('<a href="#faq-heading">FAQ</a>')
    mid_links.append('<a href="#contact">Contact</a>')
    nav_mid_html = "\n      ".join(mid_links)

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
    verify_token = (getattr(settings, "GSC_VERIFICATION_META", "") or "").strip()
    verify_meta = (
        f'<meta name="google-site-verification" content="{_esc(verify_token)}" />'
        if verify_token else ""
    )
    share_bar = _share_bar(public_url, block.title or block.h1 or "", featured)

    return f"""<!doctype html>
<html lang="en">
<head>
{gtm_head}
{adsense_head}
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>{title}</title>
<meta name="description" content="{desc}" />
{verify_meta}
<meta property="og:type" content="article" />
<meta property="og:title" content="{title}" />
<meta property="og:description" content="{desc}" />
{og_img}
{canonical_tag}
<meta name="robots" content="index,follow" />
<link rel="icon" type="image/png" href="/static/zeorbit-logo.png" />
<link rel="apple-touch-icon" href="/static/zeorbit-logo.png" />
<style>
  :root {{
    --brand:#2563EB; --brand-dark:#1D4ED8; --navy:#0B1F3A; --signal:#38BDF8;
    --ink:#0B1220; --body:#2A2A2A; --muted:#5B6676; --faint:#8A94A6;
    --line:#E6E3DD; --bg:#FFFFFF; --soft:#F7F5F1;
    /* Apple system font stack (SF Pro on Apple devices) */
    --apple:-apple-system,BlinkMacSystemFont,'SF Pro Text','SF Pro Display','Helvetica Neue',Helvetica,Arial,sans-serif;
    --sans:var(--apple);
    --serif:var(--apple);
    --display:var(--apple);
  }}
  * {{ box-sizing:border-box; }}
  html {{ scroll-behavior:smooth; }}
  body {{ margin:0; background:var(--bg); color:var(--body); font-family:var(--apple); font-size:19px; line-height:1.85; -webkit-font-smoothing:antialiased; }}
  .sr-only {{ position:absolute; width:1px; height:1px; padding:0; margin:-1px; overflow:hidden; clip:rect(0,0,0,0); white-space:nowrap; border:0; }}

  /* Black utility bar */
  .topbar {{ display:flex; align-items:center; justify-content:space-between; background:#0A0A0A; color:#fff; padding:10px 28px; font-family:var(--apple); }}
  .topbar-l {{ display:flex; align-items:center; gap:20px; flex-wrap:wrap; }}
  .topbar .mail {{ color:#fff; text-decoration:none; font-size:13px; opacity:.9; }}
  .topbar .mail:hover {{ opacity:1; }}
  .topbar .tel {{ font-weight:600; }}
  .topbar .socials {{ display:flex; gap:8px; align-items:center; }}
  .topbar .socials a.tb-social {{
    display:inline-flex; align-items:center; justify-content:center;
    width:26px; height:26px; border-radius:50%; opacity:.95;
    border:1px solid rgba(255,255,255,0.22);
    transition:opacity .15s, transform .15s;
  }}
  .topbar .socials a.tb-social:hover {{ opacity:1; transform:translateY(-1px); }}

  /* Header — compact logo | center links | call */
  .nav {{ position:sticky; top:0; z-index:10; display:grid; grid-template-columns:1fr auto 1fr; align-items:center; gap:10px;
          padding:8px 20px; background:rgba(255,255,255,0.96); backdrop-filter:blur(12px); border-bottom:1px solid var(--line);
          font-family:var(--apple); min-height:0; }}
  .brand {{ display:inline-flex; align-items:center; text-decoration:none; justify-self:start; }}
  .brand img {{ height:24px; width:auto; display:block; }}
  .nav-mid {{ display:flex; align-items:center; justify-content:center; gap:2px 14px; flex-wrap:nowrap; }}
  .nav-mid a {{
    font-family:var(--apple); font-size:11px; font-weight:600; color:var(--ink); text-decoration:none;
    text-transform:uppercase; letter-spacing:.06em; padding:4px 0; border-bottom:2px solid transparent;
    transition:color .15s, border-color .15s; white-space:nowrap;
  }}
  .nav-mid a:hover {{ color:var(--brand); border-bottom-color:var(--brand); }}
  .nav .cta {{
    font-family:var(--apple); font-size:11px; font-weight:600; color:#fff; background:#F33A3A;
    padding:8px 14px; border-radius:20px; text-decoration:none; letter-spacing:.06em;
    flex-shrink:0; transition:background .15s, transform .15s; justify-self:end;
    border:1px solid #fff; text-align:center; text-transform:uppercase; white-space:nowrap;
  }}
  .nav .cta:hover {{ background:#E02828; }}
  .progress {{ position:fixed; top:0; left:0; height:2px; width:0; background:#F33A3A; z-index:20; }}

  @media (max-width:800px) {{
    .nav {{ grid-template-columns:1fr auto; }}
    .nav-mid {{ display:none; }}
  }}
  @media (max-width:640px) {{
    .topbar {{ padding:8px 16px; }}
    .nav {{ padding:7px 14px; gap:10px; }}
    .brand img {{ height:22px; }}
    .nav .cta {{ padding:7px 12px; font-size:10px; }}
  }}

  /* Content — wider column so less empty left/right space on desktop */
  article {{ max-width:1080px; width:100%; margin:0 auto; padding:40px 28px 40px; box-sizing:border-box; }}
  .eyebrow {{ display:inline-block; font-family:var(--sans); font-size:12px; font-weight:600; text-transform:uppercase; letter-spacing:.14em; color:var(--ink); border:1.5px solid var(--ink); padding:9px 22px; border-radius:999px; margin-bottom:26px; }}
  h1 {{ font-family:var(--display); font-size:clamp(32px,5vw,48px); line-height:1.12; font-weight:800; letter-spacing:-0.02em; color:var(--ink); margin:0 0 20px; }}
  .byline {{ display:flex; align-items:center; gap:12px; font-family:var(--sans); margin:0 0 28px; }}
  .byline .who {{ font-size:14px; font-weight:600; color:var(--ink); }}
  .byline .sub {{ font-size:13px; color:var(--faint); }}
  /* Banner — full width of article column */
  .hero-wrap {{
    width:100%; margin:0 0 28px; max-height:min(52vh, 480px); overflow:hidden; position:relative;
    background:var(--soft); border-radius:14px; border:1px solid var(--line);
  }}
  .hero-wrap img {{ width:100%; height:100%; min-height:240px; max-height:min(52vh, 480px); object-fit:cover; display:block; }}
  .hero-wrap::after {{ content:''; position:absolute; inset:0; background:linear-gradient(180deg, rgba(0,0,0,0) 55%, rgba(11,18,32,0.22) 100%); pointer-events:none; border-radius:inherit; }}
  @media (max-width:640px) {{
    .hero-wrap {{ border-radius:10px; }}
    article {{ padding:28px 16px 24px; }}
    .hero-wrap img {{ min-height:180px; }}
  }}

  .quick {{ background:var(--soft); border-left:4px solid var(--navy); border-radius:4px; padding:18px 22px; margin:0 0 28px; }}
  .quick-l {{ font-family:var(--sans); font-size:11px; font-weight:700; text-transform:uppercase; letter-spacing:.1em; color:var(--navy); margin-bottom:6px; }}
  .quick p {{ margin:0; font-size:18px; color:var(--ink); line-height:1.55; }}

  .toc {{ border-top:1px solid var(--line); border-bottom:1px solid var(--line); padding:18px 4px; margin:0 0 32px; }}
  .toc-title {{ font-family:var(--sans); font-size:12px; font-weight:700; text-transform:uppercase; letter-spacing:.1em; color:var(--muted); margin-bottom:12px; }}
  .toc ol {{ margin:0; padding-left:20px; columns:2; column-gap:28px; }} .toc li {{ margin:6px 0; }}
  .toc a {{ font-family:var(--sans); font-size:14px; color:var(--body); text-decoration:none; }}
  .toc a:hover {{ color:var(--brand); }}

  p {{ margin:0 0 22px; color:var(--body); font-size:18px; line-height:1.75; }}
  .seo-intro {{ font-size:20px; line-height:1.7; color:#1B2536; }}
  h2 {{ font-family:var(--display); font-size:clamp(26px,3.5vw,34px); font-weight:700; letter-spacing:-0.015em; color:var(--ink); margin:44px 0 14px; scroll-margin-top:90px; }}
  #overview, #contact, #faq-heading {{ scroll-margin-top:90px; }}
  h3 {{ font-family:var(--sans); font-size:19px; font-weight:700; color:var(--ink); margin:28px 0 10px; }}
  ul,ol {{ margin:0 0 22px; padding-left:24px; }} li {{ margin:8px 0; line-height:1.6; }}
  a {{ color:var(--brand); text-underline-offset:2px; }}

  /* Red highlight CALL NOW buttons — matches zeorbit.com blog CTAs */
  .call-now-wrap {{ text-align:center; margin:28px 0 32px; }}
  .call-now-btn {{
    display:inline-block; background:#F33A3A; color:#fff !important; border:1px solid #fff;
    border-radius:30px; padding:20px 30px; font-family:var(--sans); font-size:20px; font-weight:500;
    line-height:1.15; text-decoration:none !important; text-align:center; text-transform:capitalize;
    transition:background .15s, transform .15s; box-shadow:none;
  }}
  .call-now-btn:hover {{ background:#E02828; transform:translateY(-1px); color:#fff !important; }}
  @media (max-width:640px) {{
    .call-now-btn {{ font-size:16px; padding:16px 22px; width:100%; max-width:340px; box-sizing:border-box; }}
  }}
  figure, .wp-block-image {{
    margin:28px 0; padding:0; background:var(--soft); border:1px solid var(--line); border-radius:12px;
    overflow:hidden; width:100%;
  }}
  figure img, .wp-block-image img {{
    width:100%; max-height:min(48vh, 440px); object-fit:cover; display:block; border-radius:0;
  }}
  figure figcaption, .wp-block-image figcaption {{
    font-family:var(--sans); font-size:12.5px; color:var(--muted); text-align:left;
    margin:0; padding:12px 16px 14px; line-height:1.5; border-top:1px solid var(--line); background:#fff;
  }}

  /* Trust badges */
  .trust-section {{
    margin:48px 0 8px; padding:28px 24px; border:1px solid var(--line); border-radius:12px; background:#fff;
  }}
  .trust-kicker {{
    font-family:var(--sans); font-size:12px; font-weight:700; letter-spacing:.1em; text-transform:uppercase;
    color:var(--muted); margin:0 0 16px;
  }}
  .trust-badges {{ display:flex; flex-wrap:wrap; gap:10px; margin:0; }}
  .trust-badge {{ display:inline-flex; align-items:center; gap:8px; padding:11px 15px; border-radius:8px;
    background:var(--soft); border:1px solid var(--line); font-family:var(--sans); font-size:13.5px;
    font-weight:600; color:var(--navy); }}
  .trust-badge svg {{ color:var(--brand); flex-shrink:0; }}

  .faq-wrap {{
    margin:48px 0 0; padding:32px 28px 18px; border-radius:14px; border:1px solid var(--line);
    background:linear-gradient(180deg, #FBFBFA 0%, #FFFFFF 40%);
  }}
  .faq-wrap > h2 {{ margin-top:0; margin-bottom:8px; }}
  .faq-lead {{
    font-family:var(--sans); font-size:15px; color:var(--muted); margin:0 0 18px; line-height:1.55;
  }}
  .faq-section {{ margin:0; }}
  .faq-item {{
    border:1px solid var(--line); border-radius:10px; padding:0; margin:0 0 10px; background:#fff;
    overflow:hidden;
  }}
  .faq-item summary {{
    display:flex; align-items:center; justify-content:space-between; gap:16px;
    padding:16px 18px; margin:0; font-size:17px; font-family:var(--sans); font-weight:700;
    color:var(--ink); cursor:pointer; list-style:none; user-select:none; line-height:1.35;
  }}
  .faq-item summary::-webkit-details-marker {{ display:none; }}
  .faq-item summary::after {{
    content:''; flex-shrink:0; width:10px; height:10px; margin-right:2px;
    border-right:2px solid var(--muted); border-bottom:2px solid var(--muted);
    transform:rotate(45deg); transition:transform .2s ease; margin-top:-4px;
  }}
  .faq-item[open] summary {{ border-bottom:1px solid var(--line); }}
  .faq-item[open] summary::after {{ transform:rotate(-135deg); margin-top:2px; }}
  .faq-item summary:hover {{ color:var(--brand); }}
  .faq-item p {{ margin:0; padding:14px 18px 18px; font-size:16px; line-height:1.7; color:var(--muted); font-family:var(--sans); }}

  .end-note {{
    margin:28px 0 0; font-family:var(--sans); font-size:15.5px; line-height:1.6; color:var(--muted);
    padding:0; border:0;
  }}
  .pull-quote {{ display:none; }} /* legacy pages */

  .share-bar {{
    margin:36px 0 8px; padding:18px 0 6px; border-top:1px solid var(--line);
    display:flex; align-items:center; gap:16px; flex-wrap:wrap;
    font-family:var(--sans);
  }}
  .share-label {{
    font-size:12px; font-weight:700; letter-spacing:.1em; text-transform:uppercase; color:var(--faint);
  }}
  .share-icons {{ display:flex; gap:10px; align-items:center; flex-wrap:wrap; }}
  .share-btn {{
    width:40px; height:40px; border-radius:50%; display:inline-flex; align-items:center; justify-content:center;
    color:#fff; text-decoration:none; box-shadow:0 1px 2px rgba(0,0,0,.12);
    transition:transform .15s ease, opacity .15s ease, box-shadow .15s ease;
  }}
  .share-btn:hover {{ transform:translateY(-2px); opacity:.95; box-shadow:0 4px 10px rgba(0,0,0,.18); }}

  .article-end {{
    margin:40px 0 8px; display:grid; gap:16px;
  }}
  .contact-card {{
    margin:0; padding:0; overflow:hidden; border-radius:14px; scroll-margin-top:90px;
    background:var(--navy); color:#fff;
    display:grid; grid-template-columns:1.4fr 1fr; gap:0;
    border:1px solid rgba(11,31,58,0.2);
  }}
  .contact-card .cc-main {{ padding:34px 32px; }}
  .contact-card .cc-side {{
    padding:34px 28px; background:rgba(0,0,0,0.18); border-left:1px solid rgba(255,255,255,0.08);
    display:flex; flex-direction:column; justify-content:center; gap:14px;
  }}
  .contact-card .cc-kicker {{
    font-family:var(--sans); font-size:11px; font-weight:700; letter-spacing:.12em; text-transform:uppercase;
    color:var(--signal); margin:0 0 10px;
  }}
  .contact-card .cc-l {{ font-family:var(--display); font-size:clamp(24px, 3vw, 30px); font-weight:800; margin:0 0 10px; color:#fff; line-height:1.2; }}
  .contact-card p {{ font-family:var(--sans); font-size:15px; color:rgba(255,255,255,0.78); margin:0 0 22px; max-width:460px; line-height:1.6; }}
  .cc-actions {{ display:flex; gap:14px; flex-wrap:wrap; align-items:center; }}
  .cc-actions .call-now-btn {{ padding:16px 26px; font-size:17px; }}
  .cc-btn {{ font-family:var(--sans); font-size:14.5px; font-weight:700; text-decoration:none; padding:13px 20px; border-radius:6px; background:#fff; color:var(--navy); letter-spacing:.01em; border:none; cursor:pointer; display:inline-flex; align-items:center; }}
  .cc-btn.ghost {{ background:transparent; color:#fff; border:1.5px solid rgba(255,255,255,0.35); }}
  .cc-btn:hover {{ opacity:.94; }}
  .cc-side-label {{ font-family:var(--sans); font-size:12px; font-weight:600; letter-spacing:.06em; text-transform:uppercase; color:rgba(255,255,255,0.45); margin:0; }}
  .cc-side a {{ font-family:var(--sans); color:#fff; text-decoration:none; font-size:15px; font-weight:600; }}
  .cc-side a:hover {{ color:var(--signal); }}
  .cc-side .cc-meta {{ font-family:var(--sans); font-size:13.5px; color:rgba(255,255,255,0.62); line-height:1.55; margin:0; }}

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

  @media (max-width:800px) {{
    .contact-card {{ grid-template-columns:1fr; }}
    .contact-card .cc-side {{ border-left:0; border-top:1px solid rgba(255,255,255,0.08); padding-top:22px; }}
    .faq-wrap {{ padding:24px 16px 12px; }}
  }}

  /* ── Premium footer system ───────────────────────────────────── */
  .ft-shell {{ width:100%; max-width:none; margin:0; padding:0 28px; box-sizing:border-box; }}

  .prefoot {{
    margin-top:48px; padding:40px 0;
    background:#0B1F3A;
    color:#fff; border-top:1px solid rgba(255,255,255,0.06);
  }}
  .prefoot-inner {{
    display:flex; align-items:center; justify-content:space-between; gap:28px;
  }}
  .prefoot-kicker {{
    font-family:var(--sans); font-size:11px; font-weight:700; letter-spacing:.12em; text-transform:uppercase;
    color:var(--signal); margin:0 0 8px;
  }}
  .prefoot-h {{
    font-family:var(--sans); font-size:clamp(22px, 2.6vw, 28px); font-weight:800;
    letter-spacing:-0.02em; line-height:1.2; margin:0 0 8px; color:#fff;
  }}
  .prefoot-p {{
    font-family:var(--sans); font-size:14.5px; line-height:1.6; color:rgba(255,255,255,0.68);
    margin:0; max-width:480px;
  }}
  .prefoot-actions {{ display:flex; gap:10px; flex-wrap:wrap; flex-shrink:0; }}
  .prefoot-btn {{
    font-family:var(--sans); font-size:13.5px; font-weight:700; text-decoration:none;
    padding:12px 18px; border-radius:6px; border:1px solid transparent; cursor:pointer;
    display:inline-flex; align-items:center; justify-content:center; letter-spacing:.01em;
    transition:transform .15s, background .15s, border-color .15s, color .15s;
  }}
  .prefoot-btn-primary {{ background:#fff; color:#0B1F3A; }}
  .prefoot-btn-primary:hover {{ transform:translateY(-1px); background:#F3F4F6; }}
  .prefoot-btn-ghost {{ background:transparent; color:#fff; border-color:rgba(255,255,255,0.28); }}
  .prefoot-btn-ghost:hover {{ border-color:rgba(255,255,255,0.55); background:rgba(255,255,255,0.06); }}

  .site-footer {{
    background: linear-gradient(180deg, #070B14 0%, #05070D 100%);
    color:rgba(255,255,255,0.78); font-family:var(--sans);
    border-top:1px solid rgba(255,255,255,0.05);
  }}

  .ft-trust {{
    display:flex; align-items:center; justify-content:space-between; gap:18px; flex-wrap:wrap;
    padding:22px 0; border-bottom:1px solid rgba(255,255,255,0.08);
  }}
  .ft-trust-label {{
    font-size:12px; font-weight:600; letter-spacing:.08em; text-transform:uppercase;
    color:rgba(255,255,255,0.45);
  }}
  .ft-trust-list {{ list-style:none; margin:0; padding:0; display:flex; flex-wrap:wrap; gap:8px; }}
  .ft-trust-list li {{
    font-size:12.5px; font-weight:600; color:rgba(255,255,255,0.82);
    padding:7px 12px; border:1px solid rgba(255,255,255,0.12); border-radius:999px;
    background:rgba(255,255,255,0.03);
  }}

  .ft-grid {{
    display:grid; grid-template-columns:1.5fr 1fr 1fr 1fr; gap:36px 28px;
    padding:42px 0 36px;
  }}
  .ft-logo {{
    display:inline-flex; align-items:center; margin-bottom:18px;
  }}
  .ft-logo img {{
    height:36px; width:auto; display:block;
  }}
  .ft-brand-p {{
    font-size:14px; line-height:1.7; color:rgba(255,255,255,0.62); margin:0 0 18px; max-width:320px;
  }}
  .ft-socials {{ display:flex; gap:10px; margin-bottom:18px; }}
  .ft-social {{
    width:34px; height:34px; border-radius:999px; display:inline-flex; align-items:center; justify-content:center;
    color:#fff; border:1px solid transparent;
    transition:transform .15s, opacity .15s, filter .15s;
  }}
  .ft-social:hover {{ transform:translateY(-1px); opacity:.92; filter:brightness(1.08); color:#fff; }}
  .ft-contact-mini {{
    display:flex; flex-direction:column; gap:6px; font-size:13px; color:rgba(255,255,255,0.5); line-height:1.5;
  }}
  .ft-contact-mini a {{ color:rgba(255,255,255,0.72); text-decoration:none; }}
  .ft-contact-mini a:hover {{ color:#fff; }}

  .ft-col {{ border:0; margin:0; padding:0; background:transparent; }}
  .ft-col summary {{
    list-style:none; cursor:default; font-family:var(--sans); font-size:12px; font-weight:700;
    letter-spacing:.1em; text-transform:uppercase; color:rgba(255,255,255,0.92); margin:0 0 16px;
  }}
  .ft-col summary::-webkit-details-marker {{ display:none; }}
  .ft-col ul {{ list-style:none; margin:0; padding:0; display:flex; flex-direction:column; gap:11px; }}
  .ft-col a {{
    font-size:14px; color:rgba(255,255,255,0.62); text-decoration:none; line-height:1.4;
    transition:color .15s;
  }}
  .ft-col a:hover {{ color:#fff; }}

  .ft-bottom {{
    border-top:1px solid rgba(255,255,255,0.08);
    padding:18px 0 22px; background:rgba(0,0,0,0.22);
  }}
  .ft-bottom-inner {{
    display:flex; align-items:center; justify-content:space-between; gap:16px; flex-wrap:wrap;
  }}
  .ft-copy {{ font-size:13px; color:rgba(255,255,255,0.48); }}
  .ft-legal {{ display:flex; flex-wrap:wrap; gap:8px 18px; }}
  .ft-legal a {{ font-size:13px; color:rgba(255,255,255,0.55); text-decoration:none; }}
  .ft-legal a:hover {{ color:#fff; }}
  .ft-disclaimer {{ margin-top:12px; }}
  .ft-disclaimer p {{
    margin:0; font-size:11.5px; line-height:1.55; color:rgba(255,255,255,0.35); max-width:760px;
  }}

  @media (max-width:900px) {{
    .prefoot-inner {{ flex-direction:column; align-items:flex-start; }}
    .ft-grid {{ grid-template-columns:1fr 1fr; gap:28px 20px; }}
  }}
  @media (max-width:640px) {{
    .ft-shell {{ padding:0 16px; }}
    .prefoot {{ padding:36px 0 32px; margin-top:40px; }}
    .prefoot-actions {{ width:100%; }}
    .prefoot-btn {{ flex:1; min-height:46px; }}
    .ft-trust {{ flex-direction:column; align-items:flex-start; gap:12px; padding:18px 0; }}
    .ft-grid {{ grid-template-columns:1fr; gap:8px; padding:18px 0 10px; }}
    .ft-brand {{ padding-bottom:18px; border-bottom:1px solid rgba(255,255,255,0.08); margin-bottom:6px; }}
    .ft-col {{ border-bottom:1px solid rgba(255,255,255,0.08); }}
    .ft-col summary {{
      cursor:pointer; display:flex; align-items:center; justify-content:space-between;
      padding:14px 0; margin:0; font-size:13px;
    }}
    .ft-col summary::after {{
      content:''; width:8px; height:8px; border-right:1.5px solid rgba(255,255,255,0.55);
      border-bottom:1.5px solid rgba(255,255,255,0.55); transform:rotate(45deg); transition:transform .2s;
      margin-top:-4px;
    }}
    .ft-col[open] summary::after {{ transform:rotate(-135deg); margin-top:2px; }}
    .ft-col ul {{ padding:0 0 14px; gap:12px; }}
    .ft-col a {{ font-size:15px; display:inline-block; padding:4px 0; min-height:28px; }}
    .ft-bottom-inner {{ flex-direction:column; align-items:flex-start; gap:12px; }}
    .ft-legal {{ gap:10px 14px; }}
  }}

  .ad-slot {{ margin:8px 0 38px; min-height:0; overflow:hidden; }}

  @media (max-width:600px) {{ body {{ font-size:18px; }} article {{ padding:28px 16px 24px; }} .topbar .mail {{ font-size:12px; }} .toc ol {{ columns:1; }} }}
</style>
</head>
<body>
{gtm_body}
  <div class="progress" id="pb"></div>
  {_social_bar()}
  <div class="nav">
    <a class="brand" href="{WEBSITE}" target="_blank" rel="noreferrer">
      <img src="/static/zeorbit-logo.png" alt="ZeOrbit" />
    </a>
    <nav class="nav-mid" aria-label="On this page">
      {nav_mid_html}
    </nav>
    <a class="cta" href="tel:6197249517">CALL NOW : 619-724-9517</a>
  </div>

  {hero}

  <article id="overview">
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
    {share_bar}
    <div class="article-end">
      <div class="contact-card" id="contact">
        <div class="cc-main">
          <div class="cc-kicker">Free consultation</div>
          <div class="cc-l">Ready for a clearer next step?</div>
          <p>Get practical advice on your {biz.lower() or 'project'} — website, SEO, and local visibility — with no obligation.</p>
          <div class="cc-actions">
            <a class="call-now-btn" href="tel:6197249517">CALL NOW : 619-724-9517</a>
            <button type="button" class="cc-btn" id="ccOpenDialog">Get a Free Quote</button>
          </div>
        </div>
        <div class="cc-side">
          <p class="cc-side-label">Talk to ZeOrbit</p>
          <a href="tel:{PHONE}">{PHONE_DISPLAY}</a>
          <a href="mailto:{EMAIL}">{EMAIL}</a>
          <p class="cc-meta">{ADDRESS}</p>
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
    var ccOpenFooter=document.getElementById('ccOpenDialogFooter');
    var ccCloseBtn=document.getElementById('ccCloseDialog');
    var ccForm=document.getElementById('ccLeadForm');
    function openLead(){{ if(leadDialog) leadDialog.showModal(); }}
    if(leadDialog && ccOpenBtn){{
      ccOpenBtn.addEventListener('click', openLead);
      if(ccCloseBtn) ccCloseBtn.addEventListener('click', function(){{ leadDialog.close(); }});
      leadDialog.addEventListener('click', function(e){{ if(e.target===leadDialog) leadDialog.close(); }});
    }}
    if(ccOpenFooter){{ ccOpenFooter.addEventListener('click', openLead); }}
    // Mobile: collapse footer nav groups by default
    if(window.matchMedia('(max-width:640px)').matches){{
      document.querySelectorAll('.ft-col').forEach(function(el){{ el.removeAttribute('open'); }});
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
