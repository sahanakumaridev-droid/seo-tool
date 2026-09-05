"""
ZeOrbit AI Search Visibility & Local SEO, master implementation helpers.

Intent selection, factual copy rails, title/FAQ variation, image concepts,
duplicate detection, and publish quality scoring.
"""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence, Tuple

# ── Verified ZeOrbit facts only (never invent beyond these) ──────────────────
ZEORBIT_FACTS = {
    "pricing_range": "$500-$3,000",
    "experience": "20+ years",
    "reviews": "1,000+ client reviews",
    "services": [
        "Custom WordPress website development",
        "Shopify website development",
        "Website redesign and rebuild",
        "Mobile-friendly website development",
        "SEO-friendly website structure",
        "Conversion-focused website development",
        "Mobile application development",
    ],
}

BANNED_CLAIM_PATTERNS = (
    r"\b#\s*1\b",
    r"\bbest\s+in\s+[A-Z]",
    r"\bcheapest\b",
    r"\blowest\s+priced\b",
    r"\bguaranteed\s+rankings?\b",
    r"\b5[-\s]?star\s+reviews?\b",  # only if unverified individual claims
)

AI_FLUFF = (
    "cutting-edge",
    "digital transformation",
    "revolutionary",
    "seamless solutions",
    "unlock your potential",
    "leverage technology",
    "next-generation",
    "comprehensive digital ecosystem",
    "best-in-class",
    "synergies",
    "holistic solutions",
)

INDUSTRY_POOL = (
    "contractors",
    "construction companies",
    "roofing companies",
    "HVAC companies",
    "plumbers",
    "electricians",
    "healthcare providers",
    "dentists",
    "restaurants",
    "retailers",
    "e-commerce businesses",
    "real estate businesses",
    "professional services",
    "consultants",
    "salons",
    "fitness businesses",
    "local startups",
    "home-service businesses",
)

# Catch-all labels that must never be prepended to keywords / slugs.
GENERIC_INDUSTRY_LABELS = frozenset({
    "",
    "professional services",
    "other",
    "services",
    "local services",
    "digital services",
    "business",
    "small business",
    "general",
    "seo",
})

_NICHE_INDUSTRY_RULES = (
    (re.compile(r"\b(remodel(?:ing|ling)?|contractors?|plumb(?:er|ing)?|hvac|roof(?:er|ing)?|electric(?:ian|al)?|landscap(?:e|er|ing)?|paint(?:er|ing)?|pest|clean(?:ing|er)?|home[\s-]?service|construction)\b", re.I), "Contractors"),
    (re.compile(r"\b(restaurants?|cafe|catering|dining|food service|bistro)\b", re.I), "Restaurants"),
    (re.compile(r"\b(health(?:care)?|dental|clinic|medical|doctors?|dentists?|physician|pediatric|primary[\s-]?care)\b", re.I), "Healthcare"),
    (re.compile(r"\b(real estate|realtors?|property)\b", re.I), "Real Estate"),
    (re.compile(r"\b(legal|law|attorneys?|lawyers?)\b", re.I), "Legal"),
    (re.compile(r"\b(financ(?:e|ial)?|account(?:ing|ant)?|bank(?:ing)?|invest(?:ment|ing)?|wealth|bookkeep(?:ing|er)?)\b", re.I), "Finance"),
    (re.compile(r"\b(educat(?:ion|ional)?|tutors?|tutoring|schools?|courses?|university|college|learning)\b", re.I), "Education"),
    (re.compile(r"\b(retail(?:ers?)?|stores?|shops?|ecommerce|e-commerce)\b", re.I), "Retail"),
)


def is_generic_industry(industry: str) -> bool:
    return (industry or "").strip().lower() in GENERIC_INDUSTRY_LABELS


def resolve_industry_label(
    industry: str = "",
    business_type: str = "",
    keywords: Optional[Sequence[str]] = None,
) -> str:
    """Keep a real buyer vertical; never invent 'Professional Services'.

    Prefer an explicit non-generic industry. Otherwise infer from niche / keywords.
    Returns '' when nothing useful is known — keyword + niche already drive the page.
    """
    ind = (industry or "").strip()
    blob = " ".join(
        [business_type or ""]
        + [str(k).strip() for k in (keywords or [])[:6] if k and str(k).strip()]
    )
    inferred = ""
    for rx, label in _NICHE_INDUSTRY_RULES:
        if rx.search(blob):
            inferred = label
            break
    if inferred and ind and inferred.lower() != ind.lower():
        # Keyword/niche wins when the selected industry disagrees (e.g. doctor vs gym).
        return inferred
    if ind and not is_generic_industry(ind):
        return ind
    return inferred


def strip_generic_industry_prefix(text: str) -> str:
    """Remove a leading catch-all industry from a keyword / slug seed."""
    raw = (text or "").strip()
    if not raw:
        return raw
    return re.sub(
        r"^(professional[\s-]+services|digital[\s-]+services|local[\s-]+services|other)\s+",
        "",
        raw,
        flags=re.I,
    ).strip() or raw


@dataclass(frozen=True)
class SearchIntent:
    id: str
    label: str
    customer_problem: str
    service_emphasis: str  # wordpress | shopify | redesign | leads | mobile_app | affordable | general
    platform_hint: str  # WordPress | Shopify | either | mobile app
    title_templates: Tuple[str, ...]
    faq_seeds: Tuple[str, ...]
    image_scenes: Tuple[str, ...]


SEARCH_INTENTS: Tuple[SearchIntent, ...] = (
    SearchIntent(
        id="discovery",
        label="Website discovery",
        customer_problem="needs a clear professional website so local customers can find and trust the business",
        service_emphasis="general",
        platform_hint="WordPress",
        title_templates=(
            "Finding the Right Website Designer in {city}",
            "Website Design for Local Businesses in {city}",
            "Need a Website for Your Small Business in {city}?",
            "Building a Professional Website for Your {city} Business",
        ),
        faq_seeds=(
            "Who builds websites for small businesses in {city}?",
            "What should I look for in a website designer?",
            "What does a small-business website usually include?",
            "How long does website development usually take?",
        ),
        image_scenes=(
            "small-business owner reviewing a professional website on a laptop with a web designer",
            "local business owner pointing at a website mockup on a laptop in an office",
        ),
    ),
    SearchIntent(
        id="affordable",
        label="Affordable website",
        customer_problem="wants a professional site without overspending",
        service_emphasis="affordable",
        platform_hint="WordPress",
        title_templates=(
            "Affordable Website Design for Small Businesses in {city}",
            "How Much Does a Small-Business Website Cost in {city}?",
            "Reasonably Priced Website Design in {city}",
            "Small-Business Friendly Website Pricing in {city}",
        ),
        faq_seeds=(
            "How much does a small-business website cost in {city}?",
            "What is included in a website in the ${pricing} range?",
            "Is a cheaper website still professional enough?",
            "What should I budget for besides the website build?",
        ),
        image_scenes=(
            "small-business owner reviewing website pricing options on a laptop",
            "entrepreneur comparing website packages with a designer at a desk",
        ),
    ),
    SearchIntent(
        id="wordpress",
        label="WordPress",
        customer_problem="needs a flexible WordPress site they can update",
        service_emphasis="wordpress",
        platform_hint="WordPress",
        title_templates=(
            "WordPress Website Design in {city}",
            "Custom WordPress Websites for {city} Businesses",
            "WordPress Website Designer for Small Businesses in {city}",
            "Building a WordPress Site for Your {city} Business",
        ),
        faq_seeds=(
            "Is WordPress a good choice for a small business?",
            "Can I update a WordPress site myself after launch?",
            "How long does a WordPress website take to build?",
            "Do WordPress sites work well for local SEO?",
        ),
        image_scenes=(
            "web designer building a WordPress website on a desktop computer",
            "business owner reviewing a WordPress admin dashboard on a laptop",
        ),
    ),
    SearchIntent(
        id="shopify",
        label="Shopify",
        customer_problem="needs an online store that can take orders",
        service_emphasis="shopify",
        platform_hint="Shopify",
        title_templates=(
            "Shopify Website Development in {city}",
            "Shopify Store Design for {city} Businesses",
            "Building an Online Store for Your {city} Business",
            "Shopify Website Developer for Small Businesses in {city}",
        ),
        faq_seeds=(
            "Is Shopify better for an online store?",
            "When should a {city} business choose Shopify over WordPress?",
            "What does a basic Shopify store include?",
            "Can ZeOrbit set up payments and products on Shopify?",
        ),
        image_scenes=(
            "retailer reviewing a Shopify online store on a laptop",
            "e-commerce product page open on a laptop next to packaged goods",
        ),
    ),
    SearchIntent(
        id="redesign",
        label="Website redesign",
        customer_problem="has an outdated site that loses visitors on phones",
        service_emphasis="redesign",
        platform_hint="WordPress",
        title_templates=(
            "Website Redesign Services for Businesses in {city}",
            "Outdated Website? Redesign Help for {city} Businesses",
            "Rebuilding a Professional Website in {city}",
            "Website Redesign for Local Businesses in {city}",
        ),
        faq_seeds=(
            "Can an outdated website be redesigned?",
            "Will a redesign keep my existing content and URLs?",
            "How do I know if my website needs a rebuild?",
            "Does a redesign help with mobile users?",
        ),
        image_scenes=(
            "business owner comparing an old website and a redesigned site on two screens",
            "web designer showing a refreshed mobile-friendly website mockup",
        ),
    ),
    SearchIntent(
        id="leads",
        label="Lead generation",
        customer_problem="wants the website to bring more calls and form fills",
        service_emphasis="leads",
        platform_hint="WordPress",
        title_templates=(
            "Website Design That Helps {city} Businesses Get More Leads",
            "Conversion-Focused Website Design in {city}",
            "Websites Built to Generate Leads in {city}",
            "Turn Website Visitors into Customers in {city}",
        ),
        faq_seeds=(
            "How can a website help generate leads?",
            "What makes a website useful for a local business?",
            "Should every page have a clear call to action?",
            "Do landing pages help with ads and campaigns?",
        ),
        image_scenes=(
            "business owner reviewing lead form submissions on a laptop",
            "designer pointing at a clear call-to-action on a website mockup",
        ),
    ),
    SearchIntent(
        id="new_business",
        label="New business",
        customer_problem="is starting out and needs a first professional website",
        service_emphasis="general",
        platform_hint="WordPress",
        title_templates=(
            "Starting a Business in {city}? Build Your First Website",
            "Website Design for New Businesses in {city}",
            "What to Put on a New Business Website in {city}",
            "First Website for Your {city} Startup",
        ),
        faq_seeds=(
            "What should a new business put on its website?",
            "Do I need a website before I open for business?",
            "How simple can a first website be?",
            "When should a new business add e-commerce?",
        ),
        image_scenes=(
            "new business owner planning website pages on a notepad next to a laptop",
            "startup founder reviewing a first website draft with a designer",
        ),
    ),
    SearchIntent(
        id="mobile_app",
        label="Website vs mobile app",
        customer_problem="is unsure whether a website or a mobile app comes first",
        service_emphasis="mobile_app",
        platform_hint="mobile app",
        title_templates=(
            "Do You Need a Website or Mobile App for Your {city} Business?",
            "Website vs Mobile App for {city} Businesses",
            "When {city} Businesses Should Consider a Mobile App",
            "Mobile App Development Alongside Your Website in {city}",
        ),
        faq_seeds=(
            "When does a business need a mobile app?",
            "Should I build a website before a mobile app?",
            "Can ZeOrbit build both a website and a mobile app?",
            "Does my business need a mobile-friendly website first?",
        ),
        image_scenes=(
            "business owner comparing a website on a laptop and an app on a phone",
            "designer reviewing a mobile app prototype next to a website mockup",
        ),
    ),
    SearchIntent(
        id="industry_local",
        label="Industry local",
        customer_problem="needs a site that speaks to their trade and local customers",
        service_emphasis="general",
        platform_hint="WordPress",
        title_templates=(
            "Website Design for {industry_title} in {city}",
            "{industry_title} Website Design in {city}",
            "Professional Websites for {industry_title} in {city}",
            "Local Website Help for {industry_title} in {city}",
        ),
        faq_seeds=(
            "What should a local {industry} include on its website?",
            "Does my {industry} business need a mobile-friendly website?",
            "How can a website help {industry} get more local customers?",
            "Should {industry} use WordPress or Shopify?",
        ),
        image_scenes=(
            "{industry} business owner reviewing a professional website on a laptop",
            "web designer showing a service website mockup to a {industry} owner",
        ),
    ),
)


def _stable_int(*parts: str) -> int:
    seed = "|".join((p or "").strip().lower() for p in parts)
    return int(hashlib.md5(seed.encode("utf-8")).hexdigest(), 16)


def pick_industry(explicit: str, city: str, index: int) -> str:
    """Use explicit non-generic industry when set; otherwise rotate a fitting pool.

    Generic placeholders like 'Professional Services' are treated as unset so they
    are not stamped onto every keyword/slug.
    """
    if (explicit or "").strip() and not is_generic_industry(explicit):
        return explicit.strip()
    return INDUSTRY_POOL[_stable_int(city, str(index)) % len(INDUSTRY_POOL)]


def detect_intent_from_brief(brief: str, keywords: Sequence[str]) -> Optional[str]:
    """Force intent from the editor brief, or from strongly explicit keywords.

    Soft website keywords (e.g. “website design”) do NOT force a single intent —
    those still rotate for variety — but they DO block mobile_app unless the
    brief/keywords explicitly ask for apps.
    """
    blob = (brief or "").lower()
    kw_blob = " ".join(str(k).lower() for k in (keywords or []) if k)
    # Brief wins when present
    if blob.strip():
        rules = (
            ("shopify", ("shopify", "ecommerce", "e-commerce", "online store")),
            ("wordpress", ("wordpress site", "wordpress website", "wordpress design", "wordpress developer")),
            ("affordable", ("affordable", "cheap", "cost", "pricing", "budget", "reasonably priced", "how much")),
            ("redesign", ("redesign", "rebuild", "outdated", "refresh")),
            ("leads", ("lead generation", "more leads", "conversion", "get more customers", "more calls")),
            ("mobile_app", ("mobile app", "ios app", "android app", "website or app", "app vs website")),
            ("new_business", ("new business", "startup", "starting a business", "first website")),
        )
        for intent_id, needles in rules:
            if any(n in blob for n in needles):
                return intent_id
    # Explicit keyword signals (strong only)
    if kw_blob.strip():
        if any(n in kw_blob for n in ("mobile app", "ios app", "android app", "app development", "app vs website")):
            return "mobile_app"
        if any(n in kw_blob for n in ("shopify", "ecommerce", "e-commerce", "online store")):
            return "shopify"
        if "wordpress" in kw_blob:
            return "wordpress"
        if any(n in kw_blob for n in ("affordable web", "affordable website", "cheap website", "website cost")):
            return "affordable"
        if "redesign" in kw_blob:
            return "redesign"
    return None


def keywords_imply_website_not_app(keywords: Optional[Sequence[str]], brief: str = "") -> bool:
    """True when the editor's keywords are clearly about websites, not mobile apps."""
    blob = " ".join(
        [str(k).lower() for k in (keywords or []) if k] + [((brief or "").lower())]
    )
    if not blob.strip():
        return False
    if any(n in blob for n in ("mobile app", "ios app", "android app", "app development")):
        return False
    return any(
        n in blob
        for n in (
            "website", "web design", "web designer", "wordpress", "shopify",
            "landing page", "website design", "custom website", "small business website",
        )
    )


def pick_search_intent(
    city: str,
    index: int,
    industry: str = "",
    brief: str = "",
    keywords: Optional[Sequence[str]] = None,
) -> SearchIntent:
    forced = detect_intent_from_brief(brief, keywords or [])
    if forced:
        for intent in SEARCH_INTENTS:
            if intent.id == forced:
                return intent
    # Rotate intents so many locations are not the same article shape.
    # Prefer industry_local every 3rd page when an industry is set.
    if industry and index % 3 == 2:
        return next(i for i in SEARCH_INTENTS if i.id == "industry_local")
    pool = [i for i in SEARCH_INTENTS if i.id != "industry_local"]
    # Never stamp a Mobile App title onto website-design keyword campaigns.
    if keywords_imply_website_not_app(keywords, brief):
        pool = [i for i in pool if i.id != "mobile_app"]
    if not pool:
        pool = [i for i in SEARCH_INTENTS if i.id == "discovery"]
    return pool[_stable_int(city, industry, str(index)) % len(pool)]


def format_title(intent: SearchIntent, city: str, industry: str, index: int) -> str:
    industry_l = (industry or "local businesses").strip()
    industry_title = industry_l[:1].upper() + industry_l[1:] if industry_l else "Local Businesses"
    tpl = intent.title_templates[_stable_int(city, intent.id, str(index)) % len(intent.title_templates)]
    title = tpl.format(
        city=city or "Your Area",
        industry=industry_l,
        industry_title=industry_title,
        pricing=ZEORBIT_FACTS["pricing_range"],
    )
    return title[:78]


def title_from_primary_keyword(
    primary_keyword: str,
    city: str,
    industry: str,
    intent: SearchIntent,
    index: int = 0,
) -> str:
    """Prefer SEO title from the editor's primary keyword + city.

    Intent templates are a fallback when the keyword is empty or already too long.
    Never let a rotated mobile_app template override a website-design keyword.
    """
    raw = re.sub(r"\s+", " ", (primary_keyword or "").strip())
    city_l = (city or "").strip()
    city_low = city_l.lower()

    # Drop trailing location fragments already in the keyword (full city or last token)
    if city_low and raw.lower().endswith(city_low):
        raw = raw[: -len(city_l)].strip(" ,-")
    elif city_low:
        # e.g. keyword ends with "san diego" while city is a neighborhood — keep as-is
        # but avoid "… National City in National City"
        pass

    if not raw:
        return format_title(intent, city, industry, index)

    small = {"in", "for", "of", "and", "a", "the", "to", "on", "vs"}
    parts = []
    for i, w in enumerate(raw.split(" ")):
        low = w.lower()
        if low == "wordpress":
            parts.append("WordPress")
        elif low == "seo":
            parts.append("SEO")
        elif i and low in small:
            parts.append(low)
        else:
            parts.append(w[:1].upper() + w[1:] if w else w)
    pretty = " ".join(parts)

    pretty_low = pretty.lower()
    if city_l and city_low not in pretty_low:
        # Also skip append when every significant city token is already present
        city_tokens = [t for t in re.split(r"[^a-z0-9]+", city_low) if len(t) > 2]
        if not city_tokens or not all(t in pretty_low for t in city_tokens):
            candidate = f"{pretty} in {city_l}"
        else:
            candidate = pretty
    else:
        candidate = pretty

    if len(candidate) > 78:
        candidate = candidate[:75].rstrip(" -,") + "…"
    if intent.id == "mobile_app" and keywords_imply_website_not_app([primary_keyword]):
        return candidate[:78]
    return candidate[:78]


def intent_h2_set(
    intent: SearchIntent,
    city: str,
    industry: str,
    layout: str,
) -> List[str]:
    ind = industry or "local"
    city_l = city or "your area"
    pricing = ZEORBIT_FACTS["pricing_range"]
    by_intent = {
        "discovery": [
            f"What {city_l} small businesses need from a website",
            "What ZeOrbit can build for you",
            "WordPress, Shopify, and redesign options",
            f"Practical pricing for {city_l} projects ({pricing})",
            "How to choose a website designer",
            f"Next step for your {city_l} business",
        ],
        "affordable": [
            f"What “affordable” should mean for a {city_l} website",
            f"Typical ZeOrbit website project range ({pricing})",
            "What is included in a small-business website",
            "WordPress vs Shopify for your budget",
            "How to avoid hidden website costs",
            "Talk with ZeOrbit about a practical plan",
        ],
        "wordpress": [
            f"Why WordPress fits many {city_l} businesses",
            "What a custom WordPress build includes",
            "Mobile-friendly and SEO-friendly structure",
            "Can you update the site yourself?",
            f"Timeline and pricing ({pricing})",
            "Start a WordPress project with ZeOrbit",
        ],
        "shopify": [
            f"When a {city_l} business needs Shopify",
            "What ZeOrbit sets up on Shopify",
            "Products, payments, and mobile shopping",
            "Shopify vs WordPress for your store",
            f"Budgeting a store ({pricing} for many website projects)",
            "Launch your store with ZeOrbit",
        ],
        "redesign": [
            f"Signs your {city_l} website needs a redesign",
            "What a redesign or rebuild can fix",
            "Keeping useful content while improving the experience",
            "Mobile-friendly rebuilds that convert",
            f"What redesign projects typically cost ({pricing})",
            "Plan a redesign with ZeOrbit",
        ],
        "leads": [
            f"Why {city_l} websites lose leads",
            "Pages and CTAs that make contacting you easy",
            "Service pages vs landing pages",
            "Local SEO structure that supports lead gen",
            "Measuring calls and form fills",
            "Improve lead flow with ZeOrbit",
        ],
        "new_business": [
            f"What a first website should cover in {city_l}",
            "Pages every new business needs",
            "WordPress for a flexible first site",
            "When to add Shopify or a mobile app later",
            f"Starting within a practical budget ({pricing})",
            "Launch your first site with ZeOrbit",
        ],
        "mobile_app": [
            f"Website first or app first for {city_l} businesses?",
            "What a mobile-friendly website must do",
            "When a mobile app becomes worth it",
            "How ZeOrbit approaches apps and websites",
            "Budget and timeline considerations",
            "Decide your next step with ZeOrbit",
        ],
        "industry_local": [
            f"What {ind} in {city_l} need on a website",
            f"Service pages that speak to {ind} customers",
            "WordPress or Shopify for your business type",
            "Mobile-friendly design and clear contact paths",
            f"Pricing context ({pricing}) and experience",
            f"Website help for {ind} with ZeOrbit",
        ],
    }
    base = by_intent.get(intent.id) or by_intent["discovery"]
    # Light layout nudge without forcing identical headings everywhere.
    if layout == "steps":
        return [f"Step {i + 1}: {h}" if i < 4 and not h.lower().startswith("step") else h for i, h in enumerate(base[:5])] + base[5:]
    if layout == "qa":
        return [
            h if h.endswith("?") else (h.rstrip(".") + "?")
            for h in base[:3]
        ]
    return list(base)[:3]


def intent_faqs(
    intent: SearchIntent,
    city: str,
    industry: str,
    index: int,
) -> List[Dict[str, str]]:
    pricing = ZEORBIT_FACTS["pricing_range"]
    exp = ZEORBIT_FACTS["experience"]
    reviews = ZEORBIT_FACTS["reviews"]
    ind = industry or "local business"
    industry_l = ind
    seeds = list(intent.faq_seeds)
    # Rotate which seeds lead so FAQs differ across locations.
    rot = _stable_int(city, intent.id, str(index)) % max(1, len(seeds))
    seeds = seeds[rot:] + seeds[:rot]
    answers = {
        "discovery": [
            f"ZeOrbit builds custom WordPress and Shopify websites for small businesses, including businesses in {city}. Website projects typically range from {pricing}.",
            "Look for clear communication, mobile-friendly design, SEO-friendly structure, realistic pricing, and experience with businesses like yours, not vague “best in town” claims.",
            "Most small-business sites need clear services, contact options, mobile layouts, proof, and pages that match how people search locally.",
            "Straightforward builds often take a few weeks after content and goals are clear. ZeOrbit shares a timeline before work starts.",
        ],
        "affordable": [
            f"ZeOrbit website projects typically range from {pricing}. The right fit depends on pages, features, and whether you need WordPress, Shopify, or a redesign.",
            f"In the {pricing} range you can usually cover a professional multi-page site with mobile-friendly layouts and a clear path for customers to contact you.",
            "A lower price still needs to cover useful pages, mobile usability, and a clear offer. Extremely cheap sites often skip the parts that get leads.",
            "Budget for domain, hosting, photos, and ongoing updates, not only the initial design.",
        ],
        "wordpress": [
            "WordPress is a strong fit when you need flexible pages, blogs, and room to grow without rebuilding from scratch.",
            "Yes, after training, many owners update text and photos themselves. ZeOrbit can also handle ongoing changes if you prefer.",
            "Most small WordPress projects land in a few weeks once services, photos, and goals are ready.",
            "Yes. Clear headings, local service pages, and useful FAQs help search engines and AI systems understand the business.",
        ],
        "shopify": [
            "Shopify is usually better when selling products online is the main job of the site.",
            f"Choose Shopify when checkout and inventory matter most. Choose WordPress when you need a broader marketing site, ZeOrbit builds both for {city} businesses.",
            "A basic store typically includes products, payments, mobile shopping, and clear shipping/contact details.",
            "Yes. ZeOrbit can set up the storefront structure and help you get products and payments ready for launch.",
        ],
        "redesign": [
            "Yes. An outdated site can be redesigned or rebuilt so it works on phones, loads faster, and explains your services clearly.",
            "Often yes, useful pages and URLs can be kept or redirected carefully so you do not throw away what already works.",
            "If customers leave on mobile, cannot find contact info, or the site looks years behind your competitors, a redesign is worth discussing.",
            "Yes. Mobile-friendly layouts are a core part of modern redesigns.",
        ],
        "leads": [
            "A clear offer, fast pages, strong contact paths, and landing pages matched to your ads or services help turn visits into calls and forms.",
            "It should explain what you do, who you help, where you work, and how to contact you, without making people hunt.",
            "Yes. Every important page should make the next step obvious: call, form, or book.",
            "Yes. Dedicated landing pages keep campaign visitors focused on one offer.",
        ],
        "new_business": [
            "Start with who you help, what you offer, how to contact you, and proof you are real, even a simple site beats no site.",
            "A simple professional site helps people trust you before they call. You can expand pages as you grow.",
            "Yes. A focused first site with a few clear pages is often better than a large unfinished one.",
            "Add Shopify when you are ready to sell online regularly; add an app when customers need repeat actions on their phones.",
        ],
        "mobile_app": [
            "Consider an app when customers need frequent logins, bookings, or account tools. Many businesses should start with a strong mobile-friendly website.",
            "Usually yes, a website is how people find and evaluate you. An app can come later if the workflow needs it.",
            "Yes. ZeOrbit provides website development and mobile application development based on what the business actually needs.",
            "Yes. If your site is hard to use on a phone, customers may leave before contacting you.",
        ],
        "industry_local": [
            f"A {industry_l} site should explain services clearly, show how to contact you, work on phones, and answer common customer questions for {city}.",
            f"Yes. Many {industry_l} customers search and call from phones, if the site is awkward on mobile, you can lose the lead.",
            f"Clear service pages and easy contact options help {industry_l} get found and contacted by local customers.",
            f"WordPress fits most service sites; Shopify fits product sellers. ZeOrbit helps {industry_l} choose based on the real need.",
        ],
    }
    ans = answers.get(intent.id) or answers["discovery"]
    out: List[Dict[str, str]] = []
    for i, q_tpl in enumerate(seeds[:3]):
        q = q_tpl.format(
            city=city or "your area",
            industry=industry_l,
            pricing=pricing,
        )
        a = ans[i % len(ans)]
        out.append({"question": q, "answer": a})
    return out


def image_concept(
    intent: SearchIntent,
    city: str,
    industry: str,
    index: int,
) -> str:
    ind = (industry or "small-business").strip()
    scene = intent.image_scenes[_stable_int(city, intent.id, str(index)) % len(intent.image_scenes)]
    scene = scene.format(industry=ind, city=city or "local")
    # LOCATION + INDUSTRY + SERVICE + PROBLEM + INTENT
    return (
        f"{city + '-area ' if city else ''}{scene}, "
        f"related to {intent.service_emphasis.replace('_', ' ')} website work "
        f"for a business that {intent.customer_problem}"
    )


def stock_query_from_concept(intent: SearchIntent, industry: str, index: int) -> Tuple[str, List[str]]:
    """On-topic stock queries, always website/laptop accurate, never trade/tourism/classroom scenery.

    Industry may tint modifiers lightly, but the PRIMARY query stays website design so
    Unsplash does not return cameras, classrooms, or plumbing for “Education/Plumbing + website”.
    """
    emphasis = intent.service_emphasis
    topics = {
        "shopify": ("shopify ecommerce website laptop", ["online store mockup screen", "product page laptop", "checkout website ui", "retail owner laptop website"]),
        "wordpress": ("wordpress website designer laptop", ["cms dashboard screen", "web design office laptop", "ui website mockup", "developer desk laptop code"]),
        "redesign": ("website redesign mockup laptop", ["ux designer laptop screen", "mobile website phone desk", "design review laptop", "web mockup desk"]),
        "leads": ("business website contact form laptop", ["marketing website laptop", "lead generation website desk", "call to action website screen", "office laptop website"]),
        "mobile_app": ("mobile app website prototype phone laptop", ["app ui mockup phone laptop", "smartphone website mockup", "ux wireframe laptop", "developer phone app website"]),
        "affordable": ("small business website laptop", ["web design consult laptop", "entrepreneur laptop website", "office desk website mockup", "budget website planning laptop"]),
        "general": ("web designer laptop business website", ["website mockup screen", "client website laptop", "ui design office laptop", "office computer website"]),
        "discovery": ("website design laptop mockup", ["web designer office laptop", "business website screen", "responsive website phone", "laptop website mockup"]),
        "industry_local": ("local business website laptop", ["service business website laptop", "owner laptop website", "mobile website phone", "web design meeting laptop"]),
        "new_business": ("startup website laptop desk", ["new business website laptop", "entrepreneur laptop website", "website planning meeting laptop", "first website mockup"]),
    }
    topic, mods = topics.get(emphasis, topics["general"])
    # Keep industry out of the primary Unsplash query, it pulls off-topic stock
    # (e.g. Education → classroom, Photography → camera). Website visuals only.
    _ = (industry or "").strip()
    rot = index % len(mods)
    mods = mods[rot:] + mods[:rot]
    return topic, mods


def facts_blurb(variant: int = 0) -> str:
    pricing = ZEORBIT_FACTS["pricing_range"]
    exp = ZEORBIT_FACTS["experience"]
    reviews = ZEORBIT_FACTS["reviews"]
    variants = (
        f"ZeOrbit website projects typically range from {pricing}. "
        f"With more than two decades of experience and {reviews}, "
        f"ZeOrbit builds custom WordPress and Shopify sites, redesigns, and mobile apps when a business needs more than a basic website.",
        f"ZeOrbit brings {exp} to website projects and has {reviews}. "
        f"Typical website projects range from {pricing}, covering WordPress, Shopify, redesign, and conversion-focused builds.",
        f"Businesses looking for WordPress, Shopify, a redesign, or a mobile-friendly site can work with ZeOrbit. "
        f"Website projects typically range from {pricing}, backed by {exp} and {reviews}.",
    )
    return variants[variant % len(variants)]


def scrub_ceo_dashes(text: str) -> str:
    """Reduce em/en dashes in published copy (CEO preference). Keep simple $500-$3,000 hyphens."""
    if not text:
        return text
    t = str(text)
    t = t.replace("$500-$3,000", "$500-$3,000").replace("$500—$3,000", "$500-$3,000")
    t = re.sub(r"\s*[—–]\s*", ", ", t)
    t = re.sub(r",\s*,+", ",", t)
    t = re.sub(r"[ \t]{2,}", " ", t)
    return t


def master_voice_rules() -> str:
    from services.master_custom_instruction import master_instruction_for_prompt

    return f"""
VOICE (helpful small-business English, ZeOrbit local SEO):
- Write as if explaining to a real {ZEORBIT_FACTS['experience']} shop owner sitting across from you.
- Prefer concrete lines like: "If your website is difficult to use on a phone, customers may leave before contacting you."
- FORBIDDEN fluff: {", ".join(AI_FLUFF)}.
- NEVER claim #1, cheapest, best in [city], fake reviews, fake clients, fake offices, fake awards, or fake case studies.
- FACTS YOU MAY USE (only these): pricing {ZEORBIT_FACTS['pricing_range']}; experience {ZEORBIT_FACTS['experience']}; {ZEORBIT_FACTS['reviews']}; services: {", ".join(ZEORBIT_FACTS['services'])}.
- Pricing language: affordable / reasonably priced / small-business friendly. Never say "cheapest".
- Punctuation: avoid em dashes (—) and en dashes (–). Prefer commas, periods, or short sentences. Do not stack dashes in body copy.
- Pricing ranges may use a simple hyphen only when needed (e.g. $500-$3,000), not an em dash.
- Make entity relationships explicit: ZeOrbit → website design → WordPress/Shopify/mobile apps → small businesses → this location → industry → customer problem.
- Every location page must feel unique: different intro, problem, industry examples, FAQs, and CTA. Do not only swap the city name.
- NEVER paste writing briefs or Custom Content Requirements into published fields.

MASTER CUSTOM INSTRUCTION (keyword + niche + location drive the article; follow this for intent, problem, service focus, FAQs, CTA, tone):
{master_instruction_for_prompt()}
"""


def ai_page_brief_block(
    intent: SearchIntent,
    city: str,
    state: str,
    industry: str,
    title: str,
    h2s: List[str],
    image_concept_text: str,
    zip: str = "",
) -> str:
    place = place_label(city, state, zip) or (f"{city}, {state}".strip(", ") if state else city)
    z = re.sub(r"\D", "", zip or "")[:5]
    maps_md = zip_hyperlink(z, city, state) if z else ""
    zip_line = (
        f"LOCATION PIN: only in the last FAQ answer, hyperlink the full place "
        f"{maps_md} (Location Name, State ZIP — never ZIP alone). "
        f"Never put {z} in the title, H1, intro, body, conclusion, meta, or CTA."
        if z else
        f"LOCATION: {place} — do not invent a ZIP if you do not have one."
    )
    faqs = intent_faqs(intent, city, industry, 0)
    faq_lines = "\n".join(f"- {f['question']}" for f in faqs)
    return f"""
SEARCH INTENT FOR THIS PAGE ONLY: {intent.label} ({intent.id})
CUSTOMER PROBLEM: A business that {intent.customer_problem}.
SERVICE EMPHASIS: {intent.service_emphasis} ({intent.platform_hint})
INDUSTRY EXAMPLES TO WEAVE IN (do not force all): {industry}
{zip_line}
LOCATION: {place} — do not invent local offices, addresses, competitors, or unverified local statistics.
If you lack reliable local facts, use neutral wording ("businesses in {place}") instead of inventing details.

REQUIRED TITLE (use exactly or very close): {title}
REQUIRED H2 STRUCTURE (refine lightly if needed, keep intent): {h2s}
IMAGE CONCEPT (do not describe tourism): {image_concept_text}

MUST COVER IN NATURAL LANGUAGE:
- Who ZeOrbit helps and what problem this page solves
- Relevant ZeOrbit services (WordPress / Shopify / redesign / mobile-friendly / SEO structure / conversions / mobile apps as relevant)
- Pricing context: typically {ZEORBIT_FACTS['pricing_range']}
- Experience/trust: {ZEORBIT_FACTS['experience']}, {ZEORBIT_FACTS['reviews']} (no fake individual reviews)
- Practical advice for choosing a provider
- FAQs aligned to this intent (suggested questions):\n{faq_lines}

DEPTH: 320–480 words. Tight and useful — 3 H2s, short paragraphs, no filler. Not a 700-word essay.
"""


def strip_banned_claims(text: str) -> str:
    out = text or ""
    for pat in BANNED_CLAIM_PATTERNS:
        out = re.sub(pat, "", out, flags=re.I)
    for fluff in AI_FLUFF:
        out = re.sub(re.escape(fluff), "", out, flags=re.I)
    out = re.sub(r"\s{2,}", " ", out)
    return out.strip()


def _tokenize(text: str) -> set:
    return {w for w in re.findall(r"[a-z0-9]{4,}", (text or "").lower()) if w not in {
        "that", "with", "from", "this", "your", "have", "will", "about", "their", "them",
        "website", "websites", "business", "businesses", "zeorbit", "wordpress",
    }}


def content_similarity(a: str, b: str) -> float:
    """Jaccard similarity on significant tokens (0–1)."""
    ta, tb = _tokenize(a), _tokenize(b)
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)


def is_too_similar(candidate: str, existing: Sequence[str], threshold: float = 0.78) -> bool:
    return any(content_similarity(candidate, other) >= threshold for other in existing if other)


@dataclass
class QualityResult:
    score: float
    breakdown: Dict[str, float] = field(default_factory=dict)
    publishable: bool = False
    reasons: List[str] = field(default_factory=list)


MIN_PUBLISH_SCORE = 90.0
MIN_KEYWORD_USE_SCORE = 90.0


def scores_meet_floor(quality: float, keyword_use: float) -> bool:
    """Every visible score gauge must clear 90 before generate/publish."""
    return float(quality or 0) >= MIN_PUBLISH_SCORE and float(keyword_use or 0) >= MIN_KEYWORD_USE_SCORE


def _location_tokens(city: str) -> List[str]:
    """Tokens that count as local mentions (handles 'Downtown Chula Vista')."""
    c = (city or "").strip()
    if not c:
        return []
    tokens = [c.lower()]
    # Drop leading neighborhood words so "Chula Vista" still matches.
    parts = re.split(r"\s+", c)
    drop = {"downtown", "east", "west", "north", "south", "central", "old", "new"}
    while parts and parts[0].lower() in drop and len(parts) > 1:
        parts = parts[1:]
        tokens.append(" ".join(parts).lower())
    if len(parts) >= 2:
        tokens.append(parts[-1].lower())
    # Unique, longest-first for matching
    uniq = []
    for t in sorted(set(tokens), key=len, reverse=True):
        if len(t) >= 3:
            uniq.append(t)
    return uniq


def _body_mentions_city(body: str, city: str) -> int:
    body_l = (body or "").lower()
    return sum(1 for t in _location_tokens(city) if t and t in body_l)


# Places that often leak from a shared Content Brief into the wrong city page.
_BRIEF_PLACE_HINTS = (
    "San Diego", "Chula Vista", "Coronado", "La Jolla", "Carlsbad", "Oceanside",
    "Escondido", "El Cajon", "National City", "Imperial Beach", "Lemon Grove",
    "Poway", "Santee", "Encinitas", "Solana Beach", "Del Mar", "Vista",
    "Los Angeles", "Orange County", "Irvine", "San Francisco", "Sacramento",
    "Austin", "Dallas", "Houston", "Driftwood", "Miami", "Phoenix", "Seattle",
)


def extract_foreign_places(brief: str, city: str) -> List[str]:
    """Place names from a shared editor brief that must not appear on this city page."""
    city_l = (city or "").strip().lower()
    found: List[str] = []
    blob = brief or ""
    for place in _BRIEF_PLACE_HINTS:
        if place.lower() == city_l:
            continue
        if city_l and place.lower() in city_l:
            continue
        if re.search(rf"\b{re.escape(place)}\b", blob, flags=re.I):
            found.append(place)
    for m in re.finditer(r"\bin\s+([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+)?)\b", blob):
        cand = m.group(1).strip()
        if cand.lower() in {"the", "your", "this", "that", "united", "wordpress", "shopify"}:
            continue
        if cand.lower() == city_l or (city_l and cand.lower() in city_l):
            continue
        if cand not in found and len(cand) >= 4:
            found.append(cand)
    return sorted(set(found), key=len, reverse=True)


def scrub_foreign_places(text: str, city: str, foreign: Sequence[str]) -> str:
    """Replace leaked place names with the page's city."""
    out = text or ""
    if not city or not foreign:
        return out
    for place in foreign:
        if not place or place.lower() == city.lower():
            continue
        out = re.sub(rf"\b{re.escape(place)}\b", city, out, flags=re.I)
    return out


def ensure_title_names_city(title: str, city: str, state: str = "") -> str:
    """Guarantee title/H1 includes this page's city (bulk pages must not share one title)."""
    t = (title or "").strip()
    c = (city or "").strip()
    if not c:
        return t
    foreign = extract_foreign_places(t, c)
    if foreign:
        t = scrub_foreign_places(t, c, foreign)
    if c.lower() in t.lower():
        return t
    place = f"{c}, {state}".strip(", ") if state else c
    base = re.sub(r"[\s|,\-–—]+$", "", t) or "Website Design"
    return f"{base} in {place}"


def place_label(city: str, state: str = "", zip: str = "") -> str:
    """City, ST — ZIP is FAQ-only and must not appear in body labels."""
    city = (city or "").strip()
    state = (state or "").strip()
    if city and state:
        return f"{city}, {state}"
    return (city or state).strip()


def digits_zip(zip: str = "") -> str:
    z = re.sub(r"\D", "", zip or "")[:5]
    return z if len(z) == 5 else ""


def maps_anchor_label(city: str = "", state: str = "", zip: str = "") -> str:
    """Visible Maps text: Location Name, ST ZIP."""
    z = digits_zip(zip)
    city = (city or "").strip()
    state = (state or "").strip()
    if city and state and z:
        return f"{city}, {state} {z}"
    if city and z:
        return f"{city} {z}"
    if city and state:
        return f"{city}, {state}"
    return z or city


def maps_lat_lng(city: str = "", state: str = "") -> tuple[float, float]:
    try:
        from services.location_service import _geocode_from_dataset
        rec = _geocode_from_dataset(f"{city}, {state}".strip(", "))
        if rec:
            return float(rec.get("lat") or 0), float(rec.get("lon") or rec.get("lng") or 0)
    except Exception:
        pass
    return 0.0, 0.0


def zip_maps_url(code: str, city: str = "", state: str = "", lat: float = 0.0, lng: float = 0.0) -> str:
    """Google Maps search for the full place, with viewport when we have coordinates."""
    from urllib.parse import quote
    label = maps_anchor_label(city, state, code) or digits_zip(code)
    path = quote(label.replace(" ", "+"), safe="+,")
    url = f"https://www.google.com/maps/search/{path}"
    la, ln = lat, lng
    if abs(la) < 0.01 and abs(ln) < 0.01:
        la, ln = maps_lat_lng(city, state)
    if abs(la) > 0.01 and abs(ln) > 0.01:
        url += f"/@{la},{ln},2824m/data=!3m2!1e3!4b1"
    return url


def zip_hyperlink(z: str, city: str = "", state: str = "", lat: float = 0.0, lng: float = 0.0) -> str:
    """FAQ Maps link uses the full location name, not ZIP alone."""
    code = digits_zip(z)
    if not code:
        return z or ""
    label = maps_anchor_label(city, state, code)
    return f"[{label}]({zip_maps_url(code, city, state, lat, lng)})"


INTERNAL_LINK_LINE = (
    "See [ZeOrbit website design](https://zeorbit.com/website-designing), "
    "[mobile apps](https://zeorbit.com/mobile-apps), and [SEO & PPC](https://zeorbit.com/seo-ppc)."
)

# First unlinked phrase in the body → ZeOrbit service page (in-paragraph, TinyFrog-style).
ZEO_INLINE_LINKS = (
    (re.compile(r"\b(web design services)\b", re.I), "https://zeorbit.com/website-designing"),
    (re.compile(r"\b(website designing)\b", re.I), "https://zeorbit.com/website-designing"),
    (re.compile(r"\b(website design)\b", re.I), "https://zeorbit.com/website-designing"),
    (re.compile(r"\b(mobile apps?)\b", re.I), "https://zeorbit.com/mobile-apps"),
    (re.compile(r"\b(SEO(?:\s*[&/]| and )\s*PPC|paid search)\b", re.I), "https://zeorbit.com/seo-ppc"),
)

# Unlinked directory names (AI engines match these brands to ZeOrbit profiles).
EXTERNAL_LINK_LINE = (
    "ZeOrbit is listed on DesignRush, GoodFirms, Thumbtack, and Yelp "
    "for website and mobile app work in San Diego."
)

# Highlighted in-body words → third-party profiles ChatGPT/Gemini pull for "best of" lists.
CITATION_HIGHLIGHTS = (
    (
        re.compile(r"\b(website design(?:ing|er|ers)?)\b", re.I),
        "https://www.designrush.com/agency/profile/zeorbit",
    ),
    (
        re.compile(r"\b(mobile apps?)\b", re.I),
        "https://www.goodfirms.co/company/zeorbit",
    ),
    (
        re.compile(r"\b(websites?)\b", re.I),
        "https://www.yelp.com/biz/zeorbit-san-diego-2",
    ),
)

_INTERNAL_LINE_RE = re.compile(
    r"(?:See \[ZeOrbit website design\].*?seo-ppc\)\.?)",
    re.I | re.S,
)
_EXTERNAL_LINE_RE = re.compile(
    r"(?:You can also find ZeOrbit on \[Thumbtack\].*?zeorbit-san-diego-2\)\.?"
    r"|ZeOrbit is listed on DesignRush, GoodFirms, Thumbtack, and Yelp[^.]*\.)",
    re.I | re.S,
)


def _protect_markdown_links(text: str) -> tuple[str, list[str]]:
    held: list[str] = []

    def stash(m: re.Match) -> str:
        held.append(m.group(0))
        return f"@@LINK{len(held) - 1}@@"

    return re.sub(r"\[[^\]]+\]\([^)]+\)", stash, text or ""), held


def _restore_markdown_links(text: str, held: list[str]) -> str:
    out = text or ""
    for i, chunk in enumerate(held):
        out = out.replace(f"@@LINK{i}@@", chunk)
    return out


def highlight_zeorbit_internal(content: str) -> str:
    """Wrap natural service phrases with ZeOrbit URLs inside existing paragraphs."""
    text, held = _protect_markdown_links(content or "")
    used_urls: set[str] = set()
    blob = content or ""
    for pattern, url in ZEO_INLINE_LINKS:
        if url in used_urls or re.search(rf"\]\({re.escape(url)}\)", blob, re.I):
            continue

        def repl(m: re.Match, href: str = url) -> str:
            return f"[{m.group(1)}]({href})"

        text, n = pattern.subn(repl, text, count=1)
        if n:
            used_urls.add(url)
            blob = text
    return _restore_markdown_links(text, held)


def highlight_citation_keywords(content: str) -> str:
    """Wrap first leftover 'website design' / 'mobile app' / 'website' with listing URLs."""
    text, held = _protect_markdown_links(content or "")
    for pattern, url in CITATION_HIGHLIGHTS:
        if re.search(rf"\]\({re.escape(url)}\)", content or "", re.I):
            continue

        def repl(m: re.Match, href: str = url) -> str:
            return f"[{m.group(1)}]({href})"

        text, n = pattern.subn(repl, text, count=1)
        if n:
            continue
    return _restore_markdown_links(text, held)


def ensure_body_hyperlinks(content: str) -> str:
    """ZeOrbit links stay inside paragraphs. Directory mention is a last-sentence, not a link band."""
    text = (content or "").strip()
    text = _INTERNAL_LINE_RE.sub("", text)
    text = _EXTERNAL_LINE_RE.sub("", text)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    text = highlight_zeorbit_internal(text)
    text = highlight_citation_keywords(text)
    if not re.search(r"DesignRush|GoodFirms|Yelp", text, re.I):
        text = f"{text.rstrip()}\n\n{EXTERNAL_LINK_LINE}" if text else EXTERNAL_LINK_LINE
    return text


def strip_zip_from_copy(text: str, zip: str = "") -> str:
    """Remove this location's 5-digit ZIP (and any other ZIP) from body/intro/meta/title."""
    z = digits_zip(zip)
    out = text or ""
    if z:
        out = re.sub(rf"\[{re.escape(z)}\]\([^)]*\)", "", out)
        out = re.sub(rf"\b{re.escape(z)}\b", "", out)
    # Never leave a postal code in titles or body even if it is not the stored ZIP.
    out = re.sub(r"\[\d{5}\]\([^)]*\)", "", out)
    out = re.sub(r"\b\d{5}(?:-\d{4})?\b", "", out)
    out = re.sub(r"[ \t]{2,}", " ", out)
    out = re.sub(r"\s+,", ",", out)
    out = re.sub(r",\s*,", ",", out)
    out = re.sub(r"\s+\.", ".", out)
    return out.strip()


def linkify_zip(text: str, zip: str = "", city: str = "", state: str = "") -> str:
    """Turn a ZIP or old ZIP-only Maps link into a full Name, ST ZIP Maps link."""
    z = digits_zip(zip)
    if not z or not (text or ""):
        return text or ""
    linked = zip_hyperlink(z, city, state)
    out = text
    out = re.sub(
        rf"\[[^\]]*{re.escape(z)}[^\]]*\]\(https?://(?:www\.)?google\.com/maps[^)]*\)",
        linked,
        out,
        count=1,
        flags=re.I,
    )
    if linked.split("](")[0][1:] in out and "](https://www.google.com/maps/search/" in out:
        return out
    if f"[{z}](" in out:
        return re.sub(rf"\[{re.escape(z)}\]\([^)]*\)", linked, out, count=1)
    return re.sub(rf"\b{re.escape(z)}\b", linked, out, count=1)


def copy_has_zip(text: str, zip: str = "") -> bool:
    z = digits_zip(zip)
    blob = text or ""
    if z:
        return z in blob
    return bool(re.search(r"\b\d{5}\b", blob))


def force_zip_into_copy(text: str, city: str, state: str = "", zip: str = "") -> str:
    """Body must not contain ZIP — strip it."""
    return strip_zip_from_copy(text or "", zip)


def ensure_zip_in_meta(meta: str, city: str, state: str = "", zip: str = "") -> str:
    """Meta must not contain ZIP."""
    out = strip_zip_from_copy(meta or "", zip)
    if city and city.lower() not in out.lower():
        place = place_label(city, state, "")
        extra = f" in {place}." if place else ""
        out = (out.rstrip(". ") + extra).strip()
    return out[:160]


def ensure_zip_in_conclusion(text: str, city: str, state: str = "", zip: str = "") -> str:
    """ZIP does not belong in the conclusion/body."""
    return strip_zip_from_copy(text or "", zip)


def _faq_answer(faq: Any) -> str:
    if hasattr(faq, "answer"):
        return faq.answer or ""
    if isinstance(faq, dict):
        return faq.get("answer") or ""
    return ""


def _set_faq_answer(faq: Any, answer: str) -> None:
    if hasattr(faq, "answer"):
        faq.answer = answer
    elif isinstance(faq, dict):
        faq["answer"] = answer


def _set_faq_question(faq: Any, question: str) -> None:
    if hasattr(faq, "question"):
        faq.question = question
    elif isinstance(faq, dict):
        faq["question"] = question


def ensure_zip_in_last_faq(faqs: Sequence[Any], city: str, state: str = "", zip: str = "") -> list:
    """ZIP only in FAQ answers, as a full-place Google Maps hyperlink."""
    z = digits_zip(zip)
    out = list(faqs or [])
    if not z:
        return out
    linked = zip_hyperlink(z, city, state)
    place = place_label(city, state, "") or city or "this area"
    extra = f" We serve {place}, including {linked}."
    found = False
    for faq in out:
        q = getattr(faq, "question", None) if hasattr(faq, "question") else (faq.get("question") if isinstance(faq, dict) else "")
        _set_faq_question(faq, strip_zip_from_copy(q or "", z))
        ans = _faq_answer(faq)
        if z in ans:
            _set_faq_answer(faq, linkify_zip(ans, z, city, state))
            found = True
    if found:
        return out
    if not out:
        return [{"question": f"Does ZeOrbit work with businesses in {place}?", "answer": extra.strip()}]
    last = out[-1]
    _set_faq_answer(last, ((_faq_answer(last) or "").rstrip() + extra).strip())
    return out


def ensure_zip_in_body(text: str, city: str, state: str = "", zip: str = "") -> str:
    return strip_zip_from_copy(text or "", zip)


def apply_zip_faq_only(block: Any, city: str = "", state: str = "", zip: str = "") -> Any:
    """Strip ZIP from every body field; keep a hyperlinked ZIP in FAQs only."""
    z = digits_zip(zip or getattr(block, "zip", "") or "")
    for attr in ("title", "h1", "intro", "content", "meta_description", "cta"):
        if hasattr(block, attr):
            setattr(block, attr, strip_zip_from_copy(getattr(block, attr) or "", z))
    block.faqs = ensure_zip_in_last_faq(getattr(block, "faqs", None) or [], city, state, z)
    return block


def ensure_location_body(
    *,
    intro: str,
    content: str,
    city: str,
    state: str = "",
    industry: str = "",
    intent_id: str = "",
    index: int = 0,
    brief: str = "",
    zip: str = "",
) -> Tuple[str, str]:
    """Guarantee city-specific body — scrub foreign places + vague 'local / this area' stubs."""
    zip_bit = ""
    place = (
        f"{city}, {state}".strip(", ") if city and state else (city or state or "")
    )
    if not place:
        return intro or "", content or ""
    ind = industry or "small business"
    foreign = extract_foreign_places(brief or "", city)
    foreign = list(dict.fromkeys(foreign + extract_foreign_places(f"{intro}\n{content}", city)))
    intro_out = scrub_foreign_places(intro or "", city, foreign)
    content_out = scrub_foreign_places(content or "", city, foreign)
    # Scrub generic locality phrases that tank local relevance.
    generics = (
        (r"\blocal visitors\b", f"visitors in {city}"),
        (r"\bvisitors in this area\b", f"visitors in {city}"),
        (r"\bin this area\b", f"in {city}"),
        (r"\byour area\b", place),
        (r"\byour local area\b", place),
        (r"\bnearby customers\b", f"customers in {city}"),
        (r"\blocal businesses\b", f"businesses in {city}"),
        (r"\blocal customers\b", f"customers in {city}"),
    )
    for pattern, repl in generics:
        intro_out = re.sub(pattern, repl, intro_out, flags=re.I)
        content_out = re.sub(pattern, repl, content_out, flags=re.I)
    body = f"{intro_out}\n{content_out}"
    mentions = _body_mentions_city(body, city)
    if mentions < 3:
        inject = (
            f"\n\n## Why location matters in {city}\n\n"
            f"Businesses in {place} compete for attention from people who search on phones between errands. "
            f"A website for a {ind} owner here should name real services, make contact easy, and answer "
            f"questions {city} customers ask before they call.\n\n"
            f"ZeOrbit builds WordPress and Shopify sites, redesigns, and mobile-friendly layouts with "
            f"projects typically ranging from {ZEORBIT_FACTS['pricing_range']}. "
            f"With {ZEORBIT_FACTS['experience']} and {ZEORBIT_FACTS['reviews']}, the focus stays on a clear site "
            f"for {city} — not a thin page that only swaps the city name."
        )
        # Vary inject slightly by index so 33 locations are not identical add-ons.
        if index % 2:
            inject = (
                f"\n\n## Serving {ind} owners in {city}\n\n"
                f"If you run a {ind} in {place}, customers decide quickly whether your site looks trustworthy. "
                f"Pages should explain what you do in {city}, show how to reach you, and work on mobile.\n\n"
                f"ZeOrbit provides custom WordPress website development, Shopify builds when you sell online, "
                f"and redesigns when the current site is losing people. Typical website projects range from "
                f"{ZEORBIT_FACTS['pricing_range']} — practical scope, not empty “cheap” promises."
            )
        content_out = (content_out or "").rstrip() + inject
    # Ensure pricing + experience appear for scoring / factual gate.
    blob = f"{intro_out}\n{content_out}"
    if "500" not in blob and "$500" not in blob:
        content_out += (
            f"\n\nWebsite projects with ZeOrbit typically range from {ZEORBIT_FACTS['pricing_range']}, "
            f"backed by {ZEORBIT_FACTS['experience']} and {ZEORBIT_FACTS['reviews']}."
        )
    return intro_out, content_out


def score_page_quality(
    *,
    title: str,
    intro: str,
    content: str,
    faqs: Sequence[Any],
    city: str,
    intent_id: str,
    image_url: str,
    image_alt: str,
    image_concept_text: str,
    meta: str,
    existing_bodies: Optional[Sequence[str]] = None,
    content_type: str = "service",
    focus_keyword: str = "",
) -> QualityResult:
    """Master-rule weighted score. Fail factual / image / local gates → not publishable.

    For blogs (content_type=blog), local relevance is replaced by topic/query relevance
    so national how-to posts are not penalized for missing a city.
    """
    is_blog = (content_type or "").lower() in ("blog", "post")
    body = f"{intro or ''}\n{content or ''}"
    faq_txt = ""
    for f in faqs or []:
        if hasattr(f, "answer"):
            faq_txt += f" {getattr(f, 'question', '') or ''} {f.answer or ''}"
        elif isinstance(f, dict):
            faq_txt += f" {f.get('question') or ''} {f.get('answer') or ''}"
    zip_blob = faq_txt
    body_l = body.lower()
    reasons: List[str] = []

    # Factual accuracy 25%
    factual = 25.0
    # Penalize assertive "cheapest / #1 / best in City" claims — not educational warnings.
    if re.search(r"\bcheapest\b", body_l) and not re.search(
        r"(not|never|avoid|without|no|empty|don'?t|do not)\b[^.?]{0,50}\bcheapest\b|\bcheapest\b[^.?]{0,40}\b(promise|claim|in \{?city)",
        body_l,
    ):
        # Also allow quotes explaining what not to say
        if not re.search(r"[“\"'].{0,20}cheapest.{0,40}[”\"']", body_l):
            factual -= 15
            reasons.append("Unsupported superlative or cheapest claim")
    if re.search(r"\b#\s*1\b|best in " + re.escape((city or "").lower()), body_l):
        if not re.search(
            r"(not|never|avoid|without|don'?t|do not)\b[^.?]{0,40}(best in|#\s*1)",
            body_l,
        ):
            factual -= 15
            reasons.append("Unsupported #1 / best-in-city claim")
    # Flag only assertive fake-proof claims, not warnings like "avoid fake reviews".
    if re.search(
        r"(?<!avoid )(?<!avoiding )(?<!without )(?<!inventing )(?<!no )"
        r"\b(fake reviews?|fake clients?|fake testimonials?|fake awards?|guaranteed #1)\b",
        body_l,
    ):
        # Still allow educational "avoid … fake reviews" / "without inventing fake…"
        if not re.search(
            r"(avoid|without|never|don'?t|do not|not)\b[^.?]{0,40}\bfake (reviews?|clients?|testimonials?|awards?)\b",
            body_l,
        ):
            factual -= 20
            reasons.append("Suspicious unverifiable claim")
    pricing_ok = "500" in body or "$500" in body or "3,000" in body or "3000" in body
    # Location pages: soft price context. Blogs: only when the query is about cost/pricing.
    topic_l = (focus_keyword or title or "").lower()
    needs_pricing = (not is_blog) and intent_id in (
        "affordable", "discovery", "wordpress", "shopify", "redesign",
        "industry_local", "leads", "new_business", "general", "",
    )
    if is_blog:
        needs_pricing = bool(re.search(r"\b(cost|price|pricing|affordable|cheap)\b", topic_l))
    if needs_pricing and not pricing_ok:
        factual -= 5
        reasons.append("Missing pricing context")
    if (
        not is_blog
        and ZEORBIT_FACTS["experience"].split("+")[0] not in body
        and "two decades" not in body_l
        and "20+" not in body
    ):
        # soft — not always required on every page
        factual -= 2
    factual = max(0.0, factual)

    # Local relevance 20%  — OR topic/query relevance for blogs
    title_l = (title or "").lower()
    if is_blog:
        local = 0.0
        focus = (focus_keyword or "").lower().strip()
        focus_tokens = [t for t in re.findall(r"[a-z0-9]+", focus) if len(t) > 2]
        if focus and focus in body_l:
            local += 10
        elif focus_tokens:
            hits = sum(1 for t in focus_tokens if t in body_l)
            local += min(10.0, 2.5 * hits)
        if focus and (focus in title_l or all(t in title_l for t in focus_tokens[:3])):
            local += 6
        elif focus_tokens and sum(1 for t in focus_tokens if t in title_l) >= max(1, len(focus_tokens) // 2):
            local += 4
        # Practical how-to signals
        if re.search(r"\b(step|check|fix|guide|how to|mistake|test)\b", body_l):
            local += 4
        local = min(20.0, local)
        if local < 12:
            reasons.append("Weak topic / query relevance")
    else:
        local = 0.0
        city_hits = _body_mentions_city(body, city)
        if city_hits >= 3:
            local += 14
        elif city_hits >= 1:
            local += 10
        if city and any(t in title_l for t in _location_tokens(city)):
            local += 4
        if intent_id:
            local += 2
        if not copy_has_zip(zip_blob):
            local = 0.0
            reasons.append("ZIP code is mandatory in FAQ answers")
        local = min(20.0, local)
        if local < 12:
            reasons.append("Weak local relevance")

    # Customer usefulness 20%
    useful = 0.0
    markers = (
        "wordpress", "shopify", "mobile", "redesign", "lead", "cost", "price", "faq", "contact",
        "step", "fix", "check", "plugin", "hosting", "ssl", "dns", "browser", "backup",
    )
    useful += min(12.0, 2.0 * sum(1 for m in markers if m in body_l))
    useful += 4 if len(faqs or []) >= 3 else 2 if faqs else 0
    words = len(body.split())
    if 280 <= words <= 650:
        useful += 4
    elif words >= 220:
        useful += 2
    elif words > 900:
        useful += 1  # long pages are not a quality bonus
    useful = min(20.0, useful)
    if useful < 10:
        reasons.append("Insufficient customer usefulness / depth")

    # Uniqueness 15% — batch pages/posts share structure; only hard-penalize near-clones.
    unique = 15.0
    city_hits = _body_mentions_city(body, city) if city else 0
    if existing_bodies and is_too_similar(body, existing_bodies, threshold=0.88):
        long_enough = len(body.split()) >= 220
        local_ok = (not is_blog) and city_hits >= 2 and long_enough
        blog_ok = is_blog and long_enough
        if local_ok or blog_ok:
            unique = 12.0  # bulk set — still 90+ when specific enough
            reasons.append("Overlaps another page — kept (distinct enough copy)")
        else:
            unique = 7.0
            reasons.append("Too similar to another location page")
    elif len(body.split()) < 180:
        unique = 8.0

    # Image relevance 10%
    image = 0.0
    alt_l = (image_alt or "").lower()
    concept_l = (image_concept_text or "").lower()
    bad_img = ("beach", "hotel", "resort", "skyline", "tourist", "landscape", "picsum", "pipe", "wrench")
    if image_url and "picsum" not in (image_url or "").lower():
        image += 4
    if any(b in alt_l or b in concept_l for b in bad_img):
        image = 0
        reasons.append("Image appears tourism/unrelated")
    else:
        if any(k in alt_l or k in concept_l for k in ("website", "laptop", "designer", "shopify", "wordpress", "business", "owner", "mockup", "app", "web design")):
            image += 6
        image = min(10.0, image)
    if image < 5:
        reasons.append("Weak image relevance")

    # Natural language 5%
    natural = 5.0
    fluff_hits = sum(1 for f in AI_FLUFF if f in body_l)
    natural -= min(5.0, fluff_hits * 1.5)
    natural = max(0.0, natural)

    # SEO structure 5%
    seo = 0.0
    if title:
        seo += 1.5
    if meta and 110 <= len(meta) <= 170:
        seo += 1.5
    if len(faqs or []) >= 3:
        seo += 1
    if is_blog and focus_keyword and focus_keyword.lower() in title_l:
        seo += 1
    elif city and any(t in title_l for t in _location_tokens(city)):
        seo += 1
    seo = min(5.0, seo)

    breakdown = {
        "factual_accuracy": round(factual, 1),
        "local_relevance": round(local, 1),
        "customer_usefulness": round(useful, 1),
        "content_uniqueness": round(unique, 1),
        "image_relevance": round(image, 1),
        "natural_language": round(natural, 1),
        "seo_structure": round(seo, 1),
    }
    total = sum(breakdown.values())
    # Hard gates from master rule + user floor (90+)
    publishable = (
        factual >= 15
        and local >= 12
        and image >= 5
        and unique >= 7
        and total >= MIN_PUBLISH_SCORE
        and (is_blog or copy_has_zip(zip_blob))
    )
    if not is_blog and city and not copy_has_zip(zip_blob):
        reasons.append("ZIP code missing — location pages need the 5-digit ZIP in an FAQ answer")
    if total < MIN_PUBLISH_SCORE:
        reasons.append(f"Score {round(total, 1)} below {int(MIN_PUBLISH_SCORE)} floor")
    if not publishable and not reasons:
        reasons.append("Failed factual, local, image, uniqueness, or 90+ score gate")
    return QualityResult(score=round(total, 1), breakdown=breakdown, publishable=publishable, reasons=reasons)


def build_template_page_copy(
    intent: SearchIntent,
    city: str,
    state: str,
    industry: str,
    pretty_keyword: str,
    index: int,
    zip: str = "",
) -> Dict[str, Any]:
    """Deep, intent-specific template copy when LLM is unavailable."""
    place = place_label(city, state, zip) or (f"{city}, {state}".strip(", ") if state else (city or "your area"))
    ind = industry or "this business"
    pricing = ZEORBIT_FACTS["pricing_range"]
    facts = facts_blurb(index)
    problem = intent.customer_problem
    title = title_from_primary_keyword(pretty_keyword, city, ind, intent, index)
    h2s = intent_h2_set(intent, city, ind, "cards")
    faqs = intent_faqs(intent, city, ind, index)
    faqs = ensure_zip_in_last_faq(faqs, city, state, zip)
    concept = image_concept(intent, city, ind, index)
    example_a = ind
    example_b = ind

    intros = {
        "affordable": (
            f"If you're a small business in {place} looking for a reasonably priced website designer, "
            f"the right solution depends on what your business needs — not on stuffing “{city} website design” onto a thin page.\n\n"
            f"A {example_a} owner may need a lead-generation website, while {example_b} may need Shopify e-commerce. "
            f"{facts}"
        ),
        "shopify": (
            f"If your {ind} in {place} needs to sell online, a brochure site is not enough — you need a store that works on phones and makes checkout clear.\n\n"
            f"ZeOrbit provides Shopify website development along with WordPress builds when you need a broader marketing site. {facts}"
        ),
        "wordpress": (
            f"Many {ind} owners in {place} want a website they can update without calling a developer for every text change. WordPress is often the practical answer.\n\n"
            f"ZeOrbit builds custom WordPress websites with mobile-friendly layouts and SEO-friendly structure. {facts}"
        ),
        "redesign": (
            f"If your website is difficult to use on a phone, customers in {place} may leave before contacting you. That is a redesign problem, not a “post more on social” problem.\n\n"
            f"ZeOrbit provides website redesign and rebuild services so your services, contact paths, and mobile experience match what people expect. {facts}"
        ),
        "leads": (
            f"A website should help your {ind} in {place} get more leads — calls, forms, and booked conversations — not just look busy.\n\n"
            f"ZeOrbit focuses on conversion-focused website development: clear offers, service pages, and mobile-friendly paths to contact. {facts}"
        ),
        "mobile_app": (
            f"Do you need a website or a mobile app for your {ind} in {place}? For most businesses, a strong mobile-friendly website comes first; an app makes sense when customers need frequent, logged-in actions.\n\n"
            f"ZeOrbit provides website development and mobile application development so you can choose based on the real workflow. {facts}"
        ),
        "new_business": (
            f"If you are starting a business in {place}, you do not need a giant website on day one — you need a clear site that explains what you do and how to reach you.\n\n"
            f"ZeOrbit builds first websites for new businesses with room to grow into WordPress blogs, Shopify stores, or apps later. {facts}"
        ),
        "industry_local": (
            f"If you run a {ind} business in {place} and need a website that speaks to your customers, generic templates rarely explain your services well enough.\n\n"
            f"ZeOrbit builds websites for {ind} with clear service pages, local relevance, and practical next steps. {facts}"
        ),
        "discovery": (
            f"If you're looking for who can build a website for a small business in {place}, start with your real need: leads, online sales, a redesign, or a first site.\n\n"
            f"For example, {example_a} often need service pages that generate calls, while {example_b} may need product pages or booking flows. "
            f"ZeOrbit is a website design and development provider for WordPress, Shopify, redesigns, and mobile apps. {facts}"
        ),
    }
    intro = intros.get(intent.id, intros["discovery"])

    angle = _stable_int(city, intent.id, ind, str(index)) % 4
    angle_paras = (
        (
            f"In {city}, people often compare options on a phone between errands. "
            f"If your homepage is slow, vague, or missing a clear next step, they move on. "
            f"Your site should answer what you do, who you help, and how to contact you within a few seconds."
        ),
        (
            f"Owners of {ind} in {place} usually do not need buzzwords — they need a site that looks trustworthy and makes calling easy. "
            f"That means readable service pages, real photos when you have them, and forms that work on mobile."
        ),
        (
            f"Search engines and AI assistants look for clear relationships: who the provider is, what services exist, "
            f"which location is relevant, and what problem is solved. Thin “website design in {city}” pages do not help that understanding."
        ),
        (
            f"A practical plan for {ind} in {city} often starts with WordPress for marketing pages, Shopify when you sell products, "
            f"and a redesign when the current site is losing mobile visitors. ZeOrbit maps that choice before building."
        ),
    )

    platform_blocks = {
        "shopify": (
            f"Shopify fits when products, inventory, and checkout are the point. ZeOrbit can set up a Shopify storefront that is mobile-friendly and clear for first-time buyers in {city}.\n\n"
            f"If you also need service pages or a blog, ZeOrbit can advise whether Shopify alone is enough or whether a WordPress marketing site should sit alongside the store.\n\n"
            f"Common Shopify needs for {ind}: product collections, shipping clarity, and a checkout people finish on a phone.\n\n"
        ),
        "wordpress": (
            f"Custom WordPress website development gives {ind} in {city} flexible pages, blogs, and forms without locking you into a single template.\n\n"
            f"ZeOrbit structures sites for SEO-friendly headings and AI-search clarity so it is obvious what you do, who you help, and how to contact you.\n\n"
            f"You should be able to update text and photos later without rebuilding the whole site.\n\n"
        ),
        "mobile_app": (
            f"A mobile-friendly website is still how most people find and evaluate a {ind} in {city}. A mobile app helps when the same customers return often for bookings, accounts, or ordering.\n\n"
            f"ZeOrbit can map which path fits before you spend on the wrong build.\n\n"
            f"If customers only need to call or request a quote, start with the website. If they need repeat logged-in actions, discuss an app.\n\n"
        ),
        "redesign": (
            f"A redesign is not just new colors. For {ind} in {city}, it usually means clearer service pages, faster mobile layouts, and contact paths that do not hide behind clutter.\n\n"
            f"ZeOrbit can rebuild on WordPress or improve an existing site while protecting useful URLs with redirects when needed.\n\n"
        ),
        "leads": (
            f"Lead-focused sites for {ind} in {place} need strong service pages, simple forms, click-to-call, and landing pages that match ads or promotions.\n\n"
            f"ZeOrbit builds conversion-focused layouts so visitors are not left guessing what to do next.\n\n"
        ),
        "affordable": (
            f"Reasonably priced does not mean empty. In the {pricing} range, a {city} business can usually get a professional multi-page site with mobile-friendly layouts and a clear contact path.\n\n"
            f"ZeOrbit keeps scope honest so you are not paying for features you will not use in year one.\n\n"
        ),
    }
    platform_para = platform_blocks.get(
        intent.service_emphasis,
        (
            f"ZeOrbit provides custom WordPress website development, Shopify website development, website redesign, "
            f"mobile-friendly builds, SEO-friendly structure, conversion-focused layouts, and mobile application development when needed.\n\n"
            f"The right mix depends on whether your {ind} in {city} needs leads, online sales, a rebuild, or a first site. "
            f"Nearby examples: {example_a} often need service/lead pages; {example_b} may need catalog or booking flows.\n\n"
        ),
    )

    content = (
        f"## {h2s[0]}\n\n"
        f"A business that {problem} usually needs more than a one-paragraph homepage. "
        f"In {place}, people compare options quickly — especially on phones — so your site should explain services, show how to contact you, and answer obvious questions.\n\n"
        f"{angle_paras[angle]}\n\n"
        f"## {h2s[1]}\n\n"
        f"{platform_para}"
        f"## {h2s[2]}\n\n"
        f"Technology should follow the job: WordPress for flexible marketing sites, Shopify for stores, redesign when the current site is losing people. "
        f"ZeOrbit maps that choice for {ind} in {city} before building. "
        f"Projects typically range from {pricing}.\n\n"
    )

    meta = (
        f"ZeOrbit builds WordPress and Shopify websites for {ind} in {place}. "
        f"Projects typically {pricing}. Practical, mobile-friendly sites — talk with us."
    )
    meta = ensure_zip_in_meta(meta, city, state, zip)

    cta_options = (
        f"If your {ind} in {city} needs a website that matches a real business problem, ZeOrbit can help with WordPress, Shopify, redesign, or mobile apps. Not sure where to start? We're here to help.",
        f"Ready to talk through a reasonably priced website for your {city} business? ZeOrbit website projects typically range from {pricing}. Reach out and we'll map a practical plan.",
        f"Need a clearer website for customers in {place}? ZeOrbit builds conversion-focused, mobile-friendly sites with SEO-friendly structure. Contact ZeOrbit to get started.",
        f"Building or rebuilding a site for {ind} in {city}? ZeOrbit can recommend WordPress, Shopify, or a redesign based on what customers need to do next.",
    )
    cta = cta_options[index % len(cta_options)]

    return {
        "title": title,
        "h1": title if len(title) < 70 else f"{pretty_keyword} in {place}",
        "meta_description": meta,
        "intro": intro,
        "content": content,
        "h2s": h2s,
        "h3s": [
            "WordPress and Shopify options",
            "Mobile-friendly and SEO-friendly structure",
            f"Practical pricing ({pricing})",
            "A clear next step with ZeOrbit",
        ],
        "faqs": faqs,
        "cta": cta,
        "search_intent": intent.id,
        "customer_problem": problem,
        "image_concept": concept,
        "industry": ind,
    }
