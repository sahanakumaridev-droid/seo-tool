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

    kws = [strip_generic_industry_prefix(str(k).strip()) for k in (target_keywords or []) if str(k).strip()]
    ind = resolve_industry_label(industry, business_type, kws)
    ind_l = ind.lower()

    def _with_industry(kw: str) -> str:
        kw = strip_generic_industry_prefix(kw)
        if not ind or is_generic_industry(ind) or ind_l in (kw or "").lower():
            return kw
        if re.search(r"website|wordpress|web design|landing page", kw, re.I):
            # "WordPress Website Design" → "Healthcare WordPress Website Design"
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
        if brief_l and len(brief_l) > 40 and (
            pl == brief_l or (brief_l in pl and len(pl) < len(brief_l) + 40)
        ):
            continue
        keep.append(p)
    return "\n\n".join(keep)


def _looks_like_search_query(text: str) -> bool:
    t = (text or "").strip()
    if not t:
        return False
    if "?" in t:
        return True
    if re.match(r"^(how|what|why|when|which|who|where|should|is|are|can|do|does|will)\b", t, re.I):
        return True
    return len(t.split()) >= 4


def article_topic(brief: str, target_keywords: list, business_type: str) -> str:
    """Blog topic = the editor's search query / first target keyword.

    For blogs, the keyword IS the subject (e.g. a question or how-to sentence).
    Do not replace it with niche, industry, or a leftover page brief.
    """
    kws = [str(k).strip() for k in (target_keywords or []) if str(k).strip()]
    for k in kws:
        if _looks_like_search_query(k) or not _looks_like_writing_brief(k):
            if "working title" in k.lower():
                continue
            return k
    parsed_topic = extract_brief_topic(brief, kws, business_type)
    if parsed_topic and (_looks_like_search_query(parsed_topic) or not _looks_like_writing_brief(parsed_topic)):
        return parsed_topic
    return kws[0] if kws else (business_type or "guide")


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
    h = (heading or q).strip()
    return (
        f"{h} — this section answers the search for “{q}.” "
        f"Explain the situation in plain language, name the checks or facts the reader needs, "
        f"and finish with one practical next step. Keep it about the query, not a generic agency pitch."
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
            joined = f"{joined} {_section_pad(h, q or h)}"
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
    # Prefer the service portion of "service city" focus keywords for readable sentences
    display_kw = kw
    if city and kw.lower().endswith(city.lower()):
        display_kw = kw[: -len(city)].strip(" ,-") or kw

    boosters = [
        f"Businesses comparing {display_kw}{city_bit} want clear scope, mobile-friendly pages, and a site that turns visits into calls.",
        f"ZeOrbit builds WordPress and Shopify websites for {display_kw}{city_bit} — projects typically run $500–$3,000 depending on pages and features.",
        f"If {display_kw}{city_bit} is your next step, start with goals, budget, and a homepage that answers what you do and how to contact you.",
        f"Local searchers looking for {display_kw}{city_bit} notice fast load times, readable copy, and contact paths above the fold.",
    ]
    if len((kw or "").split()) >= 6 or "?" in (kw or "") or re.search(r"\bhow to\b", kw or "", re.I):
        boosters = [
            f"If you opened this page for “{display_kw}”, use the sections above in order and confirm the result before you add extras.",
            f"Stay on “{display_kw}” — do not switch the topic to an unrelated product or a website rebuild.",
        ]
    new_intro = intro or ""
    if display_kw.lower() not in new_intro.lower():
        new_intro = (
            f"{new_intro} Teams evaluating {display_kw}{city_bit} usually start with pricing, timeline, and what launches first."
        ).strip()

    parts = [content or ""]
    for b in boosters:
        candidate = "\n\n".join(p for p in parts + [b] if p).strip()
        density = _keyword_density(f"{new_intro}\n{candidate}", kw)
        parts.append(b)
        if density >= min_score:
            break
    new_content = "\n\n".join(p for p in parts if p).strip()
    density = _keyword_density(f"{new_intro}\n{new_content}", kw)
    return new_intro, new_content, density

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
- Forbidden fluff: cutting-edge, digital transformation, revolutionary, seamless solutions, unlock your potential, next-generation, comprehensive digital ecosystem.
- Second person ("you") over "businesses seeking world-class partners".
- NEVER paste Custom Content Requirements, writing briefs, or meta-instructions into the article body.
- NEVER leave an H2 empty — every heading needs 2–4 full sentences of real content.
- Vary structure: do not reuse the same five generic H2s on every page. Match the BODY LAYOUT note and SEARCH INTENT.
- Quality bar: content should read like a strong ChatGPT / Claude / Gemini draft — specific, natural, topic-aware.
- Never invent fake reviews, clients, offices, awards, rankings, or "best/cheapest in [city]" claims.
- Use only verified ZeOrbit facts: website projects typically $500–$3,000; 20+ years experience; 1,000+ client reviews; WordPress, Shopify, redesign, mobile-friendly, SEO-friendly structure, conversion-focused sites, mobile apps.
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


def blog_layout_for_query(query: str, brief: str = "") -> str:
    """How-to/fix → steps even if the keyword ends with '?'; other questions → Q&A."""
    t = f"{query or ''} {brief or ''}".lower()
    if re.search(r"\b(how to|how do i|how do you|step-by-step|guide)\b", t):
        return "steps"
    if re.search(r"\b(fix|repair|broken|not working|error)\b", t):
        return "steps"
    if "?" in t or re.search(r"^\s*(what|why|when|which|who|where|should|is|are|can|do|does)\b", t):
        return "qa"
    if re.search(r"\bquestion\b", t):
        return "qa"
    return "story"


def _query_task_phrase(query: str) -> str:
    t = re.sub(r"[?!.]+$", "", (query or "").strip())
    t = re.sub(r"^(how to|how do i|how do you)\s+", "", t, flags=re.I)
    return t.strip() or (query or "this").strip()


def _blog_query_copy(primary: str) -> dict:
    """Fallback blog copy that actually teaches the editor's query — never agency filler."""
    q = (primary or "").strip()
    ql = q.lower()
    pretty = pretty_keyword(q)
    task = _query_task_phrase(q)
    layout = blog_layout_for_query(q)
    is_howto = layout == "steps"
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

    if is_howto:
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

    # Q&A / other topics — still answer the query, not web-design filler
    intro = (
        f"You searched “{q}”. This post answers that in direct language, then explains what to check "
        "and what to skip."
    )
    content = (
        f"## Direct answer: {pretty}\n\n"
        f"The practical answer to “{q}” is to treat the words in that search as the whole job. "
        f"If the query is about {task}, explain {task}, show how to verify it, and do not switch the topic "
        "to an unrelated service.\n\n"
        f"## What “{task}” involves\n\n"
        "Name the tool, browser, or product in the query. Say what the reader should see on screen. "
        "Give one way to confirm they are done. Keep examples inside that topic.\n\n"
        "## What to do next\n\n"
        "1. Restate the question in your own words.\n"
        "2. Do the smallest action that would prove the answer (open the app, load the page, toggle the setting).\n"
        "3. If it fails, change one thing and retry.\n\n"
        "## Common mix-ups\n\n"
        "Swapping in a different product, following an ad instead of the official site, or stopping at a login wall "
        "are the usual reasons this still feels unsolved.\n\n"
        "## When to get help\n\n"
        "If the official page will not load, or you are changing a live website rather than an account setting, "
        "get a specialist. ZeOrbit helps with websites — not with replacing the answer to this query."
    )
    h2s = [
        f"Direct answer: {pretty}",
        f"What “{task}” involves",
        "What to do next",
        "Common mix-ups",
        "When to get help",
    ]
    faqs = [
        FAQItem(question=f"What is {ql}?", answer=f"It is the exact question this article answers: {pretty}."),
        FAQItem(question="Can I do this myself?", answer="Usually yes. Use the checks in this post before paying anyone."),
        FAQItem(question="How long does it take?", answer="A clear answer and one verification pass often take minutes."),
        FAQItem(question="What if I get it wrong?", answer="Undo the last change and retry with the official site or app named in the query."),
        FAQItem(question="Do I need a developer?", answer="Only if the problem is a website, domain, or custom integration — not a normal how-to."),
        FAQItem(question="What's the next step?", answer=f"Finish {task}, confirm it, then stop. Do not add extra tools until that works."),
    ]
    return {"intro": intro, "content": content, "h2s": h2s, "faqs": faqs, "h3s": []}


def pick_layout_variant(city: str, business_type: str, kind: str = "service") -> str:
    seed = f"{kind}|{(business_type or '').lower()}|{(city or '').lower()}"
    h = int(hashlib.md5(seed.encode()).hexdigest(), 16)
    return LAYOUT_VARIANTS[h % len(LAYOUT_VARIANTS)]



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
) -> SEOBlock:
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
    city, state = _one_place(city, state)
    original_niche = normalize_niche_text(business_type or "")
    # Keep ZeOrbit's service (WordPress / web design). Industry is the buyer vertical.
    business_type = resolve_campaign_niche(original_niche, industry or "")
    requested_kind = "blog" if (content_kind or "page") == "post" else "service"
    # Blog section only: always use the query/keyword article path (never location-page engine).
    kind = "blog" if requested_kind == "blog" else "service"
    content_type_out = "blog" if requested_kind == "blog" else "service"
    if kind != "blog" and (city or "").strip():
        from services.location_service import lookup_place_zip
        from services.zeorbit_local_seo import digits_zip
        zip = digits_zip(zip) or await lookup_place_zip(city, state, zip)
        zip = digits_zip(zip)
        if not zip:
            raise RuntimeError(
                f"ZIP is mandatory for location pages. Could not resolve a postal code for {city}, {state}."
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
        keywords=target_keywords or [],
    ) if kind != "blog" else None
    if intent and parsed_brief.get("search_intent"):
        from services.zeorbit_local_seo import SEARCH_INTENTS, detect_intent_from_brief
        forced = detect_intent_from_brief(parsed_brief["search_intent"], [])
        if forced:
            for i in SEARCH_INTENTS:
                if i.id == forced:
                    intent = i
                    break
    primary_kw = (
        article_topic(custom_requirements, target_keywords, business_type)
        if requested_kind == "blog"
        else pick_primary_keyword(
            [
                k for k in (target_keywords or [])
                if k and not _looks_like_writing_brief(str(k))
            ] or [extract_brief_topic(custom_requirements, target_keywords, business_type)],
            business_type, city, keyword_index, industry=industry or "",
        )
    )
    if requested_kind != "blog":
        primary_kw = strip_generic_industry_prefix(primary_kw)
    if kind == "blog":
        layout = blog_layout_for_query(primary_kw, custom_requirements or "")
    else:
        layout = pick_layout_variant(city, f"{primary_kw or business_type}|{(intent.id if intent else '')}", kind)
    concept = image_concept(intent, city, industry, keyword_index) if intent else ""
    gen_kwargs = dict(
        business_type=business_type, city=city, state=state, target_keywords=target_keywords,
        industry=industry, custom_requirements=custom_requirements, content_kind=kind,
        audience=audience, layout_variant=layout, keyword_index=keyword_index,
        primary_keyword=primary_kw,
        search_intent=intent.id if intent else "",
        image_concept_text=concept,
        customer_problem=(parsed_brief.get("customer_problem") or (intent.customer_problem if intent else "")),
        zip=zip or "",
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

    if kind == "blog" and len((block.content or "").split()) < 80:
        print("[SEO] Blog body too thin — using query-shaped template")
        block = await _generate_template_block(**gen_kwargs)

    # Soft uniqueness retry for location pages that are near-duplicates.
    if kind != "blog" and existing_bodies and is_too_similar(
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
        gen_kwargs["layout_variant"] = pick_layout_variant(city, f"{primary_kw}|{alt_intent.id}|alt", kind)
        try:
            if use_ai:
                block = await _generate_ai_block(llm_provider=llm_provider, **gen_kwargs)
            else:
                block = await _generate_template_block(**gen_kwargs)
        except Exception:
            block = await _generate_template_block(**gen_kwargs)
        intent = alt_intent
        concept = gen_kwargs["image_concept_text"]

    from services.slug_utils import article_slug
    slug_kws = [primary_kw] + [k for k in (target_keywords or []) if k and k != primary_kw and not _looks_like_writing_brief(str(k))]
    slug_seed = primary_kw if content_type_out == "blog" else business_type
    block.slug = article_slug(slug_kws, city, slug_seed)
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
    from services.zeorbit_local_seo import apply_zip_faq_only, digits_zip
    apply_zip_faq_only(block, city or "", state or "", digits_zip(zip or getattr(block, "zip", "") or ""))

    # Location pages only — never rewrite blog body around a city.
    if city and content_type_out != "blog":
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

    try:
        from services.image_service import generate_article_images, blog_image_plan
        plan = blog_image_plan(
            (image_keyword or "").strip() or primary_kw or block.focus_keyword or block.title or "",
            niche="",
        )
        img_focus = plan["topic"]
        img_niche = plan["category"]
        img_concept = plan.get("concept") or block.image_concept or (
            f"{industry or primary_kw or 'business'} website on laptop"
        )
        img_industry = industry or ""
        loc_offset = int(hashlib.md5(f"{city}|{state}|{zip}".encode()).hexdigest(), 16) % 997
        images = await generate_article_images(
            img_focus, f"{city}, {state} {zip}".strip(), "ZeOrbit", count=3,
            exclude_urls=exclude_image_urls,
            industry=img_industry,
            niche=img_niche,
            search_intent=block.search_intent or ("guide" if content_type_out == "blog" else "discovery"),
            image_concept_text=img_concept,
            keyword_index=keyword_index + loc_offset,
            content_type=content_type_out,
            match_query=(image_keyword or "").strip() or primary_kw or "",
            audience=audience or "",
            image_keyword=(image_keyword or "").strip(),
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
        print(f"[Image] Set {len(block.in_content_images or [])} image(s) for {img_focus} in {city or 'blog'}")
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
    if city and quality.score < MIN_PUBLISH_SCORE and kind != "blog":
        packed = None
        try:
            from services.zeorbit_local_seo import build_template_page_copy, SEARCH_INTENTS
            intent_obj = intent
            if not intent_obj:
                intent_obj = pick_search_intent(city, keyword_index, industry=industry)
            packed = build_template_page_copy(
                intent_obj, city, state or "", industry or "", pretty_keyword(primary_kw), keyword_index,
                zip=zip or "",
            )
            # Prefer AI intro if it already names the city; otherwise use template intro/content.
            body_l = f"{block.intro}\n{block.content}".lower()
            if city.lower() not in body_l or len((block.content or "").split()) < 220:
                block.intro = packed["intro"]
                block.content = packed["content"]
                if packed.get("faqs") and len(block.faqs or []) < 4:
                    from models.schemas import FAQItem
                    block.faqs = [FAQItem(question=f["question"], answer=f["answer"]) for f in packed["faqs"]]
                if packed.get("title"):
                    block.title = packed["title"]
                    block.h1 = packed.get("h1") or packed["title"]
                if packed.get("meta_description"):
                    block.meta_description = packed["meta_description"]
                if packed.get("cta"):
                    block.cta = packed["cta"]
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
        kw_use = _keyword_density(f"{block.intro or ''}\n{block.content or ''}", focus_for_density)
        block.keyword_density = kw_use
    else:
        block.intro, block.content, kw_use = ensure_keyword_coverage(
            block.intro or "",
            block.content or "",
            focus_for_density,
            city=city or "",
            min_score=MIN_KEYWORD_USE_SCORE,
        )
        block.keyword_density = kw_use
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
    block.publishable = bool(
        quality.publishable
        and scores_meet_floor(quality.score, kw_use)
    ) if city else True
    # UI Score column uses readability_score — keep it aligned with the master quality gate.
    block.readability_score = quality.score
    # Always store readable markdown (## on own lines, short paragraphs).
    block.content = ensure_body_hyperlinks(
        normalize_markdown_sections(block.content or "", list(block.h2s or []))
    )
    block.intro = (block.intro or "").strip()
    if not block.publishable and city:
        print(
            f"[Quality] {city} quality={quality.score} keyword_use={kw_use} "
            f"reasons={quality.reasons}"
        )

    return _scrub_block_dashes(block)


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
    max_attempts: int = 6,
    **kwargs,
) -> tuple["SEOBlock", int]:
    """Keep regenerating a location until Quality and Keyword use both hit 90+.

    Returns (block, extra_attempts) where extra_attempts is how many times we
    had to generate again after the first pass scored below the floor.
    """
    from services.zeorbit_local_seo import scores_meet_floor

    keyword_index = int(kwargs.get("keyword_index") or 0)
    existing_bodies = kwargs.get("existing_bodies")
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


def boost_block_to_floor(block: "SEOBlock") -> "SEOBlock":
    """Client AI-fix: raise keyword use (and refresh quality) to the 90% floor."""
    from services.zeorbit_local_seo import (
        score_page_quality,
        MIN_KEYWORD_USE_SCORE,
        scores_meet_floor,
        ensure_body_hyperlinks,
    )
    kw = (
        (getattr(block, "focus_keyword", None) or "")
        or (block.keywords.primary if getattr(block, "keywords", None) else "")
        or ""
    ).strip()
    intro, content, kw_use = ensure_keyword_coverage(
        block.intro or "",
        block.content or "",
        kw,
        city=block.city or "",
        min_score=MIN_KEYWORD_USE_SCORE,
    )
    block.intro = intro
    block.content = ensure_body_hyperlinks(
        normalize_markdown_sections(content, list(getattr(block, "h2s", None) or []))
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
    search_intent: str = "",
    image_concept_text: str = "",
    customer_problem: str = "",
    zip: str = "",
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
        target_keywords, business_type, city, keyword_index, industry=industry or "",
    )).strip()
    layout = layout_variant if layout_variant in LAYOUT_INSTRUCTIONS else (
        blog_layout_for_query(primary_kw, brief) if content_kind == "blog"
        else pick_layout_variant(city, business_type, content_kind)
    )
    layout_note = LAYOUT_INSTRUCTIONS[layout]
    provider_key = (llm_provider or "").lower().strip()
    provider_note = PROVIDER_STYLE_NOTES.get(provider_key, "Write at the quality level of ChatGPT, Claude, or Gemini — specific and human.")

    if content_kind == "blog":
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
        prompt = f"""You are a US content writer creating ONE blog post for ZeOrbit.com.
Model style: {provider_note}

═══ BLOG QUERY RULE (blog section only — mandatory) ═══
The editor's search query / keyword is the ONLY subject of this article:
SEARCH QUERY: "{topic}"

- Title, H1, intro, every H2, body paragraphs, and FAQs MUST directly answer or teach that query.
- If the query is "how to fix a website", write a practical fix guide (diagnose → fix → verify) — not generic web design sales copy.
- If the query is a full sentence or question, that sentence IS the article. Answer it in the intro, every H2, the body, and the FAQs. Do not change the topic to web design, ZeOrbit services, or a city landing page unless the sentence itself is about that.
- If the query is a problem ("broken website", "site not loading"), diagnose and solve that problem.
- Niche / industry may color EXAMPLES only — they must NOT replace the query as the topic.
- Do NOT write a location landing page, city SEO page, or "web design in San Diego" article unless the query itself is that.

Custom notes from the editor (guidance only — NEVER paste into the published body):
{extra_brief or "None — stay on the search query above."}

Business context (mention ZeOrbit only where help is natural, usually near the end/CTA): ZeOrbit builds websites, apps, and SEO for US companies.
Industry field (examples only — ZeOrbit is NOT a {industry or "clinic"}): {industry or "n/a"}
{audience_line}
Secondary keywords to weave lightly (do not hijack the topic): {", ".join(secondary) if secondary else "none"}
BODY LAYOUT ({layout}): {layout_note}
{loc_note}

{VOICE_RULES}
{master_voice_rules()}

NON-NEGOTIABLE:
- The article must feel written for someone who typed "{topic}" into Google.
- Title and H1 must name the query (how-to / question / problem wording is fine).
- H2s must be steps or sub-questions of "{topic}", not generic agency sections.
- content MUST use markdown H2 lines that exactly match each string in h2s, with 1–2 short paragraphs under EVERY H2 (40–70 words each).
- Include concrete steps, checks, or examples that match the query (tools, settings, files, or UI when technical).
- Do NOT paste Custom Content Requirements into intro, content, faqs, or cta.
- Soft CTA only after the reader has a usable answer.

Generate a JSON response with EXACTLY this structure:
{{
  "title": "SEO title 50-60 chars that names the search query",
  "meta_description": "150-160 chars promising an answer to: {topic}",
  "h1": "Clear H1 that matches the search query (question or how-to is fine)",
  "h2s": ["3 DISTINCT H2s that break down the search query — steps or sub-questions, not generic filler"],
  "h3s": ["4 short supporting labels (not empty body sections)"],
  "intro": "2-3 sentences. Open on the reader's situation for this query, then say what the post will teach.",
  "content": "Markdown: for EACH h2 write '## Exact H2' then 1-2 short paragraphs answering that part of the query. 320-480 words total. Numbered/bulleted steps when teaching. Separate paragraphs with double newlines.",
  "faqs": [
    {{"question": "Practical FAQ 1 about the search query", "answer": "2-3 sentence answer"}},
    {{"question": "FAQ 2 about the search query", "answer": "2-3 sentence answer"}},
    {{"question": "FAQ 3 about the search query", "answer": "2-3 sentence answer"}}
  ],
  "cta": "Soft American CTA: invite help applying this answer — not a hard sell."
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
        )
        pretty = pretty_keyword(primary_kw)
        intent = pick_search_intent(city, keyword_index, industry=industry or "", brief=custom_requirements or "", keywords=target_keywords or [])
        if search_intent:
            for i in SEARCH_INTENTS:
                if i.id == search_intent:
                    intent = i
                    break
        title_locked = title_from_primary_keyword(primary_kw, city, industry or "", intent, keyword_index)
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
        prompt = f"""You are writing ONE ZeOrbit service / location PAGE for AI search visibility (Google, AI Overviews, ChatGPT Search, Gemini, Bing/Copilot).
Model style: {provider_note}

WHO WE ARE: ZeOrbit is a technology company that provides website design and development. We are NOT a {industry or "healthcare"} provider.

WHAT THIS PAGE SELLS: {business_type}
WHO IT IS FOR: {who}
WHERE: {place or "the United States"} — this is the ONLY place named on the page.
Include the 5-digit ZIP {re.sub(r'\D', '', zip or '')[:5] or '(resolve before write)'} only in the last FAQ answer as markdown [{re.sub(r'\D', '', zip or '')[:5] or 'ZIP'}](https://www.google.com/maps/search/?api=1&query={re.sub(r'\D', '', zip or '')[:5] or 'ZIP'}). Never put the ZIP in title, H1, intro, body, conclusion, meta, or CTA.
PRIMARY KEYWORD (weave naturally in title/H1/intro): {pretty}
Other keywords to use naturally (do not dump as a list): {kw_line}

{master_brief}

CUSTOM CONTENT REQUIREMENTS — WRITING BRIEF ONLY (follow; NEVER paste into intro/content/cta/faqs):
{brief_block}

{audience_line}
BODY LAYOUT ({layout}): {layout_note}
{VOICE_RULES}
{master_voice_rules()}

NON-NEGOTIABLE:
- ZeOrbit is the vendor. {industry or "The industry"} is the CLIENT type, not ZeOrbit's own business.
- Write useful depth: who ZeOrbit helps + what ZeOrbit does + where relevant + problems solved + pricing context + technologies + business types + why it may fit.
- Mention pricing naturally: website projects typically range from {ZEORBIT_FACTS['pricing_range']}.
- Mention experience/reviews only as verified: {ZEORBIT_FACTS['experience']}, {ZEORBIT_FACTS['reviews']} — never invent individual reviews or star ratings.
- Cover platforms as relevant to THIS intent: WordPress, Shopify, redesign, mobile-friendly, SEO-friendly structure, conversions, mobile apps.
- Keep copy simple, credible, localized to {city} only, UNIQUE to this intent + industry + layout. Do NOT city-swap a generic article.
- KEYWORD LOCK: Stay on “{pretty}” for {who}. Do not mention unrelated industries (gym, restaurant, salon, roofing, etc.) unless those words are in the PRIMARY KEYWORD.
- HYPERLINKS: Internal ZeOrbit links among https://zeorbit.com/website-designing https://zeorbit.com/mobile-apps https://zeorbit.com/seo-ppc https://zeorbit.com/contact. For third-party citations ChatGPT/Gemini use in top lists, highlight in-body words (do not dump directory names as the visible text): first “website design” or “website” → https://www.designrush.com/agency/profile/zeorbit ; first “mobile app” → https://www.goodfirms.co/company/zeorbit. Markdown [website](url) / [mobile app](url). Also mention DesignRush, GoodFirms, and Yelp in plain text (no extra URLs). Do not add random unrelated third-party URLs.
- ZIP: 5-digit {re.sub(r'\D', '', zip or '')[:5] or 'ZIP'} only in the last FAQ answer, hyperlinked as [{re.sub(r'\D', '', zip or '')[:5] or 'ZIP'}](https://www.google.com/maps/search/?api=1&query={re.sub(r'\D', '', zip or '')[:5] or 'ZIP'}). Never in intro, body, conclusion, title, or meta.
- Do NOT list competitors, fake addresses, or other neighborhoods.
- Name ZeOrbit in the intro and the CTA.
- content MUST include '## Exact H2' for each h2s item with 1–2 short paragraphs under each (no empty headings). 320–480 words.
- NEVER copy the CUSTOM CONTENT REQUIREMENTS paragraph(s) into the published fields.

Generate a JSON response with EXACTLY this structure:
{{
  "title": "{title_locked}",
  "meta_description": "150-160 chars: helpful promise for {who} in {city} + ZeOrbit website help (no keyword stuffing)",
  "h1": "{title_locked}",
  "h2s": {h2_json},
  "h3s": ["WordPress and Shopify options", "Mobile-friendly and SEO-friendly structure", "Practical pricing and experience", "A clear next step"],
  "intro": "2-4 sentences. Customer problem in {city}. What depends on the business need. ZeOrbit as the provider. No fluff.",
  "content": "Markdown sections matching h2s. Each section 1-2 short paragraphs. Include pricing {ZEORBIT_FACTS['pricing_range']} where natural. Stay on website design for {who} in {city} for intent {intent.id}. 320-480 words.",
  "faqs": [
    {{"question": "Intent-specific FAQ 1 for {city}", "answer": "2-3 factual sentences"}},
    {{"question": "FAQ 2", "answer": "2-3 sentences"}},
    {{"question": "FAQ 3", "answer": "2-3 sentences"}},
    {{"question": "FAQ 4", "answer": "2-3 sentences"}},
    {{"question": "FAQ 5", "answer": "2-3 sentences"}},
    {{"question": "FAQ 6", "answer": "2-3 sentences"}}
  ],
  "cta": "Natural CTA for this intent — invite a conversation, not a hard sell. Name ZeOrbit."
}}

FAQ questions to address (vary answers; do not clone other cities):
{faq_questions}

Customer problem to keep central: {customer_problem or intent.customer_problem}

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

    # Pages: lock SEO title + H1 to intent-varied pattern (do not trust LLM drift).
    if content_kind == "blog":
        title = _as_text(data.get("title")) or pretty_keyword(primary_kw)[:60]
        h1 = _as_text(data.get("h1")) or pretty_keyword(primary_kw)
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
        title = title_from_primary_keyword(primary_kw, city, industry or "", intent_obj, keyword_index)
        h1 = _as_text(data.get("h1")) or title
        if pretty_keyword(primary_kw).lower() not in (h1 or "").lower() and city and city.lower() not in (h1 or "").lower():
            h1 = title
        search_intent_id = intent_obj.id
        customer_problem_out = customer_problem or intent_obj.customer_problem
        image_concept_out = image_concept_text or ""
    meta = _strip_instruction_leak(_as_text(data.get("meta_description")), brief)
    h2s = [_as_text(h) for h in (data.get("h2s") or []) if _as_text(h)]
    if content_kind == "blog" and len(h2s) < 3:
        pretty_h = pretty_keyword(primary_kw)
        h2s = [
            f"Direct answer: {pretty_h}",
            f"What “{primary_kw}” is really asking",
            "How to act on this answer",
            "Mistakes to avoid",
        ]
    if content_kind != "blog" and len(h2s) < 3:
        from services.zeorbit_local_seo import pick_search_intent, SEARCH_INTENTS, intent_h2_set
        intent_obj = pick_search_intent(city, keyword_index, industry=industry or "", brief=brief, keywords=target_keywords or [])
        if search_intent:
            for i in SEARCH_INTENTS:
                if i.id == search_intent:
                    intent_obj = i
                    break
        h2s = intent_h2_set(intent_obj, city, industry or "", layout)
    h3s = [_as_text(h) for h in (data.get("h3s") or []) if _as_text(h)]
    intro = _strip_instruction_leak(_as_text(data.get("intro")), brief)
    content = _sectioned_body(h2s, intro, data.get("content"), brief=brief, query=primary_kw)
    content = _strip_instruction_leak(content, brief)
    md_h2s = [h.strip() for h in re.findall(r"(?m)^##\s+(.+)$", content or "") if h.strip()]
    if content_kind == "blog" and md_h2s:
        h2s = md_h2s
    cta = _strip_instruction_leak(_as_text(data.get("cta")), brief)
    content_text = intro + " " + content

    seo_score = _seo_score(content_text, title, meta, h2s, faqs, primary_kw, city, slug, h1=h1)
    density = _keyword_density(content_text, primary_kw)

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
    if content_kind == "blog":
        topic = article_topic(brief, target_keywords, business_type)
        primary = (primary_keyword or topic).strip()
        slug = _slugify(primary)
        title = pretty_keyword(topic)[:60]
        h1 = pretty_keyword(topic)
        packed_blog = _blog_query_copy(primary)
        is_redirect = bool(re.search(r"301|302|redirect", primary, re.I))
        q = primary.lower().strip()
        pretty = pretty_keyword(primary)
        is_howto = bool(re.search(r"^(how to|how do i)\b", q, re.I)) or "how to" in q
        is_fix = bool(re.search(r"\b(fix|repair|broken|not working|error)\b", q, re.I))
        is_q = (not is_howto) and (not is_fix) and (
            blog_layout_for_query(primary, brief) == "qa" or "?" in primary
        )
        if packed_blog and not is_redirect:
            intro = packed_blog["intro"]
            content = packed_blog["content"]
            h2s = packed_blog["h2s"]
            h3s = packed_blog.get("h3s") or []
            faqs = packed_blog["faqs"]
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
                "map the fix. Website projects typically range from $500–$3,000 depending on scope."
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
                "ZeOrbit can diagnose and apply a safe fix with you. Website projects for small businesses typically start "
                "around $500–$3,000 depending on scope — a repair consult is often smaller than a full redesign."
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
        schema = _build_schema(business_type.title(), city or "United States", state, faqs, article_title=title)
        content = _sectioned_body(h2s, intro, content, brief=brief, query=primary)
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
    from services.zeorbit_local_seo import (
        pick_search_intent,
        SEARCH_INTENTS,
        build_template_page_copy,
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
    schema = _build_schema(bt, city, state, faqs)
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
    # Seed from already-published pages so new blogs don't reuse live featured photos
    try:
        from db import AsyncSessionLocal, PageRecord
        from sqlalchemy import select
        from services.image_service import collect_image_urls_from_seo_block
        async with AsyncSessionLocal() as session:
            rows = (await session.execute(select(PageRecord))).scalars().all()
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
    return blocks
