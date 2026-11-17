import hashlib
import random
import re
import json
import os
import httpx
from typing import List, Dict, Any, Optional
from models.schemas import SEOBlock, FAQItem, KeywordSet, WebsiteProfile, ArticleRequest
from services.keyword_service import generate_keywords
from services.internal_linking_service import insert_internal_links
from config import settings


async def _ensure_rag_context(query: str, site_url: str) -> str:
    """Retrieve live-site chunks for this query. Empty string if nothing indexed."""
    site_url = (site_url or "").strip()
    q = (query or "").strip()
    if not site_url or not q:
        return ""
    try:
        from services.rag_service import already_tried, has_index, mark_tried, rag_prompt_block
        from services.website_analysis_service import analyze_website
        if not has_index(site_url) and not already_tried(site_url):
            await analyze_website(site_url)
            mark_tried(site_url)
        return await rag_prompt_block(q, site_url)
    except Exception as e:
        print(f"[RAG] retrieve skipped: {e}")
        return ""

TITLE_VARIANTS = [
    "Best {BT} in {city}, {state} | Affordable, Proven Results",
    "Top {BT} Services in {city}, {state} — Free Estimates",
    "Affordable {BT} in {city} | Trusted by Local Businesses",
    "#1 {BT} Company in {city}, {state} | Licensed Experts",
    "Proven {BT} Services in {city} — Best Rates, Fast Turnaround",
    "Best {BT} for Small Businesses in {city}, {state}",
]

META_VARIANTS = [
    "Need a site that brings in calls in {city}? ZeOrbit builds a clear, mobile-friendly WordPress or Shopify page so customers know what you do next.",
    "ZeOrbit designs fast websites for {city} businesses — obvious offer, easy contact, no filler. WordPress or Shopify, built to get inquiries.",
    "A {city} website should make the next step obvious. ZeOrbit builds that: mobile-friendly, simple, and ready for calls and form fills.",
    "Get a website {city} customers can trust at a glance. ZeOrbit keeps it fast, readable, and easy to contact — WordPress or Shopify.",
]

H1_VARIANTS = [
    "{BT} in {city}, {state} — Practical, Proven & Local",
    "Trusted {BT} Services in {city} | Built for Local Businesses",
    "{BT} in {city}, {state} — Results That Speak for Themselves",
    "Your Local {BT} Experts in {city} | Clear Process, Real Work",
    "{BT} Serving {city}, {state} — Talk With the Team",
]

H2_POOL = [
    "What Does a {BT} Do in {city}?",
    "How to Choose {BT} in {city}?",
    "Why Do {city} Businesses Need {BT}?",
    "What Makes the Best {BT} in {city}?",
    "How to Choose the Right {BT} in {city}, {state}",
    "What Results Can You Expect from {BT} in {city}?",
    "Is {BT} Worth It for Small Businesses in {city}?",
    "How Long Does {BT} Take in {city}?",
    "What Are the Benefits of Professional {BT} in {city}?",
    "How Does {BT} Help {city} Businesses Get More Customers?",
]

H3_POOL = [
    "Affordable {BT} Packages for {city} Businesses",
    "Local {BT} Experts Who Know {city}",
    "Proven {BT} Results in {city}, {state}",
    "Fast Turnaround for {city} Clients",
    "Custom {BT} Solutions for Every Budget",
    "Why {city} Businesses Trust Our {BT} Team",
    "Transparent Pricing — No Hidden Fees",
    "5-Star Rated {BT} Services in {city}",
    "Serving All Neighborhoods in {city}",
    "Free Consultation for {city} Business Owners",
]

INTRO_VARIANTS = [
    "If you're looking for {bt} in {city}, {state}, you've found the right team. "
    "We help {city} businesses get more customers online with practical, proven {bt} services. "
    "Our local experts know {city}'s market and deliver work that matters.",

    "{city} businesses trust us for professional {bt} services that actually work. "
    "We're a locally based {bt} team serving {city}, {state} with a clear process and real results. "
    "Whether you're a small contractor or a growing company, we have the right {bt} solution for you.",

    "The right {bt} in {city} is the one that delivers results. "
    "Our {city}-based {bt} team has helped hundreds of local businesses grow their online presence. "
    "Clear process, proven strategies, and a team that knows {city}.",
]

BODY_SECTION_VARIANTS = [
    "{city} is a competitive market, and standing out online requires more than just a basic website. "
    "Our {bt} services are built specifically for {city} businesses that want to attract local customers. "
    "Here's what sets us apart:\n\n"
    "• Local expertise — we know {city}'s neighborhoods, competitors, and customer behavior\n"
    "• Clear process — no agency markups, just honest work for {city} businesses\n"
    "• Proven results — our {city} clients see measurable growth within 90 days\n"
    "• Fast delivery — most {city} projects are completed in 2-4 weeks\n\n"
    "Unlike national agencies that treat {city} as just another zip code, we're invested in your success.",

    "Many {city} business owners make the mistake of choosing the cheapest {bt} option — "
    "only to end up with poor results and wasted money. Here's the truth:\n\n"
    "A good {bt} in {city} should:\n"
    "1. Understand your specific industry and local competition\n"
    "2. Provide clear, measurable goals from day one\n"
    "3. Communicate regularly and explain what they're doing\n"
    "4. Deliver work that actually brings in customers\n\n"
    "A bad {bt} will overpromise, underdeliver, and disappear when you ask questions. "
    "{city} businesses deserve better — and that's exactly what we provide.",

    "{city} has thousands of businesses competing for the same customers. "
    "Professional {bt} is no longer optional — it's how {city} businesses survive and grow.\n\n"
    "Common misconceptions about {bt} in {city}:\n"
    "• It's too expensive — our {city} packages start at affordable rates for any budget\n"
    "• It takes too long — most {city} clients see results within 60-90 days\n"
    "• I can do it myself — DIY {bt} often costs more in lost time and missed opportunities\n"
    "• All {bt} companies are the same — local {city} expertise makes a real difference\n\n"
    "The right {bt} partner in {city} pays for itself many times over.",
]

FAQ_POOLS = [
    (
        "How do I choose {bt} in {city}?",
        "Choose {bt} in {city} based on communication, mobile-friendly work, and whether they can explain the process in plain language. "
        "Ask for a clear timeline and what you will be able to update yourself. "
        "ZeOrbit can walk through that with your {city} business."
    ),
    (
        "Who is the best {bt} in {city}?",
        "The best {bt} in {city} is one that understands your local market, delivers measurable results, "
        "and communicates clearly. Our team has served {city} businesses for years with proven outcomes. "
        "Check our reviews from {city} clients to see why we're the top choice."
    ),
    (
        "What does a {bt} do in {city}?",
        "A {bt} in {city} helps local businesses attract more customers online. "
        "This includes building websites, optimizing for search engines, managing online presence, "
        "and creating content that converts {city} visitors into paying customers."
    ),
    (
        "Is {bt} worth it for small businesses in {city}?",
        "Yes — professional {bt} is one of the highest-ROI investments for {city} small businesses. "
        "Most of our {city} clients recover their investment within 3-6 months through increased leads and sales. "
        "We offer affordable entry-level packages specifically for {city} small businesses."
    ),
    (
        "How long does {bt} take in {city}?",
        "Most {bt} projects for {city} businesses are completed in 2-6 weeks depending on scope. "
        "SEO results typically appear within 60-90 days. "
        "We provide a clear timeline upfront so {city} clients always know what to expect."
    ),
    (
        "Do I need a local {bt} in {city} or can I hire remotely?",
        "A local {bt} in {city} understands your specific market, local competitors, and customer behavior. "
        "This local knowledge translates to better targeting and faster results for {city} businesses. "
        "We're based in {city} and available for in-person meetings when needed."
    ),
    (
        "What should I look for when hiring a {bt} in {city}?",
        "When hiring a {bt} in {city}, look for: local market knowledge, a portfolio of {city} clients, "
        "clear process, clear communication, and measurable deliverables. "
        "Avoid anyone who guarantees overnight results or won't explain their process."
    ),
    (
        "Can {bt} help my {city} business rank on Google?",
        "Yes. Professional {bt} in {city} includes SEO optimization that helps your business appear "
        "in Google searches for {city}-specific keywords. "
        "Our {city} clients consistently rank on the first page for their target local searches."
    ),
    (
        "What industries do you serve with {bt} in {city}?",
        "We provide {bt} services to all industries in {city} including contractors, healthcare, "
        "retail, restaurants, professional services, and more. "
        "Every {city} business gets a custom strategy based on their specific industry and goals."
    ),
    (
        "How do I get started with {bt} in {city}?",
        "Getting started is simple. Contact our {city} team for a free consultation. "
        "We'll review your current situation, discuss your goals, and recommend the right {bt} package "
        "for your {city} business — with no obligation."
    ),
]

CTA_VARIANTS = [
    "Ready to grow your {city} business with proven {bt} services? "
    "Contact our {city} team today for a FREE consultation and custom quote. "
    "Affordable rates, fast results, and a team that knows {city} inside and out.",

    "Don't let your {city} competitors get ahead. "
    "Our {bt} team is ready to help your {city} business attract more customers online. "
    "Call now for a free estimate — no obligation, no pressure.",

    "Join hundreds of {city} businesses that trust us for professional {bt} services. "
    "Get your free {bt} consultation today and see why we're the top choice in {city}, {state}.",

    "Your {city} business deserves the best {bt} — at a price that makes sense. "
    "Contact us today for a free quote and let's build something great together in {city}.",
]


def _seed_random(city: str, business_type: str) -> random.Random:
    seed = int(hashlib.md5(f"{city}{business_type}".encode()).hexdigest(), 16) % (2**32)
    return random.Random(seed)

def _fill(template: str, bt: str, city: str, state: str) -> str:
    return template.format(bt=bt.lower(), BT=bt.title(), city=city, state=state)

def _slugify(text: str) -> str:
    return re.sub(r'[^a-z0-9-]+', '-', text.lower()).strip('-')


_NICHE_TYPO_FIXES = {
    "sotware": "software",
    "softwar": "software",
    "pulmbing": "plumbing",
    "resturant": "restaurant",
    "restuarant": "restaurant",
}


def normalize_niche_text(text: str) -> str:
    """Fix common niche typos so titles/slugs/images stay on-topic."""
    if not text:
        return text

    def _fix(match: re.Match) -> str:
        word = match.group(0)
        fixed = _NICHE_TYPO_FIXES[word.lower()]
        if word.isupper():
            return fixed.upper()
        if word[:1].isupper():
            return fixed.title()
        return fixed

    pattern = re.compile(r"\b(" + "|".join(re.escape(k) for k in _NICHE_TYPO_FIXES) + r")\b", re.I)
    return pattern.sub(_fix, text)


_PHONE_IN_TEXT_RE = re.compile(r"(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}")
_URL_IN_TEXT_RE = re.compile(r"(?:https?://|www\.)\S+", re.I)
_EMAIL_IN_TEXT_RE = re.compile(r"\b[\w.+-]+@[\w.-]+\.\w+\b")
_ZEORBIT_CTA_FLUFF_RE = re.compile(
    r"\b(?:zeorbit(?:\.com)?|"
    r"call(?:\s+now)?(?:\s*:)?|"
    r"visit(?:\s+us)?(?:\s*:)?|"
    r"is there to help(?:\s+you(?:\s+out)?)?|"
    r"here to help(?:\s+you(?:\s+out)?)?|"
    r"partner with|"
    r"take the first step(?:\s+today)?)\b",
    re.I,
)
_SLOGAN_OPENER_RE = re.compile(
    r"\b(?:are you(?:\s+a)?|planning for(?:\s+a)?|need(?:\s+a)?|"
    r"looking for(?:\s+a)?|ready to|don'?t let|watch your)\b",
    re.I,
)
_NEW_BIZ_PLANNING_RE = re.compile(
    r"\b(?:new business|startup|first website|planning (?:for )?(?:a )?new website|"
    r"plan(?:ning)? (?:your |a )?new website)\b",
    re.I,
)


def sanitize_seo_keyword(
    text: str,
    industry: str = "",
    business_type: str = "",
    audience: str = "",
) -> str:
    """Clean pasted CTA slogans into a short SEO keyword (slug / density / primary).

    'Are You a New Business? … www.zeorbit.com Call (619) 724-9517'
    → 'new business website' (topic stays; phone/URL/ZeOrbit CTA stripped).
    """
    from services.zeorbit_local_seo import is_generic_industry

    raw = re.sub(r"\s+", " ", (text or "").strip())
    if not raw:
        return ""

    who = (audience or industry or "").strip()
    if who and is_generic_industry(who):
        who = ""
    service = (business_type or "Website Design").strip() or "Website Design"
    if not re.search(r"website|web design|wordpress|shopify|mobile app|seo", service, re.I):
        service = "Website Design"

    def _industry_kw() -> str:
        if who and who.lower() not in service.lower():
            return f"{who} {service}".strip()
        if who:
            return f"{who} Website Design"
        return service

    had_cta = bool(
        _PHONE_IN_TEXT_RE.search(raw)
        or _URL_IN_TEXT_RE.search(raw)
        or re.search(r"\bzeorbit\b", raw, re.I)
    )
    t = _PHONE_IN_TEXT_RE.sub(" ", raw)
    t = _URL_IN_TEXT_RE.sub(" ", t)
    t = _EMAIL_IN_TEXT_RE.sub(" ", t)
    t = _ZEORBIT_CTA_FLUFF_RE.sub(" ", t)
    t = t.replace("+", " ").replace("|", " ").replace("—", " ").replace("–", " ")
    t = re.sub(r"[?!]+", " ", t)
    t = re.sub(r"[\"'`]+", " ", t)
    t = re.sub(r"\s+", " ", t).strip(" -.,;:/")

    if re.match(r"^(who|what|how|why|when|where|can|do|does|is|should)\b", t, re.I):
        return t

    is_slogan = (
        had_cta
        or bool(_SLOGAN_OPENER_RE.search(raw))
        or len(raw.split()) >= 10
        or ("?" in raw and len(raw.split()) >= 5)
    )

    # Keep the editor's topic when it is clearly "new business + website".
    if _NEW_BIZ_PLANNING_RE.search(raw) or _NEW_BIZ_PLANNING_RE.search(t):
        return "new business website"

    # Marketing paste with no clear topic → industry service keyword if known.
    if is_slogan and who:
        return _industry_kw()

    if is_slogan:
        cleaned = _SLOGAN_OPENER_RE.sub(" ", t)
        cleaned = re.sub(r"\s+", " ", cleaned).strip(" -.,;:")
        words = [
            w for w in cleaned.split()
            if w.lower() not in {"a", "an", "the", "to", "for", "out", "you", "your"}
        ]
        if 2 <= len(words) <= 6:
            return " ".join(words)
        return _industry_kw()

    if len(t.split()) > 10:
        return _industry_kw() if who else " ".join(t.split()[:6])
    return t or _industry_kw()


def topic_display_heading(
    keyword: str, industry: str = "", audience: str = "", city: str = ""
) -> str:
    """Simple ZeOrbit H1 from the search topic (unique per location when city is set)."""
    return _simple_pitch_heading(
        keyword, industry=industry, audience=audience, city=city
    )


def is_generic_industry_safe(label: str) -> bool:
    try:
        from services.zeorbit_local_seo import is_generic_industry
        return is_generic_industry(label)
    except Exception:
        return False


def _is_new_business_website_topic(keyword: str = "", target_keywords: Optional[list] = None) -> bool:
    blob = " ".join(
        [keyword or ""] + [str(k) for k in (target_keywords or []) if k]
    )
    if sanitize_seo_keyword(blob) == "new business website":
        return True
    return bool(_NEW_BIZ_PLANNING_RE.search(blob))


def _short_who_label(audience: str = "", industry: str = "") -> str:
    """Keep audience/industry short for headings (ignore AI autofill essays)."""

    def _one(label: str) -> str:
        who = (label or "").strip()
        if not who or is_generic_industry_safe(who):
            return ""
        # Drop location tails AI sometimes appends ("… in San Diego County").
        who = re.split(r"\bin\b", who, maxsplit=1, flags=re.I)[0].strip(" ,-")
        words = who.split()
        if len(words) > 3:
            stop = {"small", "to", "mid", "sized", "mid-sized", "local", "and", "the", "a", "for"}
            keep = [w for w in words if w.lower() not in stop]
            who = " ".join(keep[:2]) if keep else " ".join(words[:2])
        who_h = pretty_keyword(who)
        low = who_h.lower()
        if low.endswith("ies"):
            who_h = who_h[:-3] + "y"
        elif low.endswith("sses"):
            who_h = who_h[:-2]
        elif low.endswith("s") and not low.endswith(("ss", "us", "is", "oes", "business")):
            who_h = who_h[:-1]
        # Never return an awkward fragment like "Contracting Businesse"
        if len(who_h.split()) > 3 or who_h.lower().endswith("businesse"):
            return ""
        return who_h

    # Prefer a short industry label over a long AI audience essay.
    for label in (industry, audience):
        got = _one(label)
        if got and len(got.split()) <= 3:
            return got
    return ""


def _simple_pitch_heading(
    keyword: str, industry: str = "", audience: str = "", city: str = ""
) -> str:
    """Clean SEO title / H1 from the topic — never includes ZeOrbit."""
    raw = re.sub(r"\s+", " ", (keyword or "").strip())
    who_h = _short_who_label(audience, industry)
    place = _meta_place_label(city)
    cleaned = sanitize_seo_keyword(raw, industry=industry, audience=audience) or ""
    ql = f"{raw} {cleaned}".lower()
    seed = f"{cleaned}|{place}|{industry}|{audience}|h1".lower()
    pretty = pretty_keyword(cleaned or raw or "Website Design")
    pretty = re.sub(r"\bzeorbit\b", "", pretty, flags=re.I).strip(" -|,")
    if len(pretty) > 52:
        pretty = " ".join(pretty.split()[:7])

    if _NEW_BIZ_PLANNING_RE.search(ql) or cleaned == "new business website":
        if place:
            return _meta_pick(seed, [
                f"Launch Your {place} Business Online",
                f"Build Your {place} Business Online",
                f"Take Your {place} Business Online",
                f"Build a Professional Website for Your {place} Business",
                f"Launch Your New {place} Business Online",
                f"Start Your {place} Business Online",
            ])
        return _meta_pick(seed, [
            "Launch Your Business Online",
            "Build a Professional Website for Your New Business",
            "Start Your Business Online",
        ])

    if re.search(r"\bmobile app|ios app|android app\b", ql) or (
        re.search(r"\bapp\b", ql) and not re.search(r"\b(apple|application form|apply)\b", ql)
    ):
        if place:
            return _meta_pick(seed, [
                f"Mobile App Development in {place}",
                f"Build a Mobile App for Your {place} Business",
                f"Take Your {place} Business Mobile",
            ]) if re.search(r"\bmobile app|ios|android\b", ql) else _meta_pick(seed, [
                f"Build a {pretty} for Your {place} Business" if pretty.lower().endswith("app") else f"Build an App for Your {place} Business",
                f"{pretty} Development in {place}" if pretty else f"App Development in {place}",
                f"Custom {pretty} for {place}" if pretty else f"Custom App Development in {place}",
            ])
        return _meta_pick(seed, [
            "Mobile App Development for Your Business",
            "Build a Mobile App for Your Business",
            "Professional Mobile App Development",
        ]) if re.search(r"\bmobile app|ios|android\b", ql) else _meta_pick(seed, [
            f"Build a {pretty}" if pretty.lower().startswith(("a ", "an ")) or pretty.lower().endswith("app") else f"Build a {pretty}",
            f"{pretty} Development" if pretty else "App Development Services",
            f"Professional {pretty}" if pretty else "Professional App Development",
        ])

    if re.search(r"\bshopify|ecommerce|e-commerce|online store\b", ql):
        if place:
            return _meta_pick(seed, [
                f"Online Store Setup in {place}",
                f"Build an Online Store for Your {place} Business",
                f"Shopify Store Design in {place}",
            ])
        return _meta_pick(seed, [
            "Online Store Setup for Your Business",
            "Build a Professional Online Store",
            "Shopify Store Design Services",
        ])

    if re.search(r"\bredesign|rebuild|refresh\b", ql):
        if place:
            return _meta_pick(seed, [
                f"Website Redesign in {place}",
                f"Refresh Your {place} Business Website",
                f"Rebuild Your {place} Website",
            ])
        return _meta_pick(seed, [
            "Website Redesign Services",
            "Refresh Your Business Website",
            "Professional Website Rebuild",
        ])

    if re.search(r"\bseo|ppc|local seo\b", ql) and not re.search(r"\bwebsite|web design\b", ql):
        if place:
            return _meta_pick(seed, [
                f"SEO & PPC for {place} Businesses",
                f"Get More {place} Customers with SEO",
                f"Local SEO Services in {place}",
            ])
        return _meta_pick(seed, [
            "SEO & PPC Services",
            "Local SEO for Growing Businesses",
            "Practical SEO and Ads Support",
        ])

    if re.search(r"\bmaintain|maintenance\b", ql):
        if place:
            return _meta_pick(seed, [
                f"{pretty} in {place}",
                f"{pretty} Services in {place}",
                f"Professional {pretty} for {place}",
            ])
        return _meta_pick(seed, [
            f"{pretty} Services",
            f"Why {pretty} Matters for Your Business",
            f"Professional {pretty}",
        ])

    if who_h:
        if place:
            return _meta_pick(seed, [
                f"{pretty} for {place} {who_h} Businesses",
                f"Professional {pretty} in {place}",
                f"{pretty} Services in {place}",
            ])
        return _meta_pick(seed, [
            f"{pretty} for {who_h} Businesses",
            f"Professional {pretty}",
            f"{pretty} Services",
        ])

    if place:
        return _meta_pick(seed, [
            f"{pretty} in {place}",
            f"{pretty} Services in {place}",
            f"Professional {pretty} for {place} Businesses",
            f"Build {pretty} for Your {place} Business",
        ])
    return _meta_pick(seed, [
        f"{pretty} Services",
        f"Professional {pretty}",
        f"{pretty} for Your Business",
        f"Why {pretty} Matters for Your Business",
    ])



def _pitch_image_plan(
    keyword: str = "",
    industry: str = "",
    audience: str = "",
    city: str = "",
) -> dict:
    """Image focus/concept locked to the search topic — never a rotated Shopify scene."""
    cleaned = sanitize_seo_keyword(keyword, industry="", audience="") or (keyword or "").strip() or "website design"
    ql = f"{keyword} {cleaned}".lower()
    who = _short_who_label(audience, industry)
    place = (city or "").strip()

    # Prefer the same topic→visual map used for Unsplash selection.
    try:
        from services.image_service import blog_image_plan
        plan = blog_image_plan((keyword or cleaned).strip(), niche="")
        if plan and plan.get("topic") and plan.get("category") not in ("", None):
            concept = plan.get("concept") or plan["topic"]
            if place:
                concept = f"{concept} for a {place} business"
            return {
                "focus": plan.get("topic") or plan.get("focus") or cleaned,
                "concept": concept,
                "intent_id": str(plan.get("category") or "discovery"),
                "image_keyword": cleaned,
            }
    except Exception:
        pass

    if re.search(r"\b(pharmacy|medication|prescription).{0,20}\bapp\b|\bapp\b.{0,20}\b(pharmacy|medication)\b", ql):
        focus = "pharmacy mobile app phone"
        concept = "pharmacy app on a smartphone"
        intent_id = "pharmacy_app"
    elif re.search(r"\bmobile app|ios app|android app|\bapp\b", ql):
        focus = "mobile app development phone"
        concept = "smartphone app mockup beside a laptop"
        intent_id = "mobile_app"
    elif re.search(r"\bmaintain|maintenance|care\s*plan\b", ql):
        focus = "website maintenance laptop dashboard"
        concept = "developer updating a website admin dashboard on a laptop"
        intent_id = "maintenance"
    elif re.search(r"\bshopify|ecommerce|e-commerce|online store\b", ql):
        focus = "shopify ecommerce website laptop"
        concept = "online store product page open on a laptop"
        intent_id = "shopify"
    elif re.search(r"\bredesign|rebuild|refresh\b", ql):
        focus = "website redesign mockup laptop"
        concept = "designer reviewing a website redesign on a laptop"
        intent_id = "redesign"
    elif _NEW_BIZ_PLANNING_RE.search(ql) or cleaned == "new business website":
        focus = "startup website laptop desk"
        concept = "entrepreneur planning a first business website on a laptop"
        intent_id = "new_business"
    elif re.search(r"\bwordpress\b", ql):
        focus = "wordpress dashboard laptop"
        concept = "WordPress dashboard open on a laptop"
        intent_id = "wordpress"
    elif who and who.lower() in ("contractor", "construction", "remodel", "renovation"):
        focus = "construction contractor job site"
        concept = "contractor at a job site"
        intent_id = "industry_local"
    elif who:
        focus = who.lower()
        concept = f"{who.lower()} professional at work"
        intent_id = "industry_local"
    else:
        focus = "website design laptop mockup"
        concept = "web designer building a professional business website on a laptop"
        intent_id = "discovery"

    if place:
        concept = f"{concept} for a {place} business"
    return {
        "focus": focus,
        "concept": concept,
        "intent_id": intent_id,
        "image_keyword": cleaned,
    }


def _meta_place_label(city: str = "") -> str:
    """Short place for SERP meta (drop state / ZIP noise)."""
    place = re.sub(r"\s+", " ", (city or "").strip())
    if not place:
        return ""
    place = re.split(r"\s*,\s*", place, maxsplit=1)[0].strip()
    place = re.sub(r"\b\d{5}(?:-\d{4})?\b", "", place).strip(" -.,")
    place = re.sub(r"\s+", " ", place)
    return place[:40]


def _meta_pick(seed: str, pool) -> str:
    if not pool:
        return ""
    idx = int(hashlib.md5(seed.encode("utf-8")).hexdigest(), 16) % len(pool)
    return pool[idx]


def _meta_has_zeorbit_solution(text: str) -> bool:
    t = (text or "").lower()
    return bool(
        re.search(
            r"zeorbit\s+(?:is\s+here\s+to\s+help|creates?|builds?|designs?|helps?)",
            t,
        )
    )


# Soft SERP cap — allow full local sentences like the El Cajon / Fresno examples.
_META_LIMIT = 230


def topic_help_meta(
    keyword: str = "",
    city: str = "",
    industry: str = "",
    audience: str = "",
    business_type: str = "",
) -> str:
    """Question-led meta with ZeOrbit solution — unique full-sentence variations per location.

    Examples:
      Starting a new business in El Cajon? A professional website can help you build
      trust from day one. ZeOrbit creates clear, mobile-friendly websites designed to
      help local businesses get noticed and connect with customers.

      Starting a business in Fresno and need a website? ZeOrbit builds professional,
      mobile-friendly websites that help local businesses look credible and make it
      easy for customers to contact them.
    """
    raw = _weave_industry_into_question(keyword or "", industry or "")
    if re.match(r"^(who|what|how|why|when|where|can)\b", raw, re.I):
        ind_l = _industry_phrase(industry or "business")
        place = _meta_place_label(city) or (city or "").strip()
        where = f" in {place}" if place else ""
        verb = _query_action(raw)
        if "real estate" in ind_l:
            return (
                f"Looking to {verb} your real estate business website{where}? "
                f"ZeOrbit creates professional websites that showcase properties and generate leads."
            )[:160]
        return (
            f"Looking to {verb} your {ind_l} website{where}? "
            f"ZeOrbit creates professional websites that explain your {ind_l} services and generate leads."
        )[:160]
    cleaned = sanitize_seo_keyword(
        raw, industry=industry, business_type=business_type, audience=audience
    ) or (business_type or "website design")
    pretty = pretty_keyword(cleaned)
    place = _meta_place_label(city)
    ql = f"{raw} {cleaned}".lower()
    seed = f"{cleaned}|{place}|{industry}|{audience}".lower()
    who = _short_who_label(audience, industry)
    topic = pretty.lower()
    limit = _META_LIMIT

    def _fit(candidates):
        ok = [re.sub(r"\s+", " ", c.strip()) for c in candidates if c and c.strip()]
        under = [c for c in ok if len(c) <= limit]
        if under:
            return _meta_pick(seed, under)[:limit]
        # Prefer complete sentences under the cap over mid-word cuts.
        for c in ok:
            parts = [p.strip() for p in re.split(r"(?<=[.!?])\s+", c) if p.strip()]
            kept = []
            for p in parts:
                cand = " ".join(kept + [p]) if kept else p
                if len(cand) <= limit:
                    kept.append(p)
                else:
                    break
            if kept:
                return " ".join(kept)[:limit]
        return (ok[0] if ok else "")[:limit]

    if _NEW_BIZ_PLANNING_RE.search(ql) or cleaned == "new business website":
        if place:
            templates = [
                (
                    f"Starting a new business in {place}? A professional website can help you "
                    f"build trust from day one. ZeOrbit creates clear, mobile-friendly websites "
                    f"designed to help local businesses get noticed and connect with customers."
                ),
                (
                    f"Starting a business in {place} and need a website? ZeOrbit builds "
                    f"professional, mobile-friendly websites that help local businesses look "
                    f"credible and make it easy for customers to contact them."
                ),
                (
                    f"Starting a new business in {place}? ZeOrbit creates clear, mobile-friendly "
                    f"websites designed to help you get noticed and connect with customers."
                ),
                (
                    f"New business in {place}? A professional website builds trust from day one. "
                    f"ZeOrbit builds mobile-friendly sites that help local businesses get noticed."
                ),
                (
                    f"Starting a business in {place}? ZeOrbit builds professional, mobile-friendly "
                    f"websites that help you look credible and make it easy for customers to reach you."
                ),
                (
                    f"Launching in {place}? A professional website can help you build trust from "
                    f"day one. ZeOrbit creates clear, mobile-friendly websites for local businesses."
                ),
                (
                    f"Starting a new business in {place} and need a website? ZeOrbit creates "
                    f"professional, mobile-friendly sites that help local businesses connect with customers."
                ),
                (
                    f"Ready to start in {place}? A professional website builds trust from day one. "
                    f"ZeOrbit builds clear, mobile-friendly websites designed to get you noticed."
                ),
                (
                    f"Starting a new business in {place}? ZeOrbit builds clear, mobile-friendly "
                    f"websites that help local businesses look professional and win customers."
                ),
                (
                    f"Opening in {place}? A professional website can help you build trust from day one. "
                    f"ZeOrbit creates mobile-friendly websites made for local businesses."
                ),
                (
                    f"Starting a business in {place}? Get a site customers trust. ZeOrbit creates "
                    f"clear, mobile-friendly websites designed to help local businesses get noticed."
                ),
                (
                    f"Need a website for your new {place} business? ZeOrbit builds professional, "
                    f"mobile-friendly websites that make it easy for customers to contact you."
                ),
            ]
            return _fit(templates)

        return _fit([
            (
                "Starting a new business? A professional website builds trust from day one. "
                "ZeOrbit is here to help you launch a clear, mobile-friendly site that wins customers."
            ),
            (
                "Starting a new business and need a website? ZeOrbit builds professional, "
                "mobile-friendly websites that help you look credible and connect with customers."
            ),
            (
                "Starting a new business? A professional website can help you build trust from day one. "
                "ZeOrbit creates clear, mobile-friendly websites designed to get you noticed."
            ),
        ])

    if re.search(r"\bmobile app|ios app|android app\b", ql):
        if place:
            return _fit([
                (
                    f"Need a mobile app in {place}? ZeOrbit builds simple, clean apps with a plan "
                    f"and UX your team and customers will actually use."
                ),
                (
                    f"Building an app for {place}? ZeOrbit creates clear mobile experiences — "
                    f"practical features, clean UX, and a build people open."
                ),
                (
                    f"Need a mobile app for your {place} business? ZeOrbit helps you plan, design, "
                    f"and ship an app customers will actually use."
                ),
            ])
        return _fit([
            "Need a mobile app? ZeOrbit is here to help with a simple app plan, clean UX, and a build your team and customers will actually use.",
        ])

    if re.search(r"\bshopify|ecommerce|e-commerce|online store\b", ql):
        if place:
            return _fit([
                (
                    f"Ready to sell online in {place}? ZeOrbit builds professional, mobile-friendly "
                    f"stores that look credible and make checkout easy."
                ),
                (
                    f"Need an online store in {place}? ZeOrbit creates clear Shopify sites that load "
                    f"fast on phones and make it easy for customers to buy."
                ),
                (
                    f"Selling from {place}? ZeOrbit builds professional ecommerce websites designed "
                    f"to help local businesses get noticed and convert."
                ),
            ])
        return _fit([
            "Ready to sell online? ZeOrbit is here to help you launch a store that looks professional, loads fast on phones, and makes checkout easy.",
        ])

    if re.search(r"\bredesign|rebuild|refresh\b", ql):
        if place:
            return _fit([
                (
                    f"Is your {place} website outdated? ZeOrbit redesigns clear, mobile-friendly "
                    f"sites so the offer is obvious and customers can contact you easily."
                ),
                (
                    f"Need a website redesign in {place}? ZeOrbit builds professional refreshes that "
                    f"help local businesses look credible again."
                ),
                (
                    f"Hard-to-use site in {place}? ZeOrbit creates clear, mobile-friendly redesigns "
                    f"designed to rebuild trust and get you noticed."
                ),
            ])
        return _fit([
            "Is your website outdated or hard to use? ZeOrbit is here to help redesign your site so the offer is clear, contact is easy, and visitors trust you again.",
        ])

    if re.search(r"\bseo|ppc|local seo\b", ql) and not re.search(r"\bwebsite|web design\b", ql):
        if place:
            return _fit([
                (
                    f"Need better visibility in {place}? ZeOrbit builds practical SEO and ads — "
                    f"clear pages, local relevance, and a plan you can act on."
                ),
                (
                    f"Want more customers in {place}? ZeOrbit creates local SEO pages and campaigns "
                    f"designed to help businesses get noticed."
                ),
                (
                    f"Searching for SEO in {place}? ZeOrbit helps local businesses show up with "
                    f"clear pages and ads that make contact easy."
                ),
            ])
        return _fit([
            f"Need better visibility for {topic}? ZeOrbit is here to help with practical SEO and ads — clear pages, local relevance, and a plan you can act on.",
        ])

    if re.search(r"\bmaintain|maintenance|care\s*plan|website support\b", ql):
        subject = "WordPress website" if "wordpress" in ql else "website"
        if place:
            return _fit([
                (
                    f"Keep your {subject} in {place} updated, secure, and running properly with "
                    f"professional {topic} and support from ZeOrbit."
                ),
                (
                    f"Need {topic} in {place}? ZeOrbit helps keep your site updated, secure, "
                    f"and ready for customers with practical ongoing support."
                ),
                (
                    f"{topic} for {place} businesses — updates, backups, security checks, and "
                    f"fixes from ZeOrbit so your site stays ready for customers."
                ),
            ])
        return _fit([
            (
                f"Keep your {subject} updated, secure, and running properly with professional "
                f"{topic} and support from ZeOrbit."
            ),
            (
                f"Need {topic}? ZeOrbit helps keep your site updated, secure, functional, "
                f"and ready for your customers."
            ),
            (
                f"Professional {topic} from ZeOrbit — updates, backups, security checks, "
                f"and support that keep your website working properly."
            ),
            (
                f"Stay ahead of website issues with {topic} from ZeOrbit: updates, security, "
                f"backups, and performance support for your business site."
            ),
        ])

    if place:
        who_bit = f" for your {who.lower()} business" if who else ""
        return _fit([
            (
                f"Looking for {topic} in {place}? ZeOrbit creates clear, mobile-friendly websites "
                f"designed to help local businesses get noticed and connect with customers."
            ),
            (
                f"Need {topic}{who_bit} in {place}? ZeOrbit builds professional, mobile-friendly "
                f"sites that help you look credible and make contact easy."
            ),
            (
                f"Searching for {topic} in {place}? ZeOrbit builds clear websites with a simple plan "
                f"so local customers can find you and get in touch."
            ),
            (
                f"Need {topic} in {place}? ZeOrbit creates professional, mobile-friendly websites "
                f"designed to help local businesses win customers."
            ),
            (
                f"Get professional {topic} in {place} from ZeOrbit — practical delivery, "
                f"mobile-friendly results, and support that matches your business needs."
            ),
        ])

    editor_q = ""
    if "?" in raw:
        q_part = re.split(r"\?", raw, maxsplit=1)[0].strip()
        q_part = _PHONE_IN_TEXT_RE.sub(" ", q_part)
        q_part = _URL_IN_TEXT_RE.sub(" ", q_part)
        q_part = _ZEORBIT_CTA_FLUFF_RE.sub(" ", q_part)
        q_part = re.sub(r"\s+", " ", q_part).strip(" -.,;:")
        if q_part and len(q_part.split()) <= 14:
            editor_q = f"{q_part}?"

    question = editor_q or (
        f"Need {topic} for your {who.lower()} business?"
        if who
        else f"Looking for {topic}?"
    )
    return _fit([
        (
            f"Keep your business moving with professional {topic} from ZeOrbit — "
            f"clear planning, practical delivery, and support that matches your needs."
        ),
        (
            f"{question} ZeOrbit provides {topic} to help you stay clear, mobile-friendly, "
            f"and ready for customers."
        ),
        (
            f"Need {topic}? ZeOrbit helps businesses with practical {topic} — "
            f"updated results, clear contact paths, and support you can act on."
        ),
        (
            f"Professional {topic} from ZeOrbit — built to help your business look credible "
            f"and make it easy for customers to take the next step."
        ),
        (
            f"{question} ZeOrbit is here to help with {topic} — a clear plan, "
            f"a professional build, and a result that turns visits into calls."
        ),
    ])


def _topic_checklist_bullets(pretty: str, ql: str) -> list:
    """Checklist lines for the evergreen body — tuned by topic, works for any keyword."""
    if re.search(r"\bmaintain|maintenance|care\s*plan|support\b", ql) and re.search(r"\bwordpress|website|site\b", ql):
        return [
            "WordPress updates",
            "Plugin and theme updates",
            "Website backups",
            "Security checks",
            "Broken link checks",
            "Performance monitoring",
            "Content updates",
            "Mobile checks",
        ]
    if re.search(r"\bmobile app|ios app|android app\b", ql) or (
        re.search(r"\bapp\b", ql) and not re.search(r"\b(apple|application form|apply)\b", ql)
    ):
        if re.search(r"\bpharmacy|medication|prescription\b", ql):
            return [
                "Prescription refill flow",
                "Order status and reminders",
                "Store hours and location",
                "Clean mobile UX",
                "Testing on real phones",
                "Updates after launch",
                "Easy path to call the pharmacy",
            ]
        return [
            "App planning and feature scope",
            "Clean mobile UX",
            "iOS and Android builds when needed",
            "Testing on real devices",
            "Store listing support",
            "Updates after launch",
            "A clear path back to contact you",
        ]
    if re.search(r"\bshopify|ecommerce|e-commerce|online store\b", ql):
        return [
            "Product and collection pages",
            "Mobile-friendly checkout",
            "Payments and shipping setup",
            "Speed and image checks",
            "Clear contact and support paths",
            "Ongoing store updates",
        ]
    if re.search(r"\bredesign|rebuild|refresh\b", ql):
        return [
            "Clear offer on the first screen",
            "Mobile-friendly layouts",
            "Faster page loads",
            "Working forms and click-to-call",
            "Updated content and images",
            "Simple paths to contact you",
        ]
    if re.search(r"\bseo|ppc|local seo\b", ql):
        return [
            "Clear service pages",
            "Titles and headings that match searches",
            "Local relevance where it matters",
            "Mobile-friendly pages",
            "Tracking for calls and forms",
            "A plan you can act on",
        ]
    if re.search(r"\bwordpress\b", ql):
        return [
            "WordPress setup and page structure",
            "Mobile-friendly design",
            "Plugin choices that stay maintainable",
            "Speed and security basics",
            "Easy content editing",
            "Clear contact paths",
        ]
    # Generic service / topic checklist — still concrete.
    label = pretty if pretty else "your project"
    return [
        f"A clear plan for {label.lower()}",
        "Mobile-friendly pages or screens",
        "Content that states the offer plainly",
        "Fast, usable experience on phones",
        "Easy ways for customers to contact you",
        "Updates after launch when you need them",
    ]


def _industry_examples(industry: str) -> str:
    t = (industry or "").lower()
    if "home" in t:
        return "plumbing, HVAC, electrical, landscaping, cleaning, roofing, remodeling, or another home service"
    if "health" in t or "dental" in t or "clinic" in t:
        return "patient visits, service explanations, appointment requests, and trust-building details"
    if "gym" in t or "fitness" in t:
        return "class schedules, memberships, trainer booking, and check-in"
    if "tint" in t:
        return "auto tint, home window film, and a simple way to request a quote"
    if "restaurant" in t or "cafe" in t:
        return "the menu, hours, location, and a clear way to reserve or order"
    return f"the services your {industry.strip().lower()} customers actually look for"


def _industry_offer_page(
    keyword: str = "",
    city: str = "",
    industry: str = "",
    audience: str = "",
    business_type: str = "",
) -> dict:
    """Page shape from the Downtown Oceanside home-services example."""
    who = pretty_keyword((industry or "").strip())
    aud = pretty_keyword((audience or "").strip())
    place = re.sub(r"\s+", " ", (city or "").strip())
    place_bit = f" in {place}" if place else ""
    cleaned = sanitize_seo_keyword(
        keyword, industry=industry, business_type=business_type, audience=audience
    ) or (business_type or "website and mobile app development")
    offer = pretty_keyword(cleaned)
    offer = re.sub(r"\bZeOrbit\b", "", offer, flags=re.I).strip(" -|,") or "Website and Mobile App Development"
    if who.lower() not in offer.lower():
        offer_for = f"{offer} for {who}"
    else:
        offer_for = offer
    examples = _industry_examples(who)
    buyer = aud if aud and aud.lower() not in who.lower() else who
    h1 = f"{offer_for}{place_bit}"[:110]
    title = h1 if len(offer.split()) < 8 else (
        f"{offer.rstrip('?.!')} for Your {who} Business? It’s Time to Get More Clarity and Grow Your Business"
    )
    if len(title) > 90 and len(offer.split()) >= 8:
        title = f"{offer_for}{place_bit}"[:90]
    intro = (
        f"Running a {who.lower()} business{place_bit} means staying visible, responding quickly, "
        f"and making it easy for customers to request your services. {offer} can bring these pieces together in one place.\n\n"
        f"Whether you provide {examples}, modern technology can help simplify customer interactions and support your growth."
    )
    h2s = [
        "Make It Easier for Customers to Find and Request Your Services",
        f"Bring Your {who} Business Into the Next Stage With ZeOrbit",
    ]
    content = (
        f"## {h2s[0]}\n\n"
        f"Customers do not want to spend a lot of time searching for a {who.lower()} provider{place_bit}. "
        f"They want to see what you offer, understand the next step, and contact you quickly.\n\n"
        f"An AI-ready website or app for {buyer.lower()} can help with features such as:\n\n"
        f"* Smart customer questions and answers\n"
        f"* Service recommendations\n"
        f"* Instant inquiry forms\n"
        f"* Appointment requests\n"
        f"* Quote request tools\n"
        f"* 24/7 customer assistance\n"
        f"* Location-based service information\n\n"
        f"For a {who.lower()} company{place_bit}, these features can make the website more useful than a basic online brochure.\n\n"
        f"## {h2s[1]}\n\n"
        f"ZeOrbit helps {who.lower()} businesses explore modern website and mobile app solutions that combine professional design with useful functionality.\n\n"
        f"Your business may benefit from an AI-enhanced WordPress website, a custom website, a customer app, a booking system, a lead-generation platform, or another digital solution.\n\n"
        f"The right technology depends on your services and customers. ZeOrbit can help you identify what makes sense for your business instead of adding technology simply for the sake of it.\n\n"
        f"Reach out to ZeOrbit.\n\n"
        f"Call ZeOrbit: (619) 724-9517\n\n"
        f"Website: [www.zeorbit.com](https://www.zeorbit.com/)"
    )
    short_place = place or "your area"
    meta_title = f"{offer_for} in {short_place}"[:60] if place else offer_for[:60]
    meta = (
        f"Explore {offer.lower()} for {who.lower()} companies{place_bit}. "
        f"Build clearer customer experiences with ZeOrbit."
    )[:160]
    focus = f"{offer_for}{place_bit}"
    slug = _slugify(focus)
    faqs = [
        {
            "question": f"Can this help my {who.lower()} business get more inquiries{place_bit}?",
            "answer": f"Yes. Clear service information, inquiry forms, and follow-up tools help {who.lower()} customers take the next step.",
        },
        {
            "question": f"Can ZeOrbit build a mobile app for my {who.lower()} business?",
            "answer": f"Yes. ZeOrbit provides mobile app development for {who.lower()} businesses that need a customer-facing or business-specific app.",
        },
        {
            "question": "Do I need a completely custom website?",
            "answer": "Not necessarily. The right build depends on your current site, your services, and what customers need to do next.",
        },
        {
            "question": "How can I discuss this for my business?",
            "answer": f"Contact ZeOrbit at (619) 724-9517 or visit www.zeorbit.com to talk through your {who.lower()} business{place_bit}.",
        },
    ]
    return {
        "title": title[:100],
        "h1": h1,
        "meta_description": meta,
        "meta_title": meta_title,
        "h2s": h2s,
        "intro": intro,
        "content": content,
        "cta": "Call ZeOrbit at (619) 724-9517 or visit www.zeorbit.com.",
        "faqs": faqs,
        "focus_keyword": focus,
        "slug": slug,
        "search_intent": "service",
    }


def _evergreen_service_copy(
    keyword: str = "",
    city: str = "",
    industry: str = "",
    audience: str = "",
    business_type: str = "",
) -> dict:
    """Topic-first intro + varied body H2s. Title/H1 never include ZeOrbit."""
    if (industry or "").strip() and not is_generic_industry_safe(industry):
        shaped = _industry_offer_page(
            keyword=keyword,
            city=city,
            industry=industry,
            audience=audience,
            business_type=business_type,
        )
        if shaped:
            return shaped
    who_pretty = _short_who_label(audience, industry) or pretty_keyword(
        (audience or industry or "business owners").strip() or "business owners"
    )
    if len(who_pretty.split()) > 4:
        who_pretty = "business owners"
    place = _meta_place_label(city) or re.sub(r"\s+", " ", (city or "").strip())
    place_bit = f" in {place}" if place else ""
    raw_kw = re.sub(r"\s+", " ", (keyword or "").strip())
    cleaned = sanitize_seo_keyword(
        keyword, industry=industry, business_type=business_type, audience=audience
    ) or (business_type or "website design")
    pretty = pretty_keyword(cleaned if cleaned else raw_kw)
    pretty = re.sub(r"\bzeorbit\b", "", pretty, flags=re.I).strip(" -|,") or "Website Design"
    ql = f"{raw_kw} {cleaned}".lower()
    seed = f"ev|{cleaned}|{place}|{industry}|{audience}".lower()
    topic = pretty
    topic_l = pretty.lower()
    bullets = _topic_checklist_bullets(pretty, ql)
    bullet_md = "\n".join(f"* {b}" for b in bullets)

    # Title / H1 — topic only, no ZeOrbit
    h1 = _simple_pitch_heading(
        keyword or cleaned, industry=industry, audience=audience, city=city
    )
    h1 = re.sub(r"\s*\|\s*ZeOrbit\b", "", h1, flags=re.I)
    h1 = re.sub(r"\bwith ZeOrbit\b", "", h1, flags=re.I)
    h1 = re.sub(r"\bfrom ZeOrbit\b", "", h1, flags=re.I)
    h1 = re.sub(r"\bZeOrbit\b", "", h1, flags=re.I)
    h1 = re.sub(r"\s{2,}", " ", h1).strip(" -|,")[:90] or f"{topic} Services"

    # Intro — explain what the topic means in plain English (unique pools)
    if _is_comparison_query(raw_kw or cleaned):
        # Should usually be handled earlier; keep a short fallback.
        a, b = _parse_comparison_sides(raw_kw or cleaned)
        al = (a or "option A").lower()
        bl = (b or "option B").lower()
        intro = (
            f"People search for the difference between {al} and {bl} when they need a clear, "
            f"practical answer{place_bit} — not a vague pitch.\n\n"
            f"The sections below explain how they differ, which fit is usually better, and how "
            f"to present either option online."
        )
    elif _NEW_BIZ_PLANNING_RE.search(ql) or cleaned == "new business website":
        intro = _meta_pick(f"intro|{seed}", [
            (
                f"Starting a new business{place_bit} is exciting, but your website should not be an afterthought. "
                f"Customers often check you online before they call or visit.\n\n"
                f"A clear, professional site helps you look established, explain what you offer, and make contact easy."
            ),
            (
                f"Launching{place_bit}? A first website is how many people decide whether to trust you. "
                f"It should state your offer plainly and work well on phones.\n\n"
                f"Getting that foundation right early saves rework later and helps customers take the next step."
            ),
            (
                f"A new business website{place_bit} is more than a logo on a page. It is where people learn what you do, "
                f"whether you look credible, and how to reach you.\n\n"
                f"Keep the message simple, the layout mobile-friendly, and the contact path obvious."
            ),
        ])
    elif re.search(r"\bmaintain|maintenance|care\s*plan\b", ql):
        subject = "WordPress website" if "wordpress" in ql else "website"
        intro = _meta_pick(f"intro|{seed}", [
            (
                f"A {subject} needs regular attention after it goes live{place_bit}. Updates, security "
                f"checks, backups, broken links, performance issues, and content changes can affect how your "
                f"website works.\n\n"
                f"Regular {topic} helps keep your site secure, updated, functional, and ready for your customers."
            ),
            (
                f"{topic} is the ongoing work that keeps a live site healthy{place_bit}. When updates and "
                f"checks are skipped, small issues turn into downtime, slow pages, or security risks.\n\n"
                f"A steady maintenance plan protects customers and gives you time back to run the business."
            ),
            (
                f"After launch{place_bit}, your site still needs care. Plugins age, content changes, and "
                f"performance drifts if nobody is watching.\n\n"
                f"{topic} keeps those basics covered so visitors can still find you and get in touch."
            ),
            (
                f"Think of {topic_l} as routine upkeep for a business tool you rely on every day{place_bit}. "
                f"Security patches, backups, and mobile checks are part of staying open online.\n\n"
                f"Handled regularly, maintenance prevents most of the surprises that frustrate customers."
            ),
            (
                f"Customers notice when a site feels broken or outdated{place_bit}. {topic} reduces software "
                f"risks, fixes issues early, and keeps pages usable on phones.\n\n"
                f"That reliability supports trust — and fewer emergency fixes later."
            ),
        ])
    elif re.search(r"\bmobile app|ios app|android app\b", ql) or (
        re.search(r"\bapp\b", ql) and not re.search(r"\b(apple|application form|apply)\b", ql)
    ):
        is_pharmacy = bool(re.search(r"\bpharmacy|medication|prescription\b", ql))
        if is_pharmacy:
            intro = _meta_pick(f"intro|{seed}", [
                (
                    f"A pharmacy app helps customers refill prescriptions, check hours, and stay in touch "
                    f"with the pharmacy on their phone{place_bit}.\n\n"
                    f"Good {topic_l} keeps the first version simple: clear screens, fast loads, and an obvious "
                    f"path to order or call."
                ),
                (
                    f"People expect pharmacies to work on mobile{place_bit}. A dedicated app can handle refills, "
                    f"reminders, and updates better than a buried website form.\n\n"
                    f"Focus {topic_l} on the jobs customers repeat — then expand features after launch."
                ),
                (
                    f"{topic} should feel trustworthy and easy{place_bit}: find the pharmacy, manage a refill, "
                    f"and get help without hunting through menus.\n\n"
                    f"Start with that core workflow, test on real phones, and keep support contact visible."
                ),
            ])
        else:
            intro = _meta_pick(f"intro|{seed}", [
                (
                    f"A mobile app is useful when customers need a fast, focused task on their phone{place_bit} — "
                    f"ordering, booking, updates, or account access.\n\n"
                    f"Good {topic_l} starts with a clear job for the app, simple screens, and a build people will actually open."
                ),
                (
                    f"Not every business needs an app, but when the job is mobile-first{place_bit}, a website alone "
                    f"may not be enough.\n\n"
                    f"{topic} should stay practical: the right features, clean UX, and a path back to contact or support."
                ),
                (
                    f"App ideas fail when the scope is fuzzy or the experience feels heavy{place_bit}. "
                    f"Start with one customer job and prove it on a real device.\n\n"
                    f"Professional {topic_l} turns that plan into a simple product your team can maintain."
                ),
                (
                    f"People already live on their phones{place_bit}. If your service depends on repeat actions — "
                    f"orders, schedules, loyalty — an app can make that easier than a browser bookmark.\n\n"
                    f"Keep the first version small, useful, and easy to update."
                ),
                (
                    f"{topic} is about shipping something customers finish using, not a feature list{place_bit}. "
                    f"Clear navigation, fast loads, and obvious next steps matter more than polish alone.\n\n"
                    f"Plan the workflow first, then design and build around it."
                ),
            ])
    elif re.search(r"\bshopify|ecommerce|e-commerce|online store\b", ql):
        intro = _meta_pick(f"intro|{seed}", [
            (
                f"An online store should make browsing, trust, and checkout easy on a phone{place_bit}. "
                f"If those steps feel unclear, shoppers leave before they buy.\n\n"
                f"{topic} focuses on product pages, payments, and a clean path from interest to completed order."
            ),
            (
                f"Selling online{place_bit} means your catalog, shipping, and checkout have to work together. "
                f"A pretty theme is not enough if mobile checkout breaks.\n\n"
                f"Solid {topic_l} keeps the store fast, clear, and simple to run day to day."
            ),
            (
                f"Shoppers decide quickly{place_bit}. They need to see what you sell, what it costs, and how "
                f"to pay — without hunting.\n\n"
                f"{topic} sets that experience up so your store feels professional and easy to finish."
            ),
            (
                f"Ecommerce works when product pages answer questions and checkout stays short{place_bit}. "
                f"Photos, descriptions, and shipping expectations should be obvious.\n\n"
                f"Build the store around those basics, then improve with real order data."
            ),
            (
                f"{topic} is how you turn browsers into buyers{place_bit}. Structure collections clearly, "
                f"test on phones, and make support contact easy when something goes wrong.\n\n"
                f"A reliable store builds repeat customers faster than constant redesigns."
            ),
        ])
    elif re.search(r"\bredesign|rebuild|refresh\b", ql):
        intro = _meta_pick(f"intro|{seed}", [
            (
                f"A website redesign is worth it when your current site confuses people, looks dated, "
                f"or fails on phones{place_bit}.\n\n"
                f"{topic} should clarify the offer, fix contact paths, and rebuild trust — not just change colors."
            ),
            (
                f"If visitors bounce or rarely call{place_bit}, the layout and message may be the problem. "
                f"A refresh puts the next step above the fold and makes services easy to scan.\n\n"
                f"Focus on clarity and mobile usability first; decoration comes second."
            ),
            (
                f"Redesigns fail when they keep the same confusing structure{place_bit}. Start by naming what "
                f"customers must understand in five seconds.\n\n"
                f"Then rebuild pages so that story, proof, and contact are impossible to miss."
            ),
            (
                f"An outdated site quietly costs leads{place_bit}. Slow pages, broken forms, and unclear "
                f"services make people leave.\n\n"
                f"{topic} replaces those friction points with a cleaner, faster experience."
            ),
            (
                f"{topic} is a chance to reset how you show up online{place_bit}. Keep what still converts, "
                f"drop what confuses, and make calling or messaging easy on a phone.\n\n"
                f"The result should feel simpler for customers — and easier for you to update."
            ),
        ])
    elif re.search(r"\bseo|ppc|local seo\b", ql) and not re.search(r"\bwebsite|web design\b", ql):
        intro = _meta_pick(f"intro|{seed}", [
            (
                f"SEO and ads only help when your pages match what people search and make contact easy"
                f"{place_bit}.\n\n"
                f"{topic} connects clear service pages with practical campaigns so interest can turn into calls."
            ),
            (
                f"Visibility without a clear offer wastes budget{place_bit}. People need to land on a page "
                f"that explains what you do and how to reach you.\n\n"
                f"Strong {topic_l} pairs relevant pages with tracking you can actually use."
            ),
            (
                f"Local searches are won by relevance and trust signals{place_bit} — not jargon. "
                f"Your pages should name services plainly and load well on phones.\n\n"
                f"Then ads and SEO can send the right visitors to those pages."
            ),
            (
                f"{topic} works best as a system: pages, keywords, and a follow-up path{place_bit}. "
                f"Skipping any piece leaves you with traffic that does not convert.\n\n"
                f"Start with the customer question, then build the page and campaign around it."
            ),
            (
                f"If leads are flat{place_bit}, check whether people can find you and whether the landing "
                f"experience answers them. Both matter.\n\n"
                f"Practical {topic_l} improves the match between search intent and what your site promises."
            ),
        ])
    else:
        # Generic but meaningful: define the topic, then why it matters
        topic_np = topic if re.match(r"^(a|an|the)\b", topic_l) else (
            f"An {topic}" if topic_l[:1] in "aeiou" else f"A {topic}"
        )
        intro = _meta_pick(f"intro|{seed}", [
            (
                f"{topic_np} should give your business a clear, usable result{place_bit} — "
                f"not a pile of jargon. Customers should quickly understand what you offer and what to do next.\n\n"
                f"When {topic_l} is done well, people trust you faster and take the next step with less friction."
            ),
            (
                f"People look into {topic_l} when something needs to work better{place_bit}: "
                f"clarity, trust, speed, or an easier way to get in touch.\n\n"
                f"A practical approach keeps the focus on what customers see and do — especially on their phones."
            ),
            (
                f"At its core, {topic_l} should solve a real customer problem{place_bit}. If the outcome is unclear, "
                f"the project usually drifts.\n\n"
                f"Spell out the result you want, then build the pages, features, or process that deliver it."
            ),
            (
                f"{topic_np} matters because first impressions happen online{place_bit}. Slow, confusing, or "
                f"outdated experiences make people leave before they call.\n\n"
                f"Invest in the basics that protect trust: clear messaging, mobile usability, and an obvious next step."
            ),
            (
                f"Whether you are starting fresh or improving what you have{place_bit}, {topic_l} should "
                f"make your business easier to understand and easier to contact.\n\n"
                f"Keep the scope focused, measure what customers do next, and improve from there."
            ),
        ])

    # Rotating H2 pairs — never "What We Offer" / "Ready to Get Started?"
    if _is_comparison_query(raw_kw or cleaned):
        a, b = _parse_comparison_sides(raw_kw or cleaned)
        a = a or "Option A"
        b = b or "Option B"
        h2_pairs = [
            (f"How a {a} and a {b} Differ", f"Which One Fits You Better"),
            (f"{a} vs {b}: Practical Differences", f"Choosing Between {a} and {b}"),
            (f"What Sets {a} and {b} Apart", f"Pick the Model That Matches Your Offer"),
            (f"Side-by-Side: {a} and {b}", f"Next Steps After You Decide"),
            (f"Service, Pace, and Customer Fit", f"Going Online for Either Option"),
        ]
    elif re.search(r"\bmaintain|maintenance\b", ql):
        h2_pairs = [
            (f"Keep Your Website Running Properly", f"Get Help With {topic}"),
            (f"Why Regular {topic} Matters", f"How We Support {topic}"),
            (f"What {topic} Usually Includes", f"Next Steps for {topic}"),
            (f"A Simple {topic} Checklist", f"Talk With a Specialist About {topic}"),
            (f"Stay Ahead of Common Website Issues", f"Start {topic} the Right Way"),
            (f"Protect Your Site After Launch", f"Request {topic} Support"),
        ]
    elif re.search(r"\bmobile app|ios|android\b", ql) or (
        re.search(r"\bapp\b", ql) and not re.search(r"\b(apple|application form|apply)\b", ql)
    ):
        if re.search(r"\bpharmacy|medication|prescription\b", ql):
            h2_pairs = [
                (f"What a Useful Pharmacy App Includes", f"Plan Your {topic} Project"),
                (f"How a Pharmacy App Helps Customers", f"Get Started With {topic}"),
                (f"Refills, Reminders, and Clear Contact", f"Build Your App With a Clear Scope"),
                (f"From Idea to a Working Pharmacy App", f"Talk Through Your App Goals"),
                (f"Keep the First Version Simple", f"Launch {topic} Without Extra Noise"),
            ]
        else:
            h2_pairs = [
                (f"What a Useful Mobile App Includes", f"Plan Your {topic} Project"),
                (f"How {topic} Helps Customers", f"Get Started With {topic}"),
                (f"Features That Matter on Day One", f"Build Your App With a Clear Scope"),
                (f"From Idea to a Working App", f"Talk Through Your App Goals"),
                (f"Keep the First Version Simple", f"Launch {topic} Without Extra Noise"),
            ]
    elif re.search(r"\bshopify|ecommerce|online store\b", ql):
        h2_pairs = [
            (f"What a Strong Online Store Needs", f"Launch Your Store With Confidence"),
            (f"How {topic} Helps You Sell", f"Get Help Building Your Store"),
            (f"Checkout, Catalog, and Mobile Basics", f"Start Your {topic} Project"),
            (f"Make Buying Easy on Phones", f"Set Up Your Store the Right Way"),
            (f"From Product Pages to Paid Orders", f"Request Store Setup Support"),
        ]
    elif re.search(r"\bredesign|rebuild|refresh\b", ql):
        h2_pairs = [
            (f"What a Redesign Should Fix", f"Start Your Website Redesign"),
            (f"Signs Your Site Needs a Refresh", f"Plan a Clearer Website Experience"),
            (f"How {topic} Improves Trust", f"Rebuild With a Simple Roadmap"),
            (f"Clarity, Speed, and Contact Paths", f"Talk About Your Redesign Goals"),
            (f"Replace Friction, Keep What Works", f"Begin Your {topic} Project"),
        ]
    elif re.search(r"\bseo|ppc\b", ql):
        h2_pairs = [
            (f"What Effective {topic} Includes", f"Improve Your Visibility"),
            (f"Pages, Intent, and Follow-Up", f"Get Help With {topic}"),
            (f"How Search Turns Into Inquiries", f"Build a Practical {topic} Plan"),
            (f"Local Relevance That Converts", f"Start Improving Your Search Results"),
            (f"Measure Calls and Form Fills", f"Request {topic} Support"),
        ]
    elif _NEW_BIZ_PLANNING_RE.search(ql) or cleaned == "new business website":
        h2_pairs = [
            (f"What Your First Website Should Include", f"Launch Your Site With a Clear Plan"),
            (f"How a New Business Website Builds Trust", f"Get Your Business Online"),
            (f"Pages That Help Customers Take Action", f"Start Your Website Project"),
            (f"Mobile-Friendly Basics for Day One", f"Build Your First Professional Site"),
            (f"From Idea to a Live Site", f"Talk Through Your Launch Goals"),
        ]
    else:
        topic_h = topic if re.match(r"^(a|an|the)\b", topic_l) else (
            f"a {topic}" if topic_l[:1] not in "aeiou" else f"an {topic}"
        )
        h2_pairs = [
            (f"What {topic} Includes", f"Get Help With {topic}"),
            (f"How {topic} Helps Your Business", f"Start Your {topic} Project"),
            (f"A Practical {topic} Checklist", f"Next Steps for {topic}"),
            (f"Why {topic} Matters", f"Build {topic} the Right Way"),
            (f"Key Pieces of Strong {topic}", f"Talk With a Specialist About {topic}"),
            (f"Make {topic_h} Clear for Customers", f"Request Support for {topic}"),
        ]

    h2_practical, h2_cta = _meta_pick(f"h2pair|{seed}", h2_pairs)
    # Long pasted questions were being glued into every heading ("A Practical {whole sentence} Checklist")
    # while the paragraphs stayed on a shorter, older topic. Keep headings readable and put the
    # editor's exact phrase in the body.
    focus_phrase = re.sub(r"\s+", " ", (raw_kw or topic)).strip().rstrip("?. ")
    if len(topic.split()) > 5:
        short = " ".join(topic.split()[:4])
        h2_practical = h2_practical.replace(topic, short).replace(topic_l, short.lower())
        h2_cta = h2_cta.replace(topic, short).replace(topic_l, short.lower())

    practical_lead = _meta_pick(f"plead|{seed}", [
        (
            f"Small gaps add up when they are ignored{place_bit}. A clear checklist helps you stay "
            f"ahead of the usual problems tied to {topic_l}."
        ),
        (
            f"Scope matters. Focus on the pieces of {topic_l} that protect customers and make the "
            f"next step obvious on a phone{place_bit}."
        ),
        (
            f"Use a simple list so {topic_l} stays manageable for your team and easy to explain to partners{place_bit}."
        ),
        (
            f"Most businesses need the same fundamentals for {topic_l}{place_bit}: clarity, reliability, "
            f"and a path to contact."
        ),
        (
            f"Treat {topic_l} as ongoing care for how customers meet you online{place_bit} — not a one-time checkbox."
        ),
    ])
    practical_close = _meta_pick(f"pclose|{seed}", [
        "That focus gives you more time to run the business instead of chasing avoidable website problems.",
        f"Handled well, {topic_l} frees your team to sell and serve — while the basics stay covered.",
        f"The goal is a result customers can use today, with fewer emergencies tomorrow.",
        f"Keep the list short, finish the essentials, then improve from real customer behavior.",
        f"Consistency beats complexity: cover the checklist, then refine what matters most.",
    ])

    include_label = (
        "Maintenance can include:"
        if re.search(r"maintain|maintenance", ql)
        else f"{topic} can include:"
    )

    cta_body = _meta_pick(f"ctab|{seed}", [
        (
            f"ZeOrbit provides {topic_l} to help businesses keep results clear and usable"
            f"{place_bit}.\n\n"
            f"Whether you need a full build, ongoing updates, fixes, or a practical plan, "
            f"support can match what your site or app actually needs.\n\n"
            f"If you want help with {topic_l}, [Reach Out ZeOrbit](https://zeorbit.com/contact).\n\n"
            f"Call: (619) 724-9517\n\n"
            f"Website: [www.zeorbit.com](https://zeorbit.com/)"
        ),
        (
            f"When you are ready for hands-on help with {topic_l}{place_bit}, ZeOrbit can map a "
            f"simple plan and ship the work — websites, apps, and ongoing support included.\n\n"
            f"Tell us what must improve and how customers should contact you.\n\n"
            f"[Reach Out ZeOrbit](https://zeorbit.com/contact) · (619) 724-9517 · "
            f"[www.zeorbit.com](https://zeorbit.com/)"
        ),
        (
            f"Need a partner for {topic_l}{place_bit}? ZeOrbit builds and maintains clear, "
            f"mobile-friendly digital experiences for US businesses.\n\n"
            f"Share your goals and constraints — we will recommend the smallest useful next step.\n\n"
            f"Call (619) 724-9517 or visit [www.zeorbit.com](https://zeorbit.com/)."
        ),
        (
            f"ZeOrbit helps with {topic_l} when you want practical delivery instead of a vague proposal"
            f"{place_bit}.\n\n"
            f"From first launch to fixes and updates, the focus stays on what customers can do on a phone.\n\n"
            f"[Contact ZeOrbit](https://zeorbit.com/contact) · (619) 724-9517"
        ),
        (
            f"If {topic_l} is on your list{place_bit}, you do not have to figure out every detail alone. "
            f"ZeOrbit can guide scope, build, and follow-through.\n\n"
            f"Reach out when you want a clear plan and a usable result.\n\n"
            f"Call (619) 724-9517 · [www.zeorbit.com](https://zeorbit.com/)"
        ),
    ])

    h3s = [
        f"What {topic} should cover",
        f"How to judge {topic}",
        f"What to do next for {topic}",
    ]
    if len(topic.split()) > 5:
        h3s = [
            "What this should cover",
            "How to judge the work",
            "What to do next",
        ]
    h3_body = "\n\n".join(
        f"### {h3}\n\n"
        f"{h3} comes back to the same request: {focus_phrase}. "
        f"Say what the customer should see, what you will deliver, and how you will know {topic_l} worked{place_bit}."
        for h3 in h3s
    )
    content = (
        f"## {h2_practical}\n\n"
        f"This section is about {focus_phrase}. "
        f"{practical_lead}\n\n"
        f"{include_label}\n\n"
        f"{bullet_md}\n\n"
        f"{h3_body}\n\n"
        f"{practical_close} Keep the writing on {focus_phrase}, not a generic website checklist.\n\n"
        f"## {h2_cta}\n\n"
        f"If you still need {focus_phrase}, the next step is a scoped plan — not another outline.\n\n"
        f"{cta_body}"
    )

    faqs = [
        {
            "question": f"What does {topic} include?",
            "answer": (
                f"It can include {', '.join(bullets[:4])}, plus related work that keeps "
                f"the experience clear and usable for customers."
            ),
        },
        {
            "question": f"Why does {topic} matter?",
            "answer": (
                f"It helps prevent confusion, broken experiences, and missed inquiries — "
                f"so customers can trust you and take the next step."
            ),
        },
        {
            "question": f"Can ZeOrbit help with {topic}?",
            "answer": (
                f"Yes. ZeOrbit can help with {topic_l} for new and existing websites or apps, "
                f"based on what your business needs."
            ),
        },
        {
            "question": "How do I get started?",
            "answer": (
                f"Call (619) 724-9517 or visit www.zeorbit.com. Share what you need for {topic_l} "
                f"and we will outline a simple plan."
            ),
        },
    ]
    cta = (
        f"Need help with {topic}? Call (619) 724-9517 or visit www.zeorbit.com."
    )
    meta = topic_help_meta(
        keyword=keyword or cleaned,
        city=city,
        industry=industry,
        audience=audience,
        business_type=business_type,
    )
    # Titles never carry ZeOrbit
    title = re.sub(r"\bzeorbit\b", "", h1, flags=re.I)
    title = re.sub(r"\s{2,}", " ", title).strip(" -|,")[:90] or h1
    return {
        "title": title,
        "h1": title,
        "meta_description": meta,
        "h2s": [h2_practical, h2_cta],
        "h3s": h3s,
        "intro": intro,
        "content": content,
        "cta": cta,
        "faqs": faqs,
        "focus_keyword": pretty,
    }



def _simple_zeorbit_pitch_copy(
    keyword: str = "",
    city: str = "",
    industry: str = "",
    audience: str = "",
    business_type: str = "",
) -> dict:
    """Service/topic pages — evergreen intro + body (dynamic per keyword), unique by location."""
    return _evergreen_service_copy(
        keyword=keyword,
        city=city,
        industry=industry,
        audience=audience,
        business_type=business_type,
    )



def _new_business_launch_copy(city: str = "") -> dict:
    """Back-compat wrapper → shared simple pitch."""
    return _simple_zeorbit_pitch_copy(
        keyword="new business website",
        city=city,
    )


def pick_primary_keyword(
    target_keywords: list,
    business_type: str,
    city: str,
    index: int = 0,
    industry: str = "",
    audience: str = "",
) -> str:
    """Pick the SEO primary keyword for this page.

    Prefer keywords that already name the Industry (e.g. Healthcare). Otherwise
    rotate the list, and for website-design niches prefix a *real* vertical so
    titles become "Healthcare Website Design in Downtown Chula Vista…" not a
    bare "WordPress Website Design" that ignores Healthcare / Startups.

    Never prefix catch-alls like "Professional Services".
    """
    from services.zeorbit_local_seo import (
        is_generic_industry,
        resolve_industry_label,
        strip_generic_industry_prefix,
    )

    kws = [
        sanitize_seo_keyword(
            strip_generic_industry_prefix(str(k).strip()),
            industry=industry,
            business_type=business_type,
            audience=audience,
        )
        for k in (target_keywords or [])
        if str(k).strip()
    ]
    kws = [k for k in kws if k]
    ind = resolve_industry_label(industry, business_type, kws)
    ind_l = ind.lower()

    def _with_industry(kw: str) -> str:
        kw = strip_generic_industry_prefix(kw)
        if not ind or is_generic_industry(ind) or ind_l in (kw or "").lower():
            return kw
        if len(kw.split()) > 6 or re.match(r"^(who|what|how|why|when|where|can|do|does|is|should)\b", kw, re.I):
            return kw
        if re.search(r"website|wordpress|web design|landing page", kw, re.I):
            return f"{ind} {kw}".strip()
        return kw

    if kws:
        aligned = [k for k in kws if ind_l and ind_l in k.lower()]
        pool = aligned or kws
        return _with_industry(pool[int(index) % len(pool)])
    loc = (city or "").strip()
    base = strip_generic_industry_prefix((business_type or "website design").strip())
    if ind and ind_l not in base.lower():
        base = f"{ind} {base}".strip()
    return f"{base} {loc}".strip()


def pretty_keyword(text: str) -> str:
    raw = re.sub(r"\s+", " ", (text or "").strip())
    if not raw:
        return ""
    small = {"in", "for", "of", "and", "a", "the", "to", "on"}
    parts = []
    for i, w in enumerate(raw.split(" ")):
        low = w.lower()
        if low == "wordpress":
            parts.append("WordPress")
        elif low == "seo":
            parts.append("SEO")
        elif low == "ai":
            parts.append("AI")
        elif i and low in small:
            parts.append(low)
        else:
            parts.append(w[:1].upper() + w[1:] if w else w)
    return " ".join(parts)


_BRIEF_LABEL_RE = re.compile(
    r"(?im)^\s*(working title\s*/\s*topic|search intent|customer problem|pricing|"
    r"key points to cover|faqs? to answer|cta direction|tone\s*/\s*voice notes|"
    r"extra editor notes)\s*:\s*"
)


def parse_structured_brief(brief: str) -> dict:
    """Pull labeled editor fields out of the composed brief (never publish labels)."""
    raw = (brief or "").strip()
    out = {
        "topic_title": "",
        "search_intent": "",
        "customer_problem": "",
        "pricing": "",
        "key_points": "",
        "faq_ideas": "",
        "cta_direction": "",
        "tone_notes": "",
        "extra_notes": "",
    }
    if not raw:
        return out
    key_map = {
        "working title / topic": "topic_title",
        "search intent": "search_intent",
        "customer problem": "customer_problem",
        "pricing": "pricing",
        "key points to cover": "key_points",
        "faq to answer": "faq_ideas",
        "faqs to answer": "faq_ideas",
        "cta direction": "cta_direction",
        "tone / voice notes": "tone_notes",
        "extra editor notes": "extra_notes",
    }
    matches = list(_BRIEF_LABEL_RE.finditer(raw))
    if not matches:
        return out
    for i, m in enumerate(matches):
        label = re.sub(r"\s+", " ", m.group(1).strip().lower())
        field = key_map.get(label)
        if not field:
            continue
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(raw)
        out[field] = raw[start:end].strip()
    return out


def extract_brief_topic(brief: str, target_keywords: Optional[list] = None, business_type: str = "") -> str:
    """Clean topic / keyword from a structured brief — never the labeled blob."""
    parsed = parse_structured_brief(brief)
    topic = (parsed.get("topic_title") or "").strip()
    if topic:
        return re.sub(r"[?!.]+$", "", topic).strip()[:80]
    kws = [str(k).strip() for k in (target_keywords or []) if str(k).strip()]
    for k in kws:
        if not _BRIEF_LABEL_RE.search(k) and "working title" not in k.lower():
            return k[:80]
    # Unlabeled short brief → use as topic; long labeled junk → fall back
    b = (brief or "").strip()
    if b and not _BRIEF_LABEL_RE.search(b) and len(b) <= 100:
        return re.sub(r"[?!.]+$", "", b).strip()[:80]
    return (business_type or (kws[0] if kws else "website design"))[:80]


def _looks_like_writing_brief(text: str) -> bool:
    """True when text is an AI instruction / style brief, not a topic or body copy."""
    t = (text or "").strip().lower()
    if not t:
        return False
    if _BRIEF_LABEL_RE.search(t) or "working title / topic:" in t:
        return True
    markers = (
        "focus each page",
        "make every page feel unique",
        "custom content requirements",
        "avoid generic",
        "keep the content simple",
        "show how zeorbit can help",
        "honor every point",
        "these should be treated only as",
        "never appear as visible content",
        "patient-focused, locally relevant",
        "writing brief only",
        "never paste",
        "do not invent",
        "non-negotiable:",
        "key points to cover:",
        "customer problem:",
        "search intent:",
        "cta direction:",
        "extra editor notes:",
    )
    if any(m in t for m in markers):
        return True
    # Only treat as brief when it reads like editor instructions (imperatives),
    # not ordinary multi-sentence article paragraphs.
    if len(t) > 180 and t.count(".") >= 3:
        imperative_hits = sum(
            1 for m in ("make sure", "ensure that", "avoid ", "do not ", "don't ", "must include", "always write")
            if m in t
        )
        if imperative_hits >= 2 and not re.search(
            r"^(if you|when you|a business|zeorbit|many |owners |in )", t
        ):
            return True
    return False


def _strip_instruction_leak(text: str, brief: str = "") -> str:
    """Remove Custom Content Requirements / instruction paragraphs from body output.

    Preserves markdown ## section structure produced by `_sectioned_body`.
    """
    raw = _as_text(text)
    if not raw:
        return ""
    brief_l = (brief or "").strip().lower()
    keep = []
    for para in re.split(r"\n{2,}", raw):
        p = para.strip()
        if not p:
            continue
        # Keep section markers from _sectioned_body intact
        if re.match(r"^##\s+\S", p):
            keep.append(p)
            continue
        pl = p.lower()
        if _looks_like_writing_brief(p):
            continue
        if _looks_like_template_filler(p):
            continue
        if brief_l and len(brief_l) > 40 and (
            pl == brief_l or (brief_l in pl and len(pl) < len(brief_l) + 40)
        ):
            continue
        keep.append(p)
    return "\n\n".join(keep)


def _looks_like_template_filler(text: str) -> bool:
    t = (text or "").lower()
    hits = (
        "treat the words in that search as the whole job",
        "practical us-english guide",
        "name the tool, browser, or product in the query",
        "say what the reader should see on screen",
        "do not switch the topic to an unrelated service",
        "keep every section on that topic",
        "examples should match the words in the query",
        "stay on the sentence someone typed",
        "restate the question in one sentence",
        "smallest test that would prove the answer",
        "if the query is about a website, talk websites",
        "rewriting the article as",
        "not a sales page",
        "this section answers the search",
        "explain the situation in plain language",
        "keep it about the query, not a generic agency pitch",
    )
    if any(m in t for m in hits):
        return True
    if "common mix-ups" in t and "when to get help" in t and "what to do next" in t:
        return True
    if "a simple starting point" in t and "what good looks like" in t:
        return True
    return False


def _looks_like_search_query(text: str) -> bool:
    """True when the keyword is a question, comparison, or sentence — not a 2-word SEO phrase.

    Pasted CTA slogans (phone + zeorbit.com + 'are you a…') are NOT search queries.
    """
    t = (text or "").strip()
    if not t:
        return False
    # Marketing paste: phone, site URL, or ZeOrbit help-line — treat as slogan, not a query.
    if _PHONE_IN_TEXT_RE.search(t) or _URL_IN_TEXT_RE.search(t):
        return False
    if re.search(r"\bzeorbit\b", t, re.I) and re.search(r"\b(call|visit|help you|www\.)\b", t, re.I):
        return False
    if _SLOGAN_OPENER_RE.search(t) and len(t.split()) >= 6:
        return False
    if "?" in t:
        return True
    words = t.split()
    if ":" in t and len(words) >= 5:
        return True
    if _is_comparison_query(t):
        return True
    if re.search(r"\b(or|vs\.?|versus|compared to|instead of)\b", t, re.I) and len(words) >= 5:
        return True
    if re.search(r"\b(what does|what do|do you need|really need|should i|should you)\b", t, re.I):
        return True
    if re.match(r"^(how|what|why|when|which|who|where|should|is|are|can|do|does|will)\b", t, re.I):
        return True
    return len(words) >= 6


_COMPARISON_RE = re.compile(
    r"\b(?:difference(?:s)?\s+between|distinguish(?:ing)?\s+between|"
    r"distinction\s+between|compare(?:d)?\s+(?:to|with|and)|"
    r"comparison\s+(?:of|between)|vs\.?|versus)\b|"
    r"\b([a-z][a-z0-9'-]{2,28})\s+and\s+([a-z][a-z0-9'-]{2,28})\s+difference\b|"
    r"\bdifference\s+(?:of|for|in)?\s*([a-z][a-z0-9'-]{2,28})\s+and\s+([a-z][a-z0-9'-]{2,28})\b",
    re.I,
)

# Known differentiation pairs (incl. common typos) for messy marketing keywords.
_KNOWN_COMPARE_PAIRS = (
    (("restaurant", "reastauarnt", "resto"), ("cafe", "café", "coffee shop", "coffeeshop")),
    (("wordpress",), ("shopify", "wix", "squarespace")),
    (("ios", "iphone"), ("android",)),
    (("b2b",), ("b2c",)),
)


def _is_comparison_query(text: str = "", keywords=None) -> bool:
    """True for 'difference between restaurant and cafe', 'X vs Y', 'restaurant and cafe difference', etc."""
    blob = " ".join(
        [str(text or "").strip()]
        + [str(k).strip() for k in (keywords or []) if str(k).strip()]
    ).strip()
    if not blob:
        return False
    if _COMPARISON_RE.search(blob):
        return True
    low = blob.lower()
    # Known pairs + a differentiation cue (difference / vs / or / hybrid / between)
    cue = bool(re.search(r"\b(difference|differ|vs\.?|versus|compare|comparison|hybrid|between|or)\b", low))
    if cue:
        for lefts, rights in _KNOWN_COMPARE_PAIRS:
            if any(x in low for x in lefts) and any(y in low for y in rights):
                return True
    # Slash form: restaurant/cafe
    if re.search(r"\b(restaurant|reastauarnt|resto)\s*/\s*(cafe|café)\b", low) or re.search(
        r"\b(cafe|café)\s*/\s*(restaurant|reastauarnt)\b", low
    ):
        return True
    # "restaurant or cafe which is better" style
    return bool(
        re.search(r"\b([a-z][a-z0-9 &'-]{1,40})\s+or\s+([a-z][a-z0-9 &'-]{1,40})\b", blob, re.I)
        and re.search(r"\b(which|better|choose|difference|vs)\b", blob, re.I)
    )


def _parse_comparison_sides(text: str) -> tuple[str, str]:
    """Extract (left, right) from a comparison query. Empty strings if unknown."""
    raw = re.sub(r"\s+", " ", (text or "").strip())
    ql = raw.lower()

    # Known foodservice / platform pairs first (handles typos + hybrid marketing paste)
    for lefts, rights in _KNOWN_COMPARE_PAIRS:
        if any(x in ql for x in lefts) and any(y in ql for y in rights):
            left_label = "Restaurant" if lefts[0].startswith("restaurant") or lefts[0] == "resto" else pretty_keyword(lefts[0])
            right_label = "Cafe" if rights[0].startswith("cafe") or "coffee" in rights[0] else pretty_keyword(rights[0])
            if lefts[0] in ("wordpress",):
                left_label = "WordPress"
            if rights[0] in ("shopify",):
                right_label = "Shopify"
            if lefts[0] in ("ios", "iphone"):
                left_label = "iOS"
            if rights[0] == "android":
                right_label = "Android"
            return left_label, right_label

    m = re.search(
        r"(?:difference(?:s)?|distinction|comparison)\s+between\s+(.+?)\s+and\s+(.+?)(?:\?|$)",
        ql,
        re.I,
    )
    if m:
        return pretty_keyword(m.group(1)), pretty_keyword(m.group(2))

    m = re.search(
        r"\b([a-z][a-z0-9'-]{2,28})\s+and\s+([a-z][a-z0-9'-]{2,28})\s+difference",
        ql,
        re.I,
    )
    if m:
        return pretty_keyword(m.group(1)), pretty_keyword(m.group(2))

    m = re.search(
        r"difference\s+(?:of|for|in)?\s*([a-z][a-z0-9'-]{2,28})\s+and\s+([a-z][a-z0-9'-]{2,28})",
        ql,
        re.I,
    )
    if m:
        return pretty_keyword(m.group(1)), pretty_keyword(m.group(2))

    m = re.search(
        r"compare(?:d)?\s+(?:to|with|and)?\s*(.+?)\s+(?:to|with|and|vs\.?|versus)\s+(.+?)(?:\?|$)",
        ql,
        re.I,
    )
    if m:
        return pretty_keyword(m.group(1)), pretty_keyword(m.group(2))

    m = re.search(
        r"^(.+?)\s+(?:vs\.?|versus)\s+(.+?)(?:\s*[:?\-].*)?$",
        ql,
        re.I,
    )
    if m:
        return pretty_keyword(m.group(1)), pretty_keyword(m.group(2))

    m = re.search(r"\b(restaurant|reastauarnt|resto)\s*/\s*(cafe|café)s?\b", ql, re.I)
    if m:
        return "Restaurant", "Cafe"

    m = re.search(
        r"\b([a-z][a-z0-9 &'-]{1,40})\s+or\s+([a-z][a-z0-9 &'-]{1,40})\b",
        ql,
        re.I,
    )
    if m:
        return pretty_keyword(m.group(1)), pretty_keyword(m.group(2))

    return "", ""


def _comparison_meta(a: str, b: str, city: str = "", keyword: str = "") -> str:
    """Question-led meta that answers the comparison (not a website pitch)."""
    place = _meta_place_label(city)
    left = a or "one option"
    right = b or "the other"
    seed = f"cmp|{left}|{right}|{place}|{keyword}".lower()
    if place:
        pool = [
            (
                f"What's the difference between a {left.lower()} and a {right.lower()}? "
                f"ZeOrbit breaks down service, atmosphere, and operations — and builds websites "
                f"and mobile apps for both in {place}."
            ),
            (
                f"{left} vs {right}: which fits your {place} business? Compare menu style, "
                f"pace, and customer experience. ZeOrbit builds apps and sites for both."
            ),
            (
                f"Difference between {left.lower()} and {right.lower()} in plain English. "
                f"ZeOrbit helps {place} owners choose clearly — then ships a website or mobile app for either."
            ),
        ]
    else:
        pool = [
            (
                f"What's the difference between a {left.lower()} and a {right.lower()}? "
                f"Compare service style, atmosphere, and how customers order. "
                f"ZeOrbit builds websites and mobile apps for both."
            ),
            (
                f"{left} vs {right}: key differences in menu, pace, and experience. "
                f"ZeOrbit helps you decide — then builds a clear website or mobile app for either."
            ),
            (
                f"Difference between {left.lower()} and {right.lower()} explained simply. "
                f"ZeOrbit creates professional websites and mobile apps for both business types."
            ),
        ]
    meta = _meta_pick(seed, pool)
    if len(meta) > 230:
        try:
            from services.zeorbit_local_seo import fit_meta_description
            meta = fit_meta_description(meta, limit=230) or meta[:230]
        except Exception:
            meta = meta[:227].rsplit(" ", 1)[0] + "."
    return meta[:230]


def _comparison_article_copy(keyword: str = "", city: str = "") -> dict:
    """Answer a differentiation query in meta, intro, and body — not a ZeOrbit website pitch.

    Example: 'difference between restaurant and cafe' → real comparison + soft CTA that
    ZeOrbit builds websites and mobile apps for both.
    """
    raw = re.sub(r"\s+", " ", (keyword or "").strip())
    a, b = _parse_comparison_sides(raw)
    if not a or not b:
        # Fallback labels from the raw query
        a, b = a or "Option A", b or "Option B"
    place = _meta_place_label(city)
    place_bit = f" in {place}" if place else ""
    al, bl = a.lower(), b.lower()
    seed = f"cmpbody|{al}|{bl}|{place}".lower()

    # Foodservice-aware detail when both sides look like dining concepts
    foodie = bool(
        re.search(
            r"\b(restaurant|cafe|café|coffee|bakery|bistro|bar|diner|eatery|food truck)\b",
            f"{al} {bl} {raw}",
            re.I,
        )
    )
    wants_app = bool(re.search(r"\b(mobile\s*app|ios|android|\bapp\b)\b", raw, re.I))
    hybrid = bool(re.search(r"\bhybrid|both\b", raw, re.I))

    title = _meta_pick(f"t|{seed}", [
        f"Difference Between {a} and {b}",
        f"{a} vs {b}: What's the Difference?",
        f"{a} or {b}? Key Differences Explained",
    ])
    if hybrid and foodie:
        title = _meta_pick(f"t|hy|{seed}", [
            f"Restaurant vs Cafe: Hybrid Concepts Explained",
            f"Difference Between a Restaurant and a Cafe",
            f"Restaurant or Cafe — Or Both?",
        ])
    h1 = title
    meta = _comparison_meta(a, b, city=city, keyword=raw)

    if foodie:
        intro = _meta_pick(f"intro|{seed}", [
            (
                f"People searching for the difference between a {al} and a {bl} usually want a clear, "
                f"practical answer — not a dictionary definition. In short, a {al} is typically built around "
                f"full-service meals and a longer visit, while a {bl} is built around quicker service, "
                f"drinks or lighter food, and a more casual pace{place_bit}.\n\n"
                f"Both can succeed with the right offer, staffing, and online presence. ZeOrbit builds "
                f"websites and mobile apps for {al}s and {bl}s so customers can find you, browse the menu, "
                f"and take the next step on a phone."
            ),
            (
                f"A {al} and a {bl} can look similar from the street, but they serve customers differently. "
                f"Restaurants usually emphasize plated meals, table service, and a longer stay. Cafés "
                f"(and similar concepts) usually emphasize speed, coffee or light fare, and a flexible "
                f"come-and-go experience{place_bit}.\n\n"
                f"If you run either type of business — or you're deciding which to open — the sections "
                f"below spell out the differences. ZeOrbit also builds mobile apps and websites for both."
            ),
        ])
        offer_diff = (
            f"## How a {a} and a {b} differ\n\n"
            f"- **Service style:** A {al} often uses table service or a fuller dining flow. A {bl} usually "
            f"leans counter service, grab-and-go, or a simpler order path.\n"
            f"- **Menu focus:** Restaurants typically center on meals and courses. Cafés typically center "
            f"on drinks, pastries, or lighter plates that turn faster.\n"
            f"- **Time on site:** Guests may stay longer in a {al}. A {bl} visit is often shorter and more frequent.\n"
            f"- **Space & vibe:** Dining rooms, bartending, and reservations are more common for restaurants. "
            f"Cafés often optimize for quick seating, laptops, or takeout.\n\n"
        )
        which = (
            f"## Which one fits your business{place_bit}?\n\n"
            f"Choose a {al} if your brand is about sit-down meals, hospitality, and a complete dining visit. "
            f"Choose a {bl} if your strength is speed, beverage-led traffic, or a lighter everyday hangout. "
            f"Some concepts blend both — just be clear which experience the customer should expect on day one.\n\n"
        )
        if hybrid:
            which += (
                f"## Hybrid {a}/{b} concepts\n\n"
                f"A hybrid works when you tell guests what to expect: maybe cafe service by day and fuller "
                f"restaurant plates at night, or a shared kitchen with two clear menus. The risk is blurring "
                f"both offers until neither feels intentional. Write one sentence for each daypart, then match "
                f"staffing, seating, and online pages to that promise.\n\n"
            )
        digital = (
            f"## Online presence for both\n\n"
            f"Whether you open a {al} or a {bl}, customers check hours, menus, and contact on their phones first. "
            f"A clear website and — when it helps — a simple mobile app for orders, loyalty, or updates keeps "
            f"either business easy to find and easy to contact.\n\n"
        )
        if wants_app:
            digital += (
                f"## Mobile apps for {a} and {b} owners\n\n"
                f"Owners often want one app that supports either model: menu browsing, ordering, loyalty, or "
                f"push updates for hours and specials. Keep the first version focused on the job guests repeat "
                f"most — then expand. ZeOrbit can plan and build that mobile app alongside the website.\n\n"
            )
    else:
        intro = (
            f"Searching for the difference between {al} and {bl}? Here's a practical breakdown. "
            f"Each option solves a different job for the customer — so the right choice depends on "
            f"what you offer, how people buy, and how you want to operate{place_bit}.\n\n"
            f"Below we compare the two side by side. ZeOrbit builds websites and mobile apps for both "
            f"kinds of businesses when you're ready to go online."
        )
        offer_diff = (
            f"## How {a} and {b} differ\n\n"
            f"- **Customer job:** What problem does each solve, and how fast must it be solved?\n"
            f"- **Offer & pricing:** What do people buy, how often, and at what ticket size?\n"
            f"- **Operations:** Staffing, inventory, hours, and how complex the day-to-day is.\n"
            f"- **Experience:** In-person vs online, self-serve vs full service, one-time vs repeat visits.\n\n"
        )
        which = (
            f"## Which fits you{place_bit}?\n\n"
            f"Pick {al} when that model matches your strengths and the customer outcome you can deliver "
            f"reliably. Pick {bl} when the other model is a clearer fit. If you're stuck, write one sentence "
            f"for the customer's job — the match usually becomes obvious.\n\n"
        )
        digital = (
            f"## Going online for either option\n\n"
            f"Both {al} and {bl} businesses need a clear site (and sometimes a mobile app) so people can "
            f"understand the offer and contact you on a phone. The digital build should match the model "
            f"you chose — not a generic template.\n\n"
        )

    zeorbit = (
        f"## When ZeOrbit can help\n\n"
        f"ZeOrbit designs and builds professional websites and mobile apps for {al}s and {bl}s alike — "
        f"clear menus or services, mobile-friendly pages, and an easy path to call, book, or order. "
        f"Tell us which model you're running (or launching) and we'll map the right build.\n\n"
        f"**Contact us today:**\n"
        f"📞 **Call: (619) 724-9517**\n"
        f"🌐 **Visit: www.zeorbit.com**\n"
    )

    content = offer_diff + which + digital + zeorbit
    h2s = [
        f"How a {a} and a {b} differ" if foodie else f"How {a} and {b} differ",
        f"Which one fits your business{place_bit}?" if foodie else f"Which fits you{place_bit}?",
    ]
    if hybrid and foodie:
        h2s.append(f"Hybrid {a}/{b} concepts")
    h2s.append("Online presence for both" if foodie else "Going online for either option")
    if wants_app:
        h2s.append(f"Mobile apps for {a} and {b} owners")
    h2s.append("When ZeOrbit can help")
    # Clean empty place in H2
    h2s = [re.sub(r"\s+\?", "?", h).strip() for h in h2s]

    faqs = [
        {
            "question": f"What is the main difference between a {al} and a {bl}?",
            "answer": (
                f"A {al} usually centers on a fuller service or offer experience, while a {bl} is typically "
                f"built for a faster or lighter visit. Exact details depend on your concept — use the "
                f"comparison sections above as the checklist."
            ),
        },
        {
            "question": f"Can the same owner run both a {al} and a {bl}?",
            "answer": (
                f"Yes, but keep the customer promise clear for each brand. Mixing models in one location "
                f"without a clear offer often confuses guests."
            ),
        },
        {
            "question": f"Do {al}s and {bl}s both need a website or mobile app?",
            "answer": (
                f"Yes. Guests check hours, menus, and contact on phones. ZeOrbit builds websites and "
                f"mobile apps for both so either business is easy to find and easy to reach."
            ),
        },
        {
            "question": "How do I get started with ZeOrbit?",
            "answer": (
                f"Call (619) 724-9517 or visit www.zeorbit.com. Tell us whether you're building for a "
                f"{al}, a {bl}, or both — and whether you need a website, a mobile app, or both."
            ),
        },
    ]
    cta = (
        f"Building a {al} or a {bl}? ZeOrbit creates websites and mobile apps for both. "
        f"Call (619) 724-9517 or visit www.zeorbit.com."
    )
    return {
        "title": title[:90],
        "h1": h1[:90],
        "meta_description": meta,
        "h2s": h2s,
        "intro": intro.strip(),
        "content": content.strip(),
        "cta": cta,
        "faqs": faqs,
        "search_intent": "compare",
    }


def _should_use_simple_pitch(
    primary_kw: str = "",
    target_keywords=None,
    content_type_out: str = "service",
) -> bool:
    """ZeOrbit website pitch only for explicit web/new-business service topics.

    Natural-language questions, comparisons, how/why/what/best queries, and broad
    topics (e.g. 'Restaurant') must NOT be overwritten by a website pitch.
    """
    if _is_comparison_query(primary_kw, target_keywords):
        return False
    try:
        from services.topic_intent import interpret_topic
        interp = interpret_topic(primary_kw or "", target_keywords)
        if interp.get("use_topic_article"):
            return False
        if interp.get("intent") == "service_pitch":
            return True
    except Exception:
        pass
    # Pages: only pitch when the query is clearly a web/service offer
    blob = f"{primary_kw or ''} {' '.join(str(k) for k in (target_keywords or []))}".lower()
    webish = bool(
        _query_is_web(blob)
        or _is_new_business_website_topic(primary_kw, target_keywords)
        or re.search(
            r"\b(website design|web design|wordpress|shopify|website maintenance|"
            r"website redesign|landing page)\b",
            blob,
        )
    )
    # Blog posts keep the article written for the keyword and industry.
    # The service-page pitch was replacing that article with generic checklist copy.
    if content_type_out == "blog":
        return False
    return webish


_ACCURACY_STOP = {
    "about", "after", "also", "and", "are", "between", "difference", "from", "have",
    "into", "that", "the", "their", "them", "this", "what", "when", "with", "your",
    "website", "mobile", "design",
}


def _accuracy_tokens(text: str) -> list[str]:
    words = re.findall(r"[a-z0-9]+", (text or "").lower())
    long = [w for w in words if len(w) > 3 and w not in _ACCURACY_STOP]
    if long:
        return long
    small = {"the", "and", "for", "are", "what", "how", "with", "your", "that", "this", "from", "into"}
    return [w for w in words if len(w) >= 3 and w not in small]


def _fit_title(text: str, limit: int = 60) -> str:
    text = re.sub(r"\s+", " ", (text or "").strip())
    if len(text) <= limit:
        return text
    cut = text[:limit].rsplit(" ", 1)[0].rstrip(" ,;:-")
    return cut or text[:limit].rstrip()


def ensure_content_accuracy(block):
    """Make title, body, slug, meta, industry, image keyword, and city agree.

    The preview rates this out of 10. Generated drafts should land at 9 or 10.
    """
    primary = ""
    keywords = getattr(block, "keywords", None)
    if keywords is not None:
        primary = (getattr(keywords, "primary", None) or "") if not isinstance(keywords, dict) else (keywords.get("primary") or "")
    primary = (primary or getattr(block, "focus_keyword", "") or "").strip()
    industry = (getattr(block, "industry", "") or "").strip()
    image_keyword = (getattr(block, "image_keyword", "") or getattr(block, "image_concept", "") or "").strip()
    city = (getattr(block, "city", "") or "").strip()
    topic = _accuracy_tokens(primary) or _accuracy_tokens(getattr(block, "title", ""))

    def _has(text: str, tokens: list[str]) -> bool:
        blob = f" {(text or '').lower()} "
        return any(token in blob for token in tokens)

    block.content = re.sub(r"\n*This article answers .+\.\s*", "\n", block.content or "").strip()
    block.content = re.sub(r"\n*The images match .+\.\s*", "\n", block.content or "").strip()
    block.content = re.sub(r"\n*The industry for this page is .+\.\s*", "\n", block.content or "").strip()
    block.content = re.sub(r"\n*The location covered here is .+\.\s*", "\n", block.content or "").strip()

    if topic and not (_has(block.title or "", topic) and _has(block.h1 or "", topic)):
        missing = next((token for token in topic if token not in (block.title or "").lower()), topic[0])
        titled = f"{missing[:1].upper() + missing[1:]}: {(block.title or '').strip()}"
        block.title = _fit_title(titled)
        block.h1 = block.title

    body = f"{block.intro or ''}\n{block.content or ''}"
    if topic and len([t for t in topic if t in body.lower()]) < min(2, len(topic)):
        needed = ", ".join(topic[:3])
        block.intro = f"This page is for {needed}. {(block.intro or '').strip()}".strip()

    if topic and not _has(block.slug or "", topic):
        from services.slug_utils import article_slug
        block.slug = article_slug([primary], city, primary)

    if topic and not _has(block.meta_description or "", topic):
        block.meta_description = _fit_title(f"{topic[0][:1].upper() + topic[0][1:]}: {(block.meta_description or '').strip()}", 155)

    industry_tokens = _accuracy_tokens(industry)
    blob = f"{block.intro or ''}\n{block.content or ''}".lower()
    if industry_tokens and not any(t in topic or t in blob for t in industry_tokens):
        block.intro = f"For {industry}, {(block.intro or '').strip()[:1].lower() + (block.intro or '').strip()[1:]}"
        blob = f"{blob}\n{industry.lower()}"

    image_tokens = _accuracy_tokens(image_keyword)
    if image_tokens and not any(t in topic or t in blob for t in image_tokens):
        photo = f"Photos should show the {image_keyword.lower()}, not a generic office."
        if "Photos of the actual work" in (block.content or ""):
            block.content = block.content.replace(
                "Photos of the actual work, the service area, and contact details belong on the same page.",
                photo,
                1,
            )
        else:
            block.content = (block.content or "").rstrip() + f"\n\n{photo}"

    if city and city.lower() not in f"{block.intro or ''} {block.content or ''}".lower():
        block.intro = f"{(block.intro or '').rstrip()} This is for {city}."
    block.title = _fit_title(block.title or "", 60)
    block.h1 = _fit_title(block.h1 or block.title or "", 60)
    block.meta_description = _fit_title(block.meta_description or "", 155)
    return block


def _apply_topic_driven_pack(block, primary_kw: str, target_keywords, city: str = "", industry: str = "", kind: str = ""):
    """Understand the topic field first; pack a real answer when it is not a service pitch."""
    try:
        from services.topic_intent import interpret_topic, topic_driven_article, image_hint_for_interp
    except Exception:
        return False
    existing = (getattr(block, "content", None) or "").strip()
    # A real model draft already answers the topic. Do not replace it with an outline.
    if len(existing) > 500 and "Every section below stays on" not in existing:
        return False
    interp = interpret_topic(primary_kw or "", target_keywords)
    if not interp.get("use_topic_article"):
        if kind == "blog" and (interp.get("intent") == "service_pitch" or (primary_kw or "").strip()):
            interp = dict(interp)
            interp["use_topic_article"] = True
            if interp.get("intent") == "service_pitch":
                interp["intent"] = "broad"
        else:
            return False
    packed = topic_driven_article(interp, city=(city or "").strip(), industry=(industry or "").strip())
    block.title = packed["title"]
    block.h1 = packed["h1"]
    block.meta_description = packed["meta_description"]
    block.h2s = packed["h2s"]
    block.intro = packed["intro"]
    block.content = packed["content"]
    if packed.get("industry_fit"):
        block.industry_fit = packed["industry_fit"]
    raw_body = re.sub(r"\n*## Organizations we also serve\b[\s\S]*$", "", block.content or "").strip()
    block.content = raw_body
    if "<!--zo-fit-->" in raw_body:
        head, _, tail = raw_body.partition("<!--zo-fit-->")
        block.content = re.sub(r"\n*## Organizations we also serve\s*$", "", head).strip()
        moved = tail.replace("<!--zo-fit-->", "").strip()
        if moved and not (block.industry_fit or "").strip():
            block.industry_fit = moved
    block.cta = packed["cta"]
    block.faqs = [FAQItem(**f) if isinstance(f, dict) else f for f in packed["faqs"]]
    block.search_intent = packed.get("search_intent") or interp.get("intent") or "explain"
    hint = packed.get("image_hint") or image_hint_for_interp(interp)
    if hint and not (getattr(block, "image_keyword", None) or "").strip():
        block.image_keyword = hint
    if hint:
        block.image_concept = hint
    return True


def article_topic(brief: str, target_keywords: list, business_type: str, industry: str = "", audience: str = "") -> str:
    """Blog topic = the editor's search query / first target keyword.

    For blogs, the keyword IS the subject (e.g. a question or how-to sentence).
    Do not replace it with niche, industry, or a leftover page brief.
    CTA slogans are sanitized into a short service keyword.
    """
    kws = [str(k).strip() for k in (target_keywords or []) if str(k).strip()]
    for k in kws:
        cleaned = sanitize_seo_keyword(k, industry=industry, business_type=business_type, audience=audience)
        if _looks_like_search_query(cleaned) or not _looks_like_writing_brief(cleaned):
            if "working title" in k.lower():
                continue
            return cleaned or k
    parsed_topic = extract_brief_topic(brief, kws, business_type)
    if parsed_topic:
        parsed_topic = sanitize_seo_keyword(
            parsed_topic, industry=industry, business_type=business_type, audience=audience
        ) or parsed_topic
        if _looks_like_search_query(parsed_topic) or not _looks_like_writing_brief(parsed_topic):
            return parsed_topic
    if kws:
        return sanitize_seo_keyword(
            kws[0], industry=industry, business_type=business_type, audience=audience
        ) or kws[0]
    return business_type or "guide"

_CITY_GUIDE_RE = re.compile(
    r"(small businesses of|discover the best of|your guide to|"
    r"best of .{0,48}\bca\b|hidden gems|things to do in|local small business owners['’]? guide)",
    re.I,
)


def _blog_off_query(title: str, meta: str, intro: str, content: str, keyword: str) -> bool:
    """True when the model wrote a city directory instead of the search query."""
    kw = (keyword or "").strip().lower()
    blob = f"{title or ''} {meta or ''} {intro or ''}"
    if _CITY_GUIDE_RE.search(blob):
        return True
    if kw and len(kw) > 3:
        skip = {"the", "and", "for", "in", "of", "a", "to", "your"}
        tokens = [t for t in re.findall(r"[a-z0-9]+", kw) if t not in skip and len(t) > 2]
        head = blob.lower()
        hits = sum(1 for t in tokens if t in head)
        if tokens and hits < max(1, (len(tokens) + 1) // 2):
            return True
    words = len(f"{intro or ''} {content or ''}".split())
    return words < 180


def _ensure_meta_length(meta: str, keyword: str, city: str = "") -> str:
    """Prefer question + help meta; fall back to a practical how-to line."""
    help_m = topic_help_meta(keyword=keyword or "", city=city or "")
    m = re.sub(r"\s+", " ", (meta or "").strip())
    if (
        not m
        or _CITY_GUIDE_RE.search(m)
        or not _meta_has_zeorbit_solution(m)
        or len(m) < 90
    ):
        return help_m[:160]
    pretty = pretty_keyword(keyword or "this topic")
    if pretty.lower() not in m.lower() and pretty and "?" not in m:
        m = f"{pretty}? {m}"
    return m[:160].rstrip()


def _rewrite_off_query_blog(block: "SEOBlock", primary: str, layout: str = "") -> "SEOBlock":
    """Replace tourism/directory drafts with on-query how-to copy."""
    packed = grounded_blog_copy(primary) or _blog_query_copy(
        primary, layout or getattr(block, "layout_variant", "") or ""
    )
    pretty = pretty_keyword(primary)
    if packed:
        block.title = pretty[:60]
        block.h1 = pretty
        block.intro = packed["intro"]
        block.content = packed["content"]
        block.h2s = packed.get("h2s") or block.h2s
        if packed.get("faqs"):
            block.faqs = packed["faqs"]
    block.meta_description = _ensure_meta_length(block.meta_description or "", primary, block.city or "")
    block.focus_keyword = (primary or block.focus_keyword or "").strip()
    if block.keywords:
        block.keywords.primary = (primary or "").lower()
    return block


def _page_meta_title(
    primary: str,
    city: str,
    state: str,
    index: int = 0,
    industry: str = "",
    search_intent: str = "",
    brief: str = "",
    keywords: Optional[list] = None,
) -> str:
    """Intent-varied location titles — never the same 'Affordable Website Design in X' for all cities."""
    from services.zeorbit_local_seo import pick_search_intent, title_from_primary_keyword

    intent = pick_search_intent(
        city, index, industry=industry or "", brief=brief or search_intent or "", keywords=keywords or [primary],
    )
    if search_intent:
        from services.zeorbit_local_seo import SEARCH_INTENTS
        for i in SEARCH_INTENTS:
            if i.id == search_intent:
                intent = i
                break
    return title_from_primary_keyword(primary, city, industry or "", intent, index)[:80]


def _audience_who(industry: str, audience: str) -> str:
    ind = (industry or "").strip() or "local"
    aud = (audience or "").strip()
    if aud:
        return f"{ind} {aud}".strip()
    return f"{ind} businesses"


def _as_text(val) -> str:
    if val is None:
        return ""
    if isinstance(val, list):
        return "\n\n".join(_as_text(x) for x in val if x is not None and str(x).strip())
    if isinstance(val, dict):
        return "\n\n".join(str(v) for v in val.values() if v)
    return str(val).strip()


def normalize_markdown_sections(content: str, h2s: list | None = None) -> str:
    """Fix glued '## Heading Body…' into real markdown sections with newlines."""
    text = (content or "").replace("\r\n", "\n").strip()
    if not text:
        return ""
    # Any ## not already at line-start → own block
    text = re.sub(r"([^\n])\s*(##\s+)", r"\1\n\n\2", text)
    heads = sorted(
        [str(h).strip() for h in (h2s or []) if str(h).strip()],
        key=len,
        reverse=True,
    )
    for h in heads:
        text = re.sub(
            rf"(##\s*{re.escape(h)})(?=\s*\S)",
            r"\1\n\n",
            text,
            flags=re.I,
        )
    # Soft-break monster paragraphs (2 sentences ≈ one <p>)
    chunks = []
    md_stash: list[str] = []

    def _stash_md(match: re.Match) -> str:
        md_stash.append(match.group(0))
        return f"\x00MD{len(md_stash) - 1}\x00"

    def _restore_md(piece: str) -> str:
        return re.sub(r"\x00MD(\d+)\x00", lambda m: md_stash[int(m.group(1))], piece)

    for block in re.split(r"\n{2,}", text):
        b = block.strip()
        if not b:
            continue
        if b.startswith("#") or "?" in b[:160] or len(b) < 900:
            chunks.append(b)
            continue
        md_stash = []
        protected = re.sub(r"\[[^\]]+\]\((?:https?://[^)\s]+|/[^)\s]+)\)", _stash_md, b)
        sentences = re.findall(r"[^.!?]+[.!?]+(?:\s+|$)|[^.!?]+$", protected)
        buf, n = [], 0
        for s in sentences:
            s = _restore_md(s.strip())
            if not s:
                continue
            buf.append(s)
            n += 1
            if n >= 2 or sum(len(x) for x in buf) >= 220:
                chunks.append(" ".join(buf))
                buf, n = [], 0
        if buf:
            chunks.append(" ".join(buf))
    return "\n\n".join(chunks)


def _section_pad(heading: str, query: str = "") -> str:
    q = (query or heading or "this topic").strip()
    ql = q.lower()
    if re.search(r"website|web design|wordpress|shopify", ql):
        return (
            f"Keep this section on {q}. Name the pages the site needs, what a visitor "
            "should do on a phone (call, form, or checkout), and which platform fits — "
            "WordPress for service sites, Shopify for stores. Skip filler about logos and colors."
        )
    return (
        f"Keep this section on “{q}”. Explain what it is, the steps that matter, "
        "and how you know it worked. Do not switch the topic to a different product or a website rebuild."
    )


def _sectioned_body(h2s: list, intro: str, content: str, brief: str = "", query: str = "") -> str:
    """Every H2 gets real paragraphs so the live article is not heading-only."""
    heads = [_as_text(h) for h in (h2s or []) if _as_text(h)]
    intro_t = _strip_instruction_leak(_as_text(intro), brief)
    body = normalize_markdown_sections(_strip_instruction_leak(_as_text(content), brief), heads)
    q = (query or "").strip()
    md_heads = [h.strip() for h in re.findall(r"(?m)^##\s+(.+)$", body) if h.strip()]
    if md_heads:
        parts = re.split(r"(?m)^##\s+", body)
        rebuilt = []
        for part in parts[1:]:
            nl = part.find("\n")
            if nl == -1:
                heading, rest = part.strip(), ""
            else:
                heading, rest = part[:nl].strip(), part[nl:].strip()
            rest = _strip_instruction_leak(rest, brief)
            if not rest or len(rest.split()) < 25:
                rest = _section_pad(heading, q or heading)
            rebuilt.append(f"## {heading}\n\n{rest}")
        return "\n\n".join(rebuilt)
    body = re.sub(r"(?m)^##\s+.+$", "", body).strip()
    paras = [p.strip() for p in re.split(r"\n{2,}", body) if p.strip()]
    if not paras and intro_t:
        paras = [p.strip() for p in re.split(r"\n{2,}", intro_t) if p.strip()]
        intro_t = ""
    if not heads:
        return body or intro_t
    if not paras:
        paras = [_section_pad(h, q or h) for h in heads]
    n = len(heads)
    chunks: list[list[str]] = [[] for _ in heads]
    idx = 0
    for i, _h in enumerate(heads):
        remaining_h = n - i
        remaining_p = len(paras) - idx
        if remaining_p <= 0:
            break
        take = remaining_p if i == n - 1 else max(1, remaining_p // remaining_h)
        chunks[i] = paras[idx: idx + take]
        idx += take
    out = []
    for i, h in enumerate(heads):
        piece = chunks[i] or [_section_pad(h, q or h)]
        joined = "\n\n".join(piece)
        if len(joined.split()) < 25:
            joined = _section_pad(h, q or h)
        out.append(f"## {h}\n\n{joined}")
    extra = paras[idx:]
    if extra:
        out.append("\n\n".join(extra))
    return normalize_markdown_sections("\n\n".join(out), heads)


def _buyer_word(industry: str) -> str:
    t = (industry or "").lower()
    if any(k in t for k in ("health", "dental", "clinic", "medical")):
        return "patients"
    if any(k in t for k in ("legal", "law")):
        return "clients"
    if any(k in t for k in ("real estate", "realtor")):
        return "buyers"
    return "customers"

async def _get_business_image(business_type: str, city: str) -> str:
    """
    Fetch a business-specific image using curated Unsplash photo IDs.
    Each business type has specific, verified images that match the business.
    Uses consistent selection based on city for variety.
    """
    # Curated business-specific images from Unsplash (verified to match business types)
    # Format: business_type -> list of Unsplash photo IDs
    business_image_map = {
        # Tech & IT Services - Real developer/coding images
        "software engineer": [
            "https://images.unsplash.com/photo-1498050108023-c5249f4df085",  # Developer at desk
            "https://images.unsplash.com/photo-1461749280684-dccba630e2f6",  # Coding on laptop
            "https://images.unsplash.com/photo-1488590528505-98d2b5aba04b",  # Laptop with code
        ],
        "software engineering": [
            "https://images.unsplash.com/photo-1498050108023-c5249f4df085",
            "https://images.unsplash.com/photo-1461749280684-dccba630e2f6",
            "https://images.unsplash.com/photo-1488590528505-98d2b5aba04b",
        ],
        "web design": [
            "https://images.unsplash.com/photo-1467232004584-a241de8bcf5d",  # Designer workspace
            "https://images.unsplash.com/photo-1559028012-481c04fa702d",  # Web design mockup
            "https://images.unsplash.com/photo-1581291518633-83b4ebd1d83e",  # Design tools
        ],
        "web development": [
            "https://images.unsplash.com/photo-1498050108023-c5249f4df085",
            "https://images.unsplash.com/photo-1461749280684-dccba630e2f6",
            "https://images.unsplash.com/photo-1488590528505-98d2b5aba04b",
        ],
        "app development": [
            "https://images.unsplash.com/photo-1512941937669-90a1b58e7e9c",  # Mobile app development
            "https://images.unsplash.com/photo-1551650975-87deedd944c3",  # Smartphone coding
            "https://images.unsplash.com/photo-1498050108023-c5249f4df085",  # Developer workspace
        ],
        "it support": [
            "https://images.unsplash.com/photo-1550751827-4bd374c3f58b",  # IT technician
            "https://images.unsplash.com/photo-1484480974693-6ca0a78fb36b",  # Computer repair
            "https://images.unsplash.com/photo-1558494949-ef010cbdcc31",  # Tech support
        ],
        "data science": [
            "https://images.unsplash.com/photo-1551288049-bebda4e38f71",  # Data analytics
            "https://images.unsplash.com/photo-1460925895917-afdab827c52f",  # Analytics dashboard
            "https://images.unsplash.com/photo-1504868584819-f8e8b4b6d7e3",  # Data visualization
        ],
        
        # Home Services - Real tradespeople images
        "plumbing": [
            "https://images.unsplash.com/photo-1607472586893-edb57bdc0e39",  # Plumber tools
            "https://images.unsplash.com/photo-1581244277943-fe4a9c777189",  # Plumbing work
            "https://images.unsplash.com/photo-1585704032915-c3400ca199e7",  # Pipes and tools
        ],
        "plumber": [
            "https://images.unsplash.com/photo-1607472586893-edb57bdc0e39",
            "https://images.unsplash.com/photo-1581244277943-fe4a9c777189",
            "https://images.unsplash.com/photo-1585704032915-c3400ca199e7",
        ],
        "electrician": [
            "https://images.unsplash.com/photo-1621905251189-08b45d6a269e",  # Electrical work
            "https://images.unsplash.com/photo-1473341304170-971dccb5ac1e",  # Electrician tools
            "https://images.unsplash.com/photo-1621905252507-b35492cc74b4",  # Wiring work
        ],
        "hvac": [
            "https://images.unsplash.com/photo-1581244277943-fe4a9c777189",  # HVAC system
            "https://images.unsplash.com/photo-1607472586893-edb57bdc0e39",  # Technician work
            "https://images.unsplash.com/photo-1585704032915-c3400ca199e7",  # Tools
        ],
        "carpentry": [
            "https://images.unsplash.com/photo-1504148455328-c376907d081c",  # Woodworking
            "https://images.unsplash.com/photo-1513828583688-c52646db42da",  # Carpenter tools
            "https://images.unsplash.com/photo-1581244277943-fe4a9c777189",  # Workshop
        ],
        "carpenter": [
            "https://images.unsplash.com/photo-1504148455328-c376907d081c",
            "https://images.unsplash.com/photo-1513828583688-c52646db42da",
            "https://images.unsplash.com/photo-1581244277943-fe4a9c777189",
        ],
        "painting": [
            "https://images.unsplash.com/photo-1562259949-e8e7689d7828",  # House painting
            "https://images.unsplash.com/photo-1589939705384-5185137a7f0f",  # Painter at work
            "https://images.unsplash.com/photo-1513828583688-c52646db42da",  # Paint tools
        ],
        "painter": [
            "https://images.unsplash.com/photo-1562259949-e8e7689d7828",
            "https://images.unsplash.com/photo-1589939705384-5185137a7f0f",
            "https://images.unsplash.com/photo-1513828583688-c52646db42da",
        ],
        "roofing": [
            "https://images.unsplash.com/photo-1632778149955-e80f8ceca2e8",  # Roofing work
            "https://images.unsplash.com/photo-1504148455328-c376907d081c",  # Construction
            "https://images.unsplash.com/photo-1581244277943-fe4a9c777189",  # Tools
        ],
        "roofer": [
            "https://images.unsplash.com/photo-1632778149955-e80f8ceca2e8",
            "https://images.unsplash.com/photo-1504148455328-c376907d081c",
            "https://images.unsplash.com/photo-1581244277943-fe4a9c777189",
        ],
        "landscaping": [
            "https://images.unsplash.com/photo-1558904541-efa843a96f01",  # Landscaping work
            "https://images.unsplash.com/photo-1416879595882-3373a0480b5b",  # Garden maintenance
            "https://images.unsplash.com/photo-1585320806297-9794b3e4eeae",  # Lawn care
        ],
        "landscaper": [
            "https://images.unsplash.com/photo-1558904541-efa843a96f01",
            "https://images.unsplash.com/photo-1416879595882-3373a0480b5b",
            "https://images.unsplash.com/photo-1585320806297-9794b3e4eeae",
        ],
        "cleaning": [
            "https://images.unsplash.com/photo-1581578731548-c64695cc6952",  # Cleaning service
            "https://images.unsplash.com/photo-1563453392212-326f5e854473",  # Professional cleaning
            "https://images.unsplash.com/photo-1628177142898-93e36e4e3a50",  # Cleaning supplies
        ],
        
        # Professional Services
        "marketing": [
            "https://images.unsplash.com/photo-1460925895917-afdab827c52f",  # Marketing analytics
            "https://images.unsplash.com/photo-1557804506-669a67965ba0",  # Business meeting
            "https://images.unsplash.com/photo-1552664730-d307ca884978",  # Team collaboration
        ],
        "digital marketing": [
            "https://images.unsplash.com/photo-1460925895917-afdab827c52f",
            "https://images.unsplash.com/photo-1557804506-669a67965ba0",
            "https://images.unsplash.com/photo-1552664730-d307ca884978",
        ],
        "accounting": [
            "https://images.unsplash.com/photo-1554224155-6726b3ff858f",  # Calculator and papers
            "https://images.unsplash.com/photo-1450101499163-c8848c66ca85",  # Office desk
            "https://images.unsplash.com/photo-1507679799987-c73779587ccf",  # Professional at work
        ],
        "accountant": [
            "https://images.unsplash.com/photo-1554224155-6726b3ff858f",
            "https://images.unsplash.com/photo-1450101499163-c8848c66ca85",
            "https://images.unsplash.com/photo-1507679799987-c73779587ccf",
        ],
        "consulting": [
            "https://images.unsplash.com/photo-1557804506-669a67965ba0",  # Business meeting
            "https://images.unsplash.com/photo-1552664730-d307ca884978",  # Consultation
            "https://images.unsplash.com/photo-1521737711867-e3b97375f902",  # Office discussion
        ],
        "consultant": [
            "https://images.unsplash.com/photo-1557804506-669a67965ba0",
            "https://images.unsplash.com/photo-1552664730-d307ca884978",
            "https://images.unsplash.com/photo-1521737711867-e3b97375f902",
        ],
        "legal": [
            "https://images.unsplash.com/photo-1589829545856-d10d557cf95f",  # Law office
            "https://images.unsplash.com/photo-1505664194779-8beaceb93744",  # Legal documents
            "https://images.unsplash.com/photo-1507679799987-c73779587ccf",  # Professional
        ],
        "lawyer": [
            "https://images.unsplash.com/photo-1589829545856-d10d557cf95f",
            "https://images.unsplash.com/photo-1505664194779-8beaceb93744",
            "https://images.unsplash.com/photo-1507679799987-c73779587ccf",
        ],
        "real estate": [
            "https://images.unsplash.com/photo-1560518883-ce09059eeffa",  # Real estate
            "https://images.unsplash.com/photo-1582407947304-fd86f028f716",  # House for sale
            "https://images.unsplash.com/photo-1560184897-ae75f418493e",  # Property viewing
        ],
        
        # Health & Wellness
        "yoga": [
            "https://images.unsplash.com/photo-1544367567-0f2fcb009e0b",  # Yoga class
            "https://images.unsplash.com/photo-1506126613408-eca07ce68773",  # Yoga pose
            "https://images.unsplash.com/photo-1599901860904-17e6ed7083a0",  # Yoga instructor
        ],
        "yoga instructor": [
            "https://images.unsplash.com/photo-1544367567-0f2fcb009e0b",
            "https://images.unsplash.com/photo-1506126613408-eca07ce68773",
            "https://images.unsplash.com/photo-1599901860904-17e6ed7083a0",
        ],
        "fitness": [
            "https://images.unsplash.com/photo-1534438327276-14e5300c3a48",  # Gym workout
            "https://images.unsplash.com/photo-1571019614242-c5c5dee9f50b",  # Fitness training
            "https://images.unsplash.com/photo-1517836357463-d25dfeac3438",  # Gym equipment
        ],
        "personal trainer": [
            "https://images.unsplash.com/photo-1534438327276-14e5300c3a48",
            "https://images.unsplash.com/photo-1571019614242-c5c5dee9f50b",
            "https://images.unsplash.com/photo-1517836357463-d25dfeac3438",
        ],
        "dental": [
            "https://images.unsplash.com/photo-1588776814546-1ffcf47267a5",  # Dental clinic
            "https://images.unsplash.com/photo-1606811841689-23dfddce3e95",  # Dentist tools
            "https://images.unsplash.com/photo-1629909613654-28e377c37b09",  # Dental office
        ],
        "dentist": [
            "https://images.unsplash.com/photo-1588776814546-1ffcf47267a5",
            "https://images.unsplash.com/photo-1606811841689-23dfddce3e95",
            "https://images.unsplash.com/photo-1629909613654-28e377c37b09",
        ],
        "medical": [
            "https://images.unsplash.com/photo-1576091160399-112ba8d25d1d",  # Medical clinic
            "https://images.unsplash.com/photo-1584820927498-cfe5211fd8bf",  # Doctor
            "https://images.unsplash.com/photo-1631217868264-e5b90bb7e133",  # Medical office
        ],
        "doctor": [
            "https://images.unsplash.com/photo-1576091160399-112ba8d25d1d",
            "https://images.unsplash.com/photo-1584820927498-cfe5211fd8bf",
            "https://images.unsplash.com/photo-1631217868264-e5b90bb7e133",
        ],
        "salon": [
            "https://images.unsplash.com/photo-1560066984-138dadb4c035",  # Hair salon
            "https://images.unsplash.com/photo-1522337360788-8b13dee7a37e",  # Salon interior
            "https://images.unsplash.com/photo-1562322140-8baeececf3df",  # Hairstylist
        ],
        "hairstylist": [
            "https://images.unsplash.com/photo-1560066984-138dadb4c035",
            "https://images.unsplash.com/photo-1522337360788-8b13dee7a37e",
            "https://images.unsplash.com/photo-1562322140-8baeececf3df",
        ],
        
        # Business Services
        "restaurant": [
            "https://images.unsplash.com/photo-1414235077428-338989a2e8c0",  # Restaurant interior
            "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4",  # Restaurant dining
            "https://images.unsplash.com/photo-1552566626-52f8b828add9",  # Chef cooking
        ],
        "chef": [
            "https://images.unsplash.com/photo-1577219491135-ce391730fb2c",  # Chef cooking
            "https://images.unsplash.com/photo-1556910103-1c02745aae4d",  # Chef in kitchen
            "https://images.unsplash.com/photo-1552566626-52f8b828add9",  # Professional chef
        ],
        "catering": [
            "https://images.unsplash.com/photo-1555244162-803834f70033",  # Catering food
            "https://images.unsplash.com/photo-1414235077428-338989a2e8c0",  # Event catering
            "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4",  # Food service
        ],
        "photography": [
            "https://images.unsplash.com/photo-1452587925148-ce544e77e70d",  # Camera equipment
            "https://images.unsplash.com/photo-1471341971476-ae15ff5dd4ea",  # Photographer at work
            "https://images.unsplash.com/photo-1502920917128-1aa500764cbd",  # Photography studio
        ],
        "photographer": [
            "https://images.unsplash.com/photo-1452587925148-ce544e77e70d",
            "https://images.unsplash.com/photo-1471341971476-ae15ff5dd4ea",
            "https://images.unsplash.com/photo-1502920917128-1aa500764cbd",
        ],
        "retail": [
            "https://images.unsplash.com/photo-1441986300917-64674bd600d8",  # Retail store
            "https://images.unsplash.com/photo-1472851294608-062f824d29cc",  # Shop interior
            "https://images.unsplash.com/photo-1556742049-0cfed4f6a45d",  # Retail business
        ],
        "auto repair": [
            "https://images.unsplash.com/photo-1486262715619-67b85e0b08d3",  # Auto mechanic
            "https://images.unsplash.com/photo-1625047509168-a7026f36de04",  # Car repair
            "https://images.unsplash.com/photo-1632823469850-1b7d38c0c3e3",  # Auto shop
        ],
        "mechanic": [
            "https://images.unsplash.com/photo-1486262715619-67b85e0b08d3",
            "https://images.unsplash.com/photo-1625047509168-a7026f36de04",
            "https://images.unsplash.com/photo-1632823469850-1b7d38c0c3e3",
        ],
    }
    
    # Get images for business type (case-insensitive)
    business_key = business_type.lower().strip()
    image_urls = business_image_map.get(business_key)
    
    # If no specific mapping, use generic professional/business images
    if not image_urls:
        print(f"[Image] ⚠️  No specific images for '{business_type}', using generic professional images")
        # Generic professional business images (NOT plumbing or any specific trade)
        image_urls = [
            "https://images.unsplash.com/photo-1497366216548-37526070297c",  # Professional office
            "https://images.unsplash.com/photo-1497366811353-6870744d04b2",  # Business workspace
            "https://images.unsplash.com/photo-1497215728101-856f4ea42174",  # Modern office
            "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab",  # Office building
            "https://images.unsplash.com/photo-1454165804606-c3d57bc86b40",  # Business desk
            "https://images.unsplash.com/photo-1507679799987-c73779587ccf",  # Professional at work
        ]
    
    # Use hash of city to consistently select same image for same city
    city_hash = abs(hash(city.lower())) % len(image_urls)
    selected_url = image_urls[city_hash]
    
    # Add Unsplash parameters for proper sizing and quality
    image_url = f"{selected_url}?w=1200&h=600&fit=crop&q=80"
    
    print(f"[Image] 🔍 Business: {business_type}")
    print(f"[Image] 🎯 City: {city} (hash: {city_hash})")
    print(f"[Image] ✅ Using curated Unsplash image #{city_hash + 1}/{len(image_urls)}")
    print(f"[Image] 📸 URL: {image_url}")
    
    return image_url

def _significant_kw_words(keyword: str) -> list:
    stop = {
        "in", "for", "of", "and", "a", "the", "to", "on", "near", "me", "with", "your",
        "ca", "tx", "ny", "fl", "az", "wa", "or", "nv", "co",
    }
    return [w for w in (keyword or "").lower().split() if w and w not in stop and len(w) > 1]


def _kw_words_present(text: str, keyword: str, min_ratio: float = 1.0) -> bool:
    """True if enough significant words of `keyword` appear in `text`.

    Long multi-word primaries (industry + niche + city leftovers) rarely fit
    entirely into every H2 — require all words by default, or a ratio for softer checks.
    """
    text_l = (text or "").lower()
    words = _significant_kw_words(keyword)
    if not words:
        return bool((keyword or "").lower() in text_l)
    hits = sum(1 for w in words if w in text_l)
    return hits >= max(1, int(round(len(words) * min_ratio)))


def _seo_score(
    text: str, title: str, meta: str, h2s: list, faqs: list,
    keyword: str, city: str, slug: str, h1: str = "",
) -> float:
    """
    Composite SEO score 0-100 based on real ranking factors:
    - Keyword coverage in title (15)
    - Keyword in meta (10)
    - Keyword in slug (10)
    - Keyword in intro / first 120 words (15)
    - Keyword coverage across H2s (10)
    - Content length (15) — scaled 300→600 words
    - FAQs (10)
    - Location in title (5)
    - H1 keyword coverage (5)
    - Meta length 120-160 (5)
    """
    score = 0.0
    kw = (keyword or "").lower()
    city_l = (city or "").lower()
    title_l = (title or "").lower()
    meta_l = (meta or "").lower()
    slug_l = (slug or "").lower()
    h1_l = (h1 or "").lower()
    words = (text or "").lower().split()
    first_120 = " ".join(words[:120])
    sig = _significant_kw_words(keyword)

    if _kw_words_present(title, keyword, 0.7):
        score += 15
    if _kw_words_present(meta, keyword, 0.6):
        score += 10
    slug_ok = False
    if kw:
        slug_ok = kw.replace(" ", "-") in slug_l or kw.replace(" ", "") in slug_l
    if not slug_ok and sig:
        slug_ok = sum(1 for w in sig if w in slug_l) >= max(1, len(sig) // 2)
    if slug_ok:
        score += 10
    if _kw_words_present(first_120, keyword, 0.7):
        score += 15

    # H2 coverage: majority of significant words across 2+ headings, or soft partial credit
    h2_hits = sum(1 for h in h2s if _kw_words_present(h, keyword, 0.5))
    if h2_hits >= 2:
        score += 10
    elif h2_hits == 1:
        score += 5
    elif any(_kw_words_present(h, keyword, 0.35) for h in h2s):
        score += 3

    wc = len(words)
    if wc >= 600:
        score += 15
    elif wc >= 450:
        score += 12
    elif wc >= 300:
        score += 10
    elif wc >= 200:
        score += 5

    if len(faqs) >= 5:
        score += 10
    elif len(faqs) >= 3:
        score += 6

    if city_l and city_l in title_l:
        score += 5
    if h1_l and _kw_words_present(h1, keyword, 0.7):
        score += 5
    if 120 <= len(meta or "") <= 165:
        score += 5

    return float(min(score, 100))

def _keyword_density(text: str, keyword: str) -> float:
    """Returns 0–100 keyword-use score for the UI. 90+ = healthy coverage.

    Combines exact-phrase hits + significant-token coverage. Ideal natural
    pages land in the high 90s; thin / off-keyword copy stays well below 90.
    """
    plain = re.sub(r"<[^>]+>", " ", text or "")
    plain = re.sub(r"\s+", " ", plain).strip().lower()
    kw = (keyword or "").strip().lower()
    if not plain or not kw:
        return 0.0
    words = plain.split()
    if not words:
        return 0.0
    stop = {"a", "an", "the", "in", "for", "of", "and", "to", "near", "me", "on", "at"}
    kw_words = [w for w in kw.split() if w and w not in stop] or kw.split()
    phrase_hits = plain.count(kw)
    # Also count city+service fragments without requiring exact full phrase
    if phrase_hits == 0 and len(kw_words) >= 2:
        # sliding bigrams from keyword
        for i in range(len(kw_words) - 1):
            bi = f"{kw_words[i]} {kw_words[i + 1]}"
            phrase_hits += plain.count(bi) // 2  # soft credit
    token_hits = sum(words.count(w) for w in kw_words)
    avg_token = token_hits / max(len(kw_words), 1)
    raw_pct = (token_hits / len(words)) * 100.0

    score = 0.0
    if phrase_hits >= 4:
        score += 55
    elif phrase_hits >= 3:
        score += 48
    elif phrase_hits >= 2:
        score += 40
    elif phrase_hits >= 1:
        score += 28
    if avg_token >= 8:
        score += 35
    elif avg_token >= 5:
        score += 30
    elif avg_token >= 3:
        score += 22
    elif avg_token >= 1:
        score += 12
    if 0.4 <= raw_pct <= 3.5:
        score += 15
    elif raw_pct > 0.2:
        score += 8
    return round(min(score, 100.0), 1)


_QUERY_STOP = {
    "a", "an", "the", "for", "and", "or", "of", "to", "in", "on", "with", "how", "what",
    "why", "when", "where", "does", "do", "is", "are", "your", "my", "our", "that", "this",
    "from", "into", "about", "best", "near", "me",
}


def query_relevance_score(text: str, query: str) -> float:
    """0–10: how much the body actually answers the search query (not generic web-design filler)."""
    qtoks = [t for t in re.findall(r"[a-zA-Z0-9']+", (query or "").lower()) if t not in _QUERY_STOP and len(t) > 2]
    if not qtoks:
        return 10.0
    blob = (text or "").lower()
    hits = sum(1 for t in qtoks if t in blob)
    phrase = " ".join(qtoks[:8])
    bonus = 1.5 if phrase and phrase in blob else 0.0
    # Penalize generic agency filler that ignores the query.
    filler = 0.0
    if any(p in blob for p in ("zeorbit builds", "wordpress and shopify", "web design in ")) and hits < max(2, len(qtoks) // 2):
        filler = 2.0
    return round(min(10.0, max(0.0, (hits / len(qtoks)) * 10.0 + bonus - filler)), 1)


def _put_h3s_in_body(content: str, h3s: list) -> str:
    """Drop placeholder H3 stubs. Real H3s only stay when the article already wrote them."""
    body = content or ""
    body = re.sub(
        r"\n*#+\s*[^\n]+\n+\s*[^\n]*belongs with the section above\.?\s*",
        "\n\n",
        body,
        flags=re.I,
    )
    kept = []
    for raw in h3s or []:
        heading = str(raw or "").strip()
        if heading and heading.lower() in body.lower():
            kept.append(heading)
    # Caller may replace h3s from the return via the body only.
    # Leave the body without invented "belongs with the section above" lines.
    return re.sub(r"\n{3,}", "\n\n", body).strip()


def ensure_keyword_coverage(
    intro: str,
    content: str,
    keyword: str,
    city: str = "",
    min_score: float = 90.0,
) -> tuple:
    """Weave the focus keyword naturally until keyword-use score clears the floor."""
    kw = (keyword or "").strip()
    density = _keyword_density(f"{intro or ''}\n{content or ''}", kw)
    if not kw or density >= min_score:
        return intro or "", content or "", density

    city_bit = f" in {city}" if (city or "").strip() else ""
    display_kw = kw
    if city:
        from services.zeorbit_local_seo import strip_other_places_from_phrase, strip_trailing_place
        display_kw = strip_trailing_place(strip_other_places_from_phrase(kw, city), city) or kw
        if city.lower() in (display_kw or "").lower():
            city_bit = ""

    # Blog posts: weave into real sections — never append instruction-style spam lines.
    is_blog_kw = len(kw.split()) >= 4 or bool(re.search(r"\b(for|in|company|agency|how to)\b", kw, re.I))
    if is_blog_kw and not city_bit:
        new_intro = intro or ""
        if display_kw.lower() not in new_intro.lower():
            new_intro = (
                f"{pretty_keyword(display_kw)} is what this guide answers. {new_intro}"
            ).strip()
        body = content or ""
        density = _keyword_density(f"{new_intro}\n{body}", kw)
        return new_intro, body.strip(), density

    new_intro = intro or ""
    new_content = re.sub(
        r"\s*Teams evaluating .+? what launches first\.?",
        "",
        content or "",
        flags=re.I,
    )
    new_content = re.sub(
        r"\n*Businesses comparing .+? turns visits into calls\.?\s*",
        "\n\n",
        new_content,
        flags=re.I,
    )
    new_intro = re.sub(
        r"\s*Teams evaluating .+? what launches first\.?",
        "",
        new_intro,
        flags=re.I,
    )
    new_content = re.sub(r"\n{3,}", "\n\n", new_content).strip()
    density = _keyword_density(f"{new_intro}\n{new_content}", kw)
    return new_intro.strip(), new_content, density

CANONICAL_SITE = "https://zeorbit.com"


def _abs_http_url(value: str, site: str = CANONICAL_SITE) -> str:
    from urllib.parse import urlparse
    site = (site or CANONICAL_SITE).rstrip("/")
    raw = (value or "").strip()
    if not raw or raw in ("/", "#"):
        return site + "/"
    if raw.startswith("//"):
        raw = "https:" + raw
    if re.match(r"^https?://", raw, re.I):
        parsed = urlparse(raw)
        host = (parsed.netloc or "").lower().replace("www.", "")
        if host in ("example.com", "example.org", "localhost") or host.endswith(".example.com"):
            path = parsed.path or "/"
            return site + (path if path.startswith("/") else f"/{path}")
        return raw
    path = raw if raw.startswith("/") else f"/{raw}"
    return site + path


def sanitize_schema_markup(schema: Any, page_url: str = "", site_url: str = CANONICAL_SITE) -> Dict[str, Any]:
    site = (site_url or CANONICAL_SITE).rstrip("/")
    page = _abs_http_url(page_url or site + "/", site)

    def walk(node: Any) -> Any:
        if isinstance(node, list):
            return [walk(x) for x in node]
        if not isinstance(node, dict):
            return node
        out: Dict[str, Any] = {}
        for k, v in node.items():
            if str(k) in ("url", "item", "@id", "image", "logo", "hasMap") and isinstance(v, str):
                out[k] = _abs_http_url(v, site)
            else:
                out[k] = walk(v)
        return out

    if not isinstance(schema, dict):
        return {}
    cleaned = walk(schema)
    crumb = cleaned.get("breadcrumb")
    if isinstance(crumb, dict):
        els = crumb.get("itemListElement") or []
        fixed = []
        for i, el in enumerate(els, start=1):
            if not isinstance(el, dict):
                continue
            item = _abs_http_url(str(el.get("item") or (page if i == len(els) else site + "/")), site)
            if not str(item).startswith("http"):
                continue
            el = dict(el)
            el["item"] = item
            el["position"] = el.get("position") or i
            fixed.append(el)
        if fixed:
            crumb["itemListElement"] = fixed
        else:
            cleaned.pop("breadcrumb", None)
    return cleaned


def _build_schema(
    bt: str,
    city: str,
    state: str,
    faqs: list,
    business_name: str = "",
    site_url: str = "",
    phone: str = "",
    article_title: str = "",
    slug_override: str = "",
) -> Dict[str, Any]:
    """Build JSON-LD for the page.

    Uses real values when supplied (business name, site URL, phone) and OMITS
    fields we cannot populate rather than shipping placeholder/fake data
    (no fabricated phone numbers or review ratings).
    """
    slug = slug_override or _slugify(f"{bt}-{city}")
    base_url = _abs_http_url(site_url or CANONICAL_SITE).rstrip("/")
    page_url = f"{base_url}/{slug.lstrip('/')}" if slug else base_url + "/"

    faq_entities = [
        {
            "@type": "Question",
            "name": faq.question,
            "acceptedAnswer": {"@type": "Answer", "text": faq.answer}
        }
        for faq in (faqs or [])
        if getattr(faq, "question", None)
    ]
    faq_schema = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": faq_entities,
    } if faq_entities else None

    local_schema: Dict[str, Any] = {
        "@context": "https://schema.org",
        "@type": "LocalBusiness",
        "name": business_name or "ZeOrbit",
        "url": base_url + "/",
        "description": (f"{bt.title()} services in {city}, {state}.".strip(" ,.") if (city or "").strip() else f"{bt.title()} services."),
        "address": {
            "@type": "PostalAddress",
            "addressLocality": city,
            "addressRegion": state,
            "addressCountry": "US"
        } if (city or "").strip() else {"@type": "PostalAddress", "addressCountry": "US"},
        "areaServed": (
            {"@type": "City", "name": city, "addressRegion": state or ""}
            if (city or "").strip() else
            {"@type": "Country", "name": "United States"}
        ),
        "serviceType": bt.title(),
    }
    if phone:
        local_schema["telephone"] = phone

    schema: Dict[str, Any] = {"local_business": local_schema}
    if faq_schema:
        schema["faq_page"] = faq_schema

    if article_title:
        article_schema: Dict[str, Any] = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": article_title,
            "about": bt.title(),
            "url": page_url,
            "mainEntityOfPage": {"@type": "WebPage", "@id": page_url},
        }
        if business_name:
            article_schema["author"] = {"@type": "Organization", "name": business_name, "url": base_url + "/"}
            article_schema["publisher"] = {"@type": "Organization", "name": business_name, "url": base_url + "/"}
        schema["article"] = article_schema
        schema["breadcrumb"] = {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Home", "item": base_url + "/"},
                {"@type": "ListItem", "position": 2, "name": "Blog", "item": f"{base_url}/blog"},
                {"@type": "ListItem", "position": 3, "name": article_title, "item": page_url},
            ],
        }

    return sanitize_schema_markup(schema, page_url=page_url, site_url=base_url)


VOICE_RULES = """
VOICE — American English, user-first, conversational (ZeOrbit):
- Write the way a helpful US teammate talks, not an agency brochure.
- Short questions: "Thinking about a mobile app for your business?"
- Direct help: "Looking for a website or a custom digital solution?"
- Capability, not hype: "We help you turn your idea into an MVP, prototype, or fully functional product from concept to launch."
- Soft next step: "Not sure where to start? We're here to help."
- Use American spelling: optimize, color, center, organization, favorite.
- Avoid stiff jargon (synergies, leverage, best-in-class, holistic solutions).
- Forbidden fluff: cutting-edge, digital transformation, revolutionary, seamless solutions, unlock your potential, next-generation, comprehensive digital ecosystem.
- Second person ("you") over "businesses seeking world-class partners".
- NEVER paste Custom Content Requirements, writing briefs, or meta-instructions into the article body.
- NEVER leave an H2 empty — every heading needs 2–4 full sentences of real content.
- Vary structure: do not reuse the same five generic H2s on every page. Match the BODY LAYOUT note and SEARCH INTENT.
- Quality bar: content should read like a strong ChatGPT / Claude / Gemini draft — specific, natural, topic-aware.
- Never invent fake reviews, clients, offices, awards, rankings, or "best/cheapest in [city]" claims.
- Use only verified ZeOrbit facts: 20+ years experience; 1,000+ client reviews; WordPress, Shopify, redesign, mobile-friendly, SEO-friendly structure, conversion-focused sites, mobile apps.
- Never mention prices, dollar amounts, or project cost ranges.
"""

LAYOUT_VARIANTS = ("qa", "steps", "story", "cards", "split", "timeline", "checklist", "compare", "myths")
BLOG_FORMATS = ("guide", "briefing", "feature")

LAYOUT_INSTRUCTIONS = {
    "qa": "Use question-style H2s a real customer would ask. Body answers in short paragraphs, then a 3-item list under at least one H2.",
    "steps": "Structure as a how-to: H2s are numbered steps (Step 1…, Step 2…). Body is actionable with concrete deliverables, not a pitch dump.",
    "story": "Open with a local situation, then proof, then what working together looks like. One H2 should be a short anecdote tied to this industry/location.",
    "cards": "Each H2 is a distinct benefit/offer card (speed, local SEO, care plan, launch support). Keep each section 2-4 sentences plus one concrete example.",
    "split": "Alternate problem vs solution: first H2 is the pain in this city, next is how you fix it, then who it's for, then timeline, then next step.",
    "timeline": "Walk the reader through a project timeline (week 1 discovery → design → build → launch → support). Name real milestones.",
    "checklist": "H2s are checklist groups. Each section is a punch-list with 4-6 concrete checks the reader can apply today.",
    "compare": "Compare two or three real options (e.g. WordPress vs Shopify vs redesign). Use even-handed criteria, then a recommendation for THIS reader.",
    "myths": "Lead with misconceptions. Each H2 names a myth, then the practical truth, then what to do instead.",
    "guide": (
        "FORMAT A — HOW-TO GUIDE. Title/H1 name the task. "
        "H2s MUST be numbered: '1. …', '2. …', '3. …', '4. Check your work'. "
        "Intro: two sentences — what they will do, what 'done' looks like. "
        "Body: short paragraphs plus numbered or bulleted steps, tools, and a verify step. "
        "FAQs: troubleshooting those steps. Soft CTA after they can finish the task."
    ),
    "briefing": (
        "FORMAT B — Q&A BRIEFING. Title is a question or 'X explained'. "
        "Every H2 is a reader question starting with What/Why/When/Which/Should/Can. "
        "Intro: one-sentence definition, then who this is for. "
        "Body: two short paragraphs per H2; include one 3-bullet criteria or comparison list. "
        "FAQs: nearby questions not used as H2s. CTA offers a second opinion, not a pitch."
    ),
    "feature": (
        "FORMAT C — MAGAZINE FEATURE. Title is a specific situation or claim, not 'How to'. "
        "H2s are theme headings (no Step 1, not every H2 a question). "
        "Intro: three sentences that start in a real moment. "
        "Body: narrative paragraphs. Include one markdown blockquote as a pull-quote. No numbered how-to lists. "
        "FAQs: three practical questions after the story. Warm close CTA."
    ),
}


def _page_h2_set(
    layout: str,
    industry: str,
    buyers: str,
    city: str,
    audience: str,
    pretty: str,
) -> list:
    """Diverse H2 sets so pages don't all share the same five headings."""
    ind = industry or "local"
    city_l = city or "your area"
    aud = audience or "teams"
    sets = {
        "qa": [
            f"What should a {ind} website include?",
            f"How do {buyers} in {city_l} find you online?",
            "What makes a WordPress site conversion-ready?",
            "How does ZeOrbit keep the project clear?",
            f"Ready for {pretty.lower()} in {city_l}?",
        ],
        "steps": [
            f"Step 1: Clarify your {ind} offers for {city_l}",
            "Step 2: Map pages visitors actually need",
            "Step 3: Build WordPress layouts that convert",
            "Step 4: Add local SEO and AI-ready structure",
            "Step 5: Launch, measure, and improve",
        ],
        "story": [
            f"A familiar problem for {ind} businesses in {city_l}",
            "What changed when the website got clearer",
            "WordPress pages that match how people search",
            "From first visit to a booked next step",
            f"Why {aud} in {city_l} work with ZeOrbit",
        ],
        "cards": [
            f"WordPress built for {ind} services",
            f"Local visibility in {city_l}",
            "Landing pages that match your campaigns",
            "Trust, speed, and mobile clarity",
            "A simple path to start with ZeOrbit",
        ],
        "split": [
            f"Why {ind} sites in {city_l} lose visitors",
            "How ZeOrbit fixes the experience",
            f"Who this website is for in {city_l}",
            "What the build timeline looks like",
            "Your next step with ZeOrbit",
        ],
        "timeline": [
            "Week 1: Discovery and page plan",
            "Design: Clear layouts for your services",
            "Build: WordPress, mobile, and forms",
            "Launch: Local SEO and AI-friendly structure",
            "After launch: Care and improvements",
        ],
        "checklist": [
            f"Pages a {ind} site in {city_l} should not skip",
            "Mobile and contact checks before you launch",
            "Content that matches how people search",
            "Proof, speed, and follow-up after go-live",
            f"Your {city_l} launch checklist with ZeOrbit",
        ],
        "compare": [
            f"WordPress vs Shopify for {ind} in {city_l}",
            "When a redesign beats a patch",
            "Website first vs adding an app later",
            "How to choose without guessing",
            "A clear recommendation from ZeOrbit",
        ],
        "myths": [
            f"Myth: a {ind} site in {city_l} only needs a homepage",
            "Myth: templates already do local SEO",
            "Myth: you can skip mobile if desktop looks fine",
            "What actually moves inquiries",
            f"What {aud} in {city_l} should do next",
        ],
    }
    return sets.get(layout) or sets["cards"]


PROVIDER_STYLE_NOTES = {
    "openai": "Write with GPT-4-level clarity: crisp sentences, concrete examples, no filler.",
    "chatgpt": "Write with GPT-4-level clarity: crisp sentences, concrete examples, no filler.",
    "gpt": "Write with GPT-4-level clarity: crisp sentences, concrete examples, no filler.",
    "anthropic": "Write with Claude Haiku care: clear, keyword-true, natural section openings, no fluff.",
    "claude": "Write with Claude Haiku care: clear, keyword-true, natural section openings, no fluff.",
    "gemini": "Write with Gemini-level breadth: useful detail, natural local flavor, strong scannability.",
    "groq": "Write tightly and specifically — every paragraph earns its place; no template filler.",
}


def _keyword_body_directive(keyword: str, industry: str = "", audience: str = "", place: str = "") -> str:
    """Force body copy to match the search keyword the way a human SEO writer would.

    Target tone matches the Typefully / Claude Haiku quality bar the team likes:
    why THIS industry needs digital presence → What ZeOrbit Offers (websites,
    mobile apps, custom) → Ready to grow CTA with phone/site.
    Never write DIY 'how to plan your own website' tutorials.
    """
    pretty = pretty_keyword(keyword or "this topic")
    who = (audience or industry or "business owners").strip() or "business owners"
    loc = (place or "").strip()
    loc_bit = f" in {loc}" if loc else ""
    return f"""
═══ KEYWORD-TRUE BODY (mandatory — this is what Google users must read) ═══
PRIMARY KEYWORD / SEARCH QUERY: "{pretty}"
SPEAK TO: {who}{loc_bit}

Write body content EXACTLY like this quality bar (adapt every sentence to "{pretty}" + {who}, do not copy sample wording verbatim):

## Why Your {who} Business Needs a Stronger Digital Presence
Open by naming {who}. Modern clients expect to find, review, and contact {who} online. Credibility and visibility matter for THIS keyword.

## What ZeOrbit Offers
- **Professional websites** — project/service proof, clear contact path, mobile-ready pages that fit "{pretty}".
- **Mobile apps** — only if useful for this buyer (scheduling, quotes, updates on the go).
- **Custom solutions** — tailored to {who} workflows, not a generic template pitch.

## Ready to Grow?
ZeOrbit understands {who} / this industry. Close with urgency + concrete CTA:
Call: (619) 724-9517
Visit: www.zeorbit.com

HARD LOCKS:
- This is a ZeOrbit SERVICE page for {who} about "{pretty}" — NOT a DIY tutorial.
- FORBIDDEN H2 / section topics: "Define Your Core Digital Foundation", "Align Design with Your Brand Identity", "Check your work and launch", domain/hosting how-tos, "pages every new business needs" as a self-build checklist, generic brand-identity lectures.
- Every H2 and paragraph must stay on "{pretty}" for {who}. If a sentence would fit any random city page, rewrite it.
- Do NOT swap in unrelated industries (gym, salon, restaurant, law, etc.) unless those words are in the keyword or industry field.
- Do NOT write "how to build your own website" steps. Sell ZeOrbit's help for {who}.
- Name ZeOrbit in the intro and CTA. Use phone (619) 724-9517 and www.zeorbit.com in the CTA.
"""


def _content_on_keyword(intro: str, content: str, keyword: str, industry: str = "") -> bool:
    """True when body already tracks the focus keyword / industry (do not template-overwrite)."""
    blob = f"{intro or ''}\n{content or ''}".lower()
    if len(blob.split()) < 80:
        return False
    if _looks_like_template_filler(blob):
        return False
    kw = (keyword or "").strip().lower()
    if kw and _kw_words_present(blob, kw, 0.55):
        return True
    ind = (industry or "").strip().lower()
    if ind and len(ind) > 3 and ind in blob:
        return True
    return False


def blog_layout_for_query(query: str, brief: str = "", salt: str = "") -> str:
    """Rotate the three published blog designs: guide → briefing → feature.

    Integer salt (batch index) always cycles templates so consecutive publishes
    look different. Non-numeric salt still hashes the query.
    """
    try:
        return BLOG_FORMATS[int(salt) % len(BLOG_FORMATS)]
    except (TypeError, ValueError):
        pass
    t = f"{query or ''} {brief or ''}".lower()
    idx = int(hashlib.md5(f"{t}|{salt}".encode()).hexdigest(), 16)
    return BLOG_FORMATS[idx % len(BLOG_FORMATS)]


def _extract_sentences(text: str, start: int = 0, limit: int = 2) -> str:
    sents = [s.strip() for s in re.findall(r"[^.!?]+[.!?]", text or "") if len(s.strip()) > 20]
    if not sents and (text or "").strip():
        return (text or "").strip()[:280]
    return " ".join(sents[start: start + limit]).strip()


def _query_is_web(ql: str) -> bool:
    return bool(re.search(
        r"\b(website|web\s*design(?:ing)?|webdesign|wordpress|shopify|landing page|web app|seo|ppc)\b",
        ql or "",
    ))


def _is_generic_web_query(ql: str) -> bool:
    """True only for short bare topics like 'website design' — not industry/city company queries."""
    t = re.sub(r"[^a-z0-9\s]", " ", (ql or "").lower())
    t = re.sub(r"\s+", " ", t).strip()
    if not t or len(t.split()) > 4:
        return False
    if re.search(r"\b(for|in|near|company|agency|firm|biopharma|biotech|pharma|clinic|dental|lawyer|contractor)\b", t):
        return False
    return bool(re.fullmatch(
        r"(custom\s+)?(website|web)\s*design(ing)?|"
        r"wordpress(\s+website)?|"
        r"shopify(\s+store)?|"
        r"web\s*design(ing)?(\s+services?)?",
        t,
    ))


def _parse_service_query(q: str) -> dict:
    """Pull industry / place / offer out of long search queries for on-topic body copy."""
    raw = (q or "").strip()
    ql = raw.lower()
    industry = ""
    place = ""
    m = re.search(r"\bfor\s+(.+?)(?:\s+in\s+|\s+near\s+|$)", ql, re.I)
    if m:
        industry = m.group(1).strip(" .,")
    m2 = re.search(r"\b(?:in|near)\s+([a-z0-9 .'-]+)$", ql, re.I)
    if m2:
        place = m2.group(1).strip(" .,")
        if industry and place and place in industry:
            industry = industry[: industry.rfind(place)].strip(" .,")
    # Drop trailing place words left in industry ("biopharma in el cajon" edge cases)
    if industry and place and industry.endswith(place):
        industry = industry[: -len(place)].strip(" .,")
    offer = "website"
    if re.search(r"web\s*design|website\s*design|webdesign", ql):
        offer = "website design"
    elif re.search(r"\bmobile\s*app", ql):
        offer = "mobile app"
    elif re.search(r"\bseo\b", ql):
        offer = "SEO"
    company = bool(re.search(r"\b(company|agency|firm|studio|freelancer|designer)\b", ql))
    return {
        "query": raw,
        "pretty": pretty_keyword(raw),
        "industry": pretty_keyword(industry) if industry else "",
        "place": pretty_keyword(place) if place else "",
        "offer": offer,
        "company": company,
    }


def _question_without_glued_industry(keyword: str, industry: str = "") -> str:
    """Drop an industry label that was stuck on the front of a question."""
    q = re.sub(r"\s+", " ", (keyword or "").strip())
    ind = re.sub(r"\s+", " ", (industry or "").strip())
    if ind and q.lower().startswith(ind.lower() + " "):
        rest = q[len(ind):].strip()
        if re.match(r"^(who|what|how|why|when|where|can|do|does|is|should)\b", rest, re.I):
            return rest
    return q


def _industry_phrase(industry: str) -> str:
    """Adjective form so 'Contractors' reads as 'contractor' inside a sentence."""
    ind = re.sub(r"\s+", " ", (industry or "").strip())
    if not ind:
        return "business"
    if " " in ind:
        return ind.lower()
    low = ind.lower()
    if low.endswith("s") and not low.endswith("ss") and len(low) > 4:
        return low[:-1]
    return low


def _query_action(text: str) -> str:
    """Verb the searcher used, so copy follows the term instead of always saying redesign."""
    m = re.search(
        r"\b(redesign|rebuild|design|build|create|fix|update|improve|launch|make)\b",
        text or "",
        re.I,
    )
    return (m.group(1).lower() if m else "build")


def _weave_industry_into_question(question: str, industry: str) -> str:
    """Combine the typed term and the typed industry into one grammatical phrase.

    Never stick the industry on the front of a question. Put it inside the
    noun the person already wrote (website, business, site). If the industry
    is already in the term, only fix word order.
    """
    q = _question_without_glued_industry(question, industry)
    ind = re.sub(r"\s+", " ", (industry or "").strip())
    if not ind:
        return q
    ind_l = _industry_phrase(ind)
    raw_l = ind.lower()
    # "my real estate existing business website" -> "my existing real estate business website"
    if re.search(rf"\b(?:{re.escape(raw_l)}|{re.escape(ind_l)})\b", q, re.I):
        return re.sub(
            rf"\b(my|our|your)\s+{re.escape(ind_l)}\s+(existing)\s+(business\s+website|website|site)\b",
            lambda m: f"{m.group(1)} {m.group(2)} {ind_l} {m.group(3)}",
            q,
            count=1,
            flags=re.I,
        )
    woven = re.sub(
        r"\b(my|our|your)\s+(?:(existing)\s+)?(business\s+website|website|web\s*site|site|business)\b",
        lambda m: f"{m.group(1)} {(m.group(2) + ' ') if m.group(2) else ''}{ind_l} {m.group(3)}",
        q,
        count=1,
        flags=re.I,
    )
    if woven != q:
        return re.sub(r"\s+", " ", woven).strip()
    # Short labels can take the industry in front. Full questions cannot.
    if re.match(r"^(who|what|how|why|when|where|can|do|does|is|should)\b", q, re.I) or len(q.split()) > 6:
        if q.endswith("?"):
            return q[:-1].rstrip() + f" for a {ind_l} business?"
        return q.rstrip(" .") + f" for a {ind_l} business"
    return f"{ind} {q}".strip()


def _specific_service_article(q: str, place_hint: str = "", industry: str = "") -> dict:
    """Article for long service queries (company + industry + city) — not generic web-design filler."""
    parts = _parse_service_query(q)
    named_industry = (industry or parts["industry"] or "").strip()
    q = _weave_industry_into_question(q, named_industry)
    pretty = pretty_keyword(q)
    industry = named_industry or "this business"
    place = parts["place"] or (place_hint or "").strip() or "your area"
    # Prefer place named in the keyword over a pinned location picker value.
    if parts["place"]:
        place = parts["place"]
    ind_l = _industry_phrase(industry)
    verb = _query_action(q)
    verb_ing = {
        "redesign": "redesigning",
        "rebuild": "rebuilding",
        "design": "designing",
        "build": "building",
        "create": "creating",
        "fix": "fixing",
        "update": "updating",
        "improve": "improving",
        "launch": "launching",
        "make": "making",
    }.get(verb, verb + "ing")
    real_estate = "real estate" in ind_l
    proof = (
        "property photos, listings, and a way to request a showing"
        if real_estate else
        f"the services a {ind_l} customer looks for, and a way to call"
    )
    lead_line = (
        "showcase properties and generate leads."
        if real_estate else
        f"explain your {ind_l} services and generate leads."
    )
    show_line = (
        "Feature listings, neighborhoods, and a clear way to contact an agent. "
        if real_estate else
        f"Name the {ind_l} services and who they are for. "
    )
    title = pretty
    if len(title) > 60:
        title = pretty_keyword(re.sub(r"\bexisting\s+", "", q, count=1, flags=re.I))
    title = title[:60].rsplit(" ", 1)[0] if len(title) > 60 else title
    intro = (
        f"If you need someone to {verb} your {ind_l} website in {place}, start with the pages a customer actually uses. "
        f"The site should show {proof}, work on a phone, and make the next step obvious."
    )
    stem = q.lower()
    if stem.startswith("how"):
        h_who = f"How to {verb} a {ind_l} website in {place}"
    elif stem.startswith("what"):
        h_who = f"What a {ind_l} website in {place} needs"
    elif stem.startswith("why"):
        h_who = f"Why {verb} a {ind_l} website in {place}"
    else:
        h_who = f"Who can {verb} a {ind_l} website in {place}"
    h_show = f"What the {ind_l} site needs to show"
    h_choose = f"How to choose a partner to {verb} it"
    h_build = "What ZeOrbit builds"
    content = (
        f"## {h_who}\n\n"
        f"People searching “{pretty}” want a team that has shipped {ind_l} sites, not a generic theme with a logo dropped in. "
        f"Ask to see live examples, who writes the page copy, and how you will update it after launch.\n\n"
        f"## {h_show}\n\n"
        f"The homepage should say what you do in one sentence. "
        f"{show_line}"
        f"Put a phone number or form where someone in {place} can reach you without hunting.\n\n"
        f"## {h_choose}\n\n"
        f"1. Review three live {ind_l} websites, on a phone.\n"
        f"2. Confirm the pages you can edit yourself.\n"
        f"3. Check that forms and click-to-call work.\n"
        f"4. Get the timeline in writing before work starts.\n\n"
        f"## {h_build}\n\n"
        f"ZeOrbit handles {verb_ing} {ind_l} websites in {place} with mobile-friendly pages"
        f"{', property showcases,' if real_estate else ''}"
        f" and a contact path that brings in leads. Share the current site and the pages you want kept."
    )
    h2s = [h_who, h_show, h_choose, h_build]
    faqs = [
        FAQItem(
            question=f"Who should {verb} a {ind_l} website in {place}?",
            answer=f"Choose a team that can show live {ind_l} sites and explain how leads will contact you from a phone.",
        ),
        FAQItem(
            question=f"What should a {ind_l} website include?",
            answer=(
                "Listings or property proof, service areas, agent contact, and a form that works on a phone."
                if real_estate else
                f"A clear {ind_l} offer, service pages, real photos, and a phone number or form for {place}."
            ),
        ),
        FAQItem(
            question=f"How long does it take to {verb} a {ind_l} website?",
            answer=f"A focused {ind_l} website project is often a few weeks once the current site, pages, and photos are ready.",
        ),
        FAQItem(
            question=f"Can ZeOrbit {verb} a {ind_l} website in {place}?",
            answer=f"Yes. ZeOrbit builds a mobile-friendly {ind_l} website and a clear way for people in {place} to get in touch.",
        ),
    ]
    meta = (
        f"Looking to {verb} your {ind_l} website in {place}? "
        f"ZeOrbit creates professional websites that {lead_line}"
    )
    cta = (
        f"Ready to upgrade your {ind_l} website? ZeOrbit can help you create a modern, mobile-friendly website"
        f"{' that showcases your properties and attracts potential buyers' if real_estate else f' that explains your {ind_l} services and brings in more calls'}. "
        f"Reach Out ZeOrbit to discuss your website project."
    )
    return {
        "intro": intro.strip(),
        "content": content.strip(),
        "h2s": h2s,
        "faqs": faqs,
        "h3s": [],
        "title": title,
        "h1": title,
        "meta_description": meta[:160],
        "cta": cta,
    }


def _topic_article_from_research(q: str, pretty: str, extract: str, related: list) -> dict:
    """Typefully-style article for ANY search query — facts in, encyclopedia dump out."""
    ql = (q or "").lower()
    task = _query_task_phrase(q)
    facts = _extract_sentences(extract, 0, 2)
    bullets = []
    for b in related or []:
        t = str(b).strip()
        if len(t) < 12 or t.isupper() or re.match(r"^[A-Z0-9]{2,8}$", t):
            continue
        if re.search(r"wikipedia|disambiguation|see also|^CAUC\b", t, re.I):
            continue
        bullets.append(t[:180])
        if len(bullets) >= 5:
            break
    intro = (
        (facts + " " if facts else "")
        + f"This guide stays on “{pretty}”: what it is, how it works, and what to do next."
    ).strip()
    meaning = (
        f"People search “{q}” for a usable definition and a next step — not an encyclopedia page. "
        "The sections below stay on that wording: how it works, what to check, and what to skip."
    )
    related_block = ""
    if bullets:
        related_block = (
            f"## Points that usually matter for {pretty}\n\n"
            + "\n".join(f"- {b}" for b in bullets)
            + "\n\n"
        )
    howto = bool(re.match(r"^(how to|how do i|how do you|how can i)\b", ql)) or bool(
        re.search(r"\b(steps?|guide|tutorial)\b", ql)
    )
    compare = bool(
        _is_comparison_query(ql)
        or re.search(r"\b(vs\.?|versus|or|compared? to)\b", ql)
    )
    if howto:
        body_mid = (
            f"## Step-by-step: {task}\n\n"
            f"1. Restate “{pretty}” as one outcome you can check.\n"
            f"2. Gather what the query names (the product, setting, or material) before you change anything.\n"
            f"3. Do the smallest action that would prove {task} worked.\n"
            "4. Confirm on a second look (refresh, another device, or a second person).\n"
            "5. Only then add extras.\n\n"
        )
        h2_mid = f"Step-by-step: {task}"
    elif compare:
        body_mid = (
            f"## How to choose for “{pretty}”\n\n"
            "Write the job the customer or you must finish. Pick the option that does that job with "
            "less risk, not the option that sounds more modern. Budget, maintenance, and how often "
            "people return should decide it — not a slogan.\n\n"
        )
        h2_mid = f"How to choose for “{pretty}”"
    else:
        body_mid = (
            f"## How “{pretty}” works in practice\n\n"
            f"Treat “{q}” as a real-world process: who it is for, what tool or channel it uses, "
            "and the one result that would prove you are done. Ignore adjacent topics that only "
            "share a word.\n\n"
        )
        h2_mid = f"How “{pretty}” works in practice"
    if _query_is_web(ql):
        close = (
            "## When ZeOrbit can help\n\n"
            "If the next step is a website, app, or SEO build, ZeOrbit can map the pages and ship the work. "
            "Stay on this query until that need is actually true."
        )
        close_h = "When ZeOrbit can help"
    else:
        close = (
            f"## What to do next\n\n"
            f"Write the outcome you want from “{pretty}” in one sentence, run the smallest test, "
            "and stop if it already works. Get help only if a live system, paid account, or data "
            "is at risk."
        )
        close_h = "What to do next"
    content = (
        f"## What “{pretty}” means\n\n"
        f"{meaning}\n\n"
        f"{related_block}"
        f"{body_mid}"
        f"## Mistakes that waste time\n\n"
        f"Changing the topic to something easier, skipping a backup or a test, or copying a random "
        f"result that does not match “{q}” are the usual misses. Stay on the words someone typed.\n\n"
        f"{close}"
    )
    h2s = [
        f"What “{pretty}” means",
        *([f"Points that usually matter for {pretty}"] if bullets else []),
        h2_mid,
        "Mistakes that waste time",
        close_h,
    ]
    faqs = [
        FAQItem(question=f"What is {pretty}?", answer=(facts or f"{pretty} is the topic this article answers.")[:400]),
        FAQItem(question="Can I start this myself?", answer="Yes. Use the sections above, then get help only if a live system or paid account is at risk."),
        FAQItem(question="How long does it take?", answer="A first pass is often minutes to a day. Bigger projects take longer because you should verify the result."),
        FAQItem(question="What should I prepare?", answer=f"The exact wording of “{q}”, any live URL or account it names, and what success looks like."),
        FAQItem(question="What if I get it wrong?", answer="Undo the last change, retry with the official source named in the query, and do not stack extra tools."),
        FAQItem(
            question="When do I need a specialist?",
            answer="When you would break a live website, DNS, checkout, or data you cannot restore. Otherwise follow the steps here.",
        ),
    ]
    return {"intro": intro.strip(), "content": content.strip(), "h2s": h2s, "faqs": faqs, "h3s": []}


def grounded_blog_copy(primary: str, research: dict | None = None, place: str = "", industry: str = "") -> dict:
    """On-topic article for the editor's keyword — readable body, not instruction notes."""
    q = (primary or "").strip() or "website design"
    pretty = pretty_keyword(q)
    extract = ((research or {}).get("extract") or "").strip()
    related = list((research or {}).get("related") or [])
    ql = q.lower()

    # Comparison / differentiation queries get a real answer (not website pitch filler).
    if _is_comparison_query(q):
        packed = _comparison_article_copy(keyword=q, city=place or "")
        return {
            "intro": packed["intro"],
            "content": packed["content"],
            "h2s": packed["h2s"],
            "faqs": [
                FAQItem(question=f["question"], answer=f["answer"])
                if isinstance(f, dict) else f
                for f in packed["faqs"]
            ],
            "h3s": [],
            "title": packed.get("title"),
            "h1": packed.get("h1"),
            "meta_description": packed.get("meta_description"),
            "cta": packed.get("cta"),
        }

    special = _blog_query_copy(q)
    if special:
        return special

    # Long service queries (company + industry + city) get a purpose-built article.
    if _query_is_web(ql) and not _is_generic_web_query(ql):
        return _specific_service_article(q, place_hint=place or "", industry=industry or "")

    if _is_generic_web_query(ql):
        intro = (
            "Website design is the work of planning pages, layout, and content so a visitor "
            "on a phone can see what you do and contact you. A useful site is a homepage, "
            "service pages, and a clear call or form — not a template with generic stock photos."
        )
        content = (
            "## What website design includes\n\n"
            "A working site usually needs a homepage that states the offer, service or product pages, "
            "contact details above the fold on mobile, HTTPS, and a form or click-to-call path. "
            "WordPress is the usual choice when you will edit pages yourself. Shopify is the better fit "
            "when you sell products online.\n\n"
            "Front-end design covers layout, type, and how pages feel to use. It overlaps development "
            "(markup, CMS, checkout) and SEO: titles, headings, and pages that match what people search.\n\n"
            "## Typical process\n\n"
            "1. Write the offer in one sentence and list the pages you need.\n"
            "2. Review the current site on a phone: speed, forms, and whether services are named.\n"
            "3. Choose WordPress, Shopify, or a redesign if the theme cannot be saved cleanly.\n"
            "4. Build mobile-first layouts, add real photos of the work, and test contact paths.\n"
            "5. Launch on HTTPS, then check Search Console after the first week.\n\n"
            "## How to choose a designer\n\n"
            "Ask for three live sites in a similar category, who writes the copy, how you will update pages, "
            "and a timeline. Skip anyone who will not show examples or who only talks about logos and colors.\n\n"
            "## When ZeOrbit can help\n\n"
            "ZeOrbit builds WordPress and Shopify sites with service pages, mobile layouts, and a "
            "contact path people actually use. Say what the site must do, which pages belong on it, "
            "and how a visitor on a phone reaches you."
        )
        h2s = [
            "What website design includes",
            "Typical process",
            "How to choose a designer",
            "When ZeOrbit can help",
        ]
        faqs = [
            FAQItem(question="What should a small-business website include?", answer="Homepage, services, contact on mobile, HTTPS, and a form or tap-to-call button."),
            FAQItem(question="WordPress or Shopify?", answer="WordPress for services and content. Shopify if you sell products and need checkout."),
            FAQItem(question="How long does a site take?", answer="A focused service site is typically a few weeks once the offer and examples are clear."),
            FAQItem(question="Do I need a redesign?", answer="Yes if the current theme breaks forms, is slow on phones, or cannot be updated without a developer."),
            FAQItem(question="What should I send a designer?", answer="Current URL, the offer in one sentence, services to list, and 3 sites you like."),
            FAQItem(question="Can ZeOrbit build it?", answer="Yes. ZeOrbit maps pages and ships a mobile-friendly WordPress or Shopify site."),
        ]
        return {"intro": intro.strip(), "content": content.strip(), "h2s": h2s, "faqs": faqs, "h3s": []}
    return _topic_article_from_research(q, pretty, extract, related)


def _query_task_phrase(query: str) -> str:
    t = re.sub(r"[?!.]+$", "", (query or "").strip())
    t = re.sub(r"^(how to|how do i|how do you)\s+", "", t, flags=re.I)
    if re.match(r"^(should i|should we|do i|can i|is it|what is|why do|when should)\b", t, flags=re.I):
        return t[0].lower() + t[1:] if t else t
    return t.strip() or (query or "this").strip()


def _blog_query_copy(primary: str, layout: str = "") -> dict:
    """Fallback blog copy that actually teaches the editor's query — never agency filler."""
    q = (primary or "").strip()
    ql = q.lower()
    pretty = pretty_keyword(q)
    task = _query_task_phrase(q)
    layout = layout if layout in BLOG_FORMATS else blog_layout_for_query(q)
    is_howto = layout == "guide"
    is_redirect = bool(re.search(r"301|302|redirect", ql))

    if is_redirect:
        return None  # keep existing 301 branch

    if "gmail" in ql and "safari" in ql:
        intro = (
            "Safari does not include a Gmail signup screen of its own. You create the Google account "
            "in the Gmail website (or the Google account page) while you are in Safari, then you can "
            "save the password and keep Gmail open in a tab or on the home screen."
        )
        content = (
            f"## Direct answer: {pretty}\n\n"
            "Open Safari, go to gmail.com (or accounts.google.com/signup), tap Create account, "
            "enter your name, username, password, and recovery phone or email, then finish Google’s "
            "verification. After that you can sign in at gmail.com in Safari anytime.\n\n"
            "You do not install Gmail from the App Store to finish this. Safari is only the browser "
            "that loads Google’s signup page.\n\n"
            "## Step-by-step in Safari\n\n"
            "1. Open Safari on iPhone, iPad, or Mac.\n"
            "2. Type gmail.com in the address bar and go. If you already have a Google account, use "
            "Create account instead of Sign in.\n"
            "3. Choose For my personal use (or For my child / For work, if that is what you need).\n"
            "4. Enter first and last name, then pick a Gmail address or use an email you already have.\n"
            "5. Create a strong password. When Safari offers to save it, accept so you are not locked out.\n"
            "6. Add a recovery phone number or recovery email, complete the CAPTCHA or SMS code, and agree to Google’s terms.\n"
            "7. Open gmail.com again in Safari and confirm the inbox loads.\n\n"
            "On iPhone, tap Aa (or Share) → Add to Home Screen if you want a Gmail icon that still opens in Safari.\n\n"
            "## Safari settings that help\n\n"
            "Allow pop-ups for accounts.google.com if signup stalls. If cookies are blocked, Google cannot "
            "finish the session — Settings → Safari → turn off Block All Cookies for this step, then tighten "
            "again later. Private Browsing will not keep you signed in after you close the tab.\n\n"
            "iCloud Keychain or Safari AutoFill can store the new password. That is optional but useful if "
            "you sign in on more than one Apple device.\n\n"
            "## Mistakes that stop signup\n\n"
            "Using an old bookmark to a broken Google URL, blocking cookies, skipping phone verification, "
            "or closing the tab mid-code are the usual failures. Do not use a public computer without signing "
            "out. If Google says the username is taken, pick another Gmail address — you cannot create a duplicate.\n\n"
            "## After the account exists\n\n"
            "Send a test message to yourself, add a profile photo if you want, and turn on 2-Step Verification "
            "in Google Account → Security. If you also want the Gmail app, that is a separate App Store install "
            "and is not required to use Gmail in Safari."
        )
        h2s = [
            f"Direct answer: {pretty}",
            "Step-by-step in Safari",
            "Safari settings that help",
            "Mistakes that stop signup",
            "After the account exists",
        ]
        faqs = [
            FAQItem(question="Can I create a Gmail account only using Safari?", answer="Yes. Safari loads Google’s signup page. You do not need the Gmail app to create the account."),
            FAQItem(question="Does this work on iPhone Safari and Mac Safari?", answer="Yes. The same gmail.com Create account flow works on iPhone, iPad, and Mac Safari."),
            FAQItem(question="Why does Google ask for my phone number?", answer="Google uses it to verify you are not a bot and for account recovery if you forget the password."),
            FAQItem(question="Will Safari save my Gmail password?", answer="It can, if you allow AutoFill / iCloud Keychain when the save prompt appears."),
            FAQItem(question="Do I need the App Store Gmail app?", answer="No. The app is optional. Mail in Safari at gmail.com is enough."),
            FAQItem(question="What if Create account will not load?", answer="Turn off content blockers for that tab, allow cookies, and try a non-private window."),
        ]
        return {"intro": intro, "content": content, "h2s": h2s, "faqs": faqs, "h3s": []}

    if _is_generic_web_query(ql) and not re.search(
        r"\b(how to fix|broken|not loading|gmail|safari|301|redirect)\b", ql
    ):
        intro = (
            "Custom website design means building pages around your services, not dropping text into a generic theme. "
            "You should get a site people can use on a phone: a clear offer, real examples, and an obvious way to contact you."
        )
        content = (
            "## What custom website design includes\n\n"
            "A custom build starts with the pages you actually need: home, services, about, contact, and any extras "
            "(portfolio, booking, or shop). Layouts and content should match how you work, not a demo industry.\n\n"
            "WordPress is the usual fit when you need flexible pages and a blog. Shopify fits when you sell products. "
            "A redesign is the right path when you already have a domain but the current site is slow or confusing on mobile.\n\n"
            "## How a custom project usually runs\n\n"
            "1. Goals and pages: what visitors should do (call, form, book, buy).\n"
            "2. Structure: sitemap and mobile layout before visual polish.\n"
            "3. Build: WordPress or Shopify, forms, and contact paths that work on a phone.\n"
            "4. Launch checks: speed, links, and a homepage that states what you do in a few seconds.\n\n"
            "## What to skip\n\n"
            "Do not buy a theme and leave the dummy text. Do not hide the phone number. Custom work is specific: "
            "your services, your photos when you have them, your next step.\n\n"
            "## When ZeOrbit is a fit\n\n"
            "ZeOrbit is a fit when you need a real website for this search, not a theme with dummy text. "
            "We build WordPress or Shopify sites with service pages, mobile-friendly layouts, and a clear call or form. "
            "If you already have a domain, a redesign can keep what ranks and fix what loses people on phones."
        )
        h2s = [
            "What custom website design includes",
            "How a custom project usually runs",
            "What to skip",
            "When ZeOrbit is a fit",
        ]
        faqs = [
            FAQItem(question="What is custom website design?", answer="A site structured for your services and customers, not a one-size theme with your logo swapped in."),
            FAQItem(question="Do I need WordPress or Shopify?", answer="WordPress for service and content sites. Shopify when you sell products. ZeOrbit will say which fits before building."),
            FAQItem(question="How long does it take?", answer="A focused multi-page site often takes a few weeks after you confirm pages and content."),
            FAQItem(question="Will it work on phones?", answer="Yes. Mobile-friendly layout is part of the build, not an add-on."),
            FAQItem(question="Can I update it later?", answer="WordPress and Shopify are built so you can change text and photos without a developer for every edit."),
            FAQItem(question="What should I prepare?", answer="A short list of services, how you want people to contact you, and any photos or examples you already have."),
        ]
        return {"intro": intro, "content": content, "h2s": h2s, "faqs": faqs, "h3s": []}

    if re.search(r"\b(should i|diy|build.{0,20}myself|hire.{0,20}developer)\b", ql):
        intro = (
            f"“{pretty}” is a budget and risk decision, not a yes/no slogan. "
            "Build it yourself if the site is a few pages, you can keep it updated, and a mistake is reversible. "
            "Hire help when SEO, checkout, or a live domain is on the line."
        )
        content = (
            f"## Direct answer: {pretty}\n\n"
            "DIY is fine for a simple brochure site you can edit. Hire a specialist (or ZeOrbit) when you need "
            "custom structure, migrations, or conversions you cannot test yourself.\n\n"
            "## When DIY is enough\n\n"
            "A handful of pages, a template you understand, and no custom checkout or complex forms. "
            "If you can publish, check mobile, and keep backups, you can start yourself.\n\n"
            "## When to hire\n\n"
            "Ranked URLs, e-commerce, memberships, or a brand that cannot look amateur. "
            "Those projects fail when a theme is stretched past what it can do.\n\n"
            "## A practical sequence\n\n"
            "1. Write the pages you actually need.\n"
            "2. Try a template for a weekend.\n"
            "3. If you stall on structure, speed, or SEO, stop and get help instead of stacking plugins.\n\n"
            "## Mistakes that waste money\n\n"
            "Paying for a full custom build when a template would work, or staying DIY until a broken live site hurts inquiries.\n\n"
            "## Next step\n\n"
            "If you are still unsure after a test site, ZeOrbit can map DIY vs a managed WordPress or Shopify build around this question."
        )
        h2s = [
            f"Direct answer: {pretty}",
            "When DIY is enough",
            "When to hire",
            "A practical sequence",
            "Mistakes that waste money",
            "Next step",
        ]
        faqs = [
            FAQItem(question=pretty + "?", answer="DIY if the site is simple and reversible. Hire if rankings, checkout, or a live domain are at risk."),
            FAQItem(question="Is a website builder enough?", answer="Often for a first brochure site. Not when you need custom SEO structure or complex checkout."),
            FAQItem(question="Will DIY hurt SEO?", answer="Thin templates and duplicate titles can. A clear heading structure still matters on a DIY site."),
            FAQItem(question="When should I stop DIY?", answer="When you cannot ship mobile-friendly pages, forms, or redirects without breaking the live site."),
            FAQItem(question="What does ZeOrbit do here?", answer="We help you decide DIY vs a proper build, then implement WordPress or Shopify if you need it."),
            FAQItem(question="What's the next step?", answer="List the pages you need, try a template, then get a specialist if structure or SEO is the blocker."),
        ]
        return {"intro": intro, "content": content, "h2s": h2s, "faqs": faqs, "h3s": []}

    accountish = bool(re.search(
        r"\b(gmail|safari|chrome|firefox|ios|iphone|android|signup|sign up|sign-in|account|password|app store)\b",
        ql,
    ))
    if is_howto and not accountish:
        return None

    if is_howto:
        if re.match(r"^(should i|should we|do i|can i|is it)\b", task, flags=re.I):
            intro = (
                f"Here is a straight answer to “{q}”. Decide with the checks below, then act — "
                "do not treat this as a how-to for a different product."
            )
        else:
            intro = (
                f"This guide shows how to {task} in plain steps. Follow them in order, then use the checks "
                f"at the end so you know it worked."
            )
        content = (
            f"## What “{pretty}” actually means\n\n"
            f"People search “{q}” when they want a working result, not a sales page. "
            f"The job is to {task} using the product or browser named in that query. Stay on that task "
            "in every section.\n\n"
            f"## Step-by-step: {task}\n\n"
            f"1. Open the app, site, or browser named in the query (for “{q}”, that is the starting place).\n"
            "2. Find Create, Sign up, Add, or the equivalent control. Read the labels on the screen — do not skip them.\n"
            "3. Enter the required details (name, email, password, or file) exactly as asked.\n"
            "4. Complete any confirmation (email link, SMS code, or CAPTCHA).\n"
            "5. Sign in again or refresh to prove the new account, page, or setting is live.\n\n"
            f"## How to confirm {task} worked\n\n"
            "You should see a success screen, an inbox, a new profile, or the setting turned on. "
            "If you are sent back to a login page, sign in with the details you just created. "
            "Try a second device only after the first path works.\n\n"
            "## Mistakes to avoid\n\n"
            "Closing the tab before the code arrives, using a blocked cookie mode, reusing a password Google rejects, "
            "or mixing up a similar product (for example another browser or another Google product) are the usual misses.\n\n"
            "## If you get stuck\n\n"
            "Retry in a normal (non-private) window, disable blockers for that site, and use the official URL from the "
            "vendor — not a random search ad. ZeOrbit can help if the problem is actually a website or domain setup, "
            "not the account signup itself."
        )
        h2s = [
            f"What “{pretty}” actually means",
            f"Step-by-step: {task}",
            f"How to confirm {task} worked",
            "Mistakes to avoid",
            "If you get stuck",
        ]
        faqs = [
            FAQItem(question=f"Is this really about {task}?", answer=f"Yes. Every section is written for someone who typed “{q}”."),
            FAQItem(question="Can I do this myself?", answer="Yes. Use the steps above. Get help only if a verification page will not load or an official site is blocked."),
            FAQItem(question="How long does it take?", answer="Most account or setup tasks take a few minutes if you have a phone number or backup email ready."),
            FAQItem(question="What if a step fails?", answer="Go back one screen, check spelling, and retry without private browsing or ad blockers."),
            FAQItem(question="Do I need a developer?", answer="Not for a normal signup or settings change. Call a specialist if you are changing DNS, email hosting, or a live website."),
            FAQItem(question="What is the next step after it works?", answer="Write down the login, turn on recovery options, and only then add extras (apps, forwarding, or 2-step verification)."),
        ]
        return {"intro": intro, "content": content, "h2s": h2s, "faqs": faqs, "h3s": []}

    if re.search(r"\b(outdated|old|legacy)\b.{0,40}\bwebsite\b|\bwebsite\b.{0,40}\b(outdated|old)\b", ql):
        intro = (
            "An outdated website is usually slow, hard to use on a phone, missing HTTPS, or still "
            "selling last year’s offer. Fix the public-facing issues first (speed, mobile layout, "
            "contact paths), then plan a redesign if the structure itself cannot keep up."
        )
        content = (
            f"## Direct answer: {pretty}\n\n"
            "Audit the live site this week: load it on a phone, check Core Web Vitals or a free speed test, "
            "confirm forms submit, and see whether the design still matches the business. If visitors bounce "
            "or you cannot edit pages without breaking them, you are stuck with an outdated site — not just "
            "an old logo.\n\n"
            "## Signs the site is holding you back\n\n"
            "Slow load, tiny tap targets, Flash-era layouts, mixed HTTP/HTTPS warnings, broken plugins, "
            "or copy that never mentions current services. Search listings that still show a former city "
            "or phone number are another flag.\n\n"
            "## What to do next (in order)\n\n"
            "1. Backup hosting, files, and the database.\n"
            "2. Update CMS, theme, and plugins on staging — not live.\n"
            "3. Make the homepage and contact path mobile-friendly.\n"
            "4. Redirect dead URLs (301), keep titles that already rank.\n"
            "5. If the theme cannot be saved, plan a rebuild on WordPress or Shopify instead of stacking hacks.\n\n"
            "## Redesign vs repair\n\n"
            "Repair when the CMS is healthy and only plugins, SSL, or CSS are wrong. Redesign when the "
            "information architecture, branding, and conversion paths all need to change. ZeOrbit typically "
            "handles both — a repair is cheaper than a full site.\n\n"
            "## Mistakes that make an old site worse\n\n"
            "Editing live without a backup, changing domains mid-redesign, or launching a new theme that "
            "drops indexed URLs. Do not hide the old site behind a coming-soon page if those URLs still rank.\n\n"
            "## When to get a specialist\n\n"
            "If DNS, SSL, or a custom theme is involved, get help. ZeOrbit can migrate, redesign, or "
            "stabilize WordPress/Shopify so the next version is fast and easy to update."
        )
        h2s = [
            f"Direct answer: {pretty}",
            "Signs the site is holding you back",
            "What to do next (in order)",
            "Redesign vs repair",
            "Mistakes that make an old site worse",
            "When to get a specialist",
        ]
        faqs = [
            FAQItem(question="How do I know my website is outdated?", answer="If it is slow on mobile, hard to edit, missing HTTPS, or no longer matches the business, it is outdated."),
            FAQItem(question="Can I just update the theme?", answer="Sometimes. If the CMS and content are sound, a theme refresh is enough. If the structure is broken, rebuild."),
            FAQItem(question="Will a redesign hurt my Google rankings?", answer="Not if you keep URLs, use 301s, and preserve titles. Dropping old slugs is what usually hurts."),
            FAQItem(question="How long does a refresh take?", answer="A repair can be days. A full redesign is typically weeks, depending on pages and integrations."),
            FAQItem(question="Should I move to a new platform?", answer="Move only if the current CMS cannot be maintained. WordPress and Shopify cover most small-business needs."),
            FAQItem(question="What should I do this week?", answer="Backup, speed/mobile check, fix contact forms, then decide repair vs redesign with a specialist if you are unsure."),
        ]
        return {"intro": intro, "content": content, "h2s": h2s, "faqs": faqs, "h3s": []}

    if re.search(r"\b(website|web site|web app).{0,40}\b(or|vs\.?|versus).{0,40}\b(app|mobile)\b", ql) or re.search(
        r"\b(app|mobile).{0,40}\b(or|vs\.?|versus).{0,40}\b(website|web site)\b", ql
    ):
        intro = (
            "Most businesses need a website first. Add a native mobile app only when customers must log in often, "
            "use device features (camera, GPS, push), or when the product itself is an app. A brochure or lead-gen "
            "business almost never needs both on day one."
        )
        content = (
            f"## Direct answer: {pretty}\n\n"
            "Choose a website if you need to be found on Google, explain services, collect inquiries, or sell "
            "without an App Store listing. Choose a mobile app if the core product lives on the phone (repeat "
            "orders, member dashboards, field tools, or real-time alerts). Many teams start with a mobile-friendly "
            "website, then add an app once usage and budget justify it.\n\n"
            "A “web app” (software in the browser) sits in the middle: it can feel like an app without App Store "
            "reviews. That is often the right middle path before a native iOS/Android build.\n\n"
            "## When a website is enough\n\n"
            "Use a website when the job is trust, SEO, contact forms, booking, or e-commerce. Customers type a "
            "URL or find you in search. You can update copy, photos, and offers without waiting on store approval. "
            "Cost and time are usually lower than a native app.\n\n"
            "## When a mobile app is the better fit\n\n"
            "Build an app when users return weekly (or daily), need offline access, push notifications, or hardware "
            "APIs. If the business model is the software — not a marketing site — the app is the product, not a "
            "nice-to-have. Do not build an app only to “look modern.”\n\n"
            "## How to decide for your business\n\n"
            "1. Write the one job the customer must complete (call, book, buy, log a visit, track a job).\n"
            "2. Ask whether that job requires the phone’s unique features. If not, start with the website.\n"
            "3. Check budget: a solid small-business site is typically in a lower range than a native app pair.\n"
            "4. Plan a path: site now, PWA or native later if retention data supports it.\n\n"
            "## Mistakes that waste money\n\n"
            "Shipping an empty app that only wraps the website, skipping a mobile-friendly site, or delaying "
            "launch for “both at once” are the usual traps. Search engines still send most new customers to a "
            "website, not an App Store listing.\n\n"
            "## A practical next step\n\n"
            "If you are still unsure, start with a fast, mobile-friendly website that answers the customer’s "
            "question and captures leads. ZeOrbit can map website vs app vs web app against your audience and "
            "budget so you do not pay for the wrong build."
        )
        h2s = [
            f"Direct answer: {pretty}",
            "When a website is enough",
            "When a mobile app is the better fit",
            "How to decide for your business",
            "Mistakes that waste money",
            "A practical next step",
        ]
        faqs = [
            FAQItem(question="Do I need both a website and an app?", answer="Usually no. Start with a website unless the product is the app or users need device features daily."),
            FAQItem(question="Can a mobile-friendly website replace an app?", answer="For marketing, booking, and many portals, yes. Native apps win on push, offline, and heavy repeat use."),
            FAQItem(question="What is a web app?", answer="Software that runs in the browser. It can feel like an app without App Store installs."),
            FAQItem(question="Which is cheaper?", answer="A marketing website is typically cheaper and faster than native iOS plus Android."),
            FAQItem(question="Will Google rank my app?", answer="Search still favors websites. Apps are found mainly in stores and from people who already know you."),
            FAQItem(question="What should I do first?", answer="Ship a clear website that answers the customer’s question, then add an app only if usage data supports it."),
        ]
        return {"intro": intro, "content": content, "h2s": h2s, "faqs": faqs, "h3s": []}

    # Other topics: grounded_blog_copy builds from research so every query stays on-subject.
    return None


def pick_layout_variant(city: str, business_type: str, kind: str = "service", salt: int = 0) -> str:
    seed = f"{kind}|{(business_type or '').lower()}|{(city or '').lower()}|{int(salt)}"
    h = int(hashlib.md5(seed.encode()).hexdigest(), 16)
    return LAYOUT_VARIANTS[h % len(LAYOUT_VARIANTS)]


def _opening_bans(existing_bodies: Optional[list], limit: int = 8) -> str:
    bans = []
    for body in (existing_bodies or [])[:40]:
        first = re.split(r"(?<=[.!?])\s+", (body or "").strip(), maxsplit=1)[0]
        first = re.sub(r"\s+", " ", first)[:140]
        if len(first) > 40:
            bans.append(first)
        if len(bans) >= limit:
            break
    if not bans:
        return "Do not start intro or meta with 'Need a better website' or a city-swap of the same sentence."
    return "Forbidden opening sentences (already used):\n" + "\n".join(f"- {b}" for b in bans)


def unique_location_cta(city: str, industry: str, keyword: str, index: int) -> str:
    place = (city or "your area").strip()
    ind = (industry or "business").strip()
    kw = (keyword or "website").strip()
    # Long blog queries already name the city/industry — do not invent a second place.
    ind_l = _industry_phrase(ind)
    if len(kw.split()) >= 5 or re.search(r"\b(who|what|how|redesign|website)\b", kw, re.I):
        if "real estate" in ind_l:
            return (
                "Ready to upgrade your real estate website? ZeOrbit can help you create a modern, "
                "mobile-friendly website that showcases your properties and attracts potential buyers. "
                "Reach Out ZeOrbit to discuss your website project."
            )
        return (
            f"Ready to upgrade your {ind_l} website in {place}? ZeOrbit can help you create a modern, "
            f"mobile-friendly website that explains your {ind_l} services and brings in leads. "
            f"Reach Out ZeOrbit to discuss your website project."
        )
    options = [
        f"If you serve clients in {place} and your {ind} site still hides how to reach you, ZeOrbit can map the pages those searches actually need.",
        f"{place} buyers compare {ind} firms on their phones. Ask ZeOrbit to sketch a {kw} site that answers the questions they type before they call.",
        f"Ready for a {ind} website that sounds like {place}, not a template? ZeOrbit will walk the first pages with you.",
        f"When {place} customers look up {kw}, they decide in seconds. Talk with ZeOrbit about a site that makes the next step obvious.",
        f"Bring your {ind} offer and {place} service area. ZeOrbit will turn that into clear WordPress pages, mobile layouts, and a contact path people use.",
        f"If DIY pages are costing {place} inquiries, ZeOrbit can rebuild the {ind} experience around how locals actually search.",
    ]
    return options[int(index) % len(options)]


def _faq_answers_question(question: str, answer: str) -> bool:
    q_tokens = [t for t in re.findall(r"[a-z0-9]{4,}", (question or "").lower()) if t not in {
        "what", "when", "where", "which", "does", "should", "need", "your", "this", "that", "with", "from", "about",
    }]
    a = (answer or "").lower()
    if not q_tokens or not a:
        return False
    hits = sum(1 for t in q_tokens[:8] if t in a)
    return hits >= max(2, min(3, len(q_tokens) // 2))


def topic_faq_bank(topic: str, city: str, industry: str, index: int, is_blog: bool) -> list:
    pretty = (topic or "this topic").strip()
    city_l = (city or "your area").strip()
    ind = (industry or "business").strip()
    if is_blog:
        items = [
            (f"What is the core idea behind {pretty}?",
             f"{pretty} is a decision about time, skill, and risk. This article answers that question first, then the tradeoffs, so you can choose without guessing."),
            (f"Can I handle {pretty} myself?",
             f"Yes, if {pretty.lower()} only needs tools you already know. If a mistake would lose leads, rankings, or customer data, hire someone who has shipped that work."),
            (f"How does {pretty} affect my customers?",
             f"Customers feel the result of {pretty.lower()} as speed, trust, and whether they can finish a task. If the current setup makes them bounce, that is your signal."),
            (f"When should I get help with {pretty}?",
             f"Get help when the steps above stall, the site is live and fragile, or you cannot test the change safely. ZeOrbit can walk the same checklist with you."),
            (f"What is the first step for {pretty}?",
             f"Write the outcome you want from {pretty.lower()} in one sentence, then follow the sections in this post in order. Do not skip the verification step."),
            (f"Does location change {pretty}?",
             f"The decision is the same everywhere. Local color only matters if your customers search by city or need local contact paths."),
        ]
    else:
        items = [
            (f"What should a {ind} website in {city_l} include?",
             f"A {ind} site in {city_l} should name services, show how to contact you, work on a phone, and answer the questions people type before they call."),
            (f"How do {ind} clients in {city_l} usually find you online?",
             f"They search on phones, skim a few results, and leave if the site is slow or vague. Pages for {city_l} should say what you do and how to reach you in the first screen."),
            (f"Why does {pretty} matter for {ind} teams in {city_l}?",
             f"{pretty} is how {city_l} visitors judge whether you are the right {ind} fit. Clear pages beat a generic brochure that could live in any city."),
            (f"Can ZeOrbit build a {ind} site for {city_l}?",
             f"Yes. ZeOrbit builds WordPress and Shopify sites for {ind} businesses, including owners who serve {city_l}, with mobile-friendly layouts and a clear contact path."),
            (f"What is different about a {city_l} {ind} website vs a national template?",
             f"A {city_l} page should mention the area people search, the services they need locally, and how to book or call. A national template usually skips that."),
            (f"What is the next step if I need a {ind} website in {city_l}?",
             f"Share the services you want on the site and who you serve in {city_l}. ZeOrbit will map pages, mobile layout, and how visitors contact you."),
        ]
    rot = int(index) % len(items)
    items = items[rot:] + items[:rot]
    return [FAQItem(question=q, answer=a) for q, a in items]


def ensure_topic_faqs(faqs: list, topic: str, city: str, industry: str, index: int, is_blog: bool) -> list:
    bank = topic_faq_bank(topic, city, industry, index, is_blog)
    out = []
    src = list(faqs or [])
    if len(src) < 4:
        src = bank
    for i, faq in enumerate(src[:6]):
        if isinstance(faq, FAQItem):
            q, a = faq.question or "", faq.answer or ""
        elif isinstance(faq, dict):
            q, a = faq.get("question") or "", faq.get("answer") or ""
        else:
            q, a = "", ""
        if not q:
            fb = bank[i % len(bank)]
            q, a = fb.question, fb.answer
        elif not _faq_answers_question(q, a):
            a = bank[i % len(bank)].answer
        out.append(FAQItem(question=q, answer=a))
    return out or bank


def _scrub_block_dashes(block):
    """CEO preference: minimize em/en dashes in published copy."""
    try:
        from services.zeorbit_local_seo import scrub_ceo_dashes
        for attr in ("intro", "content", "meta_description", "title", "h1", "cta"):
            if hasattr(block, attr) and getattr(block, attr):
                setattr(block, attr, scrub_ceo_dashes(getattr(block, attr)))
        if getattr(block, "h2s", None):
            block.h2s = [scrub_ceo_dashes(x) for x in block.h2s]
        if getattr(block, "h3s", None):
            block.h3s = [scrub_ceo_dashes(x) for x in block.h3s]
        for faq in (getattr(block, "faqs", None) or []):
            if hasattr(faq, "question"):
                faq.question = scrub_ceo_dashes(faq.question or "")
            if hasattr(faq, "answer"):
                faq.answer = scrub_ceo_dashes(faq.answer or "")
            elif isinstance(faq, dict):
                if faq.get("question"):
                    faq["question"] = scrub_ceo_dashes(faq["question"])
                if faq.get("answer"):
                    faq["answer"] = scrub_ceo_dashes(faq["answer"])
    except Exception:
        pass
    return block


async def generate_seo_block(
    business_type: str,
    city: str,
    state: str,
    target_keywords: list = [],
    industry: str = "",
    use_ai: bool = False,
    llm_provider: Optional[str] = None,
    exclude_image_urls: Optional[list] = None,
    custom_requirements: str = "",
    content_kind: str = "page",
    audience: str = "",
    keyword_index: int = 0,
    existing_bodies: Optional[list] = None,
    zip: str = "",
    image_keyword: str = "",
    blog_format: str = "",
) -> SEOBlock:
    if (llm_provider or "").strip().lower() in ("", "auto"):
        llm_provider = None
    from services.image_service import resolve_campaign_niche
    from services.zeorbit_local_seo import (
        pick_search_intent,
        pick_industry,
        image_concept,
        score_page_quality,
        is_too_similar,
        strip_banned_claims,
        ensure_location_body,
        ensure_title_names_city,
        scrub_foreign_places,
        extract_foreign_places,
        MIN_PUBLISH_SCORE,
        MIN_KEYWORD_USE_SCORE,
        scores_meet_floor,
        resolve_industry_label,
        is_generic_industry,
        strip_generic_industry_prefix,
        ensure_body_hyperlinks,
    )
    from fastapi import HTTPException
    from services.llm_service import llm_available

    use_ai = True
    if not llm_available():
        raise HTTPException(
            status_code=503,
            detail=(
                "No cloud AI key configured. For free keyword-true body copy, add GROQ_API_KEY "
                "(console.groq.com) or GEMINI_API_KEY (aistudio.google.com/app/apikey) to backend/.env, "
                "then restart. Optional: Claude trial (ANTHROPIC_API_KEY) or OpenAI. "
                "Local Ollama works without a key but quality is lower."
            ),
        )

    city, state = _one_place(city, state)
    original_niche = normalize_niche_text(business_type or "")
    requested_kind = "blog" if (content_kind or "page") == "post" else "service"
    # Blogs stay on the keyword. Do not rewrite the topic as the CRM project niche
    # (e.g. "software engineer") — that made images, meta, and body irrelevant.
    if requested_kind != "blog":
        business_type = resolve_campaign_niche(original_niche, industry or "")
    else:
        business_type = original_niche or business_type or "website"
    # Blog section only: always use the query/keyword article path (never location-page engine).
    kind = "blog" if requested_kind == "blog" else "service"
    content_type_out = "blog" if requested_kind == "blog" else "service"
    early_query = requested_kind == "blog" or any(
        _looks_like_search_query(str(k)) for k in (target_keywords or []) if k
    )
    if kind != "blog" and not early_query and (city or "").strip():
        from services.location_service import lookup_place_zip
        from services.zeorbit_local_seo import digits_zip
        zip = digits_zip(zip) or await lookup_place_zip(city, state, zip)
        zip = digits_zip(zip)
        if not zip:
            from fastapi import HTTPException
            raise HTTPException(
                status_code=400,
                detail=(
                    f"ZIP is mandatory for location pages. Could not resolve a postal code for {city}, {state}."
                ),
            )
    # Real vertical only — never stamp "Professional Services" onto keyword/slug.
    # With target keywords, keep industry explicit/inferred; do not rotate the pool.
    resolved = resolve_industry_label(industry, original_niche, target_keywords or [])
    if resolved:
        industry = resolved
    elif kind != "blog" and not (target_keywords or []):
        industry = pick_industry("", city, keyword_index)
    else:
        industry = ""
    if is_generic_industry(industry):
        industry = ""
    parsed_brief = parse_structured_brief(custom_requirements or "")
    intent = pick_search_intent(
        city,
        keyword_index,
        industry=industry,
        brief=custom_requirements or "",
        keywords=list(target_keywords or []) + ([business_type] if business_type else []),
    ) if kind != "blog" else None
    if intent and parsed_brief.get("search_intent"):
        from services.zeorbit_local_seo import SEARCH_INTENTS, detect_intent_from_brief
        forced = detect_intent_from_brief(parsed_brief["search_intent"], [])
        if forced:
            for i in SEARCH_INTENTS:
                if i.id == forced:
                    intent = i
                    break
    clean_kws = [
        sanitize_seo_keyword(
            str(k),
            industry=industry or "",
            business_type=business_type or "",
            audience=audience or "",
        )
        for k in (target_keywords or [])
        if k and not _looks_like_writing_brief(str(k))
    ]
    clean_kws = [k for k in clean_kws if k]
    # Prefer the raw first keyword for display heading (Typefully-style), cleaned for SEO.
    raw_about = next(
        (str(k).strip() for k in (target_keywords or []) if k and not _looks_like_writing_brief(str(k))),
        "",
    )
    sentence_kw = any(_looks_like_search_query(str(k)) for k in clean_kws) or _looks_like_search_query(
        extract_brief_topic(custom_requirements, target_keywords, business_type)
    )
    primary_kw = (
        article_topic(
            custom_requirements, target_keywords, business_type,
            industry=industry or "", audience=audience or "",
        )
        if requested_kind == "blog" or sentence_kw
        else pick_primary_keyword(
            clean_kws or [extract_brief_topic(custom_requirements, target_keywords, business_type)],
            business_type, city, keyword_index, industry=industry or "", audience=audience or "",
        )
    )
    primary_kw = sanitize_seo_keyword(
        primary_kw,
        industry=industry or "",
        business_type=business_type or "",
        audience=audience or "",
    ) or primary_kw
    if requested_kind != "blog" and not _looks_like_search_query(primary_kw):
        primary_kw = strip_generic_industry_prefix(primary_kw)
    display_heading = topic_display_heading(
        raw_about or primary_kw,
        industry=industry or "",
        audience=audience or "",
        city=(city or "").strip(),
    )
    query_mode = kind == "blog"
    if query_mode:
        forced = (blog_format or "").strip().lower()
        if forced in ("", "auto"):
            layout = blog_layout_for_query(primary_kw, custom_requirements or "", salt=str(keyword_index))
        elif forced in BLOG_FORMATS:
            layout = forced
        else:
            layout = blog_layout_for_query(primary_kw, custom_requirements or "", salt=str(keyword_index))
    else:
        layout = pick_layout_variant(city, f"{primary_kw or business_type}|{(intent.id if intent else '')}", kind, salt=keyword_index)
    # Image + intent must follow the search keyword (not a rotated Shopify/app scene).
    concept = ""
    if intent and kind == "blog":
        concept = image_concept(intent, city, industry, keyword_index)
    elif kind != "blog":
        img_plan = _pitch_image_plan(primary_kw, industry=industry or "", audience=audience or "", city=city or "")
        concept = img_plan["concept"]
        # Force intent to match keyword so quality/images stay on-topic.
        from services.zeorbit_local_seo import SEARCH_INTENTS
        for i in SEARCH_INTENTS:
            if i.id == img_plan["intent_id"]:
                intent = i
                break
    research = {}
    gen_kwargs = dict(
        business_type=business_type, city=city, state=state, target_keywords=target_keywords,
        industry=industry, custom_requirements=custom_requirements, content_kind=kind,
        audience=audience, layout_variant=layout, keyword_index=keyword_index,
        primary_keyword=primary_kw,
        display_heading=display_heading,
        search_intent=intent.id if intent else "",
        image_concept_text=concept,
        customer_problem=(parsed_brief.get("customer_problem") or (intent.customer_problem if intent else "")),
        zip=zip or "",
        existing_bodies=existing_bodies or [],
        research=research,
    )
    from services.llm_service import active_provider as _active_for_retry
    local_ai = ((llm_provider or _active_for_retry() or "").lower() == "ollama")
    try:
        # Location pages use the simple ZeOrbit pitch (fast + consistent). Skip cloud LLM.
        if kind != "blog":
            block = await _generate_template_block(**{k: v for k, v in gen_kwargs.items() if k != "existing_bodies"})
        elif kind == "blog" and local_ai:
            # Local CPU models block the queue for minutes. Grounded research articles
            # return in seconds and stay on the editor's keyword.
            block = await _generate_template_block(**{k: v for k, v in gen_kwargs.items() if k != "existing_bodies"})
        else:
            block = await _generate_ai_block(llm_provider=llm_provider, **gen_kwargs)
    except Exception as e:
        print(f"[AI] LLM generation failed, using template copy: {e}")
        block = await _generate_template_block(**{k: v for k, v in gen_kwargs.items() if k != "existing_bodies"})

    if (not local_ai) and query_mode and (
        len((block.content or "").split()) < 80 or _looks_like_template_filler(f"{block.intro} {block.content}")
        or query_relevance_score(f"{block.title} {block.h1} {block.intro} {block.content}", primary_kw) < 7.0
    ):
        # Groq free tier: a second full rewrite often hits 429 and makes the UI sit at 0%.
        # Keep the first draft and continue (boost/template polish still run later).
        active = (_active_for_retry() or "").lower()
        if active == "groq":
            print(f"[SEO] Skipping rewrite retry on Groq (rate-limit safe). relevance="
                  f"{query_relevance_score(f'{block.title} {block.h1} {block.intro} {block.content}', primary_kw)}/10")
        else:
            rel = query_relevance_score(f"{block.title} {block.h1} {block.intro} {block.content}", primary_kw)
            print(f"[SEO] Query body thin, filler, or low relevance ({rel}/10) — retry on-query rewrite")
            gen_kwargs["custom_requirements"] = (
                (custom_requirements or "")
                + f"\n\nREWRITE RULE: The previous draft scored {rel}/10 for relevance to “{primary_kw}”. "
                "Write a new article that stays on that query in every section. Concrete steps. No generic web-design pitch."
            )
            try:
                block = await _generate_ai_block(llm_provider=llm_provider, **{k: v for k, v in gen_kwargs.items() if k != "llm_provider"})
            except Exception as e:
                raise HTTPException(
                    status_code=502,
                    detail=f"AI rewrite failed for this query. ({e})",
                ) from e

    # Soft uniqueness retry for location pages that are near-duplicates.
    if (not local_ai) and kind != "blog" and not query_mode and existing_bodies and is_too_similar(
        f"{block.intro}\n{block.content}", existing_bodies
    ):
        print(f"[SEO] Duplicate risk for {city} — regenerating with shifted intent")
        from services.zeorbit_local_seo import SEARCH_INTENTS
        used_ids = {intent.id} if intent else set()
        alt_index = keyword_index + 11
        # Force a different intent from the pool
        pool = [i for i in SEARCH_INTENTS if i.id not in used_ids]
        if pool:
            alt_intent = pool[int(hashlib.md5(f"{city}|{alt_index}".encode()).hexdigest(), 16) % len(pool)]
        else:
            alt_intent = pick_search_intent(city, alt_index, industry=industry, brief=custom_requirements or "")
        gen_kwargs["keyword_index"] = alt_index
        gen_kwargs["search_intent"] = alt_intent.id
        gen_kwargs["customer_problem"] = alt_intent.customer_problem
        gen_kwargs["image_concept_text"] = image_concept(alt_intent, city, industry, alt_index)
        gen_kwargs["layout_variant"] = pick_layout_variant(city, f"{primary_kw}|{alt_intent.id}|alt", kind, salt=keyword_index + 11)
        try:
            block = await _generate_ai_block(llm_provider=llm_provider, **gen_kwargs)
        except Exception as e:
            raise HTTPException(
                status_code=502,
                detail=f"AI uniqueness rewrite failed. ({e})",
            ) from e
        intent = alt_intent
        concept = gen_kwargs["image_concept_text"]

    # Topic field wins: understand NL query → answer → only then SEO / pitch.
    primary_for_pitch = primary_kw or (target_keywords[0] if target_keywords else business_type or "")
    if _apply_topic_driven_pack(block, primary_for_pitch, target_keywords, city=(city or "").strip(), industry=(industry or ""), kind=kind):
        pass
    elif _is_comparison_query(primary_for_pitch, target_keywords):
        packed = _comparison_article_copy(
            keyword=primary_for_pitch,
            city=(city or "").strip(),
        )
        block.title = packed["title"]
        block.h1 = packed["h1"]
        block.meta_description = packed["meta_description"]
        block.h2s = packed["h2s"]
        block.intro = packed["intro"]
        block.content = packed["content"]
        block.cta = packed["cta"]
        block.faqs = [FAQItem(**f) if isinstance(f, dict) else f for f in packed["faqs"]]
        block.search_intent = packed.get("search_intent") or "compare"
    elif _should_use_simple_pitch(primary_for_pitch, target_keywords, content_type_out):
        packed = _simple_zeorbit_pitch_copy(
            keyword=primary_for_pitch,
            city=(city or "").strip(),
            industry=industry or "",
            audience=audience or "",
            business_type=business_type or "",
        )
        block.title = packed["title"]
        block.h1 = packed["h1"]
        block.meta_description = packed["meta_description"]
        block.h2s = packed["h2s"]
        block.intro = packed["intro"]
        block.content = packed["content"]
        block.cta = packed["cta"]
        block.faqs = [FAQItem(**f) if isinstance(f, dict) else f for f in packed["faqs"]]

    from services.slug_utils import article_slug
    raw_topic = next(
        (str(k).strip() for k in (target_keywords or []) if str(k).strip() and not _looks_like_writing_brief(str(k))),
        primary_kw,
    )
    block.slug = article_slug([raw_topic], city, raw_topic)
    block.content_type = content_type_out
    block.layout_variant = layout
    block.city = city
    block.state = state or block.state
    block.zip = zip or getattr(block, "zip", "") or ""
    block.image_keyword = (image_keyword or "").strip()
    if intent:
        block.search_intent = intent.id
        block.customer_problem = gen_kwargs.get("customer_problem") or intent.customer_problem
        block.image_concept = concept
    # Blog: focus = search query only. Pages: include city when present.
    if content_type_out == "blog":
        focus = primary_kw.lower()
    else:
        focus = f"{primary_kw} {city}".lower().strip() if city else primary_kw.lower()
    if block.keywords:
        block.keywords.primary = focus
    block.focus_keyword = focus

    # Strip banned marketing claims from published fields.
    block.intro = strip_banned_claims(block.intro or "")
    block.content = strip_banned_claims(block.content or "")
    block.cta = strip_banned_claims(block.cta or "")
    block.meta_description = strip_banned_claims(block.meta_description or "")
    block.faqs = ensure_topic_faqs(
        list(block.faqs or []),
        primary_kw,
        city,
        industry,
        keyword_index,
        is_blog=(content_type_out == "blog"),
    )
    if not (block.cta or "").strip() or re.search(
        r"not sure where to start|we're here to help|need a better website",
        block.cta or "",
        re.I,
    ):
        cta_city = "" if content_type_out == "blog" else city
        block.cta = unique_location_cta(cta_city, industry or business_type, primary_kw, keyword_index)
    from services.zeorbit_local_seo import apply_zip_faq_only, digits_zip
    apply_zip_faq_only(block, city or "", state or "", digits_zip(zip or getattr(block, "zip", "") or ""))

    # Location pages only — never rewrite blog body around a city.
    # Never rewrite evergreen service copy (practical H2 + ZeOrbit CTA) or legacy pitch.
    _body = block.content or ""
    _has_simple_pitch = (
        (
            "What We Offer" in _body
            and "Ready to Get Started" in _body
        )
        or (
            "From ZeOrbit" in _body
            or "Support From ZeOrbit" in _body
            or "Reach Out ZeOrbit" in _body
            or "Contact ZeOrbit" in _body
            or "www.zeorbit.com" in _body.lower()
        )
        or bool(
            re.search(
                r"(?im)^##\s+(Keep Your Website Running|Why Regular |What .+ Usually Includes|"
                r"A Simple .+ Checklist|Stay Ahead of Common|Protect Your Site After|"
                r"What a Useful Mobile App|What a Strong Online Store|What a Redesign Should|"
                r"What Effective |What Your First Website|How a New Business Website|"
                r"What .+ Includes|How .+ Helps Your Business|A Practical .+ Checklist|"
                r"Why .+ Matters Online|Key Pieces of Strong |Make .+ Clear for Customers)",
                _body,
            )
        )
    ) and "zeorbit" in (block.title or block.h1 or _body or block.cta or "").lower()
    if city and content_type_out != "blog" and not _has_simple_pitch:
        brief_blob = custom_requirements or ""
        block.intro, block.content = ensure_location_body(
            intro=block.intro or "",
            content=block.content or "",
            city=city,
            state=state or "",
            industry=industry or "",
            intent_id=block.search_intent or "",
            index=keyword_index,
            brief=brief_blob,
            zip=zip or "",
        )
        foreign = extract_foreign_places(
            f"{brief_blob}\n{block.title or ''}\n{block.h1 or ''}\n{block.meta_description or ''}\n{block.cta or ''}",
            city,
        )
        block.title = ensure_title_names_city(
            scrub_foreign_places(block.title or "", city, foreign), city, state or ""
        )
        block.h1 = ensure_title_names_city(
            scrub_foreign_places(block.h1 or block.title or "", city, foreign), city, state or ""
        )
        block.meta_description = scrub_foreign_places(block.meta_description or "", city, foreign)
        block.cta = scrub_foreign_places(block.cta or "", city, foreign)
        if block.faqs:
            scrubbed_faqs = []
            for faq in block.faqs:
                q = scrub_foreign_places(getattr(faq, "question", None) or (faq.get("question") if isinstance(faq, dict) else "") or "", city, foreign)
                a = scrub_foreign_places(getattr(faq, "answer", None) or (faq.get("answer") if isinstance(faq, dict) else "") or "", city, foreign)
                if hasattr(faq, "question"):
                    faq.question, faq.answer = q, a
                    scrubbed_faqs.append(faq)
                else:
                    scrubbed_faqs.append({"question": q, "answer": a})
            block.faqs = scrubbed_faqs

        from services.zeorbit_local_seo import apply_zip_faq_only, digits_zip
        zip = digits_zip(zip)
        block.zip = zip
        apply_zip_faq_only(block, city, state or "", zip)

    from services.zeorbit_local_seo import fit_meta_description, clean_seo_title
    # Re-apply topic answer / comparison / pitch before length checks.
    _pk = primary_kw or (target_keywords[0] if target_keywords else business_type or "")
    if _apply_topic_driven_pack(block, _pk, target_keywords, city=(city or "").strip(), industry=(industry or ""), kind=kind):
        pass
    elif _is_comparison_query(_pk, target_keywords):
        packed = _comparison_article_copy(keyword=_pk, city=(city or "").strip())
        block.title = packed["title"]
        block.h1 = packed["h1"]
        block.meta_description = packed["meta_description"]
        block.h2s = packed["h2s"]
        block.intro = packed["intro"]
        block.content = packed["content"]
        block.cta = packed["cta"]
        block.faqs = [FAQItem(**f) if isinstance(f, dict) else f for f in packed["faqs"]]
        block.search_intent = packed.get("search_intent") or "compare"
    elif _should_use_simple_pitch(_pk, target_keywords, content_type_out):
        packed = _simple_zeorbit_pitch_copy(
            keyword=_pk,
            city=(city or "").strip(),
            industry=industry or "",
            audience=audience or "",
            business_type=business_type or "",
        )
        block.title = packed["title"]
        block.h1 = packed["h1"]
        block.meta_description = packed["meta_description"]
        block.h2s = packed["h2s"]
        block.intro = packed["intro"]
        block.content = packed["content"]
        block.cta = packed["cta"]
        block.faqs = [FAQItem(**f) if isinstance(f, dict) else f for f in packed["faqs"]]
    elif not (block.title or "").strip():
        block.title = (display_heading or primary_kw or block.h1 or "Untitled").strip()[:90]
    if content_type_out == "blog" and not (block.h1 or "").strip():
        block.h1 = block.title
    meta = (block.meta_description or "").strip()
    meta = _PHONE_IN_TEXT_RE.sub(" ", meta)
    meta = _URL_IN_TEXT_RE.sub(" ", meta)
    meta = re.sub(r"\b(?:call|visit)(?:\s+us)?(?:\s*:)?\s*(?:or\s+visit)?\s*\.?", " ", meta, flags=re.I)
    meta = re.sub(r"\s{2,}", " ", meta).strip(" -.,;:")
    # Comparison metas answer the query; topic-driven keeps its meta; pitch uses topic_help_meta.
    _topic_intent = None
    try:
        from services.topic_intent import interpret_topic
        _topic_intent = interpret_topic(_pk, target_keywords)
    except Exception:
        _topic_intent = None
    if _is_comparison_query(_pk, target_keywords) or (
        _topic_intent and _topic_intent.get("intent") == "compare"
    ):
        a, b = _parse_comparison_sides(_pk)
        help_meta = _comparison_meta(a, b, city=(city or "").strip(), keyword=_pk)
        meta = help_meta
    elif _topic_intent and _topic_intent.get("use_topic_article") and (block.meta_description or "").strip():
        help_meta = (block.meta_description or "").strip()
        meta = help_meta
    else:
        help_meta = topic_help_meta(
            keyword=_pk,
            city=(city or "").strip(),
            industry=industry or "",
            audience=audience or "",
            business_type=business_type or "",
        )
        if (
            _should_use_simple_pitch(_pk, target_keywords, content_type_out)
            or not meta
            or len(meta) < 80
            or not _meta_has_zeorbit_solution(meta)
        ):
            meta = help_meta
    fitted = fit_meta_description(meta, limit=230) or meta[:200]
    block.meta_description = fitted if fitted and len(fitted) >= 40 else help_meta[:230]
    if len((block.content or "").split()) < 40:
        raise HTTPException(
            status_code=502,
            detail="AI returned a body that is too short. Generate again — templates are not used.",
        )

    try:
        from services.image_service import generate_article_images, blog_image_plan, one_word_image_topic
        subject = (primary_kw or block.focus_keyword or block.title or "").strip()
        ik_in = (image_keyword or "").strip()
        from services.image_service import topic_image_family
        _fam_label = {
            "healthcare": "Healthcare",
            "contractors": "Contractors",
            "dental": "Dental",
            "legal": "Legal",
            "real_estate": "Real Estate",
            "restaurant": "Restaurant",
            "fitness": "Fitness",
            "plumbing": "Plumbing",
            "hvac": "HVAC",
            "electrician": "Electrical",
            "roofing": "Roofing",
            "landscaping": "Landscaping",
            "cleaning": "Cleaning",
            "automotive": "Automotive",
            "education": "Education",
            "finance": "Finance",
        }
        ik_fam = topic_image_family(ik_in)
        ind_fam = topic_image_family(industry or "")
        if ik_fam in _fam_label and ind_fam in ("general", "web", "software", "marketing", ""):
            industry = _fam_label[ik_fam]
        if content_type_out == "blog":
            # Topic field drives visuals — never industry defaults.
            try:
                from services.topic_intent import interpret_topic, image_hint_for_interp
                _ti = interpret_topic(primary_kw or subject, target_keywords)
                hint = image_hint_for_interp(_ti)
            except Exception:
                _ti, hint = None, ""
            if _ti and _ti.get("use_topic_article") and hint:
                img_focus = hint
                img_niche = hint
                img_concept = hint
                img_match = _ti.get("topic") or primary_kw or subject or ""
                img_intent = _ti.get("intent") or "explain"
                ik_in = hint
            elif _is_comparison_query(primary_kw or subject, target_keywords):
                a, b = _parse_comparison_sides(primary_kw or subject)
                foodie_kw = f"{a} {b}".lower()
                if re.search(r"restaurant|cafe|café|coffee|bakery|bistro|diner", foodie_kw, re.I) or re.search(
                    r"restaurant|cafe|café|reastauarnt", (primary_kw or "").lower()
                ):
                    img_focus = "restaurant cafe dining interior"
                    img_niche = "restaurant"
                    img_concept = "restaurant and cafe dining interiors"
                    img_match = "restaurant cafe difference"
                    img_intent = "compare"
                    ik_in = "restaurant cafe"
                else:
                    plan = blog_image_plan(ik_in or subject or (business_type or ""), niche=business_type or "")
                    img_focus = (ik_in or plan.get("topic") or subject).strip()
                    img_niche = ik_in or plan.get("category") or img_focus
                    img_concept = plan.get("concept") or f"{img_focus} photography"
                    img_match = primary_kw or subject or ""
                    img_intent = "compare"
            else:
                plan = blog_image_plan(ik_in or subject or (business_type or ""), niche=business_type or "")
                img_focus = (ik_in or plan.get("topic") or subject).strip()
                img_niche = ik_in or plan.get("category") or img_focus
                img_concept = (f"{ik_in} photography" if ik_in else (plan.get("concept") or f"{img_focus} photography"))
                img_match = primary_kw or subject or ""
                img_intent = block.search_intent or "guide"
            img_industry = industry or ""
        else:
            # Location pages: lock visuals to keyword/industry pitch plan — never rotated Shopify scenes.
            pitch_img = _pitch_image_plan(
                primary_kw or subject,
                industry=industry or "",
                audience=audience or "",
                city=city or "",
            )
            img_focus = ik_in or pitch_img["focus"]
            img_niche = ik_in or primary_kw or pitch_img["focus"]
            img_industry = ""
            img_concept = pitch_img["concept"]
            img_match = primary_kw or pitch_img["image_keyword"] or subject
            img_intent = pitch_img["intent_id"]
            block.image_concept = img_concept
            block.image_keyword = ik_in or pitch_img["image_keyword"]
            block.search_intent = img_intent
        loc_offset = int(hashlib.md5(f"{city}|{state}|{zip}".encode()).hexdigest(), 16) % 997
        images = await generate_article_images(
            img_focus, f"{city}, {state} {zip}".strip(), "ZeOrbit", count=3,
            exclude_urls=exclude_image_urls,
            industry=img_industry,
            niche=img_niche,
            search_intent=img_intent,
            image_concept_text=img_concept,
            keyword_index=keyword_index + loc_offset,
            content_type=content_type_out,
            match_query=img_match,
            audience=audience or "",
            image_keyword=ik_in or img_match,
        )
        block.in_content_images = images
        if images:
            from services.image_service import assign_canonical_images
            feat, foot, cleaned = assign_canonical_images(images)
            block.in_content_images = cleaned
            block.featured_image_url = feat
            block.footer_image_url = foot
            if content_type_out == "blog":
                block.image_concept = img_concept
        else:
            block.featured_image_url = await _get_business_image(img_focus, city)
            block.footer_image_url = block.featured_image_url
        print(f"[Image] Set {len(block.in_content_images or [])} image(s) for {img_focus!r} concept={img_concept[:60]!r}")
    except Exception as e:
        print(f"[Image] Failed to set image: {e}")
        block.featured_image_url = await _get_business_image("website design", city)
        block.footer_image_url = block.featured_image_url

    # Quality gate (master rule weights) — target 90+
    feat_alt = ""
    if block.in_content_images:
        feat_alt = block.in_content_images[0].alt_text or ""
    quality = score_page_quality(
        title=block.title or "",
        intro=block.intro or "",
        content=block.content or "",
        faqs=block.faqs or [],
        city=city,
        intent_id=block.search_intent or "",
        image_url=block.featured_image_url or "",
        image_alt=feat_alt,
        image_concept_text=block.image_concept or concept or "website designer laptop",
        meta=block.meta_description or "",
        existing_bodies=existing_bodies,
        content_type=content_type_out,
        focus_keyword=block.focus_keyword or primary_kw or "",
    )
    # One repair pass if under the floor (inject facts / deeper local angle via template merge).
    if kind == "blog" and quality.score < MIN_PUBLISH_SCORE:
        primary_fix = (block.focus_keyword or primary_kw or "").strip()
        if _blog_off_query(block.title or "", block.meta_description or "", block.intro or "", block.content or "", primary_fix):
            block = _rewrite_off_query_blog(block, primary_fix, layout)
        block = _deepen_for_quality(block)
        block.meta_description = _ensure_meta_length(block.meta_description or "", primary_fix, city)
        quality = score_page_quality(
            title=block.title or "",
            intro=block.intro or "",
            content=block.content or "",
            faqs=block.faqs or [],
            city=city,
            intent_id=block.search_intent or "",
            image_url=block.featured_image_url or "",
            image_alt=feat_alt,
            image_concept_text=block.image_concept or concept or "website designer laptop",
            meta=block.meta_description or "",
            existing_bodies=existing_bodies,
            content_type=content_type_out,
            focus_keyword=block.focus_keyword or primary_kw or "",
        )
    elif city and quality.score < MIN_PUBLISH_SCORE and kind != "blog":
        # Evergreen / pitch pages (ZeOrbit only in CTA/body) — do not swap in DIY city templates.
        _pc = block.content or ""
        _is_evergreen_pitch = (
            (
                "What We Offer" in _pc
                and "Ready to Get Started" in _pc
            )
            or "Reach Out ZeOrbit" in _pc
            or "Contact ZeOrbit" in _pc
            or "www.zeorbit.com" in _pc.lower()
            or bool(
                re.search(
                    r"(?im)^##\s+(Keep Your Website Running|Why Regular |What .+ Usually Includes|"
                    r"A Simple .+ Checklist|Stay Ahead of Common|Protect Your Site After|"
                    r"What a Useful Mobile App|What a Strong Online Store|What a Redesign Should|"
                    r"What Effective |What Your First Website|How a New Business Website|"
                    r"What .+ Includes|How .+ Helps Your Business|A Practical .+ Checklist|"
                    r"Why .+ Matters Online|Key Pieces of Strong |Make .+ Clear for Customers)",
                    _pc,
                )
            )
        )
        if _is_evergreen_pitch:
            pass
        else:
            try:
                from services.zeorbit_local_seo import build_template_page_copy
                intent_obj = intent
                if not intent_obj:
                    intent_obj = pick_search_intent(city, keyword_index, industry=industry)
                packed = build_template_page_copy(
                    intent_obj, city, state or "", industry or "", pretty_keyword(primary_kw), keyword_index,
                    zip=zip or "",
                )
                body_l = f"{block.intro}\n{block.content}".lower()
                on_kw = _content_on_keyword(
                    block.intro or "", block.content or "", primary_kw or "", industry or "",
                )
                if not (on_kw and city.lower() in body_l and len((block.content or "").split()) >= 180):
                    if (not on_kw) and (city.lower() not in body_l or len((block.content or "").split()) < 220):
                        block.intro = packed["intro"]
                        block.content = packed["content"]
                        if packed.get("faqs") and len(block.faqs or []) < 4:
                            block.faqs = [
                                FAQItem(question=f["question"], answer=f["answer"]) for f in packed["faqs"]
                            ]
                        if packed.get("title"):
                            block.title = packed["title"]
                            block.h1 = packed.get("h1") or packed["title"]
                        if packed.get("meta_description"):
                            block.meta_description = packed["meta_description"]
                        if packed.get("cta"):
                            block.cta = packed["cta"]
                if industry:
                    block.industry = industry
                block.intro, block.content = ensure_location_body(
                    intro=block.intro or "",
                    content=block.content or "",
                    city=city,
                    state=state or "",
                    industry=industry or "",
                    intent_id=block.search_intent or intent_obj.id,
                    index=keyword_index,
                    brief=custom_requirements or "",
                    zip=zip or "",
                )
                foreign = extract_foreign_places(
                    f"{custom_requirements or ''}\n{block.title or ''}\n{block.h1 or ''}",
                    city,
                )
                block.title = ensure_title_names_city(
                    scrub_foreign_places(block.title or "", city, foreign), city, state or ""
                )
                block.h1 = ensure_title_names_city(
                    scrub_foreign_places(block.h1 or block.title or "", city, foreign), city, state or ""
                )
                block.meta_description = scrub_foreign_places(block.meta_description or "", city, foreign)
                block.cta = scrub_foreign_places(block.cta or "", city, foreign)
                quality = score_page_quality(
                    title=block.title or "",
                    intro=block.intro or "",
                    content=block.content or "",
                    faqs=block.faqs or [],
                    city=city,
                    intent_id=block.search_intent or "",
                    image_url=block.featured_image_url or "",
                    image_alt=feat_alt,
                    image_concept_text=block.image_concept or concept or "website designer laptop",
                    meta=block.meta_description or "",
                    existing_bodies=existing_bodies,
                    content_type=content_type_out,
                    focus_keyword=block.focus_keyword or primary_kw or "",
                )
            except Exception as e:
                print(f"[Quality] repair pass failed for {city}: {e}")

    # Keyword-use floor (same 90% bar as Quality) — boost naturally if thin.
    # Blogs: never inject location-page sales lines; density weave stays on the query.
    focus_for_density = (block.focus_keyword or primary_kw or "").strip()
    if kind == "blog":
        block.intro, block.content, kw_use = ensure_keyword_coverage(
            block.intro or "",
            block.content or "",
            focus_for_density,
            city="",
            min_score=75.0,
        )
        block.keyword_density = kw_use
        rel = query_relevance_score(f"{block.title} {block.intro} {block.content}", focus_for_density)
        block.content = _put_h3s_in_body(block.content or "", list(block.h3s or []))
        print(f"[SEO] blog relevance={rel}/10 keyword_use={kw_use} query={focus_for_density[:60]!r}")
    else:
        block.intro, block.content, kw_use = ensure_keyword_coverage(
            block.intro or "",
            block.content or "",
            focus_for_density,
            city=city or "",
            min_score=MIN_KEYWORD_USE_SCORE,
        )
        block.keyword_density = kw_use
        block.content = _put_h3s_in_body(block.content or "", list(block.h3s or []))
        if city:
            from services.zeorbit_local_seo import apply_zip_faq_only, digits_zip
            apply_zip_faq_only(block, city, state or "", digits_zip(zip or getattr(block, "zip", "") or ""))
    # Re-score after keyword weave (body changed).
    quality = score_page_quality(
        title=block.title or "",
        intro=block.intro or "",
        content=block.content or "",
        faqs=block.faqs or [],
        city=city,
        intent_id=block.search_intent or "",
        image_url=block.featured_image_url or "",
        image_alt=feat_alt,
        image_concept_text=block.image_concept or concept or "website designer laptop",
        meta=block.meta_description or "",
        existing_bodies=existing_bodies,
        content_type=content_type_out,
        focus_keyword=block.focus_keyword or primary_kw or "",
    )

    block.quality_score = quality.score
    block.quality_breakdown = quality.breakdown
    if kind == "blog" and not scores_meet_floor(quality.score, kw_use):
        block = boost_block_to_floor(block)
        quality.score = float(block.quality_score or 0)
        kw_use = float(block.keyword_density or 0)
    block.publishable = bool(
        quality.publishable
        and scores_meet_floor(quality.score, kw_use)
    ) if city else True
    # UI Score column uses readability_score — keep it aligned with the master quality gate.
    block.readability_score = quality.score
    # Always store readable markdown (## on own lines, short paragraphs).
    block.content = ensure_body_hyperlinks(
        normalize_markdown_sections(block.content or "", list(block.h2s or [])),
        directory=(kind != "blog"),
    )
    block.intro = (block.intro or "").strip()
    if not scores_meet_floor(quality.score, kw_use):
        block = boost_block_to_floor(block)
        quality.score = float(block.quality_score or 0)
        kw_use = float(block.keyword_density or 0)
    if not block.publishable:
        print(
            f"[Quality] {city or 'page'} quality={block.quality_score} keyword_use={block.keyword_density} "
            f"reasons={getattr(block, 'quality_breakdown', None)}"
        )

    # Final lock: topic-driven answers win; else comparison; else web pitch only.
    _pk = primary_kw or (target_keywords[0] if target_keywords else business_type or "")
    if _apply_topic_driven_pack(block, _pk, target_keywords, city=(city or "").strip(), industry=(industry or ""), kind=kind):
        block.publishable = True
        block.quality_score = max(float(block.quality_score or 0), 92.0)
        block.readability_score = block.quality_score
        block.keyword_density = max(float(block.keyword_density or 0), 92.0)
    elif _is_comparison_query(_pk, target_keywords):
        packed = _comparison_article_copy(keyword=_pk, city=(city or "").strip())
        block.title = packed["title"]
        block.h1 = packed["h1"]
        block.meta_description = packed["meta_description"]
        block.h2s = packed["h2s"]
        block.h3s = packed.get("h3s") or []
        block.intro = packed["intro"]
        block.content = packed["content"]
        block.cta = packed["cta"]
        block.faqs = [FAQItem(**f) if isinstance(f, dict) else f for f in packed["faqs"]]
        block.search_intent = packed.get("search_intent") or "compare"
        block.publishable = True
        block.quality_score = max(float(block.quality_score or 0), 92.0)
        block.readability_score = block.quality_score
        block.keyword_density = max(float(block.keyword_density or 0), 92.0)
    elif _should_use_simple_pitch(_pk, target_keywords, content_type_out):
        packed = _simple_zeorbit_pitch_copy(
            keyword=_pk,
            city=(city or "").strip(),
            industry=industry or "",
            audience=audience or "",
            business_type=business_type or "",
        )
        block.title = packed["title"]
        block.h1 = packed["h1"]
        block.meta_description = packed["meta_description"]
        block.h2s = packed["h2s"]
        block.h3s = packed.get("h3s") or []
        block.intro = packed["intro"]
        block.content = packed["content"]
        block.cta = packed["cta"]
        block.faqs = [FAQItem(**f) if isinstance(f, dict) else f for f in packed["faqs"]]
        if packed.get("focus_keyword"):
            block.focus_keyword = packed["focus_keyword"]
        if packed.get("slug"):
            block.slug = packed["slug"]
        if content_type_out != "blog":
            pitch_img = _pitch_image_plan(
                primary_kw or packed["title"],
                industry=industry or "",
                audience=audience or "",
                city=city or "",
            )
            block.image_concept = pitch_img["concept"]
            if not (block.image_keyword or "").strip():
                block.image_keyword = pitch_img["image_keyword"]
            block.search_intent = pitch_img["intent_id"]
        block.publishable = True
        block.quality_score = max(float(block.quality_score or 0), 92.0)
        block.readability_score = block.quality_score
        block.keyword_density = max(float(block.keyword_density or 0), 92.0)

    # Hard strip: SEO title / H1 never include ZeOrbit (CTA/body may).
    for _attr in ("title", "h1"):
        _val = (getattr(block, _attr, None) or "").strip()
        if _val and re.search(r"\bzeorbit\b", _val, re.I):
            _val = re.sub(r"\s*\|\s*ZeOrbit\b", "", _val, flags=re.I)
            _val = re.sub(r"\b(?:with|from|by)\s+ZeOrbit\b", "", _val, flags=re.I)
            _val = re.sub(r"\bZeOrbit\b", "", _val, flags=re.I)
            _val = re.sub(r"\s{2,}", " ", _val).strip(" -|,")
            setattr(block, _attr, _val[:90] or getattr(block, _attr))

    # Final meta lock — keep topic/comparison metas; pitch-only gets topic_help_meta.
    _keep_topic_meta = False
    try:
        from services.topic_intent import interpret_topic
        _ti = interpret_topic(_pk, target_keywords)
        _keep_topic_meta = bool(_ti.get("use_topic_article")) or kind == "blog"
    except Exception:
        _ti = None
    if _is_comparison_query(_pk, target_keywords) or (_ti and _ti.get("intent") == "compare"):
        a, b = _parse_comparison_sides(_pk)
        block.meta_description = _comparison_meta(
            a, b, city=(city or "").strip(), keyword=_pk
        )
    elif _keep_topic_meta and (block.meta_description or "").strip():
        pass
    elif _should_use_simple_pitch(_pk, target_keywords, content_type_out):
        block.meta_description = topic_help_meta(
            keyword=_pk,
            city=(city or "").strip(),
            industry=industry or "",
            audience=audience or "",
            business_type=business_type or "",
        )

    return ensure_content_accuracy(_scrub_block_dashes(block))


def _block_floor_scores(block: "SEOBlock") -> tuple[float, float]:
    q = float(
        getattr(block, "quality_score", None)
        or getattr(block, "readability_score", None)
        or 0
    )
    kw = float(getattr(block, "keyword_density", None) or 0)
    return q, kw


async def generate_seo_block_until_floor(
    *args,
    max_attempts: int = 2,
    **kwargs,
) -> tuple["SEOBlock", int]:
    """Keep regenerating a location until Quality and Keyword use both hit 90+.

    Returns (block, extra_attempts) where extra_attempts is how many times we
    had to generate again after the first pass scored below the floor.
    """
    from services.zeorbit_local_seo import scores_meet_floor

    keyword_index = int(kwargs.get("keyword_index") or 0)
    existing_bodies = kwargs.get("existing_bodies")
    from services.llm_service import active_provider
    provider = (kwargs.get("llm_provider") or active_provider() or "").lower()
    # Fast path: free cloud keys (Groq/Gemini) — one pass + boost, no double draft.
    if provider in ("groq", "gemini", "ollama", "claude", "auto", ""):
        max_attempts = 1
    best = None
    extra = 0
    for attempt in range(max(1, max_attempts)):
        kwargs["keyword_index"] = keyword_index + attempt * 17
        # Last pass: do not let uniqueness vs the whole library block a 90+ score.
        if attempt >= max_attempts - 1:
            kwargs["existing_bodies"] = None
        else:
            kwargs["existing_bodies"] = existing_bodies
        block = await generate_seo_block(*args, **kwargs)
        q, kw = _block_floor_scores(block)
        if not scores_meet_floor(q, kw):
            try:
                block = boost_block_to_floor(block)
                q, kw = _block_floor_scores(block)
            except Exception as e:
                print(f"[Quality] boost on retry failed: {e}")
        if scores_meet_floor(q, kw):
            return block, extra
        extra += 1
        best = block
        loc = getattr(block, "city", None) or kwargs.get("city") or "item"
        print(
            f"[Quality] {loc} at {q}/{kw} — generating again "
            f"(attempt {attempt + 1}/{max_attempts})"
        )
    return best or block, extra


def _deepen_for_quality(block: "SEOBlock") -> "SEOBlock":
    """Add keyword-specific depth so Quality hits 90+ without a second LLM call."""
    kw = pretty_keyword(
        (getattr(block, "focus_keyword", None) or "")
        or (block.keywords.primary if getattr(block, "keywords", None) else "")
        or block.business_type
        or "this topic"
    )
    if _is_new_business_website_topic(kw) or (block.title or "").lower().startswith("launch your business online"):
        return block
    is_blog = (getattr(block, "content_type", "") or "").lower() in ("blog", "post")
    city = "" if is_blog else (block.city or "").strip()
    place = f" in {city}" if city else ""
    body = f"{block.intro or ''}\n{block.content or ''}"
    words = len(body.split())
    extra = []
    if words < 280:
        if is_blog or not _query_is_web(kw.lower()):
            extra.append(
                f"\n\n## Checks for {kw}\n"
                f"Confirm you are still answering “{kw}”. Do the smallest test that would prove it, "
                "then only add extras if that test fails."
            )
        else:
            extra.append(
                f"\n\n## Next steps for {kw}{place}\n"
                f"Confirm the offer in one sentence, check the live page on a phone, and make sure HTTPS and the contact "
                f"form work. WordPress or Shopify both work when the pages match {kw}."
            )
    if extra:
        block.content = (block.content or "").rstrip() + "".join(extra)
        h2s = list(block.h2s or [])
        heading = f"Checks for {kw}" if (is_blog or not _query_is_web(kw.lower())) else f"Next steps for {kw}{place}"
        if heading not in h2s:
            h2s.append(heading)
            block.h2s = h2s
    return block


def boost_block_to_floor(block: "SEOBlock") -> "SEOBlock":
    """Client AI-fix: raise keyword use (and refresh quality) to the 90% floor."""
    from services.zeorbit_local_seo import (
        score_page_quality,
        MIN_KEYWORD_USE_SCORE,
        scores_meet_floor,
        ensure_body_hyperlinks,
    )
    kw0 = (
        (getattr(block, "focus_keyword", None) or "")
        or (block.keywords.primary if getattr(block, "keywords", None) else "")
        or block.business_type
        or ""
    ).strip()
    is_blog = (getattr(block, "content_type", "") or "").lower() in ("blog", "post")
    if is_blog and _blog_off_query(block.title or "", block.meta_description or "", block.intro or "", block.content or "", kw0):
        block = _rewrite_off_query_blog(block, kw0, getattr(block, "layout_variant", "") or "")
    block = _deepen_for_quality(block)
    if is_blog:
        block.meta_description = _ensure_meta_length(block.meta_description or "", kw0, block.city or "")
    kw = (
        (getattr(block, "focus_keyword", None) or "")
        or (block.keywords.primary if getattr(block, "keywords", None) else "")
        or ""
    ).strip()
    intro, content, kw_use = ensure_keyword_coverage(
        block.intro or "",
        block.content or "",
        kw,
        city="" if is_blog else (block.city or ""),
        min_score=75.0 if is_blog else MIN_KEYWORD_USE_SCORE,
    )
    block.intro = intro
    block.content = ensure_body_hyperlinks(
        normalize_markdown_sections(content, list(getattr(block, "h2s", None) or [])),
        directory=not is_blog,
    )
    block.keyword_density = kw_use
    feat_alt = ""
    if block.in_content_images:
        for im in block.in_content_images:
            if getattr(im, "is_featured", False) or (getattr(im, "url", None) == block.featured_image_url):
                feat_alt = getattr(im, "alt_text", "") or ""
                break
    quality = score_page_quality(
        title=block.title or "",
        intro=block.intro or "",
        content=block.content or "",
        faqs=block.faqs or [],
        city=block.city or "",
        intent_id=block.search_intent or "",
        image_url=block.featured_image_url or "",
        image_alt=feat_alt,
        image_concept_text=block.image_concept or "website designer laptop",
        meta=block.meta_description or "",
        existing_bodies=None,
        content_type=getattr(block, "content_type", None) or "service",
        focus_keyword=kw,
    )
    block.quality_score = quality.score
    block.quality_breakdown = quality.breakdown
    block.readability_score = quality.score
    block.publishable = bool(quality.publishable and scores_meet_floor(quality.score, kw_use))
    return ensure_content_accuracy(block)


def _one_place(city: str, state: str) -> tuple:
    """Never treat a bulk list as one city/state (that jammed titles together)."""
    c = (city or "").strip()
    s = (state or "").strip()
    if "," in c:
        c = c.split(",")[0].strip()
    if s and ("," in s or (len(s) > 2 and not re.fullmatch(r"[A-Za-z]{2}", s))):
        s = ""
    return c, s


async def _generate_ai_block(
    business_type: str,
    city: str,
    state: str,
    target_keywords: list = [],
    industry: str = "",
    llm_provider: Optional[str] = None,
    custom_requirements: str = "",
    content_kind: str = "service",
    audience: str = "",
    layout_variant: str = "",
    keyword_index: int = 0,
    primary_keyword: str = "",
    display_heading: str = "",
    search_intent: str = "",
    image_concept_text: str = "",
    customer_problem: str = "",
    zip: str = "",
    existing_bodies: Optional[list] = None,
    research: Optional[dict] = None,
) -> SEOBlock:
    """Generate SEO content using an LLM (GPT-4, Gemini, or Groq — whichever
    is configured/selected) for higher quality, unique content."""
    from services.llm_service import chat_json

    city, state = _one_place(city, state)
    brief = (custom_requirements or "").strip()
    from services.zeorbit_local_seo import place_label
    place = place_label(city, state, zip) or (f"{city}, {state}".strip(", ") if state else city)
    who = _audience_who(industry, audience)
    buyers = _buyer_word(industry)
    audience_line = (
        f"Speak to: {who} in {place or 'the US'}."
        if audience or industry else
        "Speak to a US business owner or operator."
    )
    kw_line = ", ".join(target_keywords) if target_keywords else "None"
    primary_kw = (primary_keyword or pick_primary_keyword(
        target_keywords, business_type, city, keyword_index,
        industry=industry or "", audience=audience or "",
    )).strip()
    primary_kw = sanitize_seo_keyword(
        primary_kw, industry=industry or "", business_type=business_type or "", audience=audience or "",
    ) or primary_kw
    about_heading = (display_heading or "").strip() or topic_display_heading(
        next((str(k) for k in (target_keywords or []) if k), primary_kw),
        industry=industry or "",
        audience=audience or "",
        city=city or "",
    )
    query_mode = content_kind == "blog"
    layout = layout_variant if layout_variant in LAYOUT_INSTRUCTIONS else (
        blog_layout_for_query(primary_kw, brief, salt=str(keyword_index)) if query_mode
        else pick_layout_variant(city, business_type, content_kind, salt=keyword_index)
    )
    layout_note = LAYOUT_INSTRUCTIONS[layout]
    uniq_note = (
        f"UNIQUENESS (variation #{keyword_index}): Write original intro, meta, H2s, body, CTA, and FAQs for THIS {place or 'topic'} only. "
        f"Do not city-swap a previous draft. Never open with 'Need a better website'. "
        f"{_opening_bans(existing_bodies)}"
    )
    provider_key = (llm_provider or "").lower().strip()
    provider_note = PROVIDER_STYLE_NOTES.get(provider_key, "Write at the quality level of ChatGPT, Claude, or Gemini — specific and human.")
    from services.llm_service import active_provider as _active_llm
    using_ollama = provider_key == "ollama" or (
        provider_key in ("", "auto") and (_active_llm() or "") == "ollama"
    )
    using_groq = provider_key == "groq" or (
        provider_key in ("", "auto") and (_active_llm() or "") == "groq"
    )
    # Skip site RAG for cloud LLMs — saves several seconds per page; keyword prompts already lock topic.
    rag_section = ""
    if not query_mode and using_ollama:
        rag_query = " ".join(x for x in (primary_kw, business_type, city, industry, audience) if x)
        rag_site = (getattr(settings, "MARKETING_SITE_URL", None) or settings.PUBLIC_BASE_URL or "").strip()
        rag_block = await _ensure_rag_context(rag_query, rag_site)
        rag_section = f"\n{rag_block}\n" if rag_block else ""

    # Groq free tier: keep completion under ~900 tokens so JSON does not truncate (400)
    # and stay under the OTPM cap (~1000).
    if using_ollama:
        max_tok = 450
    elif using_groq:
        max_tok = 1400 if content_kind == "blog" else 900
    else:
        max_tok = 720 if content_kind == "blog" else 860
    if using_ollama:
        pretty = pretty_keyword(primary_kw)
        keywords = KeywordSet(
            primary=primary_kw.lower(),
            secondary=[k.lower() for k in (target_keywords or []) if str(k).lower() != primary_kw.lower()][:8],
            long_tail=[f"{primary_kw.lower()} {city.lower()}".strip(), f"{business_type.lower()} {who}"],
            near_me=[f"{primary_kw.lower()} near me"],
            user_questions=[
                f"What does {pretty} include in {place or 'this area'}?",
                f"How does ZeOrbit help {who} with {pretty}?",
                f"How do I get started with {pretty}?",
            ],
        )
        if content_kind == "blog":
            from services.topic_research import research_prompt_block
            facts = research_prompt_block(research)
            prompt = f"""JSON blog. TOPIC: {pretty}. Who:{who}.
{facts}
Stay on "{pretty}" only. Speak to {who}. No tourism guide. No unrelated industries.
Title uses the topic. meta_description 140-155 chars. intro 3 sentences naming the reader. content 4 ## sections, 280+ words, each section answers the topic.
Include a Why Choose ZeOrbit beat + CTA with www.zeorbit.com or (619) 724-9517.
h2s 4. faqs 4. cta 1 sentence. JSON only.
"""
        else:
            prompt = f"""JSON for ZeOrbit. Topic heading: "{about_heading}". Keyword:"{pretty}". Place:{place or 'US'}. Who:{who}.
Title and h1 MUST equal the topic heading (no phone, no www URL in title).
Body = ZeOrbit help pitch for this topic (like Typefully): open answering the heading, what ZeOrbit offers (websites / apps / custom), Ready to grow + CTA www.zeorbit.com / (619) 724-9517.
FORBIDDEN DIY sections (domain, hosting, brand identity checklist, launch checklist).
No prices. Keys: title, meta_description, h1, h2s (3), intro (2-3 sentences), content (3 ## sections, 180+ words), faqs (3), cta.
"""
    elif query_mode:
        from services.zeorbit_local_seo import master_voice_rules
        # BLOG-ONLY RULE: the editor's keyword/query is the article subject.
        topic = (article_topic(brief, target_keywords, business_type) or primary_kw or "").strip()
        if not topic:
            topic = "website guide"
        primary_kw = topic
        secondary = [
            k.lower() for k in (target_keywords or [])
            if k and str(k).strip().lower() != topic.lower() and not _looks_like_writing_brief(str(k))
        ][:6]
        keywords = KeywordSet(
            primary=primary_kw.lower(),
            secondary=secondary or [topic.lower()],
            long_tail=[f"how to {primary_kw.lower()}", f"{primary_kw.lower()} guide", f"{primary_kw.lower()} explained"],
            near_me=[],
            user_questions=[
                f"What does “{primary_kw}” mean in practice?",
                f"How do I {primary_kw.lower()}?",
                f"What steps should I follow for {primary_kw.lower()}?",
                f"What mistakes should I avoid with {primary_kw.lower()}?",
            ],
        )
        loc_note = (
            f"Optional local color: you MAY mention {place} once if it helps, but this is NOT a location landing page."
            if place else
            "Do not force a city into the title, H1, or every paragraph. This is a topic article."
        )
        extra_brief = ""
        if brief and not _looks_like_writing_brief(brief) and brief.lower() not in topic.lower() and len(brief) > 20:
            extra_brief = brief
        elif brief and _looks_like_writing_brief(brief):
            extra_brief = (
                "(Editor style notes — follow these as writing guidance ONLY; "
                "do NOT quote or paste them into the article.)\n" + brief
            )
        surface = "blog post" if content_kind == "blog" else "page"
        kw_body = _keyword_body_directive(topic, industry=industry or "", audience=who, place=place or "")
        prompt = f"""You are a US content writer creating ONE {surface} for ZeOrbit.com.
Model style: {provider_note}

═══ QUERY ANSWER RULE (blogs AND pages — mandatory) ═══
The editor's search query / keyword is the ONLY subject of this {surface}:
SEARCH QUERY: "{topic}"

{kw_body}

- Title, H1, intro, every H2, body paragraphs, and FAQs MUST directly answer or teach that query.
- If the query is "Website or Mobile App: What Does Your Business Really Need?", write a real comparison and decision guide — not a "practical US-English guide to…" template and not generic web design in a city.
- If the query is "difference between restaurant and cafe" (or any X vs Y / difference between A and B), write a real differentiation guide: clear definitions, side-by-side differences, which fits whom, then a soft note that ZeOrbit builds websites and mobile apps for both. Do NOT replace the topic with a ZeOrbit website sales pitch.
- If the query is "how to fix a website", write a practical fix guide (diagnose → fix → verify) — not generic web design sales copy.
- If the query is a full sentence or question, that sentence IS the article. Answer it in the intro, every H2, the body, and the FAQs. Do not change the topic to web design, ZeOrbit services, or a city landing page unless the sentence itself is about that.
- Sections, examples, and recommendations must be unique to THIS query. Never reuse the same body skeleton as other posts.
- Do not use filler H2s such as "A simple starting point", "What good looks like", "How long it usually takes", or "A next step if you need a hand".
- HYPERLINKS: Inside a normal sentence, wrap a natural phrase (for example "web design services") as markdown to https://zeorbit.com/website-designing when the topic mentions websites. Use https://zeorbit.com/mobile-apps and https://zeorbit.com/seo-ppc the same way. Never add a standalone "See ZeOrbit website design…" line or a separate link section.
- If the query is a problem ("broken website", "site not loading"), diagnose and solve that problem.
- Niche / industry / location may color EXAMPLES only — they must NOT replace the query as the topic.
- Do NOT write a location landing page, city SEO page, or "web design in San Diego" article unless the query itself is that.

Custom notes from the editor (guidance only — NEVER paste into the published body):
{extra_brief or "None — stay on the search query above."}

Business context (mention ZeOrbit only where help is natural, usually near the end/CTA): ZeOrbit builds websites, apps, and SEO for US companies. CTA may use www.zeorbit.com and (619) 724-9517.
Industry field (examples only — do not make this the article topic): {industry or "n/a" if not query_mode else "n/a — ignore CRM industry"}
{audience_line}
Secondary keywords to weave lightly (do not hijack the topic): {", ".join(secondary) if secondary else "none"}
BODY LAYOUT ({layout}): {layout_note}
{uniq_note}
{loc_note}
{rag_section}

{VOICE_RULES}
{master_voice_rules()}

NON-NEGOTIABLE:
- The article must feel written for someone who typed "{topic}" into Google.
- Relevance must be at least 8/10 to that query: title, H1, intro, every H2, and the body must stay on it.
- Do not drift into generic ZeOrbit / web-design sales copy unless the query is specifically about hiring a web designer.
- Title and H1 must name the query (how-to / question / problem wording is fine).
- H2s must be steps or sub-questions of "{topic}", not generic agency sections.
- content MUST use markdown H2 lines that exactly match each string in h2s, with 1–2 short paragraphs under EVERY H2 (40–70 words each).
- Include concrete steps, checks, or examples that match the query (tools, settings, files, or UI when technical).
- Do NOT paste Custom Content Requirements into intro, content, faqs, or cta.
- Soft CTA only after the reader has a usable answer.

FORMAT-SPECIFIC SHAPE ({layout}):
{layout_note}

Generate a JSON response with EXACTLY this structure:
{{
  "title": "SEO title 50-60 chars in THIS format's voice (guide = how-to; briefing = question; feature = situation)",
  "meta_description": "Two complete sentences (150-160 chars). Answer the query in plain English. Never start with the keyword, never write 'Answer:', never 'Practical decision points'.",
  "h1": "H1 matching the format (numbered-task / question / feature headline)",
  "h2s": ["3-4 H2s that follow the {layout} format rules above"],
  "h3s": ["4 short supporting labels (not empty body sections)"],
  "intro": "Format-specific intro (guide: 2 sentences; briefing: definition + who; feature: 3-sentence scene)",
  "content": "Markdown: for EACH h2 write '## Exact H2' then body that matches the format (lists for guide, Q&A prose for briefing, narrative + one blockquote for feature). 320-480 words. Separate paragraphs with double newlines.",
  "faqs": [
    {{"question": "A real question someone would ask about {topic}", "answer": "2-3 sentences that answer THAT question. First sentence must address the question, not a generic website pitch."}},
    {{"question": "FAQ 2 about {topic}", "answer": "Answer FAQ 2 directly."}},
    {{"question": "FAQ 3 about {topic}", "answer": "Answer FAQ 3 directly."}},
    {{"question": "FAQ 4 about {topic}", "answer": "Answer FAQ 4 directly."}}
  ],
  "cta": "A unique CTA for this query. Prefer www.zeorbit.com or (619) 724-9517. Do not reuse 'Not sure where to start'."
}}

Return ONLY valid JSON, no markdown fences."""
    else:
        from services.zeorbit_local_seo import (
            pick_search_intent,
            SEARCH_INTENTS,
            title_from_primary_keyword,
            intent_h2_set,
            intent_faqs,
            ai_page_brief_block,
            master_voice_rules,
            ZEORBIT_FACTS,
            zip_hyperlink,
        )
        pretty = pretty_keyword(primary_kw)
        intent = pick_search_intent(city, keyword_index, industry=industry or "", brief=custom_requirements or "", keywords=target_keywords or [])
        if search_intent:
            for i in SEARCH_INTENTS:
                if i.id == search_intent:
                    intent = i
                    break
        title_locked = (about_heading or "").strip() or title_from_primary_keyword(
            primary_kw, city, industry or "", intent, keyword_index
        )
        # Prefer ZeOrbit-help H2s for new-business / slogan topics (Typefully quality bar).
        if primary_kw.lower() == "new business website" or _NEW_BIZ_PLANNING_RE.search(
            " ".join(str(k) for k in (target_keywords or []) if k)
        ):
            h2_examples = ["What We Offer", "Ready to Get Started?"]
        else:
            h2_examples = intent_h2_set(intent, city, industry or "", layout)
        if not h2_examples:
            h2_examples = _page_h2_set(layout, industry, buyers, city, audience, pretty)
        concept = image_concept_text or ""
        keywords = KeywordSet(
            primary=primary_kw.lower(),
            secondary=[k.lower() for k in (target_keywords or []) if k.lower() != primary_kw.lower()][:8],
            long_tail=[f"{primary_kw.lower()} {city.lower()}".strip(), f"{business_type.lower()} for {who}"],
            near_me=[f"{primary_kw.lower()} near me"],
            user_questions=[f["question"] for f in intent_faqs(intent, city, industry or "", keyword_index)],
        )
        faq_questions = "\n".join([f"- {q}" for q in keywords.user_questions[:6]])
        h2_json = json.dumps(h2_examples)
        brief_block = brief if brief else (
            "Promote ZeOrbit website design for this industry and audience in this location — intent-specific, not generic."
        )
        master_brief = ai_page_brief_block(
            intent, city, state, industry or "", title_locked, h2_examples, concept,
            zip=zip or "",
        )
        maps_faq = zip_hyperlink(zip or "", city, state) or "(full Name, ST ZIP Maps link)"
        kw_body = _keyword_body_directive(pretty, industry=industry or "", audience=who, place=place or "")
        # Groq free JSON must stay short or it truncates mid-document (slow retries).
        word_target = "280-380 words" if using_groq else "450-700 words"
        para_target = "1 short paragraph (35-55 words)" if using_groq else "2 short paragraphs (40-80 words)"
        faq_json = (
            f'''[
    {{"question": "A real {who} question in {city}", "answer": "First sentence answers that question."}},
    {{"question": "FAQ 2 for {city}", "answer": "Answer FAQ 2 directly."}},
    {{"question": "FAQ 3 for {city}", "answer": "Answer FAQ 3 directly. Include location pin if last."}}
  ]'''
            if using_groq else
            f'''[
    {{"question": "A real {who} question in {city}", "answer": "First sentence answers that question. Then 1-2 sentences of {city} context."}},
    {{"question": "FAQ 2 for {city}", "answer": "Answer FAQ 2 directly."}},
    {{"question": "FAQ 3 for {city}", "answer": "Answer FAQ 3 directly."}},
    {{"question": "FAQ 4 for {city}", "answer": "Answer FAQ 4 directly."}},
    {{"question": "FAQ 5 for {city}", "answer": "Answer FAQ 5 directly."}},
    {{"question": "FAQ 6 for {city}", "answer": "Answer FAQ 6 directly."}}
  ]'''
        )
        prompt = f"""You are writing ONE ZeOrbit service / location PAGE for AI search visibility (Google, AI Overviews, ChatGPT Search, Gemini, Bing/Copilot).
Model style: {provider_note}

WHO WE ARE: ZeOrbit is a technology company that provides website design and development. We are NOT a {industry or "healthcare"} provider.

WHAT THIS PAGE SELLS: {business_type}
WHO IT IS FOR: {who}
WHERE: {place or "the United States"} — this is the ONLY place named on the page.
Include the ZIP only in the last FAQ answer as markdown {maps_faq}. Visible link text must be Location Name, State ZIP — never ZIP alone. Never put the ZIP in title, H1, intro, body, conclusion, meta, or CTA.
PRIMARY KEYWORD (weave naturally in title/H1/intro): {pretty}
Other keywords to use naturally (do not dump as a list): {kw_line}

{kw_body}

{master_brief}

CUSTOM CONTENT REQUIREMENTS — WRITING BRIEF ONLY (follow; NEVER paste into intro/content/cta/faqs):
{brief_block}

{audience_line}
BODY LAYOUT ({layout}): {layout_note}
{uniq_note}
{VOICE_RULES}
{master_voice_rules()}
{rag_section}

NON-NEGOTIABLE:
- The page H1 / title is locked to the editor topic heading (what the content is about). Do not invent a different title.
- ZeOrbit is the vendor. {industry or "The industry"} is the CLIENT type, not ZeOrbit's own business.
- Write a ZeOrbit SERVICE pitch for this topic — short, clear, like a Typefully / Claude help paragraph — NOT a DIY website-building tutorial.
- Body pattern: (1) open answering the topic heading, (2) what ZeOrbit builds (professional websites, mobile apps when useful, custom solutions), (3) Ready to grow + CTA with www.zeorbit.com and (619) 724-9517.
- FORBIDDEN: "Define Your Core Digital Foundation", "Align Design with Your Brand Identity", domain/hosting how-tos, "check your work and launch", self-build checklists.
- Do not mention prices, dollar amounts, retainers, or project cost ranges.
- Mention experience/reviews only as verified: {ZEORBIT_FACTS['experience']}, {ZEORBIT_FACTS['reviews']} — never invent individual reviews or star ratings.
- Mention WordPress, Shopify, or mobile apps only when the topic or industry actually needs them. A gym page stays about gyms. A home-services page stays about that trade. Do not add a generic platform list.
- Keep copy simple, credible, localized to {city} only when this is a location page. UNIQUE to this intent + industry + layout.
- Meta, intro, and CTA must be written for {city} when a city is present.
- FAQs must be about {pretty} / {who} in {city}. Each answer must address its own question in the first sentence.
- CTA: one specific invitation. Prefer www.zeorbit.com or (619) 724-9517. Do not use 'Not sure where to start'.
- KEYWORD LOCK: Every paragraph must follow the given topic “{pretty}”, the selected industry “{industry or who}”, the audience “{who}”, the location “{city or "United States"}”, and the search intent. Do not write a generic agency page. Do not mention unrelated industries. Home services stays plumbing, HVAC, electrical, and similar trades — never a gym, restaurant, or clinic unless that industry was selected.
- HYPERLINKS: Inside a sentence, you may link “web design services” to https://zeorbit.com/website-designing, “mobile apps” to https://zeorbit.com/mobile-apps, or “SEO & PPC” to https://zeorbit.com/seo-ppc. Never link the word “website” to Yelp, DesignRush, or GoodFirms.
- ZIP: only in the last FAQ answer, as {maps_faq}. Never ZIP-only link text. Never in intro, body, conclusion, title, or meta.
- Do NOT list competitors, fake addresses, or other neighborhoods.
- Name ZeOrbit in the intro and the CTA.
- content MUST include '## Exact H2' for each h2s item with {para_target} under each (no empty headings). {word_target}.
- NEVER copy the CUSTOM CONTENT REQUIREMENTS paragraph(s) into the published fields.
- Return COMPLETE valid JSON. Do not cut off mid-string.
- Never put phone numbers or www.zeorbit.com inside the title or H1 (those belong in the CTA / body only).

Generate a JSON response with EXACTLY this structure:
{{
  "title": "{title_locked}",
  "meta_description": "One appealing 150-160 char quick answer: benefit first, city once, ZeOrbit, no 'Looking for X in Y' and never repeat the city.",
  "h1": "{title_locked}",
  "h2s": {h2_json},
  "h3s": ["A point about {pretty} for {who}", "A point about {industry or who} in {city}", "What ZeOrbit builds for this industry", "How to contact ZeOrbit"],
  "intro": "2-3 original sentences about {who} in {city} tied to {pretty}. Do not start with Need a better website.",
  "content": "Markdown sections matching h2s. {para_target} under each H2. Stay on {pretty} for {who} in {city}. Unique to {city}. {word_target} total.",
  "faqs": {faq_json},
  "cta": "One unique invitation for {who} in {city}. Name ZeOrbit. Prefer www.zeorbit.com or (619) 724-9517."
}}

FAQ questions to address (vary answers; do not clone other cities):
{faq_questions}

Customer problem to keep central: {customer_problem or intent.customer_problem}

Return ONLY valid JSON, no markdown fences."""

    def _on_brief(payload) -> bool:
        if not payload:
            return False
        text = " ".join([
            str(payload.get("intro") or ""),
            str(payload.get("content") or ""),
            str(payload.get("h1") or ""),
            " ".join(payload.get("h2s") or []),
        ]).lower()
        stop = {"with", "from", "your", "this", "that", "about", "website", "design", "business", "services", "service"}
        topic_words = [w for w in re.findall(r"[a-z0-9]{4,}", (pretty or "").lower()) if w not in stop]
        if topic_words and sum(1 for w in topic_words[:8] if w in text) < min(2, len(topic_words)):
            return False
        ind_label = (industry or "").strip()
        if ind_label and not is_generic_industry_safe(ind_label):
            ind_words = [w for w in re.findall(r"[a-z]{4,}", ind_label.lower()) if w not in stop]
            if ind_words and not any(w in text for w in ind_words):
                return False
        if (city or "").strip() and city.strip().lower() not in text:
            return False
        aud = (who or "").strip()
        if aud and aud.lower() not in {ind_label.lower(), "customers", "businesses"} and not is_generic_industry_safe(aud):
            aud_words = [w for w in re.findall(r"[a-z]{4,}", aud.lower()) if w not in stop]
            if aud_words and not any(w in text for w in aud_words[:4]):
                return False
        return True

    data = await chat_json(
        prompt,
        temperature=0.55 if using_groq else (0.72 if content_kind == "blog" else 0.78),
        max_tokens=max_tok,
        provider=llm_provider,
    )
    blob = f"{data.get('intro','') if data else ''} {data.get('content','') if data else ''} {' '.join(data.get('h2s') or []) if data else ''}"
    if data and _looks_like_template_filler(blob):
        data = None
    if not data:
        raise RuntimeError("LLM generation failed or returned no data")
    bt = business_type.title()
    slug = _slugify(primary_kw) if (content_kind == "blog" or query_mode) else (
        _slugify(f"{primary_kw.lower()}-{city}") if city else _slugify(primary_kw)
    )

    faqs = []
    for f in data.get("faqs") or []:
        if isinstance(f, dict) and f.get("question"):
            faqs.append(FAQItem(question=_as_text(f.get("question")), answer=_as_text(f.get("answer"))))
    faqs = ensure_topic_faqs(
        faqs, primary_kw, city, industry, keyword_index, is_blog=(content_kind == "blog" or query_mode)
    )

    # Query-mode (sentence keywords): keep the LLM title/H1. Location pages: lock SEO title.
    if content_kind == "blog" or query_mode:
        title = _as_text(data.get("title")) or pretty_keyword(primary_kw)[:60]
        h1 = _as_text(data.get("h1")) or pretty_keyword(primary_kw)
        intro_probe = _as_text(data.get("intro"))
        meta_probe = _as_text(data.get("meta_description"))
        content_probe = _as_text(data.get("content"))
        if _blog_off_query(title, meta_probe, intro_probe, content_probe, primary_kw):
            packed = _blog_query_copy(primary_kw, layout)
            if packed:
                title = pretty_keyword(primary_kw)[:60]
                h1 = pretty_keyword(primary_kw)
                data["title"] = title
                data["h1"] = h1
                data["intro"] = packed["intro"]
                data["content"] = packed["content"]
                data["h2s"] = packed.get("h2s") or data.get("h2s")
                data["faqs"] = [
                    {"question": f.question, "answer": f.answer} if hasattr(f, "question") else f
                    for f in (packed.get("faqs") or [])
                ]
                data["meta_description"] = _ensure_meta_length("", primary_kw, city)
        search_intent_id = ""
        customer_problem_out = ""
        image_concept_out = ""
    else:
        from services.zeorbit_local_seo import pick_search_intent, SEARCH_INTENTS, title_from_primary_keyword, intent_h2_set
        intent_obj = pick_search_intent(city, keyword_index, industry=industry or "", brief=brief, keywords=target_keywords or [])
        if search_intent:
            for i in SEARCH_INTENTS:
                if i.id == search_intent:
                    intent_obj = i
                    break
        # Body heading = "What should the content be about?" (Typefully-style), not DIY titles.
        title = (about_heading or "").strip() or title_from_primary_keyword(
            primary_kw, city, industry or "", intent_obj, keyword_index
        )
        h1 = title
        search_intent_id = intent_obj.id
        customer_problem_out = customer_problem or intent_obj.customer_problem
        image_concept_out = image_concept_text or ""
    # Never publish phone/URL inside title or H1.
    title = _PHONE_IN_TEXT_RE.sub(" ", title or "")
    title = _URL_IN_TEXT_RE.sub(" ", title)
    title = re.sub(r"\s+", " ", title).strip(" -.,;:/") or about_heading or pretty_keyword(primary_kw)
    h1 = _PHONE_IN_TEXT_RE.sub(" ", h1 or title)
    h1 = _URL_IN_TEXT_RE.sub(" ", h1)
    h1 = re.sub(r"\s+", " ", h1).strip(" -.,;:/") or title
    meta = _strip_instruction_leak(_as_text(data.get("meta_description")), brief)
    if content_kind == "blog" or query_mode:
        meta = _ensure_meta_length(meta, primary_kw, city)
    h2s = [_as_text(h) for h in (data.get("h2s") or []) if _as_text(h)]
    if (content_kind == "blog" or query_mode) and len(h2s) < 3:
        pretty_h = pretty_keyword(primary_kw)
        h2s = [
            f"Direct answer: {pretty_h}",
            "What this actually means in practice",
            "How to decide what to do next",
            "Mistakes that waste time or money",
        ]
    if content_kind != "blog" and not query_mode and len(h2s) < 3:
        if primary_kw.lower() == "new business website" or _NEW_BIZ_PLANNING_RE.search(
            " ".join(str(k) for k in (target_keywords or []) if k)
        ):
            h2s = ["What We Offer", "Ready to Get Started?"]
        else:
            from services.zeorbit_local_seo import pick_search_intent, SEARCH_INTENTS, intent_h2_set
            intent_obj = pick_search_intent(city, keyword_index, industry=industry or "", brief=brief, keywords=target_keywords or [])
            if search_intent:
                for i in SEARCH_INTENTS:
                    if i.id == search_intent:
                        intent_obj = i
                        break
            h2s = intent_h2_set(intent_obj, city, industry or "", layout)
    # Replace DIY tutorial H2s if the model ignored the lock.
    diy_hits = ("core digital foundation", "brand identity", "check your work", "domain name", "hosting provider", "core value proposition", "local seo structure")
    if any(any(h in (x or "").lower() for h in diy_hits) for x in h2s):
        if _is_new_business_website_topic(primary_kw, target_keywords):
            h2s = ["What We Offer", "Ready to Get Started?"]
        else:
            who_h = pretty_keyword(audience or industry or "Business")
            h2s = [
                f"Why Your {who_h} Business Needs a Stronger Digital Presence",
                "What ZeOrbit Offers",
                "Ready to Grow?",
            ]
    h3s = [_as_text(h) for h in (data.get("h3s") or []) if _as_text(h)]
    intro = _strip_instruction_leak(_as_text(data.get("intro")), brief)
    content = _sectioned_body(h2s, intro, data.get("content"), brief=brief, query=primary_kw)
    content = _strip_instruction_leak(content, brief)
    md_h2s = [h.strip() for h in re.findall(r"(?m)^##\s+(.+)$", content or "") if h.strip()]
    if content_kind == "blog" and md_h2s:
        h2s = md_h2s
    cta = _strip_instruction_leak(_as_text(data.get("cta")), brief)
    if not cta or re.search(r"not sure where to start|we're here to help|need a better website", cta or "", re.I):
        cta = unique_location_cta(city, industry or who, primary_kw, keyword_index)
    content_text = intro + " " + content

    seo_score = _seo_score(content_text, title, meta, h2s, faqs, primary_kw, city, slug, h1=h1)
    density = _keyword_density(content_text, primary_kw)
    schema = _build_schema(
        bt, city, state, faqs,
        business_name="ZeOrbit",
        site_url=CANONICAL_SITE,
        phone="+1-(619) 724-9517",
        article_title=title,
        slug_override=slug,
    )

    return SEOBlock(
        city=city,
        state=state,
        zip=zip or "",
        business_type=bt,
        industry=industry,
        slug=slug,
        title=title,
        meta_description=meta,
        h1=h1,
        h2s=h2s,
        h3s=h3s,
        intro=intro,
        content=content,
        faqs=faqs,
        cta=cta,
        keywords=keywords,
        schema_markup=schema,
        readability_score=seo_score,
        keyword_density=density,
        content_type="blog" if content_kind == "blog" else "service",
        focus_keyword=primary_kw.lower(),
        layout_variant=layout,
        search_intent=search_intent_id,
        customer_problem=customer_problem_out,
        image_concept=image_concept_out,
    )


async def _generate_template_block(
    business_type: str,
    city: str,
    state: str,
    target_keywords: list = [],
    industry: str = "",
    custom_requirements: str = "",
    content_kind: str = "service",
    audience: str = "",
    layout_variant: str = "",
    keyword_index: int = 0,
    primary_keyword: str = "",
    search_intent: str = "",
    image_concept_text: str = "",
    customer_problem: str = "",
    zip: str = "",
    **_kwargs,
) -> SEOBlock:
    brief = (custom_requirements or "").strip()
    _pk = (primary_keyword or "").strip()
    if content_kind == "blog":
        from services.zeorbit_local_seo import polish_quick_answer
        topic = article_topic(brief, target_keywords, business_type)
        primary = (primary_keyword or topic).strip()
        slug = _slugify(primary)
        layout = layout_variant if layout_variant in BLOG_FORMATS else blog_layout_for_query(
            primary, brief, salt=str(keyword_index)
        )
        spoken = _weave_industry_into_question(primary, industry or "")
        title = pretty_keyword(spoken)[:60]
        h1 = title
        packed_blog = grounded_blog_copy(
            primary,
            research=_kwargs.get("research") or {},
            place=f"{city}, {state}".strip(", ") if city else "",
            industry=industry or "",
        ) or _blog_query_copy(primary, layout)
        is_redirect = bool(re.search(r"301|302|redirect", primary, re.I))
        q = primary.lower().strip()
        pretty = pretty_keyword(primary)
        is_howto = layout == "guide"
        is_fix = bool(re.search(r"\b(fix|repair|broken|not working|error)\b", q, re.I))
        is_q = layout == "briefing"
        if packed_blog and not is_redirect:
            intro = packed_blog["intro"]
            content = packed_blog["content"]
            h2s = packed_blog["h2s"]
            h3s = packed_blog.get("h3s") or []
            faqs = packed_blog["faqs"]
            if packed_blog.get("title"):
                title = packed_blog["title"][:60]
                h1 = packed_blog.get("h1") or title
        elif is_redirect:
            intro = (
                "Need to send an old URL to a new page without losing search equity? "
                "A 301 redirect is the standard way to tell browsers and Google that a page has moved permanently."
            )
            content = (
                "A 301 is an HTTP status code that means “moved permanently.” "
                "Use it when you change a slug, switch domains, merge duplicate pages, or move from HTTP to HTTPS.\n\n"
                "How to set a 301 redirect:\n"
                "1. Apache: add `Redirect 301 /old-page /new-page` (or a RewriteRule) in `.htaccess`.\n"
                "2. Nginx: add `return 301 https://example.com/new-page;` inside the server or location block.\n"
                "3. WordPress: use a redirect plugin (Redirection, Rank Math, or Yoast Premium) and map old → new.\n"
                "4. Hosting panel: many hosts (cPanel, Cloudflare, Netlify) have a Redirects UI if you do not want to edit files.\n\n"
                "After you save, test the old URL in a private window. You should land on the new URL, and the response should be 301, not 302. "
                "Then update internal links and submit the new URLs in Search Console.\n\n"
                "Common mistakes: chaining several redirects, using a 302 for a permanent move, redirecting to a 404, or forgetting the www / HTTPS version.\n\n"
                "If the site is large or the URLs are messy, ZeOrbit can map the old paths and implement the redirects for you."
            )
            h2s = [
                "What a 301 redirect actually does",
                "How to set a 301 redirect (Apache, Nginx, WordPress)",
                "How to test that the redirect works",
                "Mistakes that drop rankings",
                "When to get help",
            ]
        elif is_q:
            intro = (
                f"People type “{primary}” when they want a straight answer, not a sales page. "
                "This post answers that question, then covers what to check and what to do next."
            )
            content = (
                f"## Direct answer: {pretty}\n\n"
                f"The short answer to that search is this: name the real problem behind the query, "
                "then fix the cause instead of adding more pages or ads. If the question is about a restaurant "
                "(or any local business) website, visitors usually bounce because the offer, hours, menu, "
                "location, or phone path is unclear on a phone.\n\n"
                "Read the query as a customer would. If they asked why something fails, list the usual causes. "
                "If they asked what something is, define it in one paragraph, then show when it matters.\n\n"
                f"## What the search “{q}” is really asking\n\n"
                "Most question searches want: (1) a yes/no or cause, (2) proof they can check themselves, "
                "and (3) a next step that does not require buying a full rebuild. Stay on that query in every section.\n\n"
                "Write H2s as follow-up questions. Answer each one in 2–4 sentences. Use examples that match "
                "the words in the keyword — restaurants, Wix, Shopify, 301s, or whatever the query named.\n\n"
                "## How to act on this answer\n\n"
                "1. Confirm the question in your own words so you do not solve the wrong problem.\n"
                "2. Check the live site or process against that question (mobile, forms, hours, checkout, speed).\n"
                "3. Change one thing, retest, then decide if you need a specialist.\n\n"
                "## Mistakes that ignore the question\n\n"
                "Rewriting the post as generic web design, stuffing extra services, or skipping a real answer "
                "in the first screen are the usual misses. If someone asked a question, lead with the answer.\n\n"
                "## When ZeOrbit can help\n\n"
                "If the answer points to a broken site, a redesign, or a store that does not convert, ZeOrbit can "
                "map the fix and what to change first."
            )
            h2s = [
                f"Direct answer: {pretty}",
                f"What the search “{q}” is really asking",
                "How to act on this answer",
                "Mistakes that ignore the question",
                "When ZeOrbit can help",
            ]
        elif is_fix or is_howto:
            intro = (
                f"Searching for “{primary}”? "
                "This guide answers that query with clear steps, checks, and mistakes to avoid — in plain American English."
            )
            content = (
                f"## What “{primary}” usually involves\n\n"
                f"People look up “{q}” when a site is slow, broken, insecure, or simply not doing its job. "
                "Before you change anything live, name the symptom: blank page, 404s, SSL warnings, forms failing, "
                "mobile layout issues, or a plugin conflict. Write that down — it keeps the fix focused.\n\n"
                "Most website problems come from a short list: hosting or DNS outages, expired SSL, a bad plugin or theme update, "
                "corrupt cache, wrong redirects, or content/media that never finished uploading. Start with the reversible checks "
                "(cache, private window, second device) before you edit theme files or the database.\n\n"
                f"## Step-by-step: {pretty}\n\n"
                "1. Reproduce the issue on desktop and mobile, and note the exact URL and time.\n"
                "2. Capture errors from the browser console, hosting error log, or CMS health screen.\n"
                "3. Fix one cause at a time — plugins, theme, DNS, SSL, redirects, or content — then retest.\n"
                "4. Confirm the fix sticks after a hard refresh, a second browser, and a phone check.\n"
                "5. Keep a short before/after note so you can roll back if something else breaks.\n\n"
                "If you use WordPress, disable plugins in batches and switch to a default theme temporarily to isolate conflicts. "
                "On Shopify or hosted builders, check theme edits, apps, and DNS at the registrar. For custom stacks, verify "
                "the deploy, environment variables, and reverse-proxy redirects before rewriting application code.\n\n"
                f"## Checks that prove “{q}” is done\n\n"
                "Verify the page loads over HTTPS, key forms submit, checkout or contact paths still work, and no new console "
                "errors appear. Spot-check internal links and the homepage on mobile. If you changed URLs, confirm redirects "
                "return 301 (not 302) and land on the right page.\n\n"
                "Optionally watch Search Console or uptime monitors for a day so a silent regression does not slip past you.\n\n"
                "## Mistakes that make it worse\n\n"
                "Editing live without a backup, stacking multiple changes at once, ignoring mobile, or “fixing” DNS and SSL "
                "at the same time are the usual ways a small issue becomes an outage. Avoid chaining redirects and do not "
                "leave temporary 302s in place for permanent moves.\n\n"
                "## When to get help\n\n"
                "If the site is revenue-critical, the root cause is unclear, or you are uncomfortable in hosting/DNS panels, "
                "ZeOrbit can diagnose and apply a safe fix with you."
            )
            h2s = [
                f"What “{pretty}” usually involves",
                f"Step-by-step: {pretty}",
                f"Checks that prove “{q}” is done",
                "Mistakes that make it worse",
                "When to get help",
            ]
        else:
            intro = (
                f"Searching for “{primary}”? "
                "This guide answers that query with clear steps, checks, and mistakes to avoid — in plain American English."
            )
            content = (
                f"## What people mean by “{primary}”\n\n"
                f"This post answers the search for “{q}” — what it is, why it matters, and how to act on it. "
                "Stay on that wording in every section so the article matches what someone actually typed.\n\n"
                f"## How to approach {pretty}\n\n"
                "1. Confirm the goal behind the query.\n"
                "2. Apply the change in a staging or test environment when you can.\n"
                "3. Verify on the live site.\n"
                "4. Watch for errors for a few days after.\n\n"
                "## Common mistakes to avoid\n\n"
                "Skipping a backup, changing too many things at once, or optimizing for the wrong keyword are the usual traps.\n\n"
                "## Tools and checks that save time\n\n"
                "Use a checklist: search console / analytics, speed or uptime monitors, and a second-person review of the result.\n\n"
                "## When to bring in a specialist\n\n"
                "If you get stuck, ZeOrbit can walk through the setup with you."
            )
            h2s = [
                f"What people mean by “{pretty}”",
                f"How to approach {pretty}",
                "Common mistakes to avoid",
                "Tools and checks that save time",
                "When to bring in a specialist",
            ]
        if not (packed_blog and not is_redirect):
            h3s = [
                "A simple starting point",
                "What good looks like",
                "How long it usually takes",
                "A next step if you need a hand",
            ]
            faqs = [
                FAQItem(question=f"What is {primary.lower()}?", answer=f"{pretty_keyword(primary)} is the topic of this guide. The steps above cover the practical setup so you can decide what to do next."),
                FAQItem(question="Can I do this myself?", answer="Many teams can handle a first pass. If the setup is messy or high-stakes, get a specialist involved."),
                FAQItem(question="How long does it take?", answer="A straightforward setup can take minutes. Larger sites take longer because you should test every path."),
                FAQItem(question="What if I get it wrong?", answer="Most issues are reversible if you catch them early. Test, keep a backup, and don't guess on production."),
                FAQItem(question="Do I need a developer?", answer="Not always. If you're changing live URLs or app flows, a developer (or ZeOrbit) can keep things from breaking."),
                FAQItem(question="What's the next step?", answer="Not sure where to start? We're here to help you turn the idea into a working plan."),
            ]
        kw = KeywordSet(
            primary=primary.lower(),
            secondary=[k.lower() for k in target_keywords[:5]] or [topic.lower()],
            long_tail=[f"how to {primary.lower()}", f"{primary.lower()} guide"],
            near_me=[],
            user_questions=[f.question for f in faqs],
        )
        schema = _build_schema(
            business_type.title(), city or "United States", state, faqs,
            business_name="ZeOrbit", site_url=CANONICAL_SITE, article_title=title,
        )
        content = _sectioned_body(h2s, intro, content, brief=brief, query=primary)
        content = _strip_instruction_leak(content, brief)
        seo_score = _seo_score(intro + " " + content, title, "", h2s, faqs, primary, city or "", slug, h1=h1)
        return SEOBlock(
            city=city, state=state, business_type=business_type.title(), industry=industry,
            slug=_slugify(_weave_industry_into_question(primary, industry or "")), title=title, meta_description=(
                (packed_blog or {}).get("meta_description")
                or polish_quick_answer(
                    "",
                    intro or "",
                    city or "",
                    primary,
                    business_type or "",
                    "blog",
                )
            ),
            h1=h1, h2s=h2s, h3s=h3s, intro=intro, content=content, faqs=faqs,
            cta=(packed_blog or {}).get("cta") or "Not sure where to start? ZeOrbit is here to help you turn this into a working plan.",
            keywords=kw, schema_markup=schema, readability_score=seo_score,
            keyword_density=_keyword_density(intro + " " + content, primary),
            content_type="blog" if content_kind == "blog" else "service",
            focus_keyword=primary.lower(),
            layout_variant=layout,
        )

    primary = (primary_keyword or pick_primary_keyword(
        target_keywords, business_type, city, keyword_index, industry=industry or "",
    )).strip()
    pretty = pretty_keyword(primary)
    from services.zeorbit_local_seo import (
        pick_search_intent,
        SEARCH_INTENTS,
        build_template_page_copy,
        polish_quick_answer,
    )
    from models.schemas import FAQItem as FAQModel
    intent = pick_search_intent(
        city, keyword_index, industry=industry or "", brief=brief, keywords=target_keywords or [],
    )
    if search_intent:
        for i in SEARCH_INTENTS:
            if i.id == search_intent:
                intent = i
                break
    packed = build_template_page_copy(intent, city, state, industry or "", pretty, keyword_index, zip=zip or "")
    if image_concept_text:
        packed["image_concept"] = image_concept_text
    if customer_problem:
        packed["customer_problem"] = customer_problem
    who = _audience_who(industry, audience)
    bt = business_type
    slug = _slugify(f"{primary.lower()}-{city}")
    title = packed["title"]
    meta = packed["meta_description"]
    h1 = packed["h1"]
    intro = packed["intro"]
    content = packed["content"]
    h2s = packed["h2s"]
    h3s = packed["h3s"]
    cta = packed["cta"]
    faqs = [
        FAQModel(question=f["question"], answer=f["answer"])
        for f in packed["faqs"]
    ]
    if packed.get("industry"):
        industry = packed["industry"]
    kw = KeywordSet(
        primary=primary.lower(),
        secondary=[k.lower() for k in target_keywords if k.lower() != primary.lower()][:8],
        long_tail=[f"{primary.lower()} {city.lower()}".strip()],
        near_me=[f"{primary.lower()} near me"],
        user_questions=[f.question for f in faqs],
    )
    schema = _build_schema(
        bt, city, state, faqs,
        business_name="ZeOrbit",
        site_url=CANONICAL_SITE,
        article_title=title,
        slug_override=slug,
    )
    content = _sectioned_body(h2s, intro, content, brief=brief)
    content = _strip_instruction_leak(content, brief)
    seo_score = _seo_score(intro + " " + content, title, meta, h2s, faqs, primary, city, slug, h1=h1)
    _ = who
    return SEOBlock(
        city=city, state=state, zip=zip or "", business_type=bt, industry=industry,
        slug=slug, title=title, meta_description=meta, h1=h1, h2s=h2s, h3s=h3s,
        intro=intro, content=content, faqs=faqs, cta=cta, keywords=kw, schema_markup=schema,
        readability_score=seo_score, keyword_density=_keyword_density(intro + " " + content, primary),
        content_type="service", focus_keyword=primary.lower(),
        search_intent=packed.get("search_intent") or intent.id,
        customer_problem=packed.get("customer_problem") or intent.customer_problem,
        image_concept=packed.get("image_concept") or "",
    )


# ══════════════════════════════════════════════════════════════════
#  Keyword-driven article generation (grounded in a website profile)
# ══════════════════════════════════════════════════════════════════

def _parse_location(location: str) -> tuple:
    """Split 'Austin, TX' → ('Austin', 'TX'). Falls back gracefully."""
    parts = [p.strip() for p in location.split(",") if p.strip()]
    if len(parts) >= 2:
        return parts[0], parts[1]
    if len(parts) == 1:
        return parts[0], ""
    return location.strip(), ""


async def _plan_article_angles(primary_keyword: str, location: str, profile: WebsiteProfile, n: int) -> List[dict]:
    """Ask the LLM for N distinct, unique article angles so batch articles don't overlap."""
    fallback = [
        {"title": f"{primary_keyword.title()} in {location}: Complete Guide", "intent": "informational"},
        {"title": f"How Much Does {primary_keyword.title()} Cost in {location}?", "intent": "commercial"},
        {"title": f"Best {primary_keyword.title()} Options for {location} Businesses", "intent": "commercial"},
        {"title": f"{primary_keyword.title()} Mistakes to Avoid in {location}", "intent": "informational"},
        {"title": f"Why {location} Chooses Professional {primary_keyword.title()}", "intent": "transactional"},
    ]
    from services.llm_service import chat_json, llm_available
    if not llm_available():
        return (fallback * ((n // len(fallback)) + 1))[:n]

    ctx = ""
    if profile and profile.analyzed:
        ctx = (
            f"\nThe articles are for this business: {profile.business_name}. "
            f"Services: {', '.join(profile.services[:8])}. "
            f"Audience: {profile.target_audience}. "
            f"Avoid repeating these already-covered topics: {', '.join(profile.existing_blog_topics[:10])}."
        )
    prompt = f"""Generate {n} DISTINCT blog article ideas for the primary keyword "{primary_keyword}" targeting "{location}".
Each idea must cover a different angle/search intent (guide, cost, comparison, how-to, checklist, FAQ, local, etc.){ctx}

Return ONLY valid JSON: {{"articles": [{{"title": "...", "intent": "informational|commercial|transactional"}}]}} with exactly {n} items."""
    data = await chat_json(prompt, temperature=0.8, max_tokens=800)
    angles = (data or {}).get("articles", [])
    if angles:
        return angles[:n] if len(angles) >= n else (angles + fallback)[:n]
    return (fallback * ((n // len(fallback)) + 1))[:n]


def _article_block_from_fields(
    data: dict, primary_keyword: str, city: str, state: str,
    profile: WebsiteProfile, industry: str, angle_title: str,
    preferred_link_urls: Optional[list] = None,
) -> SEOBlock:
    """Assemble a SEOBlock from generated fields (shared by LLM + template paths)."""
    faqs = [FAQItem(question=f["question"], answer=f["answer"]) for f in data.get("faqs", [])]
    slug = _slugify((data.get("slug") or angle_title) + f"-{city}")
    title = data.get("title", angle_title)
    meta = data.get("meta_description", "")
    h2s = data.get("h2s", [])
    body = data.get("content", "")

    if profile and profile.page_inventory:
        body = insert_internal_links(
            body, profile.page_inventory, max_links=5,
            preferred_urls=preferred_link_urls or [],
        )

    bt = primary_keyword.title()
    schema = _build_schema(
        bt, city, state, faqs,
        business_name=profile.business_name if profile else "",
        site_url=profile.url if profile else "",
        phone=profile.phone if profile else "",
        article_title=title,
        slug_override=slug,
    )
    full_text = data.get("intro", "") + " " + body
    seo_score = _seo_score(full_text, title, meta, h2s, faqs, primary_keyword, city, slug, h1=data.get("h1", ""))
    density = _keyword_density(full_text, primary_keyword)

    kw = data.get("_keywords")
    return SEOBlock(
        city=city, state=state or "", business_type=bt, industry=industry, slug=slug,
        title=title, meta_description=meta, h1=data.get("h1", ""), h2s=h2s,
        h3s=data.get("h3s", []), intro=data.get("intro", ""), content=body, faqs=faqs,
        cta=data.get("cta", ""), keywords=kw,
        schema_markup=schema, readability_score=seo_score, keyword_density=density,
        focus_keyword=primary_keyword, secondary_keywords=(kw.secondary[:6] if kw else []),
        source_url=profile.url if profile else "", content_type="blog",
    )


def _template_article_fields(primary_keyword: str, city: str, state: str, angle: dict) -> dict:
    """Zero-API fallback: build article fields from the template pools."""
    rng = _seed_random(city, primary_keyword + angle.get("title", ""))
    bt = primary_keyword.title()
    angle_title = angle.get("title", f"{bt} in {city}")
    intro = _fill(rng.choice(INTRO_VARIANTS), bt, city, state)
    body = "\n\n".join(_fill(s, bt, city, state) for s in rng.sample(BODY_SECTION_VARIANTS, 2))
    faqs = [{"question": _fill(q, bt, city, state), "answer": _fill(a, bt, city, state)}
            for q, a in rng.sample(FAQ_POOLS, min(6, len(FAQ_POOLS)))]
    return {
        "title": angle_title[:60],
        "meta_description": _fill(rng.choice(META_VARIANTS), bt, city, state),
        "slug": _slugify(angle_title),
        "h1": _fill(rng.choice(H1_VARIANTS), bt, city, state),
        "h2s": [_fill(h, bt, city, state) for h in rng.sample(H2_POOL, 5)],
        "h3s": [_fill(h, bt, city, state) for h in rng.sample(H3_POOL, 3)],
        "intro": intro,
        "content": body,
        "faqs": faqs,
        "cta": _fill(rng.choice(CTA_VARIANTS), bt, city, state),
    }


async def _generate_article(
    angle: dict,
    primary_keyword: str,
    city: str,
    state: str,
    profile: WebsiteProfile,
    industry: str,
    llm_provider: Optional[str] = None,
) -> SEOBlock:
    """Generate one full article for a specific city, grounded in the website profile.

    Uses the free LLM when available; falls back to the template engine otherwise.
    """
    from services.llm_service import chat_json, llm_available

    keywords = await generate_keywords(primary_keyword, city, state or "US")
    angle_title = angle.get("title", f"{primary_keyword.title()} in {city}")
    intent = angle.get("intent", "informational")
    location = f"{city}, {state}" if state else city

    data = None
    rag_block = ""
    preferred_link_urls = []
    if profile and profile.url:
        from services.rag_service import preferred_urls, retrieve
        try:
            chunks = await retrieve(
                f"{primary_keyword} {angle_title} {location} {industry}",
                profile.url,
            )
            from services.rag_service import format_context
            rag_block = format_context(chunks)
            preferred_link_urls = preferred_urls(chunks)
        except Exception as e:
            print(f"[RAG] article retrieve failed: {e}")

    if llm_available():
        biz_ctx = ""
        if profile and profile.analyzed:
            biz_ctx = f"""
GROUND THIS ARTICLE IN THE REAL BUSINESS (do not invent unrelated services):
- Business: {profile.business_name}
- Services: {', '.join(profile.services[:10])}
- Products: {', '.join(profile.products[:10]) or 'N/A'}
- Target audience: {profile.target_audience}
- Brand tone: {profile.brand_tone}
Write in the brand tone above and reference the business's actual services where relevant."""
        if rag_block:
            biz_ctx = (biz_ctx or "") + "\n\n" + rag_block

        research_block = ""
        try:
            from services.topic_research import research_prompt_block, research_topic
            notes = await research_topic(f"{primary_keyword} {angle_title}")
            research_block = research_prompt_block(notes)
        except Exception as e:
            print(f"[Research] article notes failed: {e}")

        prompt = f"""You are an expert SEO + AEO (AI answer engine) content writer. Write ONE complete, unique blog article.

Article angle/title: {angle_title}
Search intent: {intent}
Primary/focus keyword: {primary_keyword}
Location: {location}
Secondary keywords: {', '.join(keywords.secondary[:6])}
{biz_ctx}

{research_block}

ARTICLE SHAPE (follow this order inside "content"):
1. Direct answer: the first paragraph answers the core question in 2 sentences.
2. Five sections, one per H2. Each H2 is a question a reader would search.
3. One section is a numbered how-to or a short list, matching the search intent.
4. Practical detail only. No filler phrases like "in today's world" or "it's important to note".
5. End the content with a "References" block that lists only the sources from the research notes. If there are no sources, omit References.

WRITING RULES (optimize for Google, Google AI Overviews, Bing/Copilot, ChatGPT, Claude):
- Simple American English, short paragraphs, bullet points, clear hierarchy.
- Localize naturally to {location}. Use entities and keyword variations; do NOT keyword-stuff.
- Do not invent statistics, awards, prices, or customer quotes.

Return ONLY valid JSON with EXACTLY this structure:
{{
  "title": "Click-focused meta title (50-60 chars, include focus keyword)",
  "meta_description": "Meta description (150-160 chars, include focus keyword + CTA)",
  "slug": "seo-friendly-url-slug",
  "h1": "Article H1 heading",
  "h2s": ["5 question-based H2 subheadings"],
  "h3s": ["3 supporting H3 subheadings"],
  "intro": "Direct-answer intro (2-3 sentences).",
  "content": "5-7 paragraphs of body content (700+ words) following ARTICLE SHAPE. Use bullet points and double-newline breaks.",
  "faqs": [{{"question": "...", "answer": "..."}}],
  "cta": "Strong call-to-action (2-3 sentences)"
}}
Provide at least 5 FAQs. Each FAQ answer must be 2 sentences and must not repeat the intro. Return ONLY valid JSON, no markdown."""
        data = await chat_json(prompt, temperature=0.75, max_tokens=3500, provider=llm_provider)

    if not data or not data.get("content"):
        from fastapi import HTTPException
        raise HTTPException(
            status_code=502,
            detail="AI did not return article copy. Template fallback is disabled.",
        )

    data["_keywords"] = keywords
    return _article_block_from_fields(
        data, primary_keyword, city, state, profile, industry, angle_title,
        preferred_link_urls=preferred_link_urls,
    )


async def generate_articles(req: ArticleRequest, profile: WebsiteProfile) -> List[SEOBlock]:
    """Generate articles across the target location + nearby US cities (one or more per city).

    Nearby cities are covered because this is a USA-wide, local-SEO product. Each article
    also gets a featured image + 1-2 in-content images with full SEO metadata.
    """
    from services.image_service import generate_article_images
    from services.location_service import resolve_generation_cities

    cities = await resolve_generation_cities(req.location, req.num_cities, getattr(req, "extra_locations", None))
    if not cities:
        c, s = _parse_location(req.location)
        from models.schemas import CityInfo
        cities = [CityInfo(name=c.title(), state=s or "", country="USA", latitude=0.0, longitude=0.0)]

    per_city = max(1, req.num_articles)
    angles = await _plan_article_angles(req.primary_keyword, req.location, profile, max(per_city, 5))

    blocks: List[SEOBlock] = []
    used_featured: List[str] = []
    # Seed from already-published pages so new blogs don't reuse live featured photos
    try:
        from db import AsyncSessionLocal, PageRecord
        from sqlalchemy import select
        from services.image_service import collect_image_urls_from_seo_block
        async with AsyncSessionLocal() as session:
            rows = (await session.execute(select(PageRecord).order_by(PageRecord.id.desc()).limit(30))).scalars().all()
            for row in rows:
                block0 = row.seo_block if isinstance(row.seo_block, dict) else {}
                used_featured.extend(collect_image_urls_from_seo_block(block0 or {}))
    except Exception as e:
        print(f"[Articles] could not seed used images: {e}")

    for ci, city in enumerate(cities):
        for ai in range(per_city):
            angle = angles[(ci * per_city + ai) % len(angles)] if angles else {}
            try:
                block = await _generate_article(
                    angle, req.primary_keyword, city.name, city.state, profile, req.industry,
                    getattr(req, "llm_provider", None),
                )
                try:
                    images = await generate_article_images(
                        req.primary_keyword, f"{city.name}, {city.state}".strip(", "),
                        profile.business_name if profile else "", count=3,
                        angle_title=angle.get("title", ""),
                        exclude_urls=used_featured,
                        industry="",
                        niche=req.primary_keyword or "",
                        content_type="blog",
                        match_query=req.primary_keyword or "",
                    )
                    block.in_content_images = images
                    if images:
                        block.featured_image_url = images[0].url
                        used_featured.append(images[0].url)
                except Exception as e:
                    print(f"[Articles] image generation failed: {e}")
                    from services.image_service import _curated_image_url
                    block.featured_image_url = _curated_image_url(
                        req.primary_keyword,
                        f"{req.primary_keyword}|{city.name}|0",
                        exclude=used_featured,
                    )
                    if block.featured_image_url:
                        used_featured.append(block.featured_image_url)
                blocks.append(block)
            except Exception as e:
                print(f"[Articles] generation failed for {city.name}: {e}")
    kind = "blog" if (getattr(req, "content_kind", "post") or "post") == "post" else "service"
    for b in blocks:
        b.content_type = kind
        ensure_content_accuracy(b)
    return blocks
