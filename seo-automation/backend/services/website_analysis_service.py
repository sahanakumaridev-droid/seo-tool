"""
website_analysis_service.py
Fetches a business website, parses its structure, and uses the LLM to build a
structured WebsiteProfile (services, products, audience, brand tone, blog topics)
plus a page inventory used for internal linking.

Degrades gracefully: if the site can't be fetched or the AI call fails, it returns
a WebsiteProfile with analyzed=False so content generation still works (just less grounded).
"""
import json
import re
from urllib.parse import urljoin, urlparse
from typing import List, Optional

import httpx
from bs4 import BeautifulSoup

from config import settings
from models.schemas import WebsiteProfile, SitePage

# In-process cache so a batch of N articles only analyzes the site once.
_CACHE: dict = {}

_UA = {"User-Agent": "Mozilla/5.0 (compatible; SEO-Automation/1.0; +https://example.com/bot)"}


def _normalize_url(url: str) -> str:
    url = (url or "").strip()
    if not url:
        return ""
    if not re.match(r"^https?://", url):
        url = "https://" + url
    return url


def _classify_page(url: str, anchor: str = "") -> str:
    """Guess a page type from its URL/anchor text for internal-linking purposes."""
    text = f"{url} {anchor}".lower()
    if re.search(r"/blog|/news|/article|/post|/insights|/resources", text):
        return "blog"
    if re.search(r"contact|get-in-touch|reach-us|quote|estimate", text):
        return "contact"
    if re.search(r"service|solution|what-we-do|capabilit", text):
        return "service"
    if re.search(r"product|shop|store|pricing", text):
        return "product"
    if re.search(r"location|area|city|near|where-we", text):
        return "location"
    parsed = urlparse(url)
    if parsed.path in ("", "/"):
        return "home"
    return "other"


async def _fetch(client: httpx.AsyncClient, url: str) -> Optional[str]:
    try:
        resp = await client.get(url, headers=_UA, follow_redirects=True)
        if resp.status_code == 200 and "text/html" in resp.headers.get("content-type", "text/html"):
            return resp.text
        if resp.status_code == 200 and "xml" in resp.headers.get("content-type", ""):
            return resp.text
    except Exception as e:
        print(f"[WebsiteAnalysis] fetch error for {url}: {e}")
    return None


async def _build_page_inventory(client: httpx.AsyncClient, base_url: str, homepage_html: str) -> List[SitePage]:
    """Prefer sitemap.xml; fall back to same-domain links on the homepage."""
    base_host = urlparse(base_url).netloc
    pages: dict = {}

    # 1) Try sitemap.xml (regex avoids an lxml dependency)
    sitemap = await _fetch(client, urljoin(base_url, "/sitemap.xml"))
    if sitemap:
        try:
            locs = re.findall(r"<loc>\s*(.*?)\s*</loc>", sitemap, re.IGNORECASE | re.DOTALL)
            for loc in locs[:100]:
                loc = loc.strip()
                if loc and urlparse(loc).netloc == base_host and loc not in pages:
                    pages[loc] = SitePage(url=loc, page_type=_classify_page(loc))
        except Exception as e:
            print(f"[WebsiteAnalysis] sitemap parse error: {e}")

    # 2) Fall back / supplement with homepage links
    try:
        soup = BeautifulSoup(homepage_html, "html.parser")
        for a in soup.find_all("a", href=True):
            href = urljoin(base_url, a["href"].split("#")[0])
            if urlparse(href).netloc != base_host:
                continue
            if href in pages:
                continue
            anchor = a.get_text(strip=True)[:80]
            pages[href] = SitePage(url=href, title=anchor, page_type=_classify_page(href, anchor))
            if len(pages) >= 60:
                break
    except Exception as e:
        print(f"[WebsiteAnalysis] link parse error: {e}")

    return list(pages.values())


def _extract_text_signals(html: str) -> dict:
    """Pull the raw text signals we feed to the LLM."""
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    title = (soup.title.get_text(strip=True) if soup.title else "")
    meta_desc = ""
    md = soup.find("meta", attrs={"name": "description"})
    if md and md.get("content"):
        meta_desc = md["content"].strip()

    headings = [h.get_text(strip=True) for h in soup.find_all(["h1", "h2", "h3"])][:25]
    nav_labels = [a.get_text(strip=True) for a in soup.select("nav a, header a")][:30]
    nav_labels = [n for n in nav_labels if n]

    body_text = soup.get_text(" ", strip=True)
    body_sample = re.sub(r"\s+", " ", body_text)[:4000]

    return {
        "title": title,
        "meta_description": meta_desc,
        "headings": headings,
        "nav_labels": nav_labels,
        "body_sample": body_sample,
    }


async def _ai_profile(url: str, signals: dict) -> Optional[dict]:
    """Ask the (free) LLM to turn raw signals into a structured business profile."""
    from services.llm_service import chat_json, llm_available
    if not llm_available():
        return None

    prompt = f"""You are analyzing a business website to understand the company so we can write on-brand, relevant content.

Website URL: {url}
Page title: {signals['title']}
Meta description: {signals['meta_description']}
Navigation labels: {", ".join(signals['nav_labels'])}
Headings: {" | ".join(signals['headings'])}
Body text sample:
{signals['body_sample']}

Return ONLY valid JSON with EXACTLY this structure:
{{
  "business_name": "the company name",
  "services": ["list of services the business offers"],
  "products": ["list of products, empty if none"],
  "target_audience": "who this business serves (1-2 sentences)",
  "brand_tone": "the tone of the site copy, e.g. professional, friendly, technical",
  "existing_blog_topics": ["topics/themes already covered on the site, empty if unknown"],
  "phone": "primary phone number if visible, else empty string",
  "summary": "2-3 sentence summary of what the business does and for whom"
}}"""
    return await chat_json(prompt, temperature=0.3, max_tokens=1200)


async def analyze_website(url: str, use_cache: bool = True) -> WebsiteProfile:
    """Fetch + parse + AI-profile a website. Always returns a WebsiteProfile."""
    url = _normalize_url(url)
    if not url:
        return WebsiteProfile(url="", analyzed=False)

    if use_cache and url in _CACHE:
        return _CACHE[url]

    profile = WebsiteProfile(url=url, analyzed=False)

    async with httpx.AsyncClient(timeout=20) as client:
        homepage = await _fetch(client, url)
        if not homepage:
            _CACHE[url] = profile
            return profile

        signals = _extract_text_signals(homepage)
        profile.page_inventory = await _build_page_inventory(client, url, homepage)

    ai = await _ai_profile(url, signals)
    if ai:
        profile.business_name = ai.get("business_name", "") or ""
        profile.services = ai.get("services", []) or []
        profile.products = ai.get("products", []) or []
        profile.target_audience = ai.get("target_audience", "") or ""
        profile.brand_tone = ai.get("brand_tone", "") or ""
        profile.existing_blog_topics = ai.get("existing_blog_topics", []) or []
        profile.phone = ai.get("phone", "") or ""
        profile.summary = ai.get("summary", "") or ""
        profile.analyzed = True
    else:
        # Degraded: still expose the title/meta so generation has *some* grounding.
        profile.business_name = signals.get("title", "")
        profile.summary = signals.get("meta_description", "")
        profile.analyzed = bool(profile.page_inventory)

    _CACHE[url] = profile
    return profile
