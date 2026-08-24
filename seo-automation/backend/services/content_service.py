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

TITLE_VARIANTS = [
    "Best {BT} in {city}, {state} | Affordable, Proven Results",
    "Top {BT} Services in {city}, {state} — Free Estimates",
    "Affordable {BT} in {city} | Trusted by Local Businesses",
    "#1 {BT} Company in {city}, {state} | Licensed Experts",
    "Proven {BT} Services in {city} — Best Rates, Fast Turnaround",
    "Best {BT} for Small Businesses in {city}, {state}",
]

META_VARIANTS = [
    "Looking for the best {bt} in {city}? Our proven team delivers affordable, results-driven {bt} services for {city} businesses. Free estimate — call today.",
    "Top-rated {bt} in {city}, {state}. Affordable pricing, fast turnaround, and guaranteed results. Trusted by 500+ local businesses. Get your free quote now.",
    "Affordable {bt} services in {city}. We help local businesses grow with proven {bt} strategies. Licensed experts, transparent pricing. Call for a free consultation.",
    "Need a trusted {bt} in {city}, {state}? We specialize in helping {city} businesses get found online. Best rates, proven results. Contact us today.",
]

H1_VARIANTS = [
    "Best {BT} in {city}, {state} — Affordable, Proven & Local",
    "Top-Rated {BT} Services in {city} | Trusted by Local Businesses",
    "Affordable {BT} in {city}, {state} — Results That Speak for Themselves",
    "Your Local {BT} Experts in {city} | Best Rates, Proven Results",
    "#1 {BT} Company Serving {city}, {state} — Free Estimates",
]

H2_POOL = [
    "What Does a {BT} Do in {city}?",
    "How Much Does {BT} Cost in {city}?",
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
    "If you're looking for the best {bt} in {city}, {state}, you've found the right team. "
    "We help {city} businesses get more customers online with affordable, proven {bt} services. "
    "Our local experts know {city}'s market and deliver results that matter.",

    "{city} businesses trust us for professional {bt} services that actually work. "
    "We're a locally based {bt} team serving {city}, {state} with transparent pricing and real results. "
    "Whether you're a small contractor or a growing company, we have the right {bt} solution for you.",

    "The best {bt} in {city} isn't the most expensive — it's the one that delivers results. "
    "Our {city}-based {bt} team has helped hundreds of local businesses grow their online presence. "
    "Affordable rates, proven strategies, and a team that knows {city} inside and out.",
]

BODY_SECTION_VARIANTS = [
    "{city} is a competitive market, and standing out online requires more than just a basic website. "
    "Our {bt} services are built specifically for {city} businesses that want to attract local customers. "
    "Here's what sets us apart:\n\n"
    "• Local expertise — we know {city}'s neighborhoods, competitors, and customer behavior\n"
    "• Affordable pricing — no agency markups, just honest rates for {city} businesses\n"
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
        "How much does {bt} cost in {city}?",
        "{BT} costs in {city} vary by scope, but most small business packages range from $500 to $3,000. "
        "Our {city} team offers transparent, flat-rate pricing with no hidden fees. "
        "Contact us for a free estimate tailored to your {city} business."
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
        "transparent pricing, clear communication, and measurable deliverables. "
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


def pick_primary_keyword(
    target_keywords: list,
    business_type: str,
    city: str,
    index: int = 0,
    industry: str = "",
) -> str:
    """Pick the SEO primary keyword for this page.

    Prefer keywords that already name the Industry (e.g. Healthcare). Otherwise
    rotate the list, and for website-design niches prefix the industry so titles
    become "Healthcare Website Design in Downtown Chula Vista…" not a bare
    "WordPress Website Design" that ignores Healthcare / Startups.
    """
    kws = [str(k).strip() for k in (target_keywords or []) if str(k).strip()]
    ind = (industry or "").strip()
    ind_l = ind.lower()

    def _with_industry(kw: str) -> str:
        if not ind or ind_l in (kw or "").lower():
            return kw
        if re.search(r"website|wordpress|web design|landing page", kw, re.I):
            # "WordPress Website Design" → "Healthcare WordPress Website Design"
            # unless kw already leads with a vertical word.
            return f"{ind} {kw}".strip()
        return kw

    if kws:
        aligned = [k for k in kws if ind_l and ind_l in k.lower()]
        pool = aligned or kws
        return _with_industry(pool[int(index) % len(pool)])
    loc = (city or "").strip()
    base = (business_type or "website design").strip()
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


def _looks_like_writing_brief(text: str) -> bool:
    """True when text is an AI instruction / style brief, not a topic or body copy."""
    t = (text or "").strip().lower()
    if not t:
        return False
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
        "conversion-driven",
    )
    if any(m in t for m in markers):
        return True
    # Long multi-sentence writing directions without a clear how-to topic
    if len(t) > 160 and t.count(".") >= 2 and not re.search(
        r"^(how to|what is|why |are you |common |guide)", t
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
        if brief_l and len(brief_l) > 40 and (
            pl == brief_l or (brief_l in pl and len(pl) < len(brief_l) + 40)
        ):
            continue
        keep.append(p)
    return "\n\n".join(keep)


def article_topic(brief: str, target_keywords: list, business_type: str) -> str:
    """Blog topic = the how-to / keyword, not a leftover page brief."""
    kws = [str(k).strip() for k in (target_keywords or []) if str(k).strip()]
    for k in kws:
        if re.search(r"how to|301|302|redirect|guide|what is|why ", k, re.I):
            return k
    b = (brief or "").strip()
    if _looks_like_writing_brief(b):
        b = ""
    if kws and (not b or len(b) > 140):
        return kws[0]
    if b and len(b) <= 140 and not _looks_like_writing_brief(b):
        return re.sub(r"[?!.]+$", "", b).strip() or (kws[0] if kws else business_type)
    return kws[0] if kws else (business_type or "guide")


def _page_meta_title(
    primary: str,
    city: str,
    state: str,
    index: int = 0,
    industry: str = "",
) -> str:
    """Location SEO titles in the ZeOrbit pattern the team uses in GSC sheets.

    Examples:
    - Healthcare Website Design in Downtown Chula Vista, CA | WordPress Experts
    - WordPress Website Design for Healthcare in East Chula Vista, CA
    - Small Business Website Design for Healthcare in Eastlake, CA
    """
    loc = f"{city}, {state}" if state and state not in (city or "") else city
    pretty = pretty_keyword(primary)
    ind = pretty_keyword(industry) if industry else ""
    if ind:
        patterns = [
            f"{ind} Website Design in {loc} | WordPress Experts",
            f"{ind} Website Designer in {loc} | WordPress Design",
            f"WordPress Website Design for {ind} in {loc}",
            f"{ind} Business Website Design in {loc} | WordPress Experts",
            f"Small Business Website Design for {ind} in {loc}",
            f"Custom {ind} Website Design in {loc}",
            f"{ind} Website Designer in {loc} | WordPress",
            f"WordPress Website Design for {ind} in {loc}",
            f"{ind} Business Website Design in {loc}",
            f"{pretty} in {loc} | WordPress Experts",
        ]
    else:
        patterns = [
            f"{pretty} in {loc} | WordPress Experts",
            f"{pretty} in {loc} | WordPress Design",
            f"{pretty} in {loc} | Local Web Design",
            f"{pretty} in {loc}",
        ]
    title = patterns[int(index) % len(patterns)]
    if len(title) > 78:
        title = f"{pretty} in {loc}" if pretty else f"{ind} Website Design in {loc}"
    return title[:80]


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


def _sectioned_body(h2s: list, intro: str, content: str, brief: str = "") -> str:
    """Every H2 gets real paragraphs so the live article is not heading-only."""
    heads = [_as_text(h) for h in (h2s or []) if _as_text(h)]
    intro_t = _strip_instruction_leak(_as_text(intro), brief)
    body = _strip_instruction_leak(_as_text(content), brief)
    if heads and re.search(r"(?m)^##\s+", body):
        missing = [h for h in heads if not re.search(rf"(?m)^##\s+{re.escape(h)}\s*$", body)]
        if not missing:
            # Still ensure no section is empty
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
                    rest = (
                        f"{heading}. ZeOrbit covers this in clear, useful detail — what you offer, "
                        f"who it is for in this area, and the practical next step visitors should take."
                    )
                rebuilt.append(f"## {heading}\n\n{rest}")
            return "\n\n".join(rebuilt)
    # Drop leftover markdown headings so we do not wrap ## twice.
    body = re.sub(r"(?m)^##\s+.+$", "", body).strip()
    paras = [p.strip() for p in re.split(r"\n{2,}", body) if p.strip()]
    if not paras and intro_t:
        paras = [p.strip() for p in re.split(r"\n{2,}", intro_t) if p.strip()]
        intro_t = ""
    if not heads:
        return body or intro_t
    if not paras:
        paras = [
            f"{h}. ZeOrbit builds this into a clear, useful page — what you offer, who it is for, and the next step."
            for h in heads
        ]
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
        piece = chunks[i] or [
            f"{h}. We cover this in plain language so visitors in this area know exactly what to do next. "
            f"ZeOrbit builds WordPress sites with clear service pages, local signals, and a simple path to contact."
        ]
        # Ensure minimum substance per section
        joined = "\n\n".join(piece)
        if len(joined.split()) < 25:
            joined = (
                f"{joined} ZeOrbit helps you turn this into a practical page for local visitors — "
                f"clear messaging, mobile layout, and a next step that feels natural."
            )
        out.append(f"## {h}\n\n{joined}")
    extra = paras[idx:]
    if extra:
        out.append("\n\n".join(extra))
    return "\n\n".join(out)


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
    """Returns keyword density as a percentage (0-100 scale for display).

    Counts each significant keyword word's occurrences independently rather
    than requiring the exact contiguous phrase — natural copy mentions
    keyword components ("web design", "San Diego") throughout far more often
    than the literal full phrase back-to-back, so phrase-only counting
    under-reports real keyword coverage.
    """
    words = text.lower().split()
    kw_words = [w for w in keyword.lower().split() if w]
    if not kw_words or not words:
        return 0.0
    total_hits = sum(words.count(w) for w in kw_words)
    raw = (total_hits / len(kw_words)) / len(words) * 100  # avg occurrences per keyword word, as %
    # Ideal keyword density is 1-3%. Map 2% → 100, cap at 100.
    return round(min((raw / 2.0) * 100, 100), 1)

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
    base_url = site_url.rstrip("/") if site_url else ""
    page_url = f"{base_url}/{slug}" if base_url else ""

    faq_schema = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": faq.question,
                "acceptedAnswer": {"@type": "Answer", "text": faq.answer}
            }
            for faq in faqs
        ]
    }

    local_schema: Dict[str, Any] = {
        "@context": "https://schema.org",
        "@type": "LocalBusiness",
        "name": business_name or f"{bt.title()} Services {city}",
        "description": f"{bt.title()} services in {city}, {state}.",
        "address": {
            "@type": "PostalAddress",
            "addressLocality": city,
            "addressRegion": state,
            "addressCountry": "US"
        },
        "areaServed": {"@type": "City", "name": city, "addressRegion": state},
        "serviceType": bt.title(),
    }
    if page_url:
        local_schema["url"] = base_url
    if phone:
        local_schema["telephone"] = phone

    schema = {"local_business": local_schema, "faq_page": faq_schema}

    # ── Article + Breadcrumb schema (AEO-friendly) ──────────────
    if article_title:
        article_schema: Dict[str, Any] = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": article_title,
            "about": bt.title(),
        }
        if business_name:
            article_schema["author"] = {"@type": "Organization", "name": business_name}
            article_schema["publisher"] = {"@type": "Organization", "name": business_name}
        if page_url:
            article_schema["mainEntityOfPage"] = {"@type": "WebPage", "@id": page_url}
        schema["article"] = article_schema

        breadcrumb = {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Home", "item": base_url or "/"},
                {"@type": "ListItem", "position": 2, "name": "Blog",
                 "item": f"{base_url}/blog" if base_url else "/blog"},
                {"@type": "ListItem", "position": 3, "name": article_title,
                 "item": page_url or ""},
            ],
        }
        schema["breadcrumb"] = breadcrumb

    return schema


VOICE_RULES = """
VOICE — American English, user-first, conversational (ZeOrbit):
- Write the way a helpful US teammate talks, not an agency brochure.
- Short questions: "Thinking about a mobile app for your business?"
- Direct help: "Looking for a website or a custom digital solution?"
- Capability, not hype: "We help you turn your idea into an MVP, prototype, or fully functional product from concept to launch."
- Soft next step: "Not sure where to start? We're here to help."
- Use American spelling: optimize, color, center, organization, favorite.
- Avoid stiff jargon (synergies, leverage, best-in-class, holistic solutions).
- Second person ("you") over "businesses seeking world-class partners".
- NEVER paste Custom Content Requirements, writing briefs, or meta-instructions into the article body.
- NEVER leave an H2 empty — every heading needs 2–4 full sentences of real content.
- Vary structure: do not reuse the same five generic H2s on every page. Match the BODY LAYOUT note.
- Quality bar: content should read like a strong ChatGPT / Claude / Gemini draft — specific, natural, topic-aware.
"""

LAYOUT_VARIANTS = ("qa", "steps", "story", "cards", "split", "timeline")

LAYOUT_INSTRUCTIONS = {
    "qa": "Use question-style H2s a real customer would ask. Body answers in short paragraphs, then a 3-item list under at least one H2.",
    "steps": "Structure as a how-to: H2s are numbered steps (Step 1…, Step 2…). Body is actionable with concrete deliverables, not a pitch dump.",
    "story": "Open with a local situation, then proof, then what working together looks like. One H2 should be a short anecdote tied to this industry/location.",
    "cards": "Each H2 is a distinct benefit/offer card (speed, local SEO, care plan, cost clarity, launch support). Keep each section 2-4 sentences plus one concrete example.",
    "split": "Alternate problem vs solution: first H2 is the pain in this city, next is how you fix it, then who it's for, then timeline, then next step.",
    "timeline": "Walk the reader through a project timeline (week 1 discovery → design → build → launch → support). Name real milestones.",
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
    }
    return sets.get(layout) or sets["cards"]


PROVIDER_STYLE_NOTES = {
    "openai": "Write with GPT-4-level clarity: crisp sentences, concrete examples, no filler.",
    "chatgpt": "Write with GPT-4-level clarity: crisp sentences, concrete examples, no filler.",
    "gpt": "Write with GPT-4-level clarity: crisp sentences, concrete examples, no filler.",
    "anthropic": "Write with Claude-level care: structured, precise, naturally varied section openings.",
    "claude": "Write with Claude-level care: structured, precise, naturally varied section openings.",
    "gemini": "Write with Gemini-level breadth: useful detail, natural local flavor, strong scannability.",
    "groq": "Write tightly and specifically — every paragraph earns its place; no template filler.",
}


def pick_layout_variant(city: str, business_type: str, kind: str = "service") -> str:
    seed = f"{kind}|{(business_type or '').lower()}|{(city or '').lower()}"
    h = int(hashlib.md5(seed.encode()).hexdigest(), 16)
    return LAYOUT_VARIANTS[h % len(LAYOUT_VARIANTS)]


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
) -> SEOBlock:
    from services.image_service import resolve_campaign_niche
    city, state = _one_place(city, state)
    original_niche = normalize_niche_text(business_type or "")
    # Keep ZeOrbit's service (WordPress / web design). Industry is the buyer vertical.
    business_type = resolve_campaign_niche(original_niche, industry or "")
    kind = "blog" if (content_kind or "page") == "post" else "service"
    primary_kw = (
        article_topic(custom_requirements, target_keywords, business_type)
        if kind == "blog"
        else pick_primary_keyword(
            target_keywords, business_type, city, keyword_index, industry=industry or "",
        )
    )
    layout = pick_layout_variant(city, primary_kw or business_type, kind)
    gen_kwargs = dict(
        business_type=business_type, city=city, state=state, target_keywords=target_keywords,
        industry=industry, custom_requirements=custom_requirements, content_kind=kind,
        audience=audience, layout_variant=layout, keyword_index=keyword_index,
        primary_keyword=primary_kw,
    )
    if use_ai:
        try:
            block = await _generate_ai_block(llm_provider=llm_provider, **gen_kwargs)
        except Exception as e:
            print(f"[AI] LLM generation failed, retrying once: {e}")
            try:
                block = await _generate_ai_block(llm_provider=llm_provider, **gen_kwargs)
            except Exception as e2:
                print(f"[AI] LLM retry failed, falling back to templates: {e2}")
                block = await _generate_template_block(**gen_kwargs)
    else:
        block = await _generate_template_block(**gen_kwargs)

    from services.slug_utils import article_slug
    slug_kws = [primary_kw] + [k for k in (target_keywords or []) if k and k != primary_kw]
    slug_seed = primary_kw if kind == "blog" else business_type
    block.slug = article_slug(slug_kws, city, slug_seed)
    block.content_type = kind
    block.layout_variant = layout
    block.city = city
    block.state = state or block.state
    # Pages: primary includes location for GSC-style focus keywords.
    if kind == "blog":
        focus = primary_kw.lower()
    else:
        focus = f"{primary_kw} {city}".lower().strip() if city else primary_kw.lower()
    if block.keywords:
        block.keywords.primary = focus
    block.focus_keyword = focus

    try:
        from services.image_service import generate_article_images
        # Use one clean focus phrase — never mash primary_kw + business_type (causes bad captions).
        img_focus = primary_kw if kind == "blog" else (original_niche or primary_kw or business_type)
        images = await generate_article_images(
            img_focus, f"{city}, {state}".strip(", "), "ZeOrbit", count=3,
            exclude_urls=exclude_image_urls,
            industry="" if kind == "blog" else (industry or ""),
            niche=primary_kw if kind == "blog" else original_niche,
        )
        block.in_content_images = images
        if images:
            block.featured_image_url = images[0].url
        else:
            block.featured_image_url = await _get_business_image(img_focus, city)
        print(f"[Image] Set {len(images)} image(s) for {img_focus} in {city}")
    except Exception as e:
        print(f"[Image] Failed to set image: {e}")
        block.featured_image_url = await _get_business_image(primary_kw or business_type, city)

    return block


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
) -> SEOBlock:
    """Generate SEO content using an LLM (GPT-4, Gemini, or Groq — whichever
    is configured/selected) for higher quality, unique content."""
    from services.llm_service import chat_json

    city, state = _one_place(city, state)
    brief = (custom_requirements or "").strip()
    place = f"{city}, {state}".strip(", ") if state else city
    who = _audience_who(industry, audience)
    buyers = _buyer_word(industry)
    audience_line = (
        f"Speak to: {who} in {place or 'the US'}."
        if audience or industry else
        "Speak to a US business owner or operator."
    )
    kw_line = ", ".join(target_keywords) if target_keywords else "None"
    primary_kw = (primary_keyword or pick_primary_keyword(
        target_keywords, business_type, city, keyword_index, industry=industry or "",
    )).strip()
    layout = layout_variant if layout_variant in LAYOUT_INSTRUCTIONS else pick_layout_variant(city, business_type, content_kind)
    layout_note = LAYOUT_INSTRUCTIONS[layout]
    provider_key = (llm_provider or "").lower().strip()
    provider_note = PROVIDER_STYLE_NOTES.get(provider_key, "Write at the quality level of ChatGPT, Claude, or Gemini — specific and human.")

    if content_kind == "blog":
        topic = article_topic(brief, target_keywords, business_type) or primary_kw
        primary_kw = topic
        keywords = KeywordSet(
            primary=primary_kw.lower(),
            secondary=[k.lower() for k in (target_keywords[1:6] or [topic.lower()])],
            long_tail=[f"how to {primary_kw.lower()}", f"{primary_kw.lower()} guide", f"{primary_kw.lower()} explained"],
            near_me=[],
            user_questions=[
                f"What is {primary_kw}?",
                f"How do I {primary_kw.lower()}?",
                f"Why does {primary_kw.lower()} matter?",
                f"What mistakes should I avoid?",
            ],
        )
        loc_note = (
            f"Optional local color: you MAY mention {place} once if it helps, but this is NOT a location landing page."
            if place else
            "Do not force a city into the title, H1, or every paragraph. This is a topic article."
        )
        # Brief is prompt-only — never use instruction briefs as the article topic body.
        extra_brief = ""
        if brief and not _looks_like_writing_brief(brief) and brief.lower() not in topic.lower() and len(brief) > 20:
            extra_brief = brief
        elif brief and _looks_like_writing_brief(brief):
            extra_brief = (
                "(Editor style notes — follow these as writing guidance ONLY; "
                "do NOT quote or paste them into the article.)\n" + brief
            )
        prompt = f"""You are a US content writer creating ONE blog post / article for ZeOrbit.com.
Model style: {provider_note}

THIS ARTICLE'S TOPIC (this is the subject — teach it, do not replace it):
{topic}

Custom notes from the editor (guidance only — NEVER paste into the published body):
{extra_brief or "None — stay on the topic above."}

Business context (only mention if the topic is about hiring help): ZeOrbit builds websites, apps, and SEO for US companies. Do not turn a how-to into a ZeOrbit sales page.
Industry field (do NOT write as if ZeOrbit is a {industry or "clinic"}): {industry or "n/a"}
{audience_line}
SEO keywords to weave in naturally: {kw_line}
BODY LAYOUT ({layout}): {layout_note}
{loc_note}

{VOICE_RULES}

NON-NEGOTIABLE:
- If the topic is about 301 redirects (or any how-to), explain WHAT a 301 is, WHEN to use it, HOW to set it (Apache .htaccess, Nginx, WordPress plugins, hosting panels), how to test it, and common mistakes.
- Do not write generic "web design in San Diego" copy.
- Do not write about {industry or "an unrelated industry"} unless the topic itself is that industry.
- Title and H1 must name the topic (e.g. "How to Set 301 Redirects on a Website").
- content MUST use markdown H2 lines that exactly match each string in h2s, with 2–4 full paragraphs under EVERY H2 (80+ words each). No empty sections.
- Do NOT include Custom Content Requirements text in intro, content, faqs, or cta.

Generate a JSON response with EXACTLY this structure:
{{
  "title": "SEO title 50-60 chars, about the topic (not a list of cities)",
  "meta_description": "150-160 chars, promise the reader will learn the topic",
  "h1": "Clear article H1 that matches the topic (question or how-to is fine)",
  "h2s": ["5 DISTINCT H2s shaped by the {layout} layout — not the same generic list every time"],
  "h3s": ["4 short supporting labels (not empty body sections)"],
  "intro": "2-3 sentences. Open with a user-focused question or situation, then say what this post covers.",
  "content": "Markdown: for EACH h2 write '## Exact H2' then 2-4 paragraphs. 700+ words total. Numbered/bulleted steps when teaching. Separate paragraphs with double newlines. Include real steps (file names, plugin names, or hosting UI) when technical.",
  "faqs": [
    {{"question": "Practical FAQ 1 about the topic", "answer": "2-3 sentence answer"}},
    {{"question": "FAQ 2", "answer": "2-3 sentence answer"}},
    {{"question": "FAQ 3", "answer": "2-3 sentence answer"}},
    {{"question": "FAQ 4", "answer": "2-3 sentence answer"}},
    {{"question": "FAQ 5", "answer": "2-3 sentence answer"}},
    {{"question": "FAQ 6", "answer": "2-3 sentence answer"}}
  ],
  "cta": "Soft American CTA: invite a conversation if they need help applying this — not a hard sell."
}}

Return ONLY valid JSON, no markdown fences."""
    else:
        pretty = pretty_keyword(primary_kw)
        keywords = KeywordSet(
            long_tail=[f"{primary_kw.lower()} {city.lower()}".strip(), f"{business_type.lower()} for {who}"],
            near_me=[f"{primary_kw.lower()} near me"],
            user_questions=[
                f"Who builds {primary_kw.lower()} in {city}?",
                f"How does ZeOrbit help {who} in {city}?",
                f"What should a {industry or 'business'} website include?",
                f"How long does WordPress website design take?",
                f"Will the site help us get found by local {buyers}?",
                f"How do we get started with ZeOrbit?",
            ],
        )
        faq_questions = "\n".join([f"- {q}" for q in keywords.user_questions[:6]])
        meta_title_example = _page_meta_title(
            primary_kw, city, state, keyword_index, industry=industry or "",
        )
        h2_examples = _page_h2_set(layout, industry, buyers, city, audience, pretty)
        h2_json = json.dumps(h2_examples)
        brief_block = brief if brief else (
            "Promote ZeOrbit WordPress / website design for this industry and audience in this location."
        )
        prompt = f"""You are writing ONE ZeOrbit service / location PAGE (not a blog post, not a medical article).
Model style: {provider_note}

WHO WE ARE: ZeOrbit is a San Diego technology company. We SELL website design, WordPress, landing pages, SEO, and AI-search-friendly sites. We are NOT a {industry or "healthcare"} provider.

WHAT THIS PAGE SELLS: {business_type}
WHO IT IS FOR: {who}
WHERE: {place or "the United States"} — this is the ONLY place named on the page.
PRIMARY KEYWORD (must appear in title, H1, and intro): {pretty}
Other keywords to use naturally (do not dump as a list): {kw_line}
TITLE PATTERN to follow closely: {meta_title_example}

CUSTOM CONTENT REQUIREMENTS — WRITING BRIEF ONLY (follow these points; NEVER paste this block into intro/content/cta/faqs):
{brief_block}

{audience_line}
BODY LAYOUT ({layout}): {layout_note}
Suggested H2 set for this layout (you may refine wording, but keep this structure variety — do NOT default to the old generic five every time):
{h2_json}
{VOICE_RULES}

NON-NEGOTIABLE:
- ZeOrbit is the vendor. {industry or "The industry"} is the CLIENT type, not ZeOrbit's own business.
- Do not write as if we treat patients, file lawsuits, or sell houses unless the niche is that trade AND we are that trade. Here we build websites FOR {who}.
- Open like: "{who[:1].upper() + who[1:] if who else "Businesses"} in {city or "your city"} need a website that is easy to use, easy to find, and built to turn visitors into {buyers}."
- Then: "ZeOrbit provides WordPress website design for {industry or "local"} businesses..."
- Cover: custom WordPress, mobile layouts, service pages, high-converting landing pages, contact/appointment paths, local SEO, speed, AI-search-friendly structure, turning visitors into leads — woven into the layout, not as identical sections every page.
- Keep copy simple, credible, localized to {city} only, conversion-driven, and UNIQUE to this page's layout + brief.
- Do NOT list other neighborhoods. Do NOT write generic filler.
- Name ZeOrbit in the intro and the CTA.
- content MUST include '## Exact H2' for each h2s item with 2–4 full paragraphs under each (no empty headings). 700+ words.
- NEVER copy the CUSTOM CONTENT REQUIREMENTS paragraph(s) into the published fields.

Generate a JSON response with EXACTLY this structure:
{{
  "title": "{meta_title_example}",
  "meta_description": "150-160 chars: ZeOrbit WordPress / website design for {who} in {city}, with a helpful CTA",
  "h1": "{pretty} in {place or city}",
  "h2s": {h2_json},
  "h3s": ["Custom WordPress and landing pages", "Local SEO-friendly content", "Clear next steps for {buyers}", "A simple way to start"],
  "intro": "2-3 sentences. Audience + {city}. ZeOrbit builds the site. What they get.",
  "content": "Markdown sections matching h2s. Each section 2-4 paragraphs. Include one short bullet list of deliverables somewhere. Stay on WordPress / website design for {who} in {city}.",
  "faqs": [
    {{"question": "FAQ 1 for {who} in {city}", "answer": "2-3 sentences, ZeOrbit as the builder"}},
    {{"question": "FAQ 2", "answer": "2-3 sentences"}},
    {{"question": "FAQ 3", "answer": "2-3 sentences"}},
    {{"question": "FAQ 4", "answer": "2-3 sentences"}},
    {{"question": "FAQ 5", "answer": "2-3 sentences"}},
    {{"question": "FAQ 6", "answer": "2-3 sentences"}}
  ],
  "cta": "Need a {pretty.lower()} in {city}? ZeOrbit can build a professional WordPress website designed for local visibility, trust, and conversions. Not sure where to start? We're here to help."
}}

FAQ questions to address:
{faq_questions}

Return ONLY valid JSON, no markdown fences."""

    data = await chat_json(prompt, temperature=0.72 if content_kind == "blog" else 0.78, max_tokens=4500, provider=llm_provider)
    if not data:
        raise RuntimeError("LLM generation failed or returned no data")
    bt = business_type.title()
    slug = _slugify(f"{primary_kw.lower()}-{city}") if city else _slugify(primary_kw)

    faqs = []
    for f in data.get("faqs") or []:
        if isinstance(f, dict) and f.get("question"):
            faqs.append(FAQItem(question=_as_text(f.get("question")), answer=_as_text(f.get("answer"))))
    schema = _build_schema(bt, city, state, faqs)

    # Pages: lock SEO title + H1 to the ZeOrbit location pattern (do not trust LLM drift).
    if content_kind == "blog":
        title = _as_text(data.get("title")) or pretty_keyword(primary_kw)[:60]
        h1 = _as_text(data.get("h1")) or pretty_keyword(primary_kw)
    else:
        title = _page_meta_title(
            primary_kw, city, state, keyword_index, industry=industry or "",
        )
        h1 = f"{pretty_keyword(primary_kw)} in {place}" if place else pretty_keyword(primary_kw)
    meta = _strip_instruction_leak(_as_text(data.get("meta_description")), brief)
    h2s = [_as_text(h) for h in (data.get("h2s") or []) if _as_text(h)]
    if content_kind != "blog" and len(h2s) < 4:
        h2s = _page_h2_set(layout, industry, buyers, city, audience, pretty_keyword(primary_kw))
    h3s = [_as_text(h) for h in (data.get("h3s") or []) if _as_text(h)]
    intro = _strip_instruction_leak(_as_text(data.get("intro")), brief)
    content = _sectioned_body(h2s, intro, data.get("content"), brief=brief)
    content = _strip_instruction_leak(content, brief)
    cta = _strip_instruction_leak(_as_text(data.get("cta")), brief)
    content_text = intro + " " + content

    seo_score = _seo_score(content_text, title, meta, h2s, faqs, primary_kw, city, slug, h1=h1)
    density = _keyword_density(content_text, primary_kw)

    return SEOBlock(
        city=city,
        state=state,
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
    **_kwargs,
) -> SEOBlock:
    brief = (custom_requirements or "").strip()
    if content_kind == "blog":
        topic = article_topic(brief, target_keywords, business_type)
        primary = (primary_keyword or topic).strip()
        slug = _slugify(primary)
        title = pretty_keyword(topic)[:60]
        h1 = pretty_keyword(topic)
        is_redirect = bool(re.search(r"301|302|redirect", primary, re.I))
        if is_redirect:
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
        else:
            intro = (
                f"Looking for a clear answer on {primary.lower()}? "
                f"This guide covers what it is, how to do it, and what to watch for — in plain American English."
            )
            content = (
                f"{h1.rstrip('.')}.\n\n"
                "Start with the goal, then follow the steps in order, then test the result.\n\n"
                "1. Confirm the problem you are solving.\n"
                "2. Apply the change in a staging or test environment when you can.\n"
                "3. Verify on the live site.\n"
                "4. Watch for errors for a few days after.\n\n"
                "If you get stuck, ZeOrbit can walk through the setup with you."
            )
            h2s = [
                f"What {primary} actually means",
                f"How to {primary.lower()} step by step",
                "Common mistakes to avoid",
                "Tools and checks that save time",
                "When to bring in a specialist",
            ]
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
        schema = _build_schema(business_type.title(), city or "United States", state, faqs, article_title=title)
        content = _sectioned_body(h2s, intro, content, brief=brief)
        content = _strip_instruction_leak(content, brief)
        seo_score = _seo_score(intro + " " + content, title, "", h2s, faqs, primary, city or "", slug, h1=h1)
        return SEOBlock(
            city=city, state=state, business_type=business_type.title(), industry=industry,
            slug=slug, title=title, meta_description=f"A practical US-English guide to {primary.lower()}. Clear steps, fewer mistakes, and a next step if you need help.",
            h1=h1, h2s=h2s, h3s=h3s, intro=intro, content=content, faqs=faqs,
            cta="Not sure where to start? ZeOrbit is here to help you turn this into a working plan.",
            keywords=kw, schema_markup=schema, readability_score=seo_score,
            keyword_density=_keyword_density(intro + " " + content, primary),
            content_type="blog",
            focus_keyword=primary.lower(),
        )

    primary = (primary_keyword or pick_primary_keyword(
        target_keywords, business_type, city, keyword_index, industry=industry or "",
    )).strip()
    pretty = pretty_keyword(primary)
    who = _audience_who(industry, audience)
    buyers = _buyer_word(industry)
    loc = f"{city}, {state}".strip(", ") if state else city
    bt = business_type
    slug = _slugify(f"{primary.lower()}-{city}")
    title = _page_meta_title(primary, city, state, keyword_index, industry=industry or "")
    meta = (
        f"ZeOrbit builds WordPress websites for {who} in {loc}. "
        f"Local visibility, trust, and conversions — talk with us about {pretty.lower()}."
    )[:160]
    h1 = f"{pretty} in {loc}" if loc else pretty
    intro = (
        f"{who[:1].upper() + who[1:] if who else 'Businesses'} in {loc} need a website that is easy to use, "
        f"easy to find, and built to turn visitors into {buyers}.\n\n"
        f"ZeOrbit provides {bt.lower()} for {industry or 'local'} businesses. "
        f"We create simple, professional WordPress websites that explain your services clearly and help {buyers} take the next step."
    )
    content = (
        f"We build websites with:\n"
        f"• Custom WordPress website design\n"
        f"• Mobile-friendly layouts\n"
        f"• {(industry or 'Service').title()} service pages\n"
        f"• High-converting landing pages\n"
        f"• Clear appointment and contact options\n"
        f"• Local SEO-friendly content\n"
        f"• Fast, easy-to-use pages\n"
        f"• AI-search-friendly website structure\n\n"
        f"Your website should help people looking for {industry.lower() + ' ' if industry else ''}services in {city} "
        f"understand what you offer and why they should choose you. "
        f"We write localized pages around your services, your {buyers}, and this community — not keyword stuffing.\n\n"
        f"ZeOrbit builds sites with clear headings, useful answers, relevant service information, and strong local signals. "
        f"That helps search engines and AI-powered search understand your {industry or 'business'} and the services you provide.\n\n"
        f"A good site should make it easy to contact you or book. "
        f"We use clear calls to action, simple navigation, trust-building content, and focused landing pages "
        f"to help turn visitors into qualified leads.\n\n"
        f"For {who} in {loc}, the goal is simple: a WordPress site that matches how people search, "
        f"explains {pretty.lower()} clearly, and makes the next step feel natural."
    ).strip()
    layout = layout_variant if layout_variant in LAYOUT_INSTRUCTIONS else pick_layout_variant(city, business_type, content_kind)
    h2s = _page_h2_set(layout, industry, buyers, city, audience, pretty)
    h3s = [
        "Custom WordPress and landing pages",
        "Local SEO-friendly content",
        f"Clear next steps for {buyers}",
        "How to start with ZeOrbit",
    ]
    cta = (
        f"Need {pretty.lower()} in {city}? ZeOrbit can build a professional WordPress website "
        f"designed for local visibility, {buyers[:-1] if buyers.endswith('s') else buyers} trust, and conversions. "
        f"Not sure where to start? We're here to help."
    )
    faqs = [
        FAQItem(
            question=f"Does ZeOrbit build {pretty.lower()} for {who} in {city}?",
            answer=f"Yes. ZeOrbit designs WordPress sites for {who} in {loc}. We focus on local search, clear service pages, and conversion paths — we are not a {industry or 'local'} provider ourselves.",
        ),
        FAQItem(
            question=f"What should a {industry or 'business'} website include?",
            answer=f"Clear services, mobile layout, contact or booking, proof, and local content for {city}. We include landing pages so campaigns have a page that matches the offer.",
        ),
        FAQItem(
            question="Will the site help us get found in search and AI answers?",
            answer="We structure headings, FAQs, and local signals so Google and AI search can understand the business. Rankings still depend on competition and follow-through.",
        ),
        FAQItem(
            question="How long does a WordPress site take?",
            answer="Most small-business WordPress builds land in a few weeks after we have your services, photos, and goals. We share a timeline before we start.",
        ),
        FAQItem(
            question=f"Do you only work with {audience or 'businesses'}?",
            answer=f"This page is written for {who} in {city}. ZeOrbit also builds sites for other US industries — tell us what you need.",
        ),
        FAQItem(
            question="How do we get started?",
            answer=f"Call or email ZeOrbit. We'll review your current site (if you have one), the {city} market, and a simple plan to launch.",
        ),
    ]
    kw = KeywordSet(
        primary=primary.lower(),
        secondary=[k.lower() for k in target_keywords if k.lower() != primary.lower()][:8],
        long_tail=[f"{primary.lower()} {city.lower()}".strip()],
        near_me=[f"{primary.lower()} near me"],
        user_questions=[f.question for f in faqs],
    )
    schema = _build_schema(bt, city, state, faqs)
    content = _sectioned_body(h2s, intro, content, brief=brief)
    content = _strip_instruction_leak(content, brief)
    seo_score = _seo_score(intro + " " + content, title, meta, h2s, faqs, primary, city, slug, h1=h1)
    return SEOBlock(
        city=city, state=state, business_type=bt, industry=industry,
        slug=slug, title=title, meta_description=meta, h1=h1, h2s=h2s, h3s=h3s,
        intro=intro, content=content, faqs=faqs, cta=cta, keywords=kw, schema_markup=schema,
        readability_score=seo_score, keyword_density=_keyword_density(intro + " " + content, primary),
        content_type="service", focus_keyword=primary.lower(),
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
) -> SEOBlock:
    """Assemble a SEOBlock from generated fields (shared by LLM + template paths)."""
    faqs = [FAQItem(question=f["question"], answer=f["answer"]) for f in data.get("faqs", [])]
    slug = _slugify((data.get("slug") or angle_title) + f"-{city}")
    title = data.get("title", angle_title)
    meta = data.get("meta_description", "")
    h2s = data.get("h2s", [])
    body = data.get("content", "")

    if profile and profile.page_inventory:
        body = insert_internal_links(body, profile.page_inventory, max_links=5)

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
        "meta_description": _fill(rng.choice(META_VARIANTS), bt, city, state)[:160],
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

        prompt = f"""You are an expert SEO + AEO (AI answer engine) content writer. Write ONE complete, unique blog article.

Article angle/title: {angle_title}
Search intent: {intent}
Primary/focus keyword: {primary_keyword}
Location: {location}
Secondary keywords: {', '.join(keywords.secondary[:6])}
{biz_ctx}

WRITING RULES (optimize for Google, Google AI Overviews, Bing/Copilot, ChatGPT, Claude):
- Open with a direct, factual 1-2 sentence answer to the article's core question.
- Simple American English, short paragraphs, question-based H2s, bullet points, clear hierarchy.
- Localize naturally to {location}. Use entities and keyword variations; do NOT keyword-stuff.

Return ONLY valid JSON with EXACTLY this structure:
{{
  "title": "Click-focused meta title (50-60 chars, include focus keyword)",
  "meta_description": "Meta description (150-160 chars, include focus keyword + CTA)",
  "slug": "seo-friendly-url-slug",
  "h1": "Article H1 heading",
  "h2s": ["5 question-based H2 subheadings"],
  "h3s": ["3 supporting H3 subheadings"],
  "intro": "Direct-answer intro (2-3 sentences).",
  "content": "5-7 paragraphs of body content (600+ words). Use bullet points and double-newline breaks.",
  "faqs": [{{"question": "...", "answer": "..."}}],
  "cta": "Strong call-to-action (2-3 sentences)"
}}
Provide at least 5 FAQs. Return ONLY valid JSON, no markdown."""
        data = await chat_json(prompt, temperature=0.75, max_tokens=3500, provider=llm_provider)

    if not data or not data.get("content"):
        data = _template_article_fields(primary_keyword, city, state, angle)

    data["_keywords"] = keywords
    return _article_block_from_fields(data, primary_keyword, city, state, profile, industry, angle_title)


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
                        industry=getattr(req, "industry", "") or "",
                        niche=req.primary_keyword or "",
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
    return blocks
