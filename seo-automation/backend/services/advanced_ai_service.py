"""
advanced_ai_service.py — Multi-model AI integration
Supports OpenAI (GPT-4), Anthropic (Claude), and Cohere
Includes streaming, caching, and fallback strategies
"""
import asyncio
import logging
import re
from typing import Optional, AsyncGenerator, Dict, Any

import httpx
from bs4 import BeautifulSoup

from config import settings
from services.llm_service import chat_json

logger = logging.getLogger(__name__)

_MAX_PAGE_EXCERPT = 3000


async def _fetch_page_excerpt(url: str) -> str:
    """Best-effort fetch of a competitor's homepage text, so the analysis is
    grounded in real content instead of the LLM guessing from the URL alone.
    Returns '' on any failure — callers should degrade gracefully."""
    target = url if url.startswith(("http://", "https://")) else f"https://{url}"
    try:
        async with httpx.AsyncClient(
            timeout=15,
            follow_redirects=True,
            headers={"User-Agent": "Mozilla/5.0 (compatible; ZeOrbitSEO/1.0)"},
        ) as client:
            resp = await client.get(target)
        if resp.status_code != 200:
            return ""
        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer"]):
            tag.decompose()
        text = soup.get_text(" ", strip=True)
        return text[:_MAX_PAGE_EXCERPT]
    except Exception as e:
        logger.warning(f"Competitor page fetch failed for {url}: {e}")
        return ""


async def _fetch_page_signals(url: str) -> Dict[str, Any]:
    """Scrape lightweight SEO signals from a competitor page (no LLM)."""
    target = url if url.startswith(("http://", "https://")) else f"https://{url}"
    out = {
        "url": target,
        "title": "",
        "meta_description": "",
        "h1s": [],
        "h2s": [],
        "word_count": 0,
        "has_schema": False,
        "excerpt": "",
    }
    try:
        async with httpx.AsyncClient(
            timeout=15,
            follow_redirects=True,
            headers={"User-Agent": "Mozilla/5.0 (compatible; ZeOrbitSEO/1.0)"},
        ) as client:
            resp = await client.get(target)
        if resp.status_code != 200:
            return out
        soup = BeautifulSoup(resp.text, "html.parser")
        out["title"] = (soup.title.string or "").strip() if soup.title else ""
        md = soup.find("meta", attrs={"name": "description"}) or soup.find(
            "meta", attrs={"property": "og:description"}
        )
        if md and md.get("content"):
            out["meta_description"] = md["content"].strip()
        out["h1s"] = [h.get_text(" ", strip=True) for h in soup.find_all("h1")[:5]]
        out["h2s"] = [h.get_text(" ", strip=True) for h in soup.find_all("h2")[:8]]
        out["has_schema"] = bool(soup.find("script", attrs={"type": "application/ld+json"}))
        for tag in soup(["script", "style", "nav", "footer", "noscript"]):
            tag.decompose()
        text = soup.get_text(" ", strip=True)
        out["word_count"] = len(re.findall(r"\w+", text))
        out["excerpt"] = text[:_MAX_PAGE_EXCERPT]
    except Exception as e:
        logger.warning(f"Competitor signals fetch failed for {url}: {e}")
    return out


def _normalize_domain(url: str) -> str:
    u = (url or "").strip().lower()
    u = re.sub(r"^https?://", "", u)
    u = u.split("/")[0].split("?")[0].strip()
    if u.startswith("www."):
        u = u[4:]
    return u


# Niche → real competitor domains (used when LLM is offline)
_NICHE_COMPETITORS: Dict[str, list] = {
    "web": [
        ("webflow.com", "Popular website builder competing for design-led SMBs"),
        ("squarespace.com", "Template-driven website competitor for small businesses"),
        ("wix.com", "DIY website platform often compared in local web design searches"),
        ("godaddy.com", "Domain + website builder competing in local SMB search"),
        ("wordpress.com", "Managed WordPress competitor for small-business sites"),
        ("shopify.com", "Ecommerce website competitor when stores are in scope"),
    ],
    "marketing": [
        ("hubspot.com", "Inbound marketing / CRM platform competing for local agencies"),
        ("semrush.com", "SEO software competitor for keyword and audit workflows"),
        ("moz.com", "SEO toolkit competitor for agencies and in-house teams"),
        ("mailchimp.com", "Email / marketing automation competitor for SMBs"),
        ("hootsuite.com", "Social scheduling competitor for multi-channel agencies"),
    ],
    "plumbing": [
        ("angihomeservices.com", "National home-services brand competing in local plumbing SERPs"),
        ("mrrooter.com", "Franchise plumbing competitor in many US cities"),
        ("rotorooter.com", "National plumbing brand with strong local SEO footprint"),
        ("yelp.com", "Local directory that captures high-intent plumbing searches"),
        ("homeadvisor.com", "Lead marketplace competing for home-service intent"),
    ],
    "software": [
        ("github.com", "Developer platform competing for software-engineering visibility"),
        ("gitlab.com", "DevOps / software competitor for engineering teams"),
        ("atlassian.com", "Project tools competitor for software orgs"),
        ("digitalocean.com", "Cloud hosting competitor for software products"),
        ("vercel.com", "App hosting competitor for modern web software"),
    ],
    "general": [
        ("yelp.com", "Local directory capturing category search demand"),
        ("angi.com", "Home-services marketplace competing for local leads"),
        ("thumbtack.com", "Lead marketplace for local service businesses"),
        ("bbb.org", "Trust / directory competitor influencing local SERPs"),
        ("clutch.co", "B2B review directory competing for agency visibility"),
    ],
}


def _niche_key(business_type: str) -> str:
    t = (business_type or "").lower()
    if any(k in t for k in ("plumb",)):
        return "plumbing"
    if any(k in t for k in ("market", "seo", "advertis", "agency")) and not any(
        k in t for k in ("web", "website", "wordpress")
    ):
        return "marketing"
    if any(k in t for k in ("software", "saas", "engineer", "coding")):
        return "software"
    if any(k in t for k in ("web", "website", "wordpress", "design", "developer")):
        return "web"
    return "general"


def _heuristic_discover(website: str, business_type: str, city: str) -> Dict[str, Any]:
    own = _normalize_domain(website)
    niche = _niche_key(business_type)
    city_label = (city or "your market").split(",")[0].strip() or "your market"
    pool = list(_NICHE_COMPETITORS.get(niche) or []) + list(_NICHE_COMPETITORS["general"])
    competitors = []
    seen = {own}
    for domain, rationale in pool:
        d = _normalize_domain(domain)
        if not d or d in seen:
            continue
        seen.add(d)
        competitors.append({
            "domain": d,
            "rationale": f"{rationale} — relevant vs {business_type or 'your business'} in {city_label}.",
        })
        if len(competitors) >= 6:
            break
    # Add a couple of local-intent search patterns as actionable targets
    slug_bt = re.sub(r"[^a-z0-9]+", "-", (business_type or "business").lower()).strip("-")
    slug_city = re.sub(r"[^a-z0-9]+", "-", city_label.lower()).strip("-")
    if slug_bt and slug_city:
        competitors.append({
            "domain": f"search:{slug_bt}-{slug_city}",
            "rationale": f"Track local SERP rivals ranking for “{business_type} {city_label}” (open Google and review top results).",
        })
    return {
        "competitors": competitors[:7],
        "source": "heuristic",
        "note": "Suggestions based on your website niche and market (LLM offline / unavailable).",
    }


def _heuristic_analyze(signals: Dict[str, Any], business_type: str, city: str) -> Dict[str, Any]:
    title = signals.get("title") or ""
    meta = signals.get("meta_description") or ""
    h1s = signals.get("h1s") or []
    h2s = signals.get("h2s") or []
    words = int(signals.get("word_count") or 0)
    city_label = (city or "the local market").split(",")[0].strip()
    bt = business_type or "this niche"

    messaging = title or (h1s[0] if h1s else f"Competitor site for {bt}")
    if meta:
        messaging = f"{messaging}\n\n{meta}"

    audience = (
        f"Appears aimed at customers searching for {bt}"
        + (f" in/near {city_label}" if city_label else "")
        + "."
    )

    seo_bits = []
    if title:
        seo_bits.append(f"Title tag: “{title[:90]}”")
    if meta:
        seo_bits.append(f"Meta description present ({len(meta)} chars)")
    else:
        seo_bits.append("Meta description missing or weak")
    seo_bits.append(f"On-page copy ≈ {words} words")
    seo_bits.append("JSON-LD schema detected" if signals.get("has_schema") else "No obvious JSON-LD schema")
    if h1s:
        seo_bits.append(f"H1: {', '.join(h1s[:2])}")
    seo_strategy = "\n".join(f"• {b}" for b in seo_bits)

    expected = ["pricing", "service", "about", "contact", "faq", "blog", "portfolio", "review"]
    blob = " ".join([title, meta, " ".join(h1s), " ".join(h2s), signals.get("excerpt") or ""]).lower()
    missing = [e for e in expected if e not in blob]
    content_gaps = (
        "Likely content gaps vs a strong local SEO page: " + ", ".join(missing[:5])
        if missing else
        "Core page sections look covered — differentiate with stronger local proof and city pages."
    )

    usps = []
    if words >= 800:
        usps.append("Substantial on-page content depth")
    if signals.get("has_schema"):
        usps.append("Structured data present")
    if any(k in blob for k in ("free", "quote", "estimate", "call")):
        usps.append("Clear lead CTA language")
    if not usps:
        usps.append("Brand presence in the same category SERP")

    recs = [
        f"Publish unique city pages targeting “{bt} {city_label}” with distinct proof points.",
        "Add FAQ schema + clear CTAs (call / quote) above the fold.",
        "Differentiate with case studies, reviews, and speed/Core Web Vitals wins.",
        "Track their ranking keywords in Rankings and close content gaps you identified above.",
    ]

    return {
        "messaging": messaging,
        "target_audience": audience,
        "seo_strategy": seo_strategy,
        "content_gaps": content_gaps,
        "unique_selling_points": usps,
        "recommendations": recs,
        "source": "page-scan",
        "fetched_url": signals.get("url") or "",
    }


class AdvancedAIService:
    """Multi-model AI service with streaming and fallback."""
    
    def __init__(self):
        self.openai_enabled = bool(settings.OPENAI_API_KEY)
        self.anthropic_enabled = bool(settings.ANTHROPIC_API_KEY)
        self.cohere_enabled = bool(settings.COHERE_API_KEY)
        
        if self.openai_enabled:
            from openai import AsyncOpenAI
            self.openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        
        if self.anthropic_enabled:
            from anthropic import AsyncAnthropic
            self.anthropic_client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
        
        if self.cohere_enabled:
            import cohere
            self.cohere_client = cohere.AsyncClientV2(api_key=settings.COHERE_API_KEY)
    
    async def generate_content_with_streaming(
        self,
        prompt: str,
        model: str = "gpt-4",
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> AsyncGenerator[str, None]:
        """Generate content with streaming response."""
        
        if model.startswith("gpt"):
            async for chunk in self._stream_openai(prompt, model, temperature, max_tokens):
                yield chunk
        elif model.startswith("claude"):
            async for chunk in self._stream_anthropic(prompt, model, temperature, max_tokens):
                yield chunk
        elif model.startswith("command"):
            async for chunk in self._stream_cohere(prompt, model, temperature, max_tokens):
                yield chunk
        else:
            logger.error(f"Unknown model: {model}")
            yield "Error: Unknown model"
    
    async def _stream_openai(
        self,
        prompt: str,
        model: str,
        temperature: float,
        max_tokens: int
    ) -> AsyncGenerator[str, None]:
        """Stream from OpenAI."""
        if not self.openai_enabled:
            logger.warning("OpenAI not enabled")
            return
        
        try:
            stream = await self.openai_client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            logger.error(f"OpenAI streaming failed: {e}")
            yield f"Error: {str(e)}"
    
    async def _stream_anthropic(
        self,
        prompt: str,
        model: str,
        temperature: float,
        max_tokens: int
    ) -> AsyncGenerator[str, None]:
        """Stream from Anthropic Claude."""
        if not self.anthropic_enabled:
            logger.warning("Anthropic not enabled")
            return
        
        try:
            with self.anthropic_client.messages.stream(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}]
            ) as stream:
                for text in stream.text_stream:
                    yield text
        except Exception as e:
            logger.error(f"Anthropic streaming failed: {e}")
            yield f"Error: {str(e)}"
    
    async def _stream_cohere(
        self,
        prompt: str,
        model: str,
        temperature: float,
        max_tokens: int
    ) -> AsyncGenerator[str, None]:
        """Stream from Cohere."""
        if not self.cohere_enabled:
            logger.warning("Cohere not enabled")
            return
        
        try:
            stream = await self.cohere_client.chat(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True
            )
            
            async for event in stream:
                if hasattr(event, 'text'):
                    yield event.text
        except Exception as e:
            logger.error(f"Cohere streaming failed: {e}")
            yield f"Error: {str(e)}"
    
    async def analyze_competitor_strategy(
        self,
        competitor_url: str,
        business_type: str,
        city: str
    ) -> Dict[str, Any]:
        """AI-powered competitor analysis with page-scan fallback when LLM is offline."""
        # Always gather real page signals first
        signals = await _fetch_page_signals(competitor_url)
        excerpt = signals.get("excerpt") or await _fetch_page_excerpt(competitor_url)
        page_context = (
            f"Here is the actual visible text from their homepage:\n\"\"\"\n{excerpt}\n\"\"\"\n"
            if excerpt else
            "(Their homepage could not be fetched — base this on the URL and business context alone, "
            "and note in your analysis that the page content wasn't accessible.)\n"
        )
        prompt = f"""
        Analyze the competitor at {competitor_url} for a {business_type} business in {city}.
        {page_context}
        Provide:
        1. Key messaging and value propositions
        2. Target audience analysis
        3. SEO strategy (keywords, structure)
        4. Content strategy and gaps
        5. Unique selling points
        6. Recommendations for differentiation

        Respond as a JSON object with keys: messaging, target_audience, seo_strategy, content_gaps, unique_selling_points, recommendations.
        """

        data = await chat_json(prompt, temperature=0.6, max_tokens=2000)
        if data and not data.get("error"):
            data["source"] = "llm"
            data["fetched_url"] = signals.get("url") or competitor_url
            return data
        # LLM unavailable — still return useful analysis from the live page scan
        return _heuristic_analyze(signals, business_type, city)

    async def discover_competitors(
        self,
        website: str,
        business_type: str,
        city: str
    ) -> Dict[str, Any]:
        """AI competitor discovery with niche heuristic fallback when LLM is offline."""
        excerpt = await _fetch_page_excerpt(website)
        page_context = (
            f"Here is the actual visible text from their homepage:\n\"\"\"\n{excerpt}\n\"\"\"\n"
            if excerpt else
            "(Their homepage could not be fetched — base this on the business type and location alone.)\n"
        )
        prompt = f"""
        A {business_type} business in {city} has the website {website}.
        {page_context}
        Suggest 5 real, likely competitor businesses/websites that compete with them for
        local search visibility (same business type, same or nearby city). For each, give
        your best guess at their domain and a one-sentence rationale for why they're a
        likely competitor. Do not suggest {website} itself.

        Respond as a JSON object: {{"competitors": [{{"domain": "...", "rationale": "..."}}]}}
        """

        data = await chat_json(prompt, temperature=0.6, max_tokens=1200)
        if data and data.get("competitors"):
            data["source"] = "llm"
            return data
        return _heuristic_discover(website, business_type, city)

    async def generate_seo_recommendations(
        self,
        current_content: str,
        target_keywords: list,
        business_type: str
    ) -> Dict[str, Any]:
        """Generate AI-powered SEO recommendations."""
        prompt = f"""
        Analyze this SEO content and provide recommendations:
        
        Current Content:
        {current_content}
        
        Target Keywords: {', '.join(target_keywords)}
        Business Type: {business_type}
        
        Provide:
        1. Keyword optimization suggestions
        2. Content structure improvements
        3. Meta tag recommendations
        4. Internal linking opportunities
        5. Schema markup suggestions
        6. Readability improvements
        
        Format as JSON with specific, actionable recommendations.
        """
        
        try:
            response = ""
            async for chunk in self.generate_content_with_streaming(
                prompt,
                model="gpt-4",
                max_tokens=2000
            ):
                response += chunk
            
            import json
            return json.loads(response)
        except Exception as e:
            logger.error(f"SEO recommendations failed: {e}")
            return {"error": str(e)}
    
    async def generate_content_variants(
        self,
        base_content: str,
        num_variants: int = 3,
        tone: str = "professional"
    ) -> list:
        """Generate multiple content variants with different tones."""
        prompt = f"""
        Generate {num_variants} variants of this content with a {tone} tone:
        
        {base_content}
        
        Each variant should:
        - Maintain the same core message
        - Use different phrasing and structure
        - Appeal to different audience segments
        - Vary in length and detail level
        
        Return as JSON array of variants.
        """
        
        try:
            response = ""
            async for chunk in self.generate_content_with_streaming(
                prompt,
                model="gpt-4",
                max_tokens=3000
            ):
                response += chunk
            
            import json
            return json.loads(response)
        except Exception as e:
            logger.error(f"Content variant generation failed: {e}")
            return []


# Singleton instance
advanced_ai_service = AdvancedAIService()


async def get_advanced_ai_service() -> AdvancedAIService:
    """Dependency injection for advanced AI service."""
    return advanced_ai_service
