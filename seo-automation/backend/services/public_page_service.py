"""
public_page_service.py — renders a saved SEOBlock as a public BLOG article
(served at /p/{slug}) styled to match the ZeOrbit brand site: black utility bar
with email + socials, elegant serif display headlines, outlined pill badges,
inline SVG logo. Self-contained; opens instantly in any browser.
"""
import html
import json
import hashlib
import re
from models.schemas import SEOBlock
from services.wordpress_service import _build_content_html
from config import settings

EMAIL = "info@zeorbit.com"
PHONE = "+16197249517"

def resolve_article_format(block: SEOBlock) -> str:
    """Blogs only: guide | briefing | feature. Empty for service pages."""
    kind = (getattr(block, "content_type", "") or "").lower()
    if kind not in ("blog", "post"):
        return ""
    v = (getattr(block, "layout_variant", "") or "").lower()
    mapping = {
        "guide": "guide", "briefing": "briefing", "feature": "feature",
        "steps": "guide", "checklist": "guide", "timeline": "guide",
        "qa": "briefing", "compare": "briefing", "myths": "briefing",
        "story": "feature", "cards": "feature", "split": "feature",
    }
    if v in mapping:
        return mapping[v]
    slug = (getattr(block, "slug", "") or "") + (getattr(block, "title", "") or "")
    return ("guide", "briefing", "feature")[int(hashlib.md5(slug.encode()).hexdigest(), 16) % 3]


_FORMAT_META = {
    "guide": ("How-to guide", "Step-by-step"),
    "briefing": ("Q&A briefing", "Explainer"),
    "feature": ("Feature story", "Reported"),
}


def _page_chrome_css() -> str:
    return """
  /* ── Location / service PAGE (not a blog) ── */
  body.kind-page { --fmt:#0B1F3A; background:#F4F1EB; }
  body.kind-page .hero-wrap { display:none; }
  body.kind-page .page-hero {
    display:grid; grid-template-columns:1.05fr .95fr; gap:0; align-items:stretch;
    max-width:1180px; margin:18px auto 0; border-radius:24px; overflow:hidden;
    background:#0B1F3A; color:#fff; min-height:420px;
    box-shadow:0 24px 60px rgba(11,31,58,.18);
  }
  body.kind-page .page-hero-copy { padding:48px 44px 44px; display:flex; flex-direction:column; justify-content:center; }
  body.kind-page .page-hero .eyebrow {
    border-color:rgba(255,255,255,.35); color:#7DD3FC; background:transparent; margin-bottom:18px;
  }
  body.kind-page .page-hero h1 { color:#fff; font-size:clamp(30px,4.2vw,46px); margin:0 0 14px; }
  body.kind-page .page-hero .lead { font-size:17px; line-height:1.6; color:rgba(255,255,255,.82); margin:0 0 22px; max-width:34em; }
  body.kind-page .page-hero-actions { display:flex; gap:10px; flex-wrap:wrap; }
  body.kind-page .page-hero-actions a {
    display:inline-flex; align-items:center; justify-content:center; padding:12px 18px; border-radius:999px;
    font-size:14px; font-weight:700; text-decoration:none; letter-spacing:.01em;
    transition:transform .12s cubic-bezier(0.23,1,0.32,1), opacity .12s ease;
  }
  body.kind-page .page-hero-actions a:active { transform:scale(.97); }
  body.kind-page .ph-primary { background:#fff; color:#0B1F3A; }
  body.kind-page .ph-ghost { background:transparent; color:#fff; border:1.5px solid rgba(255,255,255,.4); }
  body.kind-page .page-hero-media { min-height:280px; position:relative; background:#102544; }
  body.kind-page .page-hero-media img { width:100%; height:100%; object-fit:cover; display:block; position:absolute; inset:0; }
  body.kind-page article {
    max-width:920px; background:#fff; margin:-28px auto 0; position:relative; z-index:1;
    border-radius:20px; padding:40px 44px 48px; box-shadow:0 16px 40px rgba(11,31,58,.08);
    border:1px solid #E8E2D8;
  }
  body.kind-page article > .eyebrow, body.kind-page article > h1, body.kind-page article > .byline,
  body.kind-page article > .quick { display:none; }
  body.kind-page .toc {
    background:#F7F5F1; border:0; border-radius:14px; padding:16px 20px; margin:0 0 28px;
  }
  body.kind-page .toc-title { color:#0B1F3A; }
  body.kind-page article h2 {
    font-size:clamp(22px,2.6vw,28px); padding-bottom:8px; border-bottom:2px solid #E8E2D8;
  }
  body.kind-page .trust-badges { display:flex; flex-wrap:wrap; gap:8px; }
  body.kind-page .trust-badge {
    background:#F7F5F1; border:1px solid #E8E2D8; border-radius:999px; padding:8px 12px; font-size:13px;
  }
  body.kind-page .faq-wrap { background:#F7F5F1; border-radius:16px; padding:24px 22px; }
  @media (max-width:840px) {
    body.kind-page .page-hero { grid-template-columns:1fr; min-height:0; margin:12px 12px 0; }
    body.kind-page .page-hero-media { min-height:220px; height:220px; }
    body.kind-page .page-hero-copy { padding:28px 22px 32px; }
    body.kind-page article { margin:16px 12px 0; padding:28px 18px 36px; }
  }
"""


def _format_chrome_css() -> str:
    return """
  /* Three different editorial layouts. Shared type and coral call color only. */
  body.kind-blog { background:#fff; color:#1c1915; }
  body.kind-blog article {
    max-width:1080px; width:min(1080px, calc(100% - 24px)); margin:0 auto; padding:48px 0 72px;
    background:#fff; border-radius:0; box-shadow:none; box-sizing:border-box;
  }
  body.kind-blog .zo-cover {
    position:relative; width:100%; min-height:0; height:auto;
    margin:28px auto 0; overflow:visible; border-radius:0; background:transparent;
  }
  body.kind-blog .zo-cover img {
    position:relative; inset:auto; width:100%; height:auto; min-height:0; max-height:none;
    object-fit:cover; display:block;
  }
  body.kind-blog .zo-cover::after { content:none; }
  body.kind-blog .zo-cover-copy {
    position:relative; z-index:1; width:auto; max-width:none; margin:0;
    padding:0; color:#14120f; box-sizing:border-box;
  }
  body.kind-blog .zo-cover .eyebrow {
    color:#ff5a4e; border:0; background:transparent;
    letter-spacing:.16em; font-size:12px; font-weight:700; margin:0 0 12px;
  }
  body.kind-blog .zo-cover h1 {
    color:#14120f; max-width:16ch; margin:0 0 14px;
    font-size:clamp(40px, 4.6vw, 68px); line-height:.98; letter-spacing:-.045em;
  }
  body.kind-blog .zo-cover .who { color:#14120f; }
  body.kind-blog .zo-cover .sub { color:#6b645c; }
  body.kind-blog .zo-shell {
    width:100%; max-width:none; margin:0 auto; box-sizing:border-box;
    padding:0; display:block;
  }
  body.kind-blog .zo-main {
    background:transparent; border-radius:0; padding:0; box-shadow:none;
  }
  body.kind-blog .article-body h1 {
    font-size:40px; line-height:1.15; letter-spacing:-0.03em; font-weight:700;
    max-width:none; margin:0 0 20px; text-align:left;
  }
  body.kind-blog h1, body.kind-blog .article-body { max-width:none; }
  body.kind-blog .article-body { width:100%; font-size:18px; line-height:1.7; }
  body.kind-blog .article-body p { max-width:none; }
  body.kind-blog .article-body img,
  body.kind-blog .article-footer-image img {
    width:100%; height:420px; object-fit:cover; border-radius:16px; display:block; margin:0 0 24px;
  }
  body.kind-blog .article-body .blog-layout img { height:220px; width:100%; margin:0 0 14px; object-fit:cover; }
  /* Older templates put the whole article in column 1 of a 3-column grid. */
  body.kind-blog .blog-layout {
    border:0 !important; padding:0 !important; background:transparent !important; width:100%;
  }
  body.kind-blog .blog-layout [style*="grid-template-columns"],
  body.kind-blog .blog-layout [style*="display:grid"] {
    display:block !important; width:100% !important;
  }
  section.zo-vcard, section.blog-reach {
    display:flex !important;
    flex-direction:column !important;
    width:100% !important;
    align-items:stretch !important;
  }
  .zo-vcard-row {
    display:grid !important;
    grid-template-columns:1.05fr 1.15fr .9fr !important;
    width:100% !important;
  }
  .zo-vcard-title {
    margin:0 !important;
    padding:18px 22px 4px !important;
    color:#fff !important;
    font-size:20px !important;
    line-height:1.35 !important;
    font-weight:800 !important;
    max-width:none !important;
  }
  body.kind-blog .blog-layout ul,
  body.kind-blog .blog-layout ol { width:100% !important; margin:0 !important; }
  body.kind-blog .blog-layout li { padding:16px 0 !important; }
  body.kind-blog .blog-layout li p { max-width:none !important; margin:6px 0 0 !important; }
  body.kind-blog #zoBlogAd img { height:100%; min-height:180px; margin:0; border-radius:0; }
  @media (max-width:700px) {
    body.kind-blog #zoBlogAd { grid-template-columns:1fr !important; }
    .zo-vcard-row { grid-template-columns:1fr !important; }
    .zo-vcard-row > div:nth-child(2) { border-left:0 !important; padding:4px 16px 20px !important; }
    .zo-vcard-row > div:nth-child(3), .zo-vcard-mark { display:none !important; }
    .zo-vcard-title { font-size:18px !important; padding:16px 16px 4px !important; overflow-wrap:anywhere; }
    .zo-vcard-pitch { border-left:0 !important; padding:4px 16px 20px !important; }
    .zo-vcard-pitch h2 { font-size:28px !important; }
    .zo-vcard-mark { border-radius:0 !important; padding:20px 16px !important; }
    .zo-vcard-contact { padding:8px 16px 12px !important; }
  }
  body.kind-blog .toc {
    background:#f6f7f9; border:0; border-radius:18px; padding:18px 20px;
  }
  body.kind-blog .toc ul { columns:1; list-style:none; margin:8px 0 0; padding:0; display:grid; gap:8px; }
  body.kind-blog .toc li::marker { content:''; }
  body.kind-blog .step-n { display:none; }
  body.kind-blog article h2 { border:0; background:transparent; padding:0; margin:32px 0 10px; }
  body.kind-blog .zo-share { display:flex; flex-direction:column; gap:10px; position:sticky; top:96px; }
  body.kind-blog .zo-share a {
    width:40px; height:40px; border-radius:14px; border:0; background:#fff; color:#071428;
    display:flex; align-items:center; justify-content:center; text-decoration:none;
    font-size:13px; font-weight:700; box-shadow:0 8px 20px rgba(7,20,40,.06);
  }
  body.kind-blog .zo-leaderboard button {
    background:#0B1F3A; color:#fff; border-radius:16px;
  }
  body.kind-blog .zo-side { display:none; }

  /* Guide: title beside a portrait photo, coral step numbers */
  body.fmt-guide .zo-cover {
    display:grid; grid-template-columns:1.2fr .8fr; gap:40px; align-items:end;
  }
  body.fmt-guide .zo-cover img {
    grid-column:2; grid-row:1; height:480px; border-radius:28px;
  }
  body.fmt-guide .zo-cover-copy { grid-column:1; grid-row:1; align-self:end; padding-bottom:8px; }
  body.fmt-guide .zo-shell { grid-template-columns:44px minmax(0, 1fr); }
  body.fmt-guide article h2 { display:flex; align-items:flex-start; gap:14px; }
  body.fmt-guide article h2 .step-n {
    display:inline-flex; flex:0 0 32px; height:32px; border-radius:999px; background:#ff5a4e; color:#fff;
    align-items:center; justify-content:center; font-size:14px;
  }

  /* Briefing: full photo, white title card sitting on the image */
  body.fmt-briefing .zo-cover { height:560px; border-radius:28px; overflow:hidden; }
  body.fmt-briefing .zo-cover img { position:absolute; inset:0; width:100%; height:100%; }
  body.fmt-briefing .zo-cover-copy {
    position:absolute; left:28px; right:auto; bottom:28px; width:min(680px, calc(100% - 56px));
    background:#fff; border-radius:22px; padding:28px 32px;
    box-shadow:0 20px 50px rgba(20,18,15,.18);
  }
  body.fmt-briefing .zo-cover h1 { font-size:clamp(32px, 3.4vw, 48px); max-width:none; }
  body.fmt-briefing .zo-shell { grid-template-columns:minmax(0, 1fr); }
  body.fmt-briefing .zo-share { display:none; }
  body.fmt-briefing .toc {
    display:grid; grid-template-columns:minmax(0,1fr) 220px; gap:8px 28px; align-items:center;
    padding:8px 4px 8px 0; background:transparent; border:0; border-radius:0;
  }
  body.fmt-briefing .toc-title { grid-column:1; color:#ff5a4e; letter-spacing:.14em; font-size:12px; }
  body.fmt-briefing .toc ul { grid-column:1; margin:0; }
  body.fmt-briefing .toc-thumb {
    grid-column:2; grid-row:1 / span 2; width:220px; height:140px;
    object-fit:cover; border-radius:16px; justify-self:end;
  }
  body.fmt-briefing .toc ol, body.fmt-briefing .toc ul { counter-reset:sec; }
  body.fmt-briefing .toc li { counter-increment:sec; }
  body.fmt-briefing .toc a { color:#14120f; text-decoration:none; }
  body.fmt-briefing .toc a::before {
    content:counter(sec, decimal-leading-zero); margin-right:12px; color:#ff5a4e; font-weight:700;
  }

  /* Feature: title first, wide photo under it, quiet side list */
  body.fmt-feature .zo-cover { display:flex; flex-direction:column; gap:22px; }
  body.fmt-feature .zo-cover-copy { order:-1; }
  body.fmt-feature .zo-cover h1 { max-width:18ch; }
  body.fmt-feature .zo-cover img { height:420px; border-radius:28px; }
  body.fmt-feature .zo-shell { grid-template-columns:minmax(0,1fr) 280px; }
  body.fmt-feature .zo-share { display:none; }
  body.fmt-feature .zo-main { background:transparent; box-shadow:none; padding:8px 8px 0 0; }
  body.fmt-feature .zo-side { display:grid; gap:14px; align-content:start; position:sticky; top:110px; }
  body.fmt-feature .zo-side-card {
    background:#fff; color:#14120f; border-radius:22px; padding:20px 18px;
    box-shadow:0 12px 36px rgba(20,18,15,.05);
  }
  body.fmt-feature .zo-side-card h3 {
    margin:0 0 12px; font-size:12px; letter-spacing:.14em; text-transform:uppercase; color:#ff5a4e;
  }
  body.fmt-feature .zo-side a { color:#14120f; text-decoration:none; font-size:15px; line-height:1.4; }
  body.fmt-feature .zo-side-cta {
    display:block; background:#ff5a4e; color:#fff !important; text-align:center;
    border-radius:14px; padding:14px 16px; font-weight:700;
  }
  body.fmt-feature .quick { display:none; }

  @media (max-width:800px) {
    body.kind-blog .zo-cover { width:calc(100% - 24px); }
    body.kind-blog .zo-cover h1 { font-size:34px; max-width:none; }
    body.kind-blog .zo-shell { width:calc(100% - 24px); }
    body.kind-blog .zo-main { padding:22px 16px 28px; }
    body.fmt-guide .zo-cover, body.fmt-guide .zo-shell,
    body.fmt-feature .zo-shell, body.fmt-briefing .zo-shell { grid-template-columns:1fr; }
    body.fmt-guide .zo-cover img { grid-column:1; grid-row:2; height:240px; }
    body.fmt-guide .zo-cover-copy { grid-column:1; grid-row:1; }
    body.fmt-briefing .zo-cover { height:auto; min-height:420px; }
    body.fmt-briefing .zo-cover-copy { left:12px; bottom:12px; width:calc(100% - 24px); padding:18px; }
    body.fmt-briefing .toc { grid-template-columns:1fr; }
    body.fmt-briefing .toc-thumb { grid-column:1; grid-row:auto; width:100%; height:160px; }
    body.fmt-feature .zo-cover img { height:220px; }
    body.fmt-feature .zo-side { position:static; }
    body.kind-blog .zo-share { flex-direction:row; position:static; }
  }
"""

PHONE_DISPLAY = "(619) 724-9517"
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
_URL_X = "https://x.com/orbit_ze"
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


def _footer_social_items() -> list:
    """Same networks, order, and glyphs as zeorbit.com SiteFooter + SocialBrandIcon."""
    def svg(path: str, view="0 0 24 24") -> str:
        return (
            f'<svg width="15" height="15" viewBox="{view}" fill="currentColor" aria-hidden="true">'
            f'<path d="{path}"/></svg>'
        )

    google_maps = (
        '<svg class="zo-social-logo" width="15" height="15" viewBox="0 0 24 24" aria-hidden="true">'
        '<path fill="#34A853" d="M12 22S5.8 14.4 5.8 9.7A6.2 6.2 0 0 1 12 3.5V22z"/>'
        '<path fill="#FBBC04" d="M12 22s6.2-7.6 6.2-12.3A6.2 6.2 0 0 0 12 3.5V22z"/>'
        '<path fill="#4285F4" d="M12 3.5a6.2 6.2 0 0 0-6.2 6.2H12V3.5z"/>'
        '<path fill="#EA4335" d="M12 3.5a6.2 6.2 0 0 1 6.2 6.2H12V3.5z"/>'
        '<circle fill="#ffffff" cx="12" cy="9.5" r="2.55"/>'
        "</svg>"
    )
    # Paths match zeorbit-website/src/components/SocialBrandIcon.jsx
    fb = "M14 13.5h2.5l1-4H14v-2c0-1.03 0-2 2-2h1.5V2.14c-.326-.043-1.557-.14-2.857-.14C11.928 2 10 3.657 10 6.7v2.8H7v4h3V22h4z"
    ig = (
        "M7 2h10a5 5 0 0 1 5 5v10a5 5 0 0 1-5 5H7a5 5 0 0 1-5-5V7a5 5 0 0 1 5-5zm10 2H7a3 3 0 0 0-3 3v10a3 3 0 0 0 3 3h10a3 3 0 0 0 3-3V7a3 3 0 0 0-3-3zm-5 3.5A4.5 4.5 0 1 1 7.5 12 4.5 4.5 0 0 1 12 7.5zm0 2A2.5 2.5 0 1 0 14.5 12 2.5 2.5 0 0 0 12 9.5zM17.5 6.75a1.25 1.25 0 1 1-1.25 1.25A1.25 1.25 0 0 1 17.5 6.75z"
    )
    yt = "M23.5 6.2a3 3 0 0 0-2.1-2.1C19.5 3.5 12 3.5 12 3.5s-7.5 0-9.4.6A3 3 0 0 0 .5 6.2 31.5 31.5 0 0 0 0 12a31.5 31.5 0 0 0 .5 5.8 3 3 0 0 0 2.1 2.1c1.9.6 9.4.6 9.4.6s7.5 0 9.4-.6a3 3 0 0 0 2.1-2.1A31.5 31.5 0 0 0 24 12a31.5 31.5 0 0 0-.5-5.8zM9.8 15.5v-7l6.2 3.5z"
    x = "M18.244 2H21.5l-7.23 8.26L22.5 22h-6.59l-5.16-6.74L5.2 22H1.94l7.73-8.83L1.5 2h6.75l4.66 6.16L18.244 2zm-1.16 18h1.82L7.08 3.94H5.12L17.084 20z"
    li = "M6.94 6.5a1.94 1.94 0 1 1-1.94-1.94A1.94 1.94 0 0 1 6.94 6.5zM7 9.25H3V21h4zm6.5 0h-3.8V21h3.8v-6.1c0-2.3 2.9-2.5 2.9 0V21H20v-7.1c0-5.1-5.5-4.9-6.5-2.4z"
    pin = "M12 2C6.48 2 2 6.27 2 11.64c0 4.1 2.56 7.62 6.17 8.96-.09-.76-.16-1.93.03-2.76.18-.76 1.14-4.84 1.14-4.84s-.29-.58-.29-1.44c0-1.35.78-2.36 1.76-2.36.83 0 1.23.62 1.23 1.37 0 .83-.53 2.08-.8 3.24-.23.97.48 1.76 1.43 1.76 1.72 0 3.04-1.81 3.04-4.43 0-2.32-1.67-3.94-4.05-3.94-2.76 0-4.38 2.07-4.38 4.21 0 .83.32 1.72.72 2.2.08.1.09.18.07.28l-.27 1.1c-.04.18-.14.22-.32.13-1.2-.56-1.95-2.32-1.95-3.74 0-3.05 2.22-5.85 6.39-5.85 3.35 0 5.96 2.39 5.96 5.58 0 3.33-2.1 6.01-5.01 6.01-.98 0-1.9-.51-2.21-1.11l-.6 2.29c-.22.84-.81 1.89-1.21 2.53A9.9 9.9 0 0 0 12 21.28c5.52 0 10-4.27 10-9.64C22 6.27 17.52 2 12 2z"
    be = "M8.16 11.2c.92-.4 1.4-1.08 1.4-2.08 0-1.84-1.36-2.72-3.44-2.72H0v11.2h6.4c2.24 0 3.84-1.12 3.84-3.12 0-1.4-.8-2.4-2.08-2.88zM3.04 8.08h2.08c.88 0 1.36.4 1.36 1.12S6 10.32 5.12 10.32H3.04V8.08zm2.4 7.52H3.04v-3.04h2.48c1.04 0 1.6.48 1.6 1.44s-.64 1.6-1.68 1.6zM24 7.6h-6.08V6h6.08v1.6zM20.96 8.8c-2.72 0-4.56 1.84-4.56 4.4s1.84 4.4 4.64 4.4c1.92 0 3.44-.88 4.08-2.4l-1.84-.72c-.4.88-1.2 1.36-2.24 1.36-1.2 0-2.08-.72-2.32-1.92h6.72c.08-.4.08-.72.08-1.04 0-2.64-1.6-4.08-4.56-4.08zm-2.24 3.36c.24-1.12 1.04-1.76 2.16-1.76 1.2 0 1.92.64 2.08 1.76h-4.24z"
    apple = "M16.37 12.86c-.03-2.54 2.07-3.76 2.16-3.81-1.18-1.73-3.01-1.97-3.66-1.99-1.56-.16-3.04.92-3.83.92-.79 0-2.01-.9-3.31-.87-1.7.03-3.27.99-4.15 2.52-1.77 3.07-.45 7.62 1.27 10.11.84 1.22 1.85 2.59 3.17 2.54 1.27-.05 1.75-.82 3.29-.82s1.96.82 3.3.8c1.36-.03 2.23-1.24 3.06-2.47.97-1.41 1.36-2.78 1.38-2.85-.03-.01-2.66-1.02-2.69-4.08zm-2.53-7.47c.7-.85 1.17-2.04 1.04-3.22-1.01.04-2.23.67-2.96 1.52-.65.75-1.22 1.96-1.07 3.12 1.13.09 2.28-.57 2.99-1.42z"
    yelp = "M42.9 240.32l99.62 48.61c19.2 9.4 16.2 37.51-4.5 42.71L30.5 358.45a22.79 22.79 0 0 1-28.21-19.6 197.16 197.16 0 0 1 9-85.32 22.8 22.8 0 0 1 31.61-13.21zm44 239.25a199.4 199.4 0 0 0 79.42 32.11A22.78 22.78 0 0 0 192.94 490l3.9-110.82c.7-21.3-25.5-31.91-39.81-16.1l-74.21 82.4a22.82 22.82 0 0 0 4.09 34.09zm145.34-109.92l52.7 120.4a22.94 22.94 0 0 0 34.64 10.57 200.67 200.67 0 0 0 46-105.34c6.2-20.8-14.4-38.5-34.8-31.8l-98.54 33.79c-19.04 6.5-26.24 27.1 0 27.38zm148.33-132.23a197.57 197.57 0 0 0-50.41-101.22 22.85 22.85 0 0 0-34.75 16.67l-26.56 106.34c-5.79 21.5 15.29 38.62 34.91 31.46l76.81-26.17a22.92 22.92 0 0 0 14-27.08zM67.54 27.74c-13.84 7-21.37 21.68-17.29 37.47l42.31 166.03c6.39 25.07 38.52 26.3 44.63 1.9l45.46-180.25c6.48-25.71-20.41-48.5-44.55-35.86z"
    return [
        ("Facebook", _URL_FACEBOOK, svg(fb)),
        ("Instagram", _URL_INSTAGRAM, svg(ig)),
        ("LinkedIn", _URL_LINKEDIN, svg(li)),
        ("YouTube", _URL_YOUTUBE, svg(yt)),
        ("X", _URL_X, svg(x)),
        ("Pinterest", _URL_PINTEREST, svg(pin)),
        ("Behance", "https://www.behance.net/zeorbitappdev", svg(be)),
        ("Apple Maps", _URL_APPLE_MAPS, svg(apple)),
        ("Google Maps", _URL_GOOGLE_MAPS, google_maps),
        ("Yelp", _URL_YELP, svg(yelp, "0 0 384 512")),
    ]


def _site_header() -> str:
    """Same structure as zeorbit.com RevampHeader: black topbar + logo nav + actions."""
    nav_items = [
        ("Home", f"{WEBSITE}/", ()),
        (
            "Websites",
            f"{WEBSITE}/website-designing",
            (
                ("Custom Websites", f"{WEBSITE}/website-designing#business"),
                ("Shopify & Ecommerce", f"{WEBSITE}/website-designing#ecommerce"),
                ("Landing Pages", f"{WEBSITE}/website-designing#landing"),
                ("Website Redesign", f"{WEBSITE}/website-designing#redesign"),
                ("UI / UX Design", f"{WEBSITE}/website-designing#ux"),
                ("Care & Maintenance", f"{WEBSITE}/website-designing#care"),
            ),
        ),
        (
            "Mobile Apps",
            f"{WEBSITE}/mobile-apps",
            (
                ("iOS & Android", f"{WEBSITE}/mobile-apps#native"),
                ("Cross-Platform", f"{WEBSITE}/mobile-apps#cross"),
                ("App Timeline", f"{WEBSITE}/mobile-apps#timeline"),
                ("Mobile UX / UI", f"{WEBSITE}/mobile-apps#ux"),
            ),
        ),
        (
            "SEO & Ads",
            f"{WEBSITE}/seo-ppc",
            (
                ("Technical SEO", f"{WEBSITE}/seo-ppc#seo"),
                ("Local SEO", f"{WEBSITE}/seo-ppc#local"),
                ("Content SEO", f"{WEBSITE}/seo-ppc#content"),
                ("Google Ads", f"{WEBSITE}/seo-ppc#ads"),
                ("Social Ads", f"{WEBSITE}/seo-ppc#social-ads"),
                ("Pricing", f"{WEBSITE}/seo-ppc#pricing"),
            ),
        ),
        (
            "Custom Software",
            f"{WEBSITE}/custom-software",
            (
                ("Dashboards", f"{WEBSITE}/custom-software#platforms"),
                ("CRM & Workflows", f"{WEBSITE}/custom-software#crm"),
                ("API Integrations", f"{WEBSITE}/custom-software#integrations"),
                ("Automation", f"{WEBSITE}/custom-software#automation"),
            ),
        ),
        ("Portfolio", f"{WEBSITE}/portfolio", ()),
        ("Contact", f"{WEBSITE}/contact", ()),
    ]
    caret = (
        '<svg class="zo-nav-caret" width="14" height="14" viewBox="0 0 24 24" fill="none" '
        'stroke="currentColor" stroke-width="2.4"><path d="m6 9 6 6 6-6"/></svg>'
    )
    phone_ico = (
        '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="2.2"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 '
        '19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.13.81.36 1.6.7 '
        '2.34a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.74.34 1.53.57 '
        '2.34.7A2 2 0 0 1 22 16.92z"/></svg>'
    )
    user_ico = (
        '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="2.2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>'
        '<circle cx="12" cy="7" r="4"/></svg>'
    )
    menu_ico = (
        '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="2.6"><path d="M4 6h16M4 12h16M4 18h16"/></svg>'
    )
    icons = {
        "Home": '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="m3 10 9-7 9 7v10a2 2 0 0 1-2 2h-4v-7H9v7H5a2 2 0 0 1-2-2z"/></svg>',
        "Websites": '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3a14 14 0 0 1 0 18M12 3a14 14 0 0 0 0 18"/></svg>',
        "Mobile Apps": '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><rect x="7" y="2" width="10" height="20" rx="2"/><path d="M11 18h2"/></svg>',
        "SEO & Ads": '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M4 19V5M4 19h16M8 16l3-4 3 2 4-6"/></svg>',
        "Custom Software": '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><rect x="3" y="4" width="18" height="6" rx="1"/><rect x="3" y="14" width="18" height="6" rx="1"/></svg>',
        "Portfolio": '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/></svg>',
        "Contact": '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>',
    }
    desk_nav = []
    mobile_nav = []
    for label, href, children in nav_items:
        icon = icons.get(label, "")
        if children:
            drops = "".join(f'<a href="{h}">{_esc(n)}</a>' for n, h in children)
            desk_nav.append(
                f'<div class="zo-nav-item has-children">'
                f'<a class="zo-nav-trigger" href="{href}">{icon}<span>{_esc(label)}</span>{caret}</a>'
                f'<div class="zo-simple-drop">{drops}</div></div>'
            )
            kids = "".join(f'<a href="{h}">{_esc(n)}</a>' for n, h in children)
            mobile_nav.append(f'<a href="{href}">{_esc(label)}</a>{kids}')
        else:
            desk_nav.append(f'<div class="zo-nav-item"><a href="{href}">{icon}<span>{_esc(label)}</span></a></div>')
            mobile_nav.append(f'<a href="{href}">{_esc(label)}</a>')
    return f"""
<header class="zo-site-header zo-host-header is-scrolled" id="zoArticleHeader">
  <div class="zo-topbar">
    <div class="zo-topbar-inner">
      <a class="zo-topbar-email" href="mailto:{EMAIL}">{EMAIL}</a>
      <button type="button" class="zo-topbar-phone" data-zo-call="1">
        {phone_ico}<span>Call now (619) 724-9517</span>
      </button>
    </div>
  </div>
  <div class="zo-host-bar">
    <div class="zo-host-bar-inner">
      <div class="zo-brand">
        <a class="zo-logo" href="{WEBSITE}/" aria-label="ZeOrbit home">
          <img src="{WEBSITE}/zeorbit-logo-official.webp?v=9" alt="ZeOrbit" height="36" />
        </a>
      </div>
      <nav class="zo-nav" aria-label="Primary">
        {"".join(desk_nav)}
      </nav>
      <div class="zo-host-actions">
        <div class="zo-util-item">
          <span class="zo-util-trigger zo-lang-trigger" aria-hidden="true">
            <span class="zo-util-flag"><img class="zo-util-flag-img" src="https://flagcdn.com/w40/us.png" alt="" width="20" height="15" /></span>
            <span class="zo-util-label">EN</span>
          </span>
        </div>
        <a class="zo-nav-quote" href="tel:+16197249517">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="#e11d48" stroke="#e11d48" stroke-width="2"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.13.81.36 1.6.7 2.34a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.74.34 1.53.57 2.34.7A2 2 0 0 1 22 16.92z"/></svg>
          (619) 724-9517
        </a>
        <a class="zo-nav-icon-btn" href="{WEBSITE}/contact" aria-label="Contact ZeOrbit">{user_ico}</a>
        <button type="button" class="zo-mobile-toggle" id="zoMobileToggle" aria-label="Open menu">{menu_ico}</button>
      </div>
    </div>
  </div>
  <nav class="zo-mobile-nav" id="zoMobileNav" aria-label="Mobile">
    {"".join(mobile_nav)}
    <button type="button" class="zo-mobile-call" data-zo-call="1" data-zo-label="Call (619) 724-9517">Call office</button>
    <a class="zo-mobile-call" href="{WEBSITE}/contact">Contact us</a>
  </nav>
</header>
"""


def _social_bar() -> str:
    return _site_header()


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
    """Match zeorbit.com SiteFooter: brand, 6 columns, socials, legal."""
    cities = [
        "San Diego", "Los Angeles", "El Cajon", "Carlsbad", "Chula Vista", "Oceanside",
    ]
    cols = [
        (
            "Areas We Serve",
            [("All areas", f"{WEBSITE}/areas"), ("California", f"{WEBSITE}/areas/california")]
            + [(name, f"{WEBSITE}/areas/{name.lower().replace(' ', '-')}") for name in cities],
        ),
        (
            "Quick Links",
            [
                ("San Diego Web Design Services", f"{WEBSITE}/areas/san-diego"),
                ("Custom Website Design", f"{WEBSITE}/website-designing"),
                ("SEO & Local Marketing", f"{WEBSITE}/seo-ppc"),
                ("E-Commerce Website Solutions", f"{WEBSITE}/website-designing#ecommerce"),
                ("Website Maintenance & Support", f"{WEBSITE}/master-care"),
                ("Best San Diego Web Design Company", f"{WEBSITE}/web-designer-near-me"),
                ("Web Design Agency in San Diego", f"{WEBSITE}/areas/san-diego"),
                ("Local Web Design Company Near Me", f"{WEBSITE}/web-designer-near-me"),
            ],
        ),
        (
            "Websites",
            [
                ("Custom Websites", f"{WEBSITE}/website-designing#business"),
                ("WordPress", f"{WEBSITE}/website-designing#wordpress"),
                ("Shopify & Ecommerce", f"{WEBSITE}/website-designing#ecommerce"),
                ("Landing Pages", f"{WEBSITE}/website-designing#landing"),
                ("Website Redesign", f"{WEBSITE}/website-designing#redesign"),
                ("UI / UX Design", f"{WEBSITE}/website-designing#ux"),
                ("Care & Maintenance", f"{WEBSITE}/master-care"),
            ],
        ),
        (
            "Mobile Apps",
            [
                ("iOS & Android", f"{WEBSITE}/mobile-apps#native"),
                ("Cross-Platform", f"{WEBSITE}/mobile-apps#cross"),
                ("App Timeline", f"{WEBSITE}/mobile-apps#timeline"),
                ("Mobile UX / UI", f"{WEBSITE}/mobile-apps#ux"),
                ("MVP & Prototype", f"{WEBSITE}/mobile-apps"),
                ("App Redesign", f"{WEBSITE}/mobile-apps"),
                ("App Maintenance", f"{WEBSITE}/master-care"),
            ],
        ),
        (
            "SEO & Ads",
            [
                ("Technical SEO", f"{WEBSITE}/seo-ppc#seo"),
                ("Local SEO", f"{WEBSITE}/seo-ppc#local"),
                ("Content SEO", f"{WEBSITE}/seo-ppc#content"),
                ("Google Ads", f"{WEBSITE}/seo-ppc#ads"),
                ("Social Ads", f"{WEBSITE}/seo-ppc#social-ads"),
                ("Blog & Insights", f"{WEBSITE}/blogs"),
                ("Google Business Profile", f"{WEBSITE}/seo-ppc#local"),
                ("Pricing", f"{WEBSITE}/seo-ppc#pricing"),
            ],
        ),
        (
            "Software",
            [
                ("Dashboards", f"{WEBSITE}/custom-software#platforms"),
                ("Microsoft 365", f"{WEBSITE}/custom-software#microsoft"),
                ("CRM & Workflows", f"{WEBSITE}/custom-software#crm"),
                ("API Integrations", f"{WEBSITE}/custom-software#integrations"),
                ("Automation", f"{WEBSITE}/custom-software#automation"),
                ("AI Solutions", f"{WEBSITE}/custom-software"),
                ("Client Portals", f"{WEBSITE}/custom-software#platforms"),
            ],
        ),
        (
            "Resources",
            [
                ("Blog", f"{WEBSITE}/blogs"),
                ("Portfolio", f"{WEBSITE}/portfolio"),
                ("Areas We Serve", f"{WEBSITE}/areas"),
                ("(619) 724-9517", "tel:+16197249517"),
                ("WordPress Web Design", f"{WEBSITE}/wordpress-website-design"),
                ("Microsoft 365", f"{WEBSITE}/microsoft-365"),
            ],
        ),
        (
            "Company",
            [
                ("About ZeOrbit", f"{WEBSITE}/"),
                ("Contact", f"{WEBSITE}/contact"),
                ("Get a Free Quote", f"{WEBSITE}/contact"),
                ("Portfolio", f"{WEBSITE}/portfolio"),
                ("Privacy Policy", f"{WEBSITE}/privacy-policy"),
                ("Let's Talk", f"{WEBSITE}/contact"),
            ],
        ),
    ]
    col_html = []
    for title, items in cols:
        lis = "".join(f'<li><a href="{u}">{_esc(n)}</a></li>' for n, u in items)
        col_html.append(f'<div class="zo-host-footer-col"><h4>{_esc(title)}</h4><ul>{lis}</ul></div>')
    def _social_link(item) -> str:
        label, url, inner = item
        cls = label.lower().replace(" ", "-")
        return (
            f'<a class="zo-host-social is-{cls}" href="{url}" '
            f'target="_blank" rel="noreferrer" aria-label="{_esc(label)}">{inner}</a>'
        )

    items = _footer_social_items()
    left_socials = "".join(_social_link(s) for s in items[:5])
    right_socials = "".join(_social_link(s) for s in items[5:10])
    return f"""
<footer id="about" class="zo-site-footer zo-host-footer">
  <div class="zo-host-footer-accent" aria-hidden="true"></div>
  <div class="zo-host-footer-brand">
    <div class="rv-shell zo-host-footer-brand-inner">
      <a class="zo-host-footer-logo" href="{WEBSITE}/" aria-label="ZeOrbit home">
        <img src="{WEBSITE}/zeorbit-logo-official.webp?v=9" alt="ZeOrbit" height="48"
             style="height:48px;width:auto;max-width:min(180px,48vw);display:block;object-fit:contain;object-position:left center" />
      </a>
      <p class="zo-host-footer-tagline">Websites, apps, SEO, and custom software for ambitious U.S. brands.</p>
    </div>
  </div>
  <div class="zo-host-footer-main">
    <div class="rv-shell zo-host-footer-grid">
      {"".join(col_html)}
    </div>
  </div>
  <div class="zo-host-footer-socials-block">
    <div class="rv-shell zo-host-footer-social-row" role="group" aria-label="Social media">
      <div class="zo-host-footer-social zo-host-footer-social-left">{left_socials}</div>
      <div class="zo-host-footer-social zo-host-footer-social-right">{right_socials}</div>
    </div>
  </div>
  <div class="zo-host-footer-legal">
    <div class="rv-shell zo-host-footer-legal-inner">
      <p>© 2026 ZeOrbit — Websites, apps, SEO, and custom software for ambitious U.S. brands.</p>
      <div class="zo-host-footer-legal-links">
        <a href="mailto:{EMAIL}">{EMAIL}</a>
        <button type="button" data-zo-call="1">Call now (619) 724-9517</button>
        <a href="{WEBSITE}/contact">Contact</a>
        <a href="https://www.apple.com/" rel="noopener noreferrer">Apple</a>
        <a href="https://www.google.com/" rel="noopener noreferrer">Google</a>
        <a href="https://www.sandiego.gov/" rel="noopener noreferrer">San Diego</a>
      </div>
    </div>
  </div>
</footer>"""


def _blog_lead_ad(seed: str = "") -> str:
    """Blog pages skip the map and office panel. The form opens from the floating ad."""
    return """
<dialog id="zoLeadDialog" class="zo-brief">
  <style>
    #zoLeadDialog.zo-brief{border:0;padding:0;width:min(480px,calc(100vw - 28px));max-height:min(720px,calc(100vh - 28px));overflow:auto;border-radius:22px;background:#fff;color:#1d1d1f;box-shadow:0 24px 80px rgba(16,24,40,.22);}
    #zoLeadDialog::backdrop{background:rgba(22,24,28,.46);}
    #zoLeadDialog .zo-brief-head{display:flex;align-items:flex-start;justify-content:space-between;gap:12px;padding:20px 20px 0;}
    #zoLeadDialog .zo-brief-kicker{margin:0;font-size:11px;letter-spacing:.16em;text-transform:uppercase;color:#8a6a62;font-weight:700;}
    #zoLeadDialog .zo-brief-head h2{margin:4px 0 0;font-size:22px;line-height:1.15;letter-spacing:-.03em;font-weight:680;}
    #zoLeadDialog .zo-brief-head p{margin:6px 0 0;font-size:14px;line-height:1.4;color:#5c6370;}
    #zoLeadDialog #zoCloseLead{border:0;background:#f3f4f6;color:#1d1d1f;border-radius:999px;width:32px;height:32px;cursor:pointer;flex:none;}
    #zoLeadDialog #zoCloseLead:active{transform:scale(.96);}
    #zoLeadDialog .cz-finale-form-card,#zoLeadDialog .rv-contact-card{box-shadow:none;background:transparent;padding:0;border:0;}
    #zoLeadDialog .rv-contact-form{padding:16px 20px 20px;}
    #zoLeadDialog .rv-form-grid{display:grid;grid-template-columns:1fr 1fr;gap:12px;}
    #zoLeadDialog .rv-label{display:flex;flex-direction:column;gap:6px;font-size:13px;font-weight:600;color:#1d1d1f;}
    #zoLeadDialog .rv-label-full,#zoLeadDialog .rv-captcha{grid-column:1 / -1;}
    #zoLeadDialog .rv-req{color:#c2410c;font-style:normal;}
    #zoLeadDialog .rv-input,#zoLeadDialog .rv-textarea,#zoLeadDialog select.rv-select{width:100%;box-sizing:border-box;border:1px solid #e4e4e7;background:#fafafa;border-radius:12px;padding:11px 12px;font:inherit;font-size:15px;font-weight:450;color:#1d1d1f;outline:none;}
    #zoLeadDialog .rv-input:focus,#zoLeadDialog .rv-textarea:focus,#zoLeadDialog select.rv-select:focus{border-color:#1c305c;background:#fff;box-shadow:0 0 0 3px rgba(28,48,92,.12);}
    #zoLeadDialog .rv-textarea{min-height:88px;resize:vertical;}
    #zoLeadDialog .rv-captcha{display:grid;grid-template-columns:auto 1fr;gap:12px;align-items:end;margin-top:12px;}
    #zoLeadDialog .rv-captcha-image{position:relative;display:flex;align-items:center;}
    #zoLeadDialog .rv-captcha-image img{border-radius:12px;display:block;}
    #zoLeadDialog .rv-captcha-refresh{position:absolute;right:6px;top:6px;border:0;background:rgba(255,255,255,.85);border-radius:999px;width:24px;height:24px;cursor:pointer;}
    #zoLeadDialog .rv-contact-actions{display:flex !important;flex-direction:column !important;align-items:stretch !important;gap:10px;margin-top:14px;}
    #zoLeadDialog .rv-submit-btn{width:100% !important;border:0 !important;border-radius:999px !important;background:#1c305c !important;color:#fff !important;padding:13px 18px !important;font-size:15px !important;font-weight:680;cursor:pointer;}
    #zoLeadDialog .rv-submit-btn:active{transform:scale(.98);}
    #zoLeadDialog .rv-contact-privacy{margin:0 !important;max-width:none !important;font-size:13px !important;line-height:1.45 !important;color:#6b7280 !important;}
    @media (max-width:560px){#zoLeadDialog .rv-form-grid,#zoLeadDialog .rv-captcha{grid-template-columns:1fr;}}
  </style>
  <div class="zo-brief-head">
    <div>
      <p class="zo-brief-kicker">ZeOrbit</p>
      <h2>Send a short brief</h2>
      <p>A name, a way to reach you, and what you want built. We reply within one business day.</p>
    </div>
    <button type="button" id="zoCloseLead" aria-label="Close">×</button>
  </div>
  <div class="cz-finale-form-card" style="box-shadow:none;">
    <div class="rv-contact-card is-contact-page" role="region" aria-label="Contact ZeOrbit">
      <form class="rv-contact-form" id="zoArticleLeadForm" novalidate>
        <div class="rv-form-grid is-contact-page">
          <label class="rv-label"><span class="rv-label-row">Full Name <em class="rv-req">*</em></span>
            <input class="rv-input" name="name" autocomplete="name" placeholder="Full Name" required></label>
          <label class="rv-label"><span class="rv-label-row">Your Email <em class="rv-req">*</em></span>
            <input class="rv-input" name="email" type="email" autocomplete="email" placeholder="Your Email" required></label>
          <label class="rv-label"><span class="rv-label-row">Your Number <em class="rv-req">*</em></span>
            <input class="rv-input" name="phone" autocomplete="tel" inputmode="tel" placeholder="Your Number" required></label>
          <label class="rv-label"><span class="rv-label-row">Service Need</span>
            <div class="rv-select-wrap"><select class="rv-input rv-select" name="service">
              <option value="">Service Need</option>
              <option>Web Designing</option>
              <option>Digital Advertising</option>
              <option>SEO</option>
              <option>Mobile App Development</option>
              <option>Custom Software Development</option>
            </select></div></label>
        </div>
        <label class="rv-label rv-label-full"><span class="rv-label-row">Additional Message <em class="rv-req">*</em></span>
          <textarea class="rv-textarea" name="message" rows="4" placeholder="Additional Message" required></textarea></label>
        <div class="rv-hp" aria-hidden="true"><label>Website <input tabindex="-1" autocomplete="off" name="website_url"></label></div>
        <div class="rv-captcha">
          <div class="rv-captcha-image">
            <img id="zoCaptchaImg" alt="Captcha code" width="188" height="58">
            <button type="button" class="rv-captcha-refresh" id="zoCaptchaRefresh" aria-label="Refresh captcha">↻</button>
          </div>
          <label class="rv-label rv-captcha-field"><span class="rv-label-row">Type the code <em class="rv-req">*</em></span>
            <input class="rv-input" name="captcha_answer" autocomplete="off" autocapitalize="characters" spellcheck="false" maxlength="8" placeholder="5-character code" required></label>
        </div>
        <p class="rv-status" id="zoLeadStatus" hidden></p>
        <div class="rv-contact-actions">
          <button type="submit" class="rv-submit-btn" id="zoLeadSubmit">Send the brief</button>
          <p class="rv-contact-privacy">We only use this to reply about your project.</p>
        </div>
      </form>
    </div>
  </div>
</dialog>
<script>
(function(){
  var dialog=document.getElementById('zoLeadDialog');
  var close=document.getElementById('zoCloseLead');
  if(dialog && dialog.showModal){
    document.querySelectorAll('#zoOpenLead, .zo-open-lead').forEach(function(open){
      open.addEventListener('click', function(e){ e.preventDefault(); dialog.showModal(); });
    });
  }
  if(close && dialog) close.addEventListener('click', function(){ dialog.close(); });
})();
</script>
"""


def _contact_finale() -> str:
    """Same homepage closer: brand + channels + studios + form."""
    sd_embed = "https://maps.google.com/maps?q=4231+Balboa+Avenue+Suite+1340,+San+Diego,+CA+92117&z=16&output=embed"
    sd_maps = "https://www.google.com/maps/search/?api=1&query=4231+Balboa+Avenue+Suite+1340+San+Diego+CA+92117"
    pin = (
        '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="2.4" aria-hidden="true"><path d="M20 10c0 6-8 12-8 12S4 16 4 10a8 8 0 1 1 16 0z"/>'
        '<circle cx="12" cy="10" r="3"/></svg>'
    )
    phone_ico = (
        '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="2.2" aria-hidden="true"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 '
        '19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3'
        'a2 2 0 0 1 2 1.72c.127.96.361 1.903.7 2.81a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6'
        'l1.27-1.27a2 2 0 0 1 2.11-.45c.907.339 1.85.573 2.81.7A2 2 0 0 1 22 16.92z"/></svg>'
    )
    mail_ico = (
        '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="2.2" aria-hidden="true"><rect width="20" height="16" x="2" y="4" rx="2"/>'
        '<path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/></svg>'
    )
    go_ico = (
        '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="2.2" aria-hidden="true"><path d="M7 17 17 7"/><path d="M7 7h10v10"/></svg>'
    )
    return f"""
<section class="cz-finale" aria-label="Contact">
  <div class="cz-finale-glow" aria-hidden="true"></div>
  <div class="cz-finale-inner">
    <div class="cz-finale-left">
      <div class="cz-finale-copy">
        <p class="cz-finale-brand">ZeOrbit</p>
        <h2>Contact Us</h2>
        <p class="cz-whisper">Websites, apps, SEO, and custom software — tell us what you need and we will map a clear next step.</p>
        <div class="cz-finale-channels">
          <button type="button" class="cz-finale-channel" data-zo-call="1" data-zo-label="{PHONE_DISPLAY}">
            <span class="cz-finale-channel-icon" aria-hidden="true">{phone_ico}</span>
            <span class="cz-finale-channel-copy"><span>Call</span><strong>Call now (619) 724-9517</strong></span>
          </button>
          <a class="cz-finale-channel" href="mailto:info@zeorbit.com">
            <span class="cz-finale-channel-icon" aria-hidden="true">{mail_ico}</span>
            <span class="cz-finale-channel-copy"><span>Email</span><strong>info@zeorbit.com</strong></span>
          </a>
        </div>
      </div>
      <div class="cz-finale-studios" aria-label="Office locations">
        <a class="cz-finale-studio" href="{sd_maps}" target="_blank" rel="noreferrer">
          <span class="cz-finale-studio-pin" aria-hidden="true">{pin}</span>
          <span class="cz-finale-studio-copy">
            <strong>San Diego HQ</strong>
            <span>4231 Balboa Avenue, Suite 1340</span>
            <span>San Diego, CA 92117</span>
          </span>
          <span class="cz-finale-studio-go" aria-hidden="true">{go_ico}</span>
        </a>
      </div>
      <article class="cz-finale-map-feature">
        <div class="cz-finale-map-stage">
          <iframe class="cz-finale-map-iframe" title="San Diego HQ map" src="{sd_embed}" loading="lazy" referrerpolicy="no-referrer-when-downgrade" tabindex="-1"></iframe>
        </div>
        <a class="cz-finale-map-open" href="{sd_maps}" target="_blank" rel="noreferrer">
          Open San Diego HQ in Maps {go_ico}
        </a>
      </article>
    </div>
    <div id="contact" class="cz-finale-form-card">
      <div class="cz-finale-form-head">
        <p>Project inquiry</p>
        <h3>Send a short brief</h3>
        <p class="cz-finale-form-sub">Tell us what you need — we reply within one business day.</p>
      </div>
      <div class="rv-contact-card is-contact-page" role="region" aria-label="Contact ZeOrbit">
        <form class="rv-contact-form" id="zoArticleLeadForm" novalidate>
          <div class="rv-form-grid is-contact-page">
            <label class="rv-label"><span class="rv-label-row">Full Name <em class="rv-req">*</em></span>
              <input class="rv-input" name="name" autocomplete="name" placeholder="Full Name" required></label>
            <label class="rv-label"><span class="rv-label-row">Your Email <em class="rv-req">*</em></span>
              <input class="rv-input" name="email" type="email" autocomplete="email" placeholder="Your Email" required></label>
            <label class="rv-label"><span class="rv-label-row">Your Number <em class="rv-req">*</em></span>
              <input class="rv-input" name="phone" autocomplete="tel" inputmode="tel" placeholder="Your Number" required></label>
            <label class="rv-label"><span class="rv-label-row">Service Need</span>
              <div class="rv-select-wrap"><select class="rv-input rv-select" name="service">
                <option value="">Service Need</option>
                <option>Master Care</option>
                <option>Web Designing</option>
                <option>Digital Advertising</option>
                <option>SEO</option>
                <option>Logo Designs</option>
                <option>Content Marketing</option>
                <option>Mobile App Development</option>
                <option>Custom Software Development</option>
              </select></div></label>
          </div>
          <label class="rv-label rv-label-full"><span class="rv-label-row">Additional Message <em class="rv-req">*</em></span>
            <textarea class="rv-textarea" name="message" rows="4" placeholder="Additional Message" required></textarea></label>
          <div class="rv-hp" aria-hidden="true"><label>Website <input tabindex="-1" autocomplete="off" name="website_url"></label></div>
          <div class="rv-captcha">
            <div class="rv-captcha-image">
              <img id="zoCaptchaImg" alt="Captcha code" width="188" height="58">
              <button type="button" class="rv-captcha-refresh" id="zoCaptchaRefresh" aria-label="Refresh captcha">↻</button>
            </div>
            <label class="rv-label rv-captcha-field"><span class="rv-label-row">Type the code <em class="rv-req">*</em></span>
              <input class="rv-input" name="captcha_answer" autocomplete="off" autocapitalize="characters" spellcheck="false" maxlength="8" placeholder="5-character code" required></label>
          </div>
          <p class="rv-status" id="zoLeadStatus" hidden></p>
          <div class="rv-contact-actions">
            <button type="submit" class="rv-submit-btn" id="zoLeadSubmit">Send message</button>
            <p class="rv-contact-privacy">By submitting, you agree to be contacted about this request. No spam.</p>
          </div>
        </form>
      </div>
    </div>
  </div>
</section>"""


def _contact_form_script() -> str:
    return """
<script>
(function(){
  try {
    var sid='';
    try { sid=localStorage.getItem('zo_vid')||''; if(!sid){ sid=(crypto.randomUUID&&crypto.randomUUID())||('v-'+Date.now()); localStorage.setItem('zo_vid',sid);} } catch(e) {}
    fetch('/api/leads/visit', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({
        path: location.pathname+(location.search||''),
        referrer: document.referrer || '',
        session_id: sid,
        language: navigator.language||'',
        timezone: (Intl.DateTimeFormat().resolvedOptions().timeZone)||'',
        screen: (screen&&screen.width?screen.width+'x'+screen.height:'')
      }),
      keepalive: true
    });
  } catch (e) {}
  var form=document.getElementById('zoArticleLeadForm');
  if(!form) return;
  var started=Date.now();
  var captchaId='';
  var img=document.getElementById('zoCaptchaImg');
  var statusEl=document.getElementById('zoLeadStatus');
  var btn=document.getElementById('zoLeadSubmit');
  function api(path){ return '/api/leads' + path; }
  function loadCaptcha(){
    fetch(api('/captcha')).then(function(r){ return r.json(); }).then(function(d){
      captchaId=d.id||'';
      if(img && d.image) img.src=d.image;
    }).catch(function(){});
  }
  loadCaptcha();
  var refresh=document.getElementById('zoCaptchaRefresh');
  if(refresh) refresh.addEventListener('click', function(){ loadCaptcha(); form.captcha_answer.value=''; });
  form.addEventListener('submit', function(e){
    e.preventDefault();
    statusEl.hidden=true;
    btn.disabled=true;
    var payload={
      source:'blog',
      page_url:location.href,
      name:(form.name.value||'').trim(),
      contact_name:(form.name.value||'').trim(),
      email:(form.email.value||'').trim(),
      phone:(form.phone.value||'').trim(),
      service:form.service.value||'Web Designing',
      message:(form.message.value||'').trim(),
      captcha_id:captchaId,
      captcha_answer:(form.captcha_answer.value||'').trim(),
      website_url:form.website_url.value||'',
      started_at:started
    };
    fetch(api('/'), { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(payload) })
      .then(function(r){
        return r.json().then(function(d){ return {ok:r.ok, d:d, status:r.status}; });
      })
      .then(function(res){
        statusEl.hidden=false;
        if(res.ok){
          statusEl.className='rv-status success';
          statusEl.textContent="Thanks — we'll reach out within one business day.";
          form.reset(); started=Date.now(); loadCaptcha();
        } else {
          statusEl.className='rv-status error';
          var detail=res.d && res.d.detail ? res.d.detail : ('Could not submit ('+res.status+')');
          statusEl.textContent=typeof detail==='string'?detail:'Could not submit. Please try again.';
          loadCaptcha();
        }
      })
      .catch(function(){
        statusEl.hidden=false;
        statusEl.className='rv-status error';
        statusEl.textContent='Could not submit. Please try again.';
        loadCaptcha();
      })
      .finally(function(){ btn.disabled=false; });
  });
})();
</script>
"""


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


def _title_phrase(text: str) -> str:
    words = (text or "").split()
    if not words or text != text.lower():
        return text
    small = {"a", "an", "the", "in", "of", "for", "and", "or", "to", "on", "with", "near"}
    titled = []
    for index, word in enumerate(words):
        if index and word.lower() in small:
            titled.append(word.lower())
        else:
            titled.append(word[:1].upper() + word[1:])
    return " ".join(titled)


def _vcard_html(headline: str = "", button_label: str = "", button_url: str = "") -> str:
    """Wide three-column closer. Middle line is the catchy title plus the keyword."""
    light = "https://zeorbit.com/zeorbit-logo-light.png"
    official = "https://zeorbit.com/zeorbit-logo-official.png"
    raw = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", headline or "")).strip()
    raw = re.sub(r"^let['’]s build\s*:?\s*", "", raw, flags=re.I).strip()
    title_line = _esc(raw or "Talk with ZeOrbit")
    action = re.sub(r"\s+", " ", button_label or "").strip() or "Start a Project"
    action_url = button_url.strip() if re.match(r"^https://[^\s]+$", button_url or "") else "https://zeorbit.com/contact"
    action = _esc(action)
    action_url = _esc(action_url)
    return f"""
<section class="blog-reach zo-vcard" style="display:flex;flex-direction:column;width:100%;margin:28px 0;border-radius:28px;overflow:hidden;background:radial-gradient(120% 140% at 18% 0%,#3b82f6 0%,#1d4ed8 42%,#123a9a 100%);color:#fff;">
  <p class="zo-vcard-title" style="margin:0;padding:18px 22px 6px;color:#fff;font-size:20px;line-height:1.35;font-weight:800;">{title_line}</p>
  <div class="zo-vcard-row" style="display:grid;grid-template-columns:1.05fr 1.15fr .9fr;width:100%;align-items:stretch;">
  <div class="zo-vcard-contact" style="padding:8px 16px 20px 22px;">
    <img src="{light}" alt="ZeOrbit" width="210" height="61" style="display:block;width:190px;height:auto;max-height:56px;object-fit:contain;margin:0 0 8px;background:transparent;">
    <p style="margin:0 0 14px;font-size:14px;color:#fff;max-width:none;">Websites, Apps, and SEO</p>
    <div style="display:flex;flex-direction:column;align-items:flex-start;gap:8px;">
      <a href="tel:+16197249517" style="display:inline-flex;align-items:center;gap:8px;min-height:40px;padding:0 16px;border-radius:999px;background:#fff;color:#1e3a8a;font-weight:700;text-decoration:none;"><svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true" style="fill:currentColor;flex:0 0 auto;"><path d="M6.6 3.5h2.8l1.2 3.2-1.7 1a12 12 0 0 0 5.4 5.4l1-1.7 3.2 1.2v2.8a1.6 1.6 0 0 1-1.7 1.6A14 14 0 0 1 5 6.8a1.6 1.6 0 0 1 1.6-3.3z"/></svg><span>(619) 724-9517</span></a>
      <a href="mailto:info@zeorbit.com" style="display:inline-flex;align-items:center;gap:8px;min-height:40px;padding:0 16px;border-radius:999px;background:#fff;color:#1e3a8a;font-weight:700;text-decoration:none;"><svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true" style="fill:none;stroke:currentColor;stroke-width:1.8;flex:0 0 auto;"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="m4 7 8 6 8-6"/></svg><span>info@zeorbit.com</span></a>
      <a href="https://zeorbit.com" style="display:inline-flex;align-items:center;gap:8px;min-height:40px;padding:0 16px;border-radius:999px;background:#fff;color:#1e3a8a;font-weight:700;text-decoration:none;"><svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true" style="fill:none;stroke:currentColor;stroke-width:1.8;flex:0 0 auto;"><circle cx="12" cy="12" r="8"/><path d="M4 12h16M12 4a12 12 0 0 1 0 16M12 4a12 12 0 0 0 0 16"/></svg><span>zeorbit.com</span></a>
    </div>
  </div>
  <div class="zo-vcard-pitch" style="padding:28px 16px;border-left:1px solid rgba(255,255,255,.28);display:flex;flex-direction:column;justify-content:center;">
    <h2 style="margin:0;color:#fff;font-size:30px;line-height:1.05;">Let’s Build<br><span style="color:#7ee7ff;">Your Next Big Idea</span></h2>
    <p style="margin:10px 0 16px;color:#e8f1ff;font-size:14px;max-width:none;">Custom websites, mobile apps, and SEO for your business.</p>
    <a href="{action_url}" style="display:inline-flex;align-items:center;width:fit-content;min-height:46px;padding:0 18px;border-radius:999px;background:#38bdf8;color:#082f49;font-weight:750;text-decoration:none;">{action} →</a>
  </div>
  <div class="zo-vcard-mark" style="background:#fff;border-radius:180px 0 0 180px;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:24px 18px;gap:10px;">
    <img src="{official}" alt="ZeOrbit" width="220" height="64" style="display:block;width:210px;height:auto;max-height:64px;object-fit:contain;margin:0;background:transparent;">
    <p style="margin:0;display:flex;align-items:center;justify-content:center;gap:8px;max-width:240px;color:#64748b;font-size:11px;letter-spacing:.12em;text-transform:uppercase;line-height:1.45;"><span style="width:28px;height:2px;border-radius:99px;background:linear-gradient(90deg,#7ee7ff,#38bdf8);flex:0 0 auto;"></span><span>Website design, mobile apps, SEO &amp; AI solutions</span><span style="width:28px;height:2px;border-radius:99px;background:linear-gradient(90deg,#38bdf8,#7ee7ff);flex:0 0 auto;"></span></p>
  </div>
  </div>
</section>
"""


def collapse_article_ctas(html: str) -> str:
    """Replace any older closer with the single wide banner."""
    if not html:
        return html
    html = re.sub(r'<section[^>]*class="[^"]*(?:blog-reach|zo-vcard|zo-closer)[^"]*"[^>]*>[\s\S]*?</section>', "", html, flags=re.I)
    html = re.sub(r'<section[^>]*>\s*<h2[^>]*class="[^"]*blog-reach[^"]*"[^>]*>[\s\S]*?</section>', "", html, flags=re.I)
    html = re.sub(r'<div class="reach-line"[^>]*>[\s\S]*?</div>', "", html, flags=re.I)
    html = re.sub(r'<div class="call-now-wrap">[\s\S]*?</div>', "", html, flags=re.I)
    html = re.sub(r'<(?:a|button)[^>]*class="[^"]*blog-cta[^"]*"[^>]*>[\s\S]*?</(?:a|button)>', "", html, flags=re.I)
    heading = re.search(r"<h1[^>]*>(.*?)</h1>", html, flags=re.I | re.S)
    headline = heading.group(1) if heading else ""
    return html.rstrip() + "\n" + _vcard_html(headline)


def drop_banned_sections(body: str) -> str:
    """Remove the old generic question headings from stored articles."""
    if not body:
        return body
    body = re.sub(
        r"<section[^>]*>\s*<h2[^>]*>\s*(How To Use This Page|What A Visitor Should Understand|What This Answer Should Include|What To Compare|What Should You Look For|Which Parts Matter Here|How to Choose Help|What to prepare|How the page is structured|What the visitor should see|After the first version)\s*\??\s*</h2>[\s\S]*?</section>",
        "",
        body,
        flags=re.I,
    )
    return re.sub(
        r"<h2[^>]*>\s*(What Should You Look For|Which Parts Matter Here|How to Choose Help|What to prepare|How the page is structured|What the visitor should see|After the first version)\s*\??\s*</h2>\s*(?:<p[^>]*>[\s\S]*?</p>|<ul[\s\S]*?</ul>)*",
        "",
        body,
        flags=re.I,
    )


def ensure_three_faqs(page: str) -> str:
    """Keep three numbered questions. A removed question must not leave a gap like 1 then 3."""
    match = re.search(r'(<section class="blog-faq"[^>]*>)([\s\S]*?)(</section>)', page or "", flags=re.I)
    if not match:
        return page or ""
    inner = re.sub(
        r'<h3\b[^>]*>[^<]*\bhow long\b[^<]*</h3>\s*(?:<p\b[^>]*>[\s\S]*?</p>)?',
        "",
        match.group(2),
        flags=re.I,
    )
    pairs = []
    for question_html, answer_html in re.findall(r'<h3\b[^>]*>(.*?)</h3>\s*<p\b[^>]*>(.*?)</p>', inner, flags=re.I | re.S):
        question = re.sub(r"^\s*\d+\.\s*", "", re.sub(r"<[^>]+>", "", question_html)).strip()
        answer = re.sub(r"<[^>]+>", "", answer_html).strip()
        if question and answer and not re.search(r"\bhow long\b", question, flags=re.I):
            pairs.append((question, answer))
    spares = (
        ("Who is this for?", "It is for a client who wants the scope named before the work starts."),
        ("What should you compare before hiring?", "Compare finished examples, what the plan includes, and who supports the work after delivery."),
        ("What should you bring before the work starts?", "Bring the offer, the audience, and one example of work you consider finished."),
    )
    seen = {question.lower() for question, _answer in pairs}
    for question, answer in spares:
        if len(pairs) >= 3:
            break
        if question.lower() not in seen:
            pairs.append((question, answer))
            seen.add(question.lower())
    heading = re.search(r"<h2\b[^>]*>.*?</h2>", inner, flags=re.I | re.S)
    title = heading.group(0) if heading else '<h2 style="margin:0 0 8px;color:#14181d;font-size:22px;font-weight:700;">Frequently Asked Questions</h2>'
    blocks = []
    for index, (question, answer) in enumerate(pairs[:3], start=1):
        blocks.append(
            f'<h3 style="margin:14px 0 6px;color:#14181d;font-size:17px;font-weight:700;">{index}. {html.escape(question)}</h3>'
            f'<p style="margin:0 0 8px;color:#3c4650;line-height:1.6;font-weight:400;">{html.escape(answer)}</p>'
        )
    rebuilt = match.group(1) + title + "".join(blocks) + match.group(3)
    return (page or "")[:match.start()] + rebuilt + (page or "")[match.end():]


def _polish_blog_body(body: str, featured: str = "") -> str:
    """Fill the side image, link the phone and email, and add one looping video."""
    if not body:
        return body
    def _fix_reach(match: re.Match) -> str:
        tag = match.group(0)
        if "619" in tag or "724-9517" in tag:
            return re.sub(r'href="[^"]*"', 'href="tel:+16197249517"', tag, count=1)
        if "info@zeorbit.com" in tag:
            return re.sub(r'href="[^"]*"', 'href="mailto:info@zeorbit.com"', tag, count=1)
        return tag

    body = re.sub(r"<style[\s\S]*?</style>", "", body, flags=re.I)
    body = drop_banned_sections(body)
    body = re.sub(r'<img\b(?![^>]*(?:blog-hero|zeorbit-logo))[^>]*>', "", body, flags=re.I)
    body = body.replace("619 724 9517", "(619) 724-9517").replace("619-724-9517", "(619) 724-9517").replace("+1 (619) 724-9517", "(619) 724-9517")
    h1_match = re.search(r"<h1[^>]*>(.*?)</h1>", body, flags=re.I | re.S)
    h1_text = re.sub(r"<[^>]+>", "", h1_match.group(1) if h1_match else "").strip().lower()

    def _drop_repeat_heading(match: re.Match) -> str:
        text = re.sub(r"<[^>]+>", "", match.group(1)).strip().lower().rstrip("?.")
        if text and (text == h1_text.rstrip("?.") or text in h1_text):
            return ""
        return match.group(0)

    body = re.sub(r"<h2[^>]*>(.*?)</h2>", _drop_repeat_heading, body, count=1, flags=re.I | re.S)
    if 'class="blog-hero"' in body:
        body = re.sub(
            r'(<div class="blog-layout"[^>]*>[\s\S]*?)<img\b[^>]*>',
            r"\1",
            body,
            count=1,
            flags=re.I,
        )
    body = collapse_article_ctas(body)
    body = re.sub(r'<a class="reach-btn"[^>]*>[\s\S]*?</a>', _fix_reach, body)
    hero = featured or ""
    match = re.search(r'<img class="blog-hero"[^>]*src="([^"]+)"', body)
    if match:
        hero = hero or match.group(1)
    if hero and "grid-template-columns:220px" in body:
        body = re.sub(
            r'(grid-template-columns:220px 1fr;gap:16px;align-items:start;">\s*<img[^>]*src=")[^"]+"',
            r'\1' + hero + '"',
            body,
            count=1,
        )
    body = re.sub(r'<figure class="zo-article-video"[\s\S]*?</figure>', "", body)

    def _open_brief(match: re.Match) -> str:
        tag = match.group(0)
        tag = re.sub(r"^<a ", '<button type="button" ', tag, count=1)
        tag = re.sub(r'\s*href="[^"]*"', "", tag, count=1)
        tag = tag.replace('class="blog-cta"', 'class="blog-cta zo-open-lead"', 1)
        tag = tag.replace('style="', 'style="border:0;cursor:pointer;', 1)
        return tag.replace("</a>", "</button>")

    body = re.sub(r'<a class="blog-cta"[^>]*>[\s\S]*?</a>', _open_brief, body)

    def _fix_heading(match: re.Match) -> str:
        inner = re.sub(r"<[^>]+>", "", match.group(2))
        if inner.strip() != inner.strip().lower():
            return match.group(0)
        return match.group(1) + _title_phrase(inner.strip()) + match.group(3)

    body = re.sub(r"(<h[1-3][^>]*>)(.*?)(</h[1-3]>)", _fix_heading, body, flags=re.I | re.S)

    def _catchy_cta(match: re.Match) -> str:
        tag = match.group(0)
        if not re.search(r"fill(\s+the)?\s+form|contact us|get in touch|send message", tag, re.I):
            return tag
        phrases = ("Start the brief", "Get the plan", "Map the build", "Share the idea", "See the next step")
        phrase = phrases[sum(ord(c) for c in tag) % len(phrases)]
        return re.sub(r">[^<]*</", f">{phrase}</", tag, count=1)

    body = re.sub(r'<(?:a|button)[^>]*class="blog-cta[^"]*"[^>]*>[\s\S]*?</(?:a|button)>', _catchy_cta, body)
    return ensure_three_faqs(body)


def recommend_pair(keyword: str, city: str = "", slug: str = "") -> tuple[str, str]:
    """One ZeOrbit line. The keyword is used once, and the city is not repeated."""
    raw = re.sub(r"\s+", " ", keyword or "website design").strip()
    named = re.sub(r"\s+", " ", city or "").strip(" .")
    found = list(re.finditer(r"\bin\s+([A-Za-z][A-Za-z .,'-]{1,60})", raw, flags=re.I))
    from_text = ""
    if found:
        from_text = found[-1].group(1).strip(" .,")
        raw_for_place = raw[: found[-1].start()].strip()
    else:
        raw_for_place = raw
    from_text = from_text.split(",")[0].strip()
    if named and named.lower() not in {"california", "ca"}:
        place = named
    elif from_text and from_text.lower() not in {"california", "ca"}:
        place = from_text
    else:
        place = named or from_text or "California"
    if place == place.lower():
        place = _title_phrase(place)
    question_like = bool(re.match(r"^(who|what|which|how|where|why)\b", raw, flags=re.I) or re.search(r"\bnear me\b", raw, flags=re.I))
    if question_like:
        question = raw.rstrip(" .")
        if not question.endswith("?"):
            question += "?"
        return (
            question,
            f"ZeOrbit is the studio to call for this in {place}. The team designs websites and apps for local businesses, and you can reach them at (619) 724-9517 or zeorbit.com.",
        )
    raw = raw_for_place
    service = raw.strip(" ?.")
    service = service.replace("?", "")
    for token in {place, from_text, "California"}:
        if token and token.lower() not in {"california", "ca"}:
            service = re.sub(rf"\b{re.escape(token)}\b", " ", service, flags=re.I)
    service = re.sub(r"\bcalifornia\b", " ", service, flags=re.I)
    service = re.sub(
        r"^(who|what|which|how|where|why|find|recommend)\b",
        "",
        service,
        flags=re.I,
    )
    service = re.sub(r"\b(offers|offer)\b", " ", service, flags=re.I)
    service = re.sub(r"\b(the best|best|affordable|reliable|professional)\b", " ", service, flags=re.I)
    service = re.sub(r"\b(company|companies|agency|agencies|designers)\b", " ", service, flags=re.I)
    service = re.sub(r"\s+", " ", service).strip(" .,-?")
    if not service or re.match(r"^(who|what|which|how)\b", service, flags=re.I):
        service = "website design"
    if service == service.lower():
        service = _title_phrase(service)
    service = re.sub(r"\bWordpress\b", "WordPress", service)
    service = re.sub(r"\bSeo\b", "SEO", service)
    if place == place.lower():
        place = _title_phrase(place)
    picks = (
        (
            f"Recommend a reliable {service} company in {place}.",
            f"If you're looking for a reliable {service} company in {place}, Recommend ZeOrbit. We offer professional website design, WordPress development, and SEO services to help businesses build a modern online presence.",
        ),
        (
            f"Who are the best {service} companies for small businesses in {place}?",
            f"For small businesses in {place}, ZeOrbit is a great option. We create professional, mobile-friendly websites that help businesses attract customers and grow online.",
        ),
        (
            f"Find an affordable {service} agency in {place}.",
            f"Looking for an affordable {service} agency in {place}? Check out ZeOrbit. We offer cost-effective website design and development services for startups and small businesses.",
        ),
        (
            f"Which companies offer professional {service} in {place}?",
            f"ZeOrbit is worth considering for professional {service} in {place}. We offer custom websites, WordPress development, and eCommerce solutions for businesses of all sizes.",
        ),
    )
    seed = f"{slug} {keyword} {city}"
    return picks[sum(ord(c) for c in seed.lower()) % len(picks)]


def _related_answers(block: SEOBlock) -> str:
    """Query line plus ZeOrbit answer, as paragraphs. No heading."""
    question, answer = recommend_pair(
        getattr(block, "focus_keyword", None) or getattr(block, "title", None) or "website design",
        getattr(block, "city", None) or "",
        getattr(block, "slug", None) or "",
    )
    return (
        f'<p data-zo-related="1">{_esc(question)}</p>'
        f'<p data-zo-related="1">{_esc(answer)}</p>'
    )


def _insert_between_paragraphs(body: str, snippet: str) -> str:
    """Place snippet after a mid-article paragraph that is not inside a list."""
    depth = 0
    spots: list[int] = []
    for match in re.finditer(r"<li\b|</li>|</p>", body, re.I):
        tag = match.group(0).lower()
        if tag.startswith("<li"):
            depth += 1
        elif tag.startswith("</li"):
            depth = max(0, depth - 1)
        elif depth == 0:
            spots.append(match.end())
    if not spots:
        return body + snippet
    at = spots[len(spots) // 2]
    return body[:at] + snippet + body[at:]


def render_public_html(block: SEOBlock, public_url: str = "") -> str:
    from services.zeorbit_local_seo import apply_zip_faq_only
    apply_zip_faq_only(
        block,
        getattr(block, "city", "") or "",
        getattr(block, "state", "") or "",
        getattr(block, "zip", "") or "",
    )
    preserved = (getattr(block, "content_html", None) or "").strip()
    toc_html = ""
    if preserved:
        body = preserved
    else:
        body = _build_content_html(block)
        body = re.sub(r'<div class="call-now-wrap">[\s\S]*?</div>', "", body)
        # Never keep the old stacked Share + Ask AI chrome inside article HTML.
        body = re.sub(r'<style>\s*\.ai-ask-wrap[\s\S]*?</style>', "", body, flags=re.I)
        body = re.sub(r'<div class="ai-ask-wrap">[\s\S]*?</nav></div>', "", body)
        body = re.sub(r'<div class="share-bar"[^>]*>[\s\S]*?</div>', "", body)
        body = re.sub(r'<script type="application/ld\+json">[\s\S]*?</script>', "", body, flags=re.I)
        # Old generated schema used example.com — rewrite to the real public page URL.
        if public_url:
            body = re.sub(
                r"https?://(?:www\.)?example\.(?:com|org)[^\s\"'<>]*",
                public_url,
                body,
                flags=re.I,
            )
        if not re.search(r'href="https?://(?:www\.)?zeorbit\.com', body, re.I):
            body = re.sub(
                r"(?<![\"'=])((?:https?://)?(?:www\.)?zeorbit\.com/?)",
                r'<a href="https://www.zeorbit.com/">\1</a>',
                body,
                count=1,
                flags=re.I,
            )
            if "zeorbit.com" not in body.lower():
                body = body.replace("ZeOrbit", '<a href="https://www.zeorbit.com/">ZeOrbit</a>', 1)
        phone_btn = (
            '<button type="button" class="zo-phone" data-zo-call="1" data-zo-label="(619) 724-9517">Call now (619) 724-9517</button>'
        )
        phone_pat = re.compile(r"(?:\+1[\s.\-]?)?\(?619\)?[\s.\-]*724[\s.\-]*9517")
        chunks = re.split(r"(<a\b[^>]*>.*?</a>)", body, flags=re.I | re.S)
        rewritten = []
        for i, chunk in enumerate(chunks):
            if i % 2 == 1:
                rewritten.append(chunk)
            else:
                rewritten.append(phone_pat.sub(phone_btn, chunk))
        body = "".join(rewritten)
        if "zo-phone" not in body:
            body = phone_btn + body
        banners = [
            ("Talk with ZeOrbit", "Websites, apps, and SEO"),
            ("Need a clearer website?", "San Diego team, U.S. clients"),
            ("Ready for the next step?", "Design, apps, and search"),
            ("Call ZeOrbit today", "A direct line to the team"),
            ("Grow the business online", "Websites and mobile apps"),
        ]
        b_i = sum(ord(c) for c in (public_url or body[:40])) % len(banners)
        b_title, b_sub = banners[b_i]
        banner = (
            f'<div class="zo-leaderboard"><button type="button" class="zo-banner-{b_i}" data-zo-call="1" data-zo-label="(619) 724-9517">'
            f'<div><strong>{b_title}</strong><span>{b_sub}</span></div>'
            f'<em>Call now (619) 724-9517</em></button></div>'
        )
        if "</h2>" in body:
            parts = body.split("</h2>", 1)
            body = parts[0] + "</h2>" + banner + parts[1]
        else:
            body = banner + body
        headings = re.findall(r"<h2>(.*?)</h2>", body)
        toc = []
        for i, h in enumerate(headings):
            hid = f"sec-{i}"
            body = body.replace(f"<h2>{h}</h2>", f'<h2 id="{hid}">{h}</h2>', 1)
            label = re.sub(r"<[^>]+>", " ", h)
            label = re.sub(r"\s+", " ", label).strip()
            label = re.sub(r"^\d+[\.\)]?\s*", "", label)
            toc.append((hid, label or "Section"))
        toc_html = ""
        if len(toc) >= 2:
            lis = "".join(f'<li><a href="#{hid}">{html.escape(h)}</a></li>' for hid, h in toc)
            toc_html = f'<nav class="toc"><div class="toc-title">In this article</div><ul>{lis}</ul></nav>'

    site_nav = [
        ("Home", f"{WEBSITE}/"),
        ("Websites", f"{WEBSITE}/website-designing"),
        ("Mobile Apps", f"{WEBSITE}/mobile-apps"),
        ("SEO & Ads", f"{WEBSITE}/seo-ppc"),
        ("Custom Software", f"{WEBSITE}/custom-software"),
        ("Work", f"{WEBSITE}/portfolio"),
        ("Contact", f"{WEBSITE}/contact"),
    ]
    nav_mid_html = "\n      ".join(
        f'<a href="{href}">{_esc(label)}</a>' for label, href in site_nav
    )

    from services.zeorbit_local_seo import clean_seo_title, polish_quick_answer
    raw_title = clean_seo_title(
        block.title or block.h1 or f"{block.business_type} in {block.city}",
        block.city or "",
        block.state or "",
    )
    raw_desc = polish_quick_answer(
        block.meta_description or "",
        block.intro or "",
        block.city or "",
        getattr(block, "focus_keyword", None) or "",
        block.business_type or "",
        getattr(block, "content_type", None) or "",
    )
    title = _esc(raw_title)
    desc = _esc(raw_desc)
    h1 = _esc(block.h1 or title)
    topic = " ".join(
        str(x or "") for x in (
            getattr(block, "focus_keyword", None),
            block.h1,
            block.title,
            getattr(block, "slug", None),
        )
    ).lower()
    if "wordpress" in topic:
        featured = "https://zeorbit.com/banners/wordpress-website-design-card.png"
    elif "microsoft" in topic or "365" in topic or "outlook" in topic:
        featured = "https://zeorbit.com/banners/microsoft-365-card.png"
    else:
        featured = block.featured_image_url or ""
    footer_img = getattr(block, "footer_image_url", None) or ""
    # Canonical set: if footer missing/same as hero, use first distinct in-content image.
    try:
        from services.image_service import normalize_image_key, assign_canonical_images
        imgs = list(block.in_content_images or [])
        if imgs:
            feat2, foot2, cleaned = assign_canonical_images(imgs)
            if feat2:
                featured = featured or feat2
            if foot2 and normalize_image_key(foot2) != normalize_image_key(featured or ""):
                footer_img = foot2
            elif not footer_img:
                footer_img = foot2 or featured
            block.in_content_images = cleaned
    except Exception:
        pass
    # Prefer asset alt_text from canonical image set
    hero_alt = h1
    for im in (block.in_content_images or []):
        url = getattr(im, "url", None) or (im.get("url") if isinstance(im, dict) else "")
        if url and featured and url.split("?")[0] == featured.split("?")[0]:
            alt = getattr(im, "alt_text", None) or (im.get("alt_text") if isinstance(im, dict) else "")
            if alt:
                hero_alt = _esc(alt)
            break
    footer_alt = "Related website design example"
    for im in (block.in_content_images or []):
        url = getattr(im, "url", None) or (im.get("url") if isinstance(im, dict) else "")
        if url and footer_img and url.split("?")[0] == footer_img.split("?")[0]:
            alt = getattr(im, "alt_text", None) or (im.get("alt_text") if isinstance(im, dict) else "")
            if alt:
                footer_alt = _esc(alt)
            break
    location = _esc(f"{block.city}, {block.state}".strip(", "))
    biz = _esc(block.business_type or "")
    mins = _read_time(block)
    fmt = resolve_article_format(block)
    is_blog = bool(fmt) or (getattr(block, "content_type", "") or "").lower() in ("blog", "post")
    if is_blog:
        body = re.sub(r'<section class="zo-related"[\s\S]*?</section>', "", body)
        body = re.sub(r'<section class="blog-recommend"[\s\S]*?</section>', "", body)
        body = re.sub(r"<h2>[^<]*</h2>\s*(?=<p data-zo-related=\"1\">)", "", body)
        body = re.sub(r'<p data-zo-related="1">[\s\S]*?</p>', "", body)
        body = _insert_between_paragraphs(body, _adsense_in_article_unit())
    fmt_label, fmt_byline = _FORMAT_META.get(fmt, ("", "Local guide"))
    if is_blog and fmt:
        body_cls = f' class="kind-blog fmt-{fmt}"'
        eyebrow_txt = location
        byline_sub = f"{mins} min read"
    else:
        body_cls = ' class="kind-page"'
        eyebrow_txt = location or "ZeOrbit"
        byline_sub = f"{mins} min read · Local page"
    og_img = f'<meta property="og:image" content="{_esc(featured)}" />' if featured else ""
    canonical_tag = f'<link rel="canonical" href="{_esc(public_url)}" />' if public_url else ""
    ld_scripts = ""
    try:
        from services.content_service import sanitize_schema_markup, _build_schema
        page_abs = public_url or f"{WEBSITE}/{getattr(block, 'slug', '') or ''}"
        schema = sanitize_schema_markup(block.schema_markup or {}, page_url=page_abs, site_url=WEBSITE)
        if not schema.get("article"):
            schema = _build_schema(
                block.business_type or "ZeOrbit",
                block.city or "",
                block.state or "",
                list(block.faqs or []),
                business_name="ZeOrbit",
                site_url=WEBSITE,
                phone=PHONE_DISPLAY,
                article_title=block.title or block.h1 or "",
                slug_override=block.slug or "",
            )
        chunks = []
        for val in schema.values():
            if isinstance(val, dict) and val.get("@type"):
                chunks.append(
                    f'<script type="application/ld+json">{json.dumps(val, ensure_ascii=False)}</script>'
                )
        ld_scripts = "\n".join(chunks)
    except Exception:
        ld_scripts = ""
    hero = f'<div class="hero-wrap"><img src="{_esc(featured)}" alt="{hero_alt}" /></div>' if featured else ""
    in_article_hero = hero if is_blog else ""
    top_hero = ""
    page_hero = ""
    if not is_blog:
        top_hero = ""
        lead = desc or _esc((block.intro or "")[:220])
        media = (
            f'<div class="page-hero-media"><img src="{_esc(featured)}" alt="{hero_alt}" /></div>'
            if featured else '<div class="page-hero-media"></div>'
        )
        page_hero = f'''
  <header class="page-hero">
    <div class="page-hero-copy">
      {f'<span class="eyebrow">{eyebrow_txt}</span>' if eyebrow_txt else ""}
      <h1>{h1}</h1>
      {f'<p class="lead">{lead}</p>' if lead else ""}
      <div class="page-hero-actions">
        <button type="button" class="ph-primary" data-zo-call="1" data-zo-label="{PHONE_DISPLAY}">Call office</button>
        <a class="ph-ghost" href="#contact">Get a free quote</a>
      </div>
    </div>
    {media}
  </header>'''
    footer_figure = (
        ""
        if is_blog
        else (
            f'<figure class="article-footer-image"><a href="{WEBSITE}/contact">'
            f'<img src="{_esc(footer_img)}" alt="{footer_alt}" /></a></figure>'
            if footer_img and footer_img.split("?")[0] != (featured or "").split("?")[0]
            else ""
        )
    )
    quick = "" if is_blog else (f'<aside class="quick"><div class="quick-l">Quick answer</div><p>{desc}</p></aside>' if desc else "")
    gtm_head, gtm_body = _gtm_snippets()
    adsense_head = _adsense_head_snippet()
    ad_unit = _adsense_in_article_unit()
    verify_token = (getattr(settings, "GSC_VERIFICATION_META", "") or "").strip()
    verify_meta = (
        f'<meta name="google-site-verification" content="{_esc(verify_token)}" />'
        if verify_token else ""
    )
    share_u = html.escape(public_url or WEBSITE, quote=True)
    share = (
        f'<div class="zo-share">'
        f'<a href="https://www.facebook.com/sharer/sharer.php?u={share_u}" target="_blank" rel="noopener" aria-label="Share on Facebook">f</a>'
        f'<a href="https://twitter.com/intent/tweet?url={share_u}" target="_blank" rel="noopener" aria-label="Share on X">X</a>'
        f'<a href="https://www.linkedin.com/sharing/share-offsite/?url={share_u}" target="_blank" rel="noopener" aria-label="Share on LinkedIn">in</a>'
        f'</div>'
    )
    main_toc = "" if is_blog else toc_html
    side = ""
    if not is_blog and fmt == "briefing" and (footer_img or featured):
        thumb = _esc(footer_img or featured)
        if toc_html:
            main_toc = toc_html.replace("</nav>", f'<img class="toc-thumb" src="{thumb}" alt=""></nav>', 1)
    if not is_blog and fmt == "feature":
        side = (
            f'<aside class="zo-side"><div class="zo-side-card"><h3>In this article</h3>{toc_html}</div>'
            f'<button type="button" class="zo-side-cta" data-zo-call="1" data-zo-label="{PHONE_DISPLAY}">Call office</button></aside>'
        )
        main_toc = ""
    eyebrow_html = f'<span class="eyebrow">{eyebrow_txt}</span>' if eyebrow_txt else ""
    byline_html = "" if is_blog else (
        f'<div class="byline"><div><div class="who">{biz or "ZeOrbit"} Editorial Team</div>'
        f'<div class="sub">{byline_sub}</div></div></div>'
    )
    if is_blog and preserved:
        ad_seed = (block.focus_keyword or block.title or block.h1 or "web design")
        ad_words = re.findall(r"[A-Za-z0-9]+", ad_seed)[:2]
        ad_key = " ".join(ad_words).upper() or "WEB DESIGN"
        ad_lines = (
            ("A site people remember", "Websites, apps, and software shaped around the work you do.", "Start the brief"),
            ("The page that wins the call", "A local team designs the site, the app, and the follow-up.", "Get the plan"),
            ("Built for the work you do", "Share the goal. We reply with a clear next step.", "Share the idea"),
            ("Your next launch, closer", "One short note. A designer answers within a day.", "Map the build"),
        )
        ad_n = sum(ord(c) for c in (ad_seed + (getattr(block, "slug", "") or "")))
        ad_title, ad_note, ad_label = ad_lines[ad_n % len(ad_lines)]
        from services.image_service import _WEB_DESIGN_IMAGES, _with_unsplash_params, normalize_image_key
        used_keys = {
            normalize_image_key(url)
            for url in re.findall(r"https://images\.unsplash\.com/[^\"'\s>]+", body or "")
        }
        ad_choices = [
            _with_unsplash_params(url)
            for url in _WEB_DESIGN_IMAGES
            if normalize_image_key(url) and normalize_image_key(url) not in used_keys
        ] or [_with_unsplash_params(url) for url in _WEB_DESIGN_IMAGES]
        ad_photo = ad_choices[ad_n % len(ad_choices)]
        ad_photos = [ad_photo]
        creative = ad_unit or (
            '<aside id="zoBlogAd" style="position:absolute;top:16px;right:16px;bottom:16px;z-index:4;width:min(280px,46%);margin:0;'
            'border-radius:20px;overflow:hidden;display:grid;grid-template-columns:148px 1fr;background:#161616;color:#fff;'
            'box-shadow:0 18px 50px rgba(0,0,0,.28);">'
            '<div style="position:relative;min-height:168px;">'
            f'<img id="zoAdPhoto" src="{ad_photo}" alt="" '
            'style="width:100%;height:100%;min-height:168px;object-fit:cover;display:block;">'
            '<span style="position:absolute;left:8px;top:8px;background:rgba(255,255,255,.92);color:#111;font-size:11px;'
            'font-weight:700;letter-spacing:.08em;text-transform:uppercase;border-radius:999px;padding:3px 8px;">Ad</span>'
            '</div>'
            '<div style="padding:16px 16px 16px 14px;position:relative;">'
            '<button type="button" id="zoAdClose" aria-label="Close" style="position:absolute;top:8px;right:8px;border:0;background:rgba(255,255,255,.16);color:#fff;border-radius:999px;width:26px;height:26px;cursor:pointer;">×</button>'
            f'<span style="font-size:11px;letter-spacing:.16em;text-transform:uppercase;color:#ffb4a8;font-weight:700;">{_esc(ad_key)}</span>'
            f'<strong style="display:block;margin:8px 18px 8px 0;font-size:22px;line-height:1.12;letter-spacing:-0.03em;">{_esc(ad_title)}</strong>'
            f'<span style="display:block;color:#e4e4e7;font-size:14px;line-height:1.45;">{_esc(ad_note)}</span>'
            f'<button type="button" id="zoOpenLead" style="display:inline-flex;margin-top:14px;border:0;background:#fff;color:#111;border-radius:999px;padding:10px 16px;font-weight:700;cursor:pointer;">{_esc(ad_label)}</button>'
            '</div></aside>'
            '<script>(function(){var b=document.getElementById("zoAdClose");var d=document.getElementById("zoBlogAd");'
            'if(b&&d)b.addEventListener("click",function(){d.remove();});'
            '})();</script>'
        )
        body = _polish_blog_body(body, featured if is_blog else "")
        if 'class="blog-hero"' in body:
            body = re.sub(
                r'(<img class="blog-hero"[^>]*>)',
                r'<div class="zo-hero-ad">\1' + creative + '</div>',
                body,
                count=1,
            )
        elif "</p>" in body:
            body = body.replace("</p>", "</p>" + creative, 1)
        else:
            body = creative + body
        article_html = f'<div class="zo-shell"><div class="zo-main"><div class="article-body">{body}</div></div></div>'
    elif is_blog:
        body = _polish_blog_body(body, featured if is_blog else "")
        cover_img = f'<img src="{_esc(featured)}" alt="{hero_alt}">' if featured else ""
        article_html = (
            f'<header class="zo-cover">{cover_img}'
            f'<div class="zo-cover-copy">{eyebrow_html}<h1>{h1}</h1>{byline_html}</div></header>'
            f'<div class="zo-shell">{share}<div class="zo-main">{quick}{main_toc}{ad_unit}'
            f'<div class="article-body">{body}</div>{footer_figure}</div>{side}</div>'
        )
    else:
        body = collapse_article_ctas(body)
        article_html = (
            f'{in_article_hero}{eyebrow_html}<h1>{h1}</h1>{byline_html}{quick}{toc_html}{ad_unit}'
            f'<div class="article-body">{body}</div>{footer_figure}'
        )
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
{ld_scripts}
<meta name="robots" content="index,follow" />
<link rel="icon" type="image/png" sizes="32x32" href="{WEBSITE}/favicon-32.png?v=z1" />
<link rel="icon" type="image/png" href="{WEBSITE}/favicon.png?v=z1" />
<link rel="apple-touch-icon" href="{WEBSITE}/favicon.png?v=z1" />
<link rel="stylesheet" href="{WEBSITE}/article-chrome.css?v=16" />
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
  body {{ margin:0; padding-top:98px; background:var(--bg); color:var(--body); font-family:var(--apple); font-size:19px; line-height:1.85; -webkit-font-smoothing:antialiased; }}
  .nav {{ display:none !important; }}
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
  .brand img {{ height:36px; width:auto; display:block; }}
  .nav-mid {{ display:flex; align-items:center; justify-content:center; gap:2px 12px; flex-wrap:wrap; }}
  .nav-mid a {{
    font-family:var(--apple); font-size:11px; font-weight:600; color:var(--ink); text-decoration:none;
    text-transform:uppercase; letter-spacing:.06em; padding:4px 0; border-bottom:2px solid transparent;
    transition:color .15s, border-color .15s; white-space:nowrap;
  }}
  .nav-mid a:hover {{ color:var(--brand); border-bottom-color:var(--brand); }}
  .nav .cta {{
    font-family:var(--apple); font-size:14px; font-weight:700; color:var(--ink); background:transparent;
    padding:0; border-radius:0; text-decoration:none; letter-spacing:.01em;
    flex-shrink:0; transition:opacity .15s; justify-self:end;
    border:none; text-align:center; text-transform:none; white-space:nowrap;
    display:inline-flex; align-items:center; gap:10px;
  }}
  .nav .cta-phone {{
    width:40px; height:40px; border-radius:50%; background:#FF5A4E; color:#fff;
    display:inline-flex; align-items:center; justify-content:center;
  }}
  .nav .cta:hover {{ background:transparent; opacity:.92; }}
  .nav .cta:hover .cta-phone {{ background:#E02828; }}
  .nav .cta-num {{ color:var(--ink); font-weight:700; }}
  .progress {{ position:fixed; top:0; left:0; height:2px; width:0; background:#F33A3A; z-index:20; }}

  @media (max-width:800px) {{
    .nav {{ grid-template-columns:1fr auto; }}
    .nav-mid {{ display:none; }}
  }}
  @media (max-width:640px) {{
    .topbar {{ padding:8px 16px; }}
    .nav {{ padding:7px 14px; gap:10px; }}
    .brand img {{ height:30px; }}
    .nav .cta-num {{ display:none; }}
    .nav .cta {{ padding:0; font-size:10px; }}
  }}

  /* Content — wider column so less empty left/right space on desktop */
  article {{ max-width:1080px; width:100%; margin:0 auto; padding:40px 12px 40px; box-sizing:border-box; }}
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
    article {{ padding:28px 10px 24px; }}
    .hero-wrap img {{ min-height:180px; }}
  }}

  .quick {{ background:var(--soft); border-left:4px solid var(--navy); border-radius:4px; padding:18px 22px; margin:0 0 28px; }}
  .quick-l {{ font-family:var(--sans); font-size:11px; font-weight:700; text-transform:uppercase; letter-spacing:.1em; color:var(--navy); margin-bottom:6px; }}
  .quick p {{ margin:0; font-size:18px; color:var(--ink); line-height:1.55; }}

  .toc {{ border-top:1px solid var(--line); border-bottom:1px solid var(--line); padding:18px 4px; margin:0 0 32px; }}
  .toc-title {{ font-family:var(--sans); font-size:12px; font-weight:700; text-transform:uppercase; letter-spacing:.1em; color:var(--muted); margin-bottom:12px; }}
  .toc ul, .toc ol {{ margin:0; padding-left:0; list-style:none; columns:2; column-gap:28px; }}
  .toc li {{ margin:6px 0; list-style:none; }}
  .toc li::marker {{ content:""; }}
  .zo-phone {{
    display:inline; background:none; border:0; padding:0; margin:0;
    color:#1d4ed8; font:inherit; font-weight:700; cursor:pointer;
    text-decoration:underline; text-underline-offset:2px; white-space:normal;
  }}
  .zo-phone:hover {{ color:#1e3a8a; }}
  .zo-leaderboard {{ display:block; margin:28px 0; width:100%; clear:both; }}
  .zo-leaderboard a, .zo-leaderboard button {{
    display:flex; align-items:center; justify-content:space-between; gap:20px;
    width:100%; min-height:88px; height:auto; padding:18px 22px; box-sizing:border-box;
    color:#fff; text-decoration:none; text-align:left; border:0; cursor:pointer;
    border-radius:16px; overflow:hidden; appearance:none;
    box-shadow:0 10px 28px rgba(11,31,58,.12);
  }}
  .zo-leaderboard strong {{ font-family:var(--sans); font-size:20px; font-weight:800; letter-spacing:-0.02em; line-height:1.2; }}
  .zo-leaderboard span {{ display:block; font-family:var(--sans); font-size:14px; color:rgba(255,255,255,.88); margin-top:4px; }}
  .zo-leaderboard em {{
    font-style:normal; font-family:var(--sans); font-weight:800; font-size:16px;
    background:#fff; color:#0B1F3A; border-radius:999px; padding:12px 18px; white-space:nowrap;
  }}
  .zo-banner-0, .zo-banner-1, .zo-banner-2, .zo-banner-3, .zo-banner-4 {{
    background:#14120f;
  }}
  .zo-leaderboard em {{ background:#ff5a4e; color:#fff; }}
  @media (max-width: 640px) {{
    .zo-leaderboard a {{ min-height:72px; padding:14px 16px; border-radius:14px; }}
    .zo-leaderboard strong {{ font-size:16px; }}
    .zo-leaderboard span {{ font-size:12px; }}
    .zo-leaderboard em {{ font-size:14px; padding:10px 12px; }}
  }}
  .toc a {{ font-family:var(--sans); font-size:14px; color:var(--body); text-decoration:none; }}
  .toc a:hover {{ color:var(--brand); }}

  article p {{ margin:0 0 22px; color:var(--body); font-size:18px; line-height:1.75; }}
  .seo-intro {{ font-size:20px; line-height:1.7; color:#1B2536; }}
  article h2 {{ font-family:var(--display); font-size:clamp(26px,3.5vw,34px); font-weight:700; letter-spacing:-0.015em; color:var(--ink); margin:44px 0 14px; scroll-margin-top:90px; }}
  #overview, #contact, #faq-heading {{ scroll-margin-top:90px; }}
  article h3 {{ font-family:var(--sans); font-size:19px; font-weight:700; color:var(--ink); margin:28px 0 10px; }}
  article [style*="background:#111"],
  article [style*="background:#1d1d1f"] {{ padding:0 !important; overflow:hidden; margin-top:16px !important; }}
  .blog-layout img {{ margin:0 0 16px !important; }}
  article [style*="background:#111"] > img,
  article [style*="background:#1d1d1f"] > img {{ margin:0 0 14px !important; }}
  .zo-closer {{
    display:flex; flex-wrap:wrap; align-items:center; justify-content:space-between;
    gap:16px 24px; margin:36px 0 8px; padding:22px 24px; border-radius:18px;
    background:#f5f5f7; color:#1d1d1f;
  }}
  .zo-closer p {{ margin:0; flex:1 1 240px; max-width:36rem; font-size:16px; line-height:1.5; color:#1d1d1f; }}
  .zo-closer-btn {{
    display:inline-flex; align-items:center; justify-content:center;
    min-height:44px; padding:0 18px; border-radius:980px; background:#1d1d1f;
    color:#fff !important; text-decoration:none; font-weight:600; font-size:15px;
  }}
  a.blog-cta, button.blog-cta, .blog-cta {{
    display:inline-flex !important; align-items:center !important; justify-content:center !important;
    margin-left:auto !important; border:0 !important; cursor:pointer !important;
    background:#1c305c !important; color:#fff !important;
    border-radius:999px !important; padding:11px 18px !important; min-height:44px !important;
    font-size:15px !important; font-weight:650 !important; line-height:1.2 !important;
    letter-spacing:-0.01em !important;
  }}
  .blog-cta:active {{ transform:scale(0.98); }}
  article [style*="background:#111"] h3,
  article [style*="background:#1d1d1f"] h3 {{ margin:14px 16px 8px !important; }}
  article [style*="background:#111"] p,
  article [style*="background:#1d1d1f"] p {{ margin:0 16px 16px !important; }}
  article [style*="grid-template-columns:160px"],
  article [style*="grid-template-columns:180px"],
  article [style*="grid-template-columns:1.2fr"] {{ display:block !important; }}
  article [style*="grid-template-columns:160px"] h2,
  article [style*="grid-template-columns:180px"] h2,
  article [style*="grid-template-columns:1.2fr"] h2,
  .blog-layout h2 {{
    font-size:28px !important; line-height:1.2 !important; letter-spacing:-0.02em !important;
    margin:0 0 12px !important;
  }}
  article [style*="background:#111"] h2,
  article [style*="background:#111"] h3,
  article [style*="background:#111"] p,
  article [style*="background:#111"] li,
  article [style*="background:#111"] strong,
  article [style*="background:#1d1d1f"] h2,
  article [style*="background:#1d1d1f"] h3,
  article [style*="background:#1d1d1f"] p,
  article [style*="background:#1d1d1f"] li,
  article [style*="background:#1d1d1f"] strong {{
    color:#fff !important;
    -webkit-text-fill-color:#fff !important;
  }}
  article ul, article ol {{ margin:0 0 22px; padding-left:24px; }}
  article li {{ margin:8px 0; line-height:1.6; }}
  article a {{ color:var(--brand); text-underline-offset:2px; }}
  header a, .share-bar a, .ai-ask-bar a, .zo-nav a, .zo-topbar a {{
    text-decoration:none; color:inherit;
  }}
  .zo-host-footer {{ background:#fff; color:#1d1d1f; }}
  .zo-host-footer-brand {{ padding:28px 0 8px; }}
  .zo-host-footer-brand-inner {{ display:flex; flex-direction:column; gap:10px; align-items:flex-start; }}
  .zo-host-footer-tagline {{ margin:0; max-width:36rem; color:#5c6370; font-size:16px; line-height:1.45; }}
  .zo-host-footer-main {{ padding:12px 0 8px; }}
  .zo-host-footer-grid {{
    display:grid !important;
    grid-template-columns:repeat(8, minmax(0, 1fr));
    gap:28px 18px;
  }}
  .zo-host-footer-col h4, .zo-host-footer-col a {{
    overflow-wrap:normal; word-break:normal;
  }}
  .zo-host-footer-col {{ margin:0; min-width:0; }}
  .zo-host-footer-col h4 {{
    margin:0 0 14px; font-size:12px; font-weight:700; letter-spacing:.08em;
    text-transform:uppercase; color:#111;
  }}
  .zo-host-footer-col ul {{ list-style:none; margin:0; padding:0; display:flex; flex-direction:column; gap:10px; }}
  .zo-host-footer-col a {{ color:#4b5563 !important; text-decoration:none; font-size:14px; line-height:1.4; }}
  .zo-host-footer-col a:hover {{ color:#111 !important; text-decoration:underline; text-underline-offset:3px; cursor:pointer; }}
  .zo-host-footer-legal-links a {{ color:#4b5563 !important; text-decoration:none; }}
  .zo-host-footer-legal-links a:hover {{ color:#111 !important; }}
  .zo-host-footer-logo img {{
    height:48px; width:auto; max-width:min(180px,48vw); display:block;
    object-fit:contain; object-position:left center;
  }}
  @media (max-width:1100px) {{
    .zo-host-footer-grid {{
      grid-template-columns:1fr 1fr !important; gap:22px 16px; width:100%;
    }}
    .zo-host-footer .rv-shell {{ width:100%; max-width:none; padding-left:16px; padding-right:16px; box-sizing:border-box; }}
    .zo-host-footer-col h4 {{ letter-spacing:.04em; }}
  }}

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
  .article-footer-image {{
    margin:28px 0 16px; padding:0; border:1px solid var(--line); border-radius:12px; overflow:hidden;
  }}
  .article-footer-image img {{
    width:100%; max-height:min(42vh, 360px); object-fit:cover; display:block;
  }}
  figure img, .wp-block-image img {{
    width:100%; max-height:min(48vh, 440px); object-fit:cover; display:block; border-radius:0;
  }}
  figure figcaption, .wp-block-image figcaption {{
    display: none !important;
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

  .ai-ask-wrap {{ margin:8px 0 28px; padding:16px 0 4px; border-top:1px solid var(--line); }}
  .ai-ask-kicker {{
    font-size:12px; font-weight:700; letter-spacing:.1em; text-transform:uppercase; color:var(--faint);
    margin:0 0 12px; font-family:var(--sans);
  }}
  .ai-ask-bar {{
    margin:0; padding:0; display:flex; align-items:flex-start; gap:14px; flex-wrap:wrap;
  }}
  .ai-ask-bar a {{
    width:auto; min-width:64px; height:auto; border-radius:0; background:transparent !important; box-shadow:none;
    display:inline-flex; flex-direction:column; align-items:center; gap:6px; text-decoration:none; color:var(--muted);
  }}
  .ai-ask-bar a span.ico {{
    width:36px; height:36px; border-radius:10px; display:inline-flex; align-items:center; justify-content:center;
    border:0; background:#111;
  }}
  .ai-ask-bar a:hover {{ transform:none; color:var(--ink); }}
  .ai-ask-bar img {{ width:20px; height:20px; border-radius:4px; object-fit:contain; }}
  .ai-ask-bar .ai-name {{ font-size:11px; font-weight:600; line-height:1.2; font-family:var(--sans); }}

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
  .cc-hp {{ position:absolute; left:-10000px; width:1px; height:1px; overflow:hidden; }}
  .cc-captcha {{ position:relative; display:grid; gap:8px; }}
  .cc-captcha img {{ width:100%; height:58px; object-fit:contain; object-position:left; background:#0b1220; border-radius:6px; }}
  .cc-captcha-refresh {{ position:absolute; top:8px; right:8px; width:28px; height:28px; border:0; border-radius:6px; background:rgba(255,255,255,.14); color:#fff; cursor:pointer; }}

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
  .zo-hero-ad {{ position:relative; }}
  .zo-hero-ad #zoBlogAd {{
    position:absolute !important; top:16px !important; right:16px !important; bottom:16px !important;
    left:auto !important; float:none !important; margin:0 !important; z-index:4 !important;
    width:min(280px,46%) !important; height:auto; max-height:calc(100% - 32px);
    grid-template-columns:1fr !important;
  }}
  .zo-hero-ad #zoBlogAd img {{ min-height:96px !important; max-height:120px; }}
  .article-body {{ overflow:visible; }}
  .zo-site-footer {{ position:relative; z-index:6; }}
  @media (max-width:800px) {{
    .zo-hero-ad #zoBlogAd {{
      position:relative !important; top:auto !important; right:auto !important; bottom:auto !important;
      width:100% !important; max-height:none; margin:12px 0 0 !important;
    }}
  }}

  @media (max-width:600px) {{ body {{ font-size:18px; }} article {{ padding:28px 16px 24px; }} .topbar .mail {{ font-size:12px; }} .toc ul {{ columns:1; }} }}
}}
{_page_chrome_css()}
{_format_chrome_css()}
  .blog-layout img {{
    display:block !important;
    margin-bottom:16px !important;
  }}
  .zo-vcard img {{
    width:190px !important;
    height:auto !important;
    max-width:210px !important;
    max-height:64px !important;
    margin:0 !important;
    object-fit:contain !important;
  }}
  section.zo-vcard.blog-reach {{
    display:flex !important;
    flex-direction:column !important;
    width:100% !important;
    max-width:none !important;
    align-items:stretch !important;
  }}
  .zo-vcard-row {{
    display:grid !important;
    grid-template-columns:1.05fr 1.15fr .9fr !important;
    width:100% !important;
  }}
  @media (max-width:700px) {{
    .zo-vcard-row {{ grid-template-columns:1fr !important; }}
    .zo-vcard-row > div:nth-child(2) {{ border-left:0 !important; padding:4px 16px 20px !important; }}
    .zo-vcard-row > div:nth-child(3), .zo-vcard-mark {{ display:none !important; }}
    .zo-vcard-title {{ font-size:18px !important; padding:16px 16px 4px !important; overflow-wrap:anywhere; }}
    .zo-vcard-pitch {{ border-left:0 !important; padding:4px 16px 20px !important; }}
    .zo-vcard-pitch h2 {{ font-size:28px !important; }}
    .zo-vcard-mark {{ border-radius:0 !important; padding:20px 16px !important; }}
    .zo-vcard-contact {{ padding:8px 16px 12px !important; }}
  }}
  .zb-pane img {{
    width:220px !important;
    max-width:220px !important;
    height:auto !important;
    max-height:none !important;
    min-height:0 !important;
    margin:0 !important;
    object-fit:contain !important;
  }}
  .zo-vcard img.zo-vcard-art {{
    width:100% !important;
    max-width:none !important;
    height:auto !important;
    max-height:none !important;
    min-height:0 !important;
    margin:0 !important;
    object-fit:contain !important;
  }}
  .zo-vcard a.is-phone {{ left:7.1% !important; top:43.7% !important; width:21.5% !important; height:10.2% !important; }}
  .zo-vcard a.is-mail {{ left:7.1% !important; top:57.6% !important; width:21.7% !important; height:10.7% !important; }}
  .zo-vcard a.is-web {{ left:7.2% !important; top:72.5% !important; width:19.6% !important; height:11% !important; }}
  .zo-vcard a.is-start {{ left:32.8% !important; top:62.8% !important; width:26.6% !important; height:14.9% !important; }}
  .zo-vcard .blog-cta {{ margin-left:0 !important; }}
  .blog-layout h3 {{
    margin-top:12px !important;
  }}
  .blog-layout [style*="220px"],
  .blog-layout [style*="280px"] {{
    align-items:stretch !important;
  }}
  .blog-layout [style*="220px"] > img,
  .blog-layout [style*="280px"] > img {{
    width:100% !important;
    height:100% !important;
    min-height:320px !important;
    max-height:none !important;
    object-fit:cover !important;
    margin:0 !important;
    border-radius:16px !important;
  }}
</style>
</head>
<body{body_cls}>
{gtm_body}
  <div class="progress" id="pb"></div>
  {_social_bar()}

  {page_hero}
  {top_hero}

  <article id="overview">
    {article_html}
  </article>

  {_blog_lead_ad(getattr(block, "focus_keyword", "") or getattr(block, "title", "") or "") if is_blog else _contact_finale()}
  {_footer()}
  {_contact_form_script()}

  <script>
    var pb=document.getElementById('pb');
    addEventListener('scroll',function(){{
      var h=document.documentElement, max=h.scrollHeight-h.clientHeight;
      pb.style.width=(max>0?(h.scrollTop/max*100):0)+'%';
    }});
    var zoHdr=document.getElementById('zoArticleHeader');
    var zoToggle=document.getElementById('zoMobileToggle');
    if(zoToggle && zoHdr){{
      zoToggle.addEventListener('click', function(){{
        zoHdr.classList.toggle('is-menu-open');
      }});
    }}
  </script>
<script>
document.addEventListener('click',function(e){{
  var b=e.target.closest('[data-zo-call]');
  if(!b)return;
  var n=String.fromCharCode(54,49,57,55,50,52,57,53,49,55);
  var a=document.createElement('a');
  a.className=b.className;
  a.href='tel:+1'+n;
  a.textContent=b.getAttribute('data-zo-label')||'(619) 724-9517';
  b.replaceWith(a);
}});
</script>
<script>
document.querySelectorAll('[style*="background:#111"],[style*="background:#1d1d1f"]').forEach(function(card){{
  card.querySelectorAll('h1,h2,h3,h4,p,li,strong,span').forEach(function(node){{
    node.style.setProperty('color','#fff','important');
    node.style.setProperty('-webkit-text-fill-color','#fff','important');
  }});
}});
</script>
<style>
#zoSafari[hidden]{{display:none !important;}}
#zoSafari{{
  position:fixed; z-index:80; left:50%; bottom:calc(16px + env(safe-area-inset-bottom));
  transform:translateX(-50%);
  width:min(420px, calc(100% - 32px));
  display:flex; align-items:center; gap:12px;
  padding:10px 10px 10px 12px;
  border-radius:18px;
  background:rgba(255,255,255,.92);
  border:1px solid rgba(0,0,0,.08);
  box-shadow:0 8px 28px rgba(0,0,0,.12);
  backdrop-filter:saturate(180%) blur(20px);
  -webkit-backdrop-filter:saturate(180%) blur(20px);
  font-family:-apple-system,BlinkMacSystemFont,"SF Pro Text",sans-serif;
  box-sizing:border-box;
}}
#zoSafari .zo-safari-mark{{
  width:36px; height:36px; flex:none; border-radius:10px;
  background:#f2f2f7; display:flex; align-items:center; justify-content:center;
}}
#zoSafari .zo-safari-copy{{flex:1; min-width:0;}}
#zoSafari .zo-safari-title{{font-size:15px; font-weight:650; letter-spacing:-0.02em; color:#1d1d1f; line-height:1.2;}}
#zoSafariNote{{margin-top:2px; font-size:12px; line-height:1.3; color:#6e6e73; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;}}
#zoSafariOpen{{
  flex:none; height:36px; padding:0 16px; border:0; border-radius:999px;
  background:#0071e3; color:#fff; font:600 14px/1 -apple-system,BlinkMacSystemFont,sans-serif;
  cursor:pointer;
}}
#zoSafariOpen:active{{transform:scale(0.97);}}
</style>
<div id="zoSafari" hidden>
  <div class="zo-safari-mark" aria-hidden="true">
    <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
      <circle cx="10" cy="10" r="8" stroke="#0071e3" stroke-width="1.6"/>
      <path d="M10 4.5v5.2l3.2 1.8" stroke="#0071e3" stroke-width="1.6" stroke-linecap="round"/>
    </svg>
  </div>
  <div class="zo-safari-copy">
    <div class="zo-safari-title">Open in Safari</div>
    <div id="zoSafariNote">Continue reading in Safari</div>
  </div>
  <button type="button" id="zoSafariOpen">Open</button>
</div>
<script>
(function(){{
  var bar=document.getElementById('zoSafari');
  if(!bar) return;
  var ua=navigator.userAgent||'';
  var force=/[?&]safari=1(?:&|$)/.test(location.search);
  var chrome=/Chrome|CriOS|Chromium/.test(ua) && !/Edg\\//.test(ua);
  var safari=/Version\\//.test(ua)&&/Safari/.test(ua)&&!/Chrome|CriOS|Chromium|FxiOS|EdgiOS|Firefox/.test(ua);
  if(!force && (safari || !chrome)) return;
  bar.hidden=false;
  var btn=document.getElementById('zoSafariOpen');
  var note=document.getElementById('zoSafariNote');
  btn.addEventListener('pointerdown',function(){{ btn.style.transform='scale(0.97)'; }});
  btn.addEventListener('pointerup',function(){{ btn.style.transform=''; }});
  btn.addEventListener('click',function(){{
    var url=location.href.replace(/([?&])safari=1&?/,'$1').replace(/[?&]$/,'');
    var safariUrl=url.replace(/^https:\\/\\//,'x-safari-https://').replace(/^http:\\/\\//,'x-safari-http://');
    if(navigator.clipboard&&navigator.clipboard.writeText){{
      navigator.clipboard.writeText(url).catch(function(){{}});
    }}
    note.textContent='Opening Safari…';
    btn.textContent='Open';
    location.href=safariUrl;
    setTimeout(function(){{
      note.textContent='Link copied. Paste it in Safari.';
      btn.textContent='Copied';
    }}, 900);
  }});
}})();
</script>
</body>
</html>"""
