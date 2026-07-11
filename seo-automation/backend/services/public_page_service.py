"""
public_page_service.py — renders a saved SEOBlock as a public BLOG article
(served at /p/{slug}) styled to match the ZeOrbit brand site: black utility bar
with email + socials, elegant serif display headlines, outlined pill badges,
inline SVG logo. Self-contained; opens instantly in any browser.
"""
import html
import re
from models.schemas import SEOBlock
from services.wordpress_service import _build_content_html

EMAIL = "info@zeorbit.com"

# Social links (brand)
_SOCIALS = [
    ("https://facebook.com/zeorbit", "M9.1 23.7v-8H6.6v-3.7h2.5v-1.6c0-4.1 1.8-6 5.9-6 .4 0 1 0 1.5.1v3.3h-1.4c-1.1 0-1.7.6-1.7 1.7V12h3.4l-.6 3.7h-2.8v8A12 12 0 1 0 9.1 23.7Z"),
    ("https://twitter.com/orbit_ze", "M18.2 2.2h3.3l-7.2 8.3 8.5 11.3h-6.7l-5.2-6.8-6 6.8H1.7l7.7-8.8L1.3 2.2h6.8l4.7 6.2 5.4-6.2Z"),
    ("https://linkedin.com/company/zeorbit", "M20.4 20.5h-3.6v-5.6c0-1.3 0-3-1.8-3s-2.1 1.4-2.1 2.9v5.7H9.4V9h3.4v1.6c.5-.9 1.6-1.9 3.4-1.9 3.6 0 4.3 2.4 4.3 5.5v6.3ZM5.3 7.4a2.1 2.1 0 1 1 0-4.1 2.1 2.1 0 0 1 0 4.1ZM7.1 20.5H3.6V9h3.5v11.5ZM22.2 0H1.8C.8 0 0 .8 0 1.7v20.5C0 23.2.8 24 1.8 24h20.4c1 0 1.8-.8 1.8-1.7V1.7C24 .8 23.2 0 22.2 0Z"),
    ("https://instagram.com/zeorbit", "M12 2.2c3.2 0 3.6 0 4.9.1 3.2.1 4.8 1.7 4.9 4.9.1 1.3.1 1.6.1 4.8s0 3.6-.1 4.8c-.1 3.2-1.7 4.8-4.9 4.9-1.3.1-1.6.1-4.9.1s-3.6 0-4.8-.1c-3.3-.1-4.8-1.7-4.9-4.9C2.2 15.6 2.2 15.2 2.2 12s0-3.6.1-4.8C2.4 4 4 2.4 7.2 2.3 8.4 2.2 8.8 2.2 12 2.2Zm0-2.2C8.7 0 8.3 0 7.1.1 2.7.3.3 2.7.1 7.1 0 8.3 0 8.7 0 12s0 3.7.1 4.9c.2 4.4 2.6 6.8 7 7 1.2.1 1.6.1 4.9.1s3.7 0 4.9-.1c4.4-.2 6.8-2.6 7-7 .1-1.2.1-1.6.1-4.9s0-3.7-.1-4.9c-.2-4.4-2.6-6.8-7-7C15.7 0 15.3 0 12 0Zm0 5.8a6.2 6.2 0 1 0 0 12.4 6.2 6.2 0 0 0 0-12.4ZM12 16a4 4 0 1 1 0-8 4 4 0 0 1 0 8Zm6.4-11.8a1.4 1.4 0 1 0 0 2.9 1.4 1.4 0 0 0 0-2.9Z"),
    ("https://youtube.com/@zeorbit", "M23.5 6.2a3 3 0 0 0-2.1-2.1C19.5 3.5 12 3.5 12 3.5s-7.5 0-9.4.5A3 3 0 0 0 .5 6.2C0 8.1 0 12 0 12s0 3.9.5 5.8a3 3 0 0 0 2.1 2.1c1.9.6 9.4.6 9.4.6s7.5 0 9.4-.5a3 3 0 0 0 2.1-2.1C24 15.9 24 12 24 12s0-3.9-.5-5.8ZM9.5 15.6V8.4l6.3 3.6-6.3 3.6Z"),
]


def _social_bar() -> str:
    icons = "".join(
        f'<a href="{url}" target="_blank" rel="noreferrer" aria-label="social">'
        f'<svg width="15" height="15" viewBox="0 0 24 24" fill="#fff"><path d="{d}"/></svg></a>'
        for url, d in _SOCIALS
    )
    return (f'<div class="topbar"><a class="mail" href="mailto:{EMAIL}">✉ {EMAIL}</a>'
            f'<div class="socials">{icons}</div></div>')


def _logo(size: int = 34) -> str:
    return f"""<svg width="{size}" height="{size}" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
  <g stroke="#1B2A6B" stroke-width="2.4" fill="none">
    <ellipse cx="32" cy="32" rx="27" ry="10.5"/>
    <ellipse cx="32" cy="32" rx="27" ry="10.5" transform="rotate(60 32 32)"/>
    <ellipse cx="32" cy="32" rx="27" ry="10.5" transform="rotate(120 32 32)"/>
  </g>
  <text x="32" y="43" text-anchor="middle" font-family="Georgia,serif" font-weight="900" font-size="30" fill="#1B2A6B">Z</text>
  <g fill="#5A1730"><circle cx="6.5" cy="24" r="3.6"/><circle cx="57.5" cy="40" r="3.6"/><circle cx="20" cy="7" r="3.6"/><circle cx="44" cy="57" r="3.6"/></g>
</svg>"""


def _esc(s: str) -> str:
    return html.escape(s or "", quote=True)


def _read_time(block: SEOBlock) -> int:
    text = " ".join([block.content or "", " ".join(block.h2s or []),
                     " ".join(f"{f.question} {f.answer}" for f in (block.faqs or []))])
    return max(1, round(len(re.findall(r"\w+", text)) / 200))


def render_public_html(block: SEOBlock) -> str:
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
    hero = f'<img class="hero" src="{_esc(featured)}" alt="{h1}" />' if featured else ""
    quick = f'<aside class="quick"><div class="quick-l">Quick answer</div><p>{desc}</p></aside>' if desc else ""

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>{title}</title>
<meta name="description" content="{desc}" />
<meta property="og:type" content="article" />
<meta property="og:title" content="{title}" />
<meta property="og:description" content="{desc}" />
{og_img}
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
  .topbar .mail {{ color:#fff; text-decoration:none; font-size:13px; opacity:.9; }}
  .topbar .socials {{ display:flex; gap:14px; align-items:center; }}
  .topbar .socials a {{ display:inline-flex; opacity:.85; transition:opacity .15s; }}
  .topbar .socials a:hover {{ opacity:1; }}

  /* Header */
  .nav {{ position:sticky; top:0; z-index:10; display:flex; align-items:center; justify-content:space-between;
          padding:16px 30px; background:rgba(255,255,255,0.95); backdrop-filter:blur(10px); border-bottom:1px solid var(--line); }}
  .brand {{ display:flex; align-items:center; gap:11px; font-family:var(--display); font-weight:800; font-size:24px; color:var(--navy); letter-spacing:1px; }}
  .nav .cta {{ font-family:var(--sans); font-size:13px; font-weight:600; color:#fff; background:var(--navy); padding:11px 20px; border-radius:2px; text-decoration:none; text-transform:uppercase; letter-spacing:.05em; }}
  .progress {{ position:fixed; top:0; left:0; height:3px; width:0; background:var(--brand); z-index:20; }}

  article {{ max-width:740px; margin:0 auto; padding:52px 22px 40px; }}
  .eyebrow {{ display:inline-block; font-family:var(--sans); font-size:12px; font-weight:600; text-transform:uppercase; letter-spacing:.14em; color:var(--ink); border:1.5px solid var(--ink); padding:9px 22px; border-radius:999px; margin-bottom:26px; }}
  h1 {{ font-family:var(--display); font-size:clamp(34px,6vw,56px); line-height:1.08; font-weight:800; letter-spacing:-0.01em; color:var(--ink); margin:0 0 24px; }}
  .byline {{ display:flex; align-items:center; gap:12px; font-family:var(--sans); margin:0 0 32px; }}
  .avatar {{ width:44px; height:44px; border-radius:50%; background:var(--navy); color:#fff; font-family:var(--display); font-weight:800; font-size:22px; display:flex; align-items:center; justify-content:center; }}
  .byline .who {{ font-size:14px; font-weight:600; color:var(--ink); }}
  .byline .sub {{ font-size:13px; color:var(--faint); }}
  img.hero {{ width:100%; border-radius:6px; margin:0 0 8px; display:block; box-shadow:0 24px 60px rgba(16,24,40,0.16); }}
  .caption {{ font-family:var(--sans); font-size:12.5px; color:var(--faint); text-align:center; margin:10px 0 34px; }}

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

  .faq-section {{ margin-top:14px; }}
  .faq-item {{ border-bottom:1px solid var(--line); padding:22px 2px; margin:0; background:transparent; }}
  .faq-item h3 {{ margin:0 0 8px; font-size:19px; font-family:var(--display); font-weight:700; }}
  .faq-item p {{ margin:0; font-size:18px; color:var(--muted); }}

  .cta-section {{ margin:52px 0 0; padding:40px; background:var(--navy); color:#fff; border-radius:6px; text-align:center; }}
  .cta-section p {{ font-family:var(--display); font-size:24px; font-weight:700; margin:0; color:#fff; }}

  .bio {{ display:flex; gap:16px; align-items:flex-start; margin:44px 0 0; padding:24px; background:var(--soft); border-radius:6px; }}
  .bio .avatar {{ width:54px; height:54px; }}
  .bio .name {{ font-family:var(--sans); font-weight:700; font-size:15px; color:var(--ink); }}
  .bio .txt {{ font-family:var(--sans); font-size:13.5px; color:var(--muted); margin-top:5px; line-height:1.6; }}

  footer {{ border-top:1px solid var(--line); margin-top:22px; background:var(--soft); }}
  .foot {{ max-width:740px; margin:0 auto; padding:28px 22px; display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:10px; font-family:var(--sans); font-size:13px; color:var(--faint); }}
  .foot .brand {{ font-size:19px; }}

  @media (max-width:600px) {{ body {{ font-size:18px; }} article {{ padding:34px 18px 30px; }} .topbar {{ padding:8px 16px; }} .topbar .mail {{ font-size:12px; }} .toc ol {{ columns:1; }} }}
</style>
</head>
<body>
  <div class="progress" id="pb"></div>
  {_social_bar()}
  <div class="nav">
    <span class="brand">ZEORBIT</span>
    <a class="cta" href="#contact">Get a Free Quote</a>
  </div>

  <article>
    {f'<span class="eyebrow">{location}</span>' if location else ''}
    <h1>{h1}</h1>
    <div class="byline">
      <span class="avatar">Z</span>
      <div>
        <div class="who">{biz or 'ZeOrbit'} Editorial Team</div>
        <div class="sub">{mins} min read · Local guide</div>
      </div>
    </div>
    {hero}
    {f'<div class="caption">{h1}</div>' if featured else ''}
    {quick}
    {toc_html}
    {body}
    <span id="contact"></span>
    <div class="bio">
      <span class="avatar">Z</span>
      <div>
        <div class="name">{biz or 'ZeOrbit'} Editorial Team</div>
        <div class="txt">Local {biz.lower() or 'service'} specialists serving {location or 'your area'}. Published and maintained by ZeOrbit — a U.S.-based web design, software &amp; SEO company.</div>
      </div>
    </div>
  </article>

  <footer>
    <div class="foot">
      <span class="brand">ZEORBIT</span>
      <span>© 2026 ZeOrbit — Crafted websites. Powerful apps. Proven results.</span>
    </div>
  </footer>

  <script>
    var pb=document.getElementById('pb');
    addEventListener('scroll',function(){{
      var h=document.documentElement, max=h.scrollHeight-h.clientHeight;
      pb.style.width=(max>0?(h.scrollTop/max*100):0)+'%';
    }});
  </script>
</body>
</html>"""
