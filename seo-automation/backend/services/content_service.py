import hashlib
import random
import re
from typing import List, Dict, Any
from models.schemas import SEOBlock, FAQItem, KeywordSet
from services.keyword_service import generate_keywords

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

def _seo_score(
    text: str, title: str, meta: str, h2s: list, faqs: list,
    keyword: str, city: str, slug: str
) -> float:
    """
    Composite SEO score 0-100 based on real ranking factors:
    - Keyword in title (15pts)
    - Keyword in meta description (10pts)
    - Keyword in slug (10pts)
    - Keyword in first 100 words / intro (15pts)
    - Keyword in at least 2 H2s (10pts)
    - Content length >= 300 words (10pts)
    - Has FAQs >= 5 (10pts)
    - Location in title (10pts)
    - Has H2s >= 4 (5pts)
    - Meta length 120-160 chars (5pts)
    """
    score = 0
    kw = keyword.lower()
    city_l = city.lower()
    title_l = title.lower()
    meta_l = meta.lower()
    slug_l = slug.lower()
    words = text.lower().split()
    first_100 = " ".join(words[:100])

    if kw in title_l:                                    score += 15
    if kw in meta_l:                                     score += 10
    if kw.replace(" ", "-") in slug_l or kw.replace(" ", "") in slug_l: score += 10
    if kw in first_100:                                  score += 15
    if sum(1 for h in h2s if kw in h.lower()) >= 2:     score += 10
    if len(words) >= 300:                                score += 10
    if len(faqs) >= 5:                                   score += 10
    if city_l in title_l:                                score += 10
    if len(h2s) >= 4:                                    score += 5
    if 120 <= len(meta) <= 165:                          score += 5

    return float(min(score, 100))

def _keyword_density(text: str, keyword: str) -> float:
    """Returns keyword density as a percentage (0-100 scale for display)."""
    words = text.lower().split()
    kw_words = keyword.lower().split()
    count = sum(1 for i in range(len(words) - len(kw_words) + 1)
                if words[i:i+len(kw_words)] == kw_words)
    raw = (count / max(len(words), 1)) * 100  # e.g. 1.5%
    # Ideal keyword density is 1-3%. Map 2% → 100, cap at 100.
    return round(min((raw / 2.0) * 100, 100), 1)

def _build_schema(bt: str, city: str, state: str, faqs: list) -> Dict[str, Any]:
    slug = _slugify(f"{bt}-{city}")
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
    local_schema = {
        "@context": "https://schema.org",
        "@type": "LocalBusiness",
        "name": f"{bt.title()} Services {city}",
        "description": f"Best {bt.lower()} services in {city}, {state}. Affordable, proven results for local businesses.",
        "url": f"https://example.com/{slug}",
        "telephone": "+1-800-555-0000",
        "priceRange": "$$",
        "address": {
            "@type": "PostalAddress",
            "addressLocality": city,
            "addressRegion": state,
            "addressCountry": "US"
        },
        "areaServed": {"@type": "City", "name": city, "addressRegion": state},
        "serviceType": bt.title(),
        "aggregateRating": {
            "@type": "AggregateRating",
            "ratingValue": "4.9",
            "reviewCount": "127",
            "bestRating": "5"
        },
    }
    return {"local_business": local_schema, "faq_page": faq_schema}


async def generate_seo_block(
    business_type: str,
    city: str,
    state: str,
    target_keywords: list = [],
    industry: str = ""
) -> SEOBlock:
    rng = _seed_random(city, business_type)
    bt = business_type.title()
    bt_lower = business_type.lower()

    keywords = await generate_keywords(business_type, city, state)

    if target_keywords:
        localised = [kw.replace("san diego", city.lower()).replace("San Diego", city) for kw in target_keywords]
        keywords.secondary = localised + [k for k in keywords.secondary if k not in localised]
        for kw in localised:
            if kw not in keywords.long_tail:
                keywords.long_tail.insert(0, kw)

    slug = _slugify(f"{bt_lower}-{city}")
    title = _fill(rng.choice(TITLE_VARIANTS), bt, city, state)
    meta = _fill(rng.choice(META_VARIANTS), bt, city, state)
    h1 = _fill(rng.choice(H1_VARIANTS), bt, city, state)
    h2s = [_fill(h, bt, city, state) for h in rng.sample(H2_POOL, 5)]
    h3s = [_fill(h, bt, city, state) for h in rng.sample(H3_POOL, 4)]
    intro = _fill(rng.choice(INTRO_VARIANTS), bt, city, state)

    body_sections = [_fill(s, bt, city, state) for s in rng.sample(BODY_SECTION_VARIANTS, 2)]

    if target_keywords:
        localised = [kw.replace("san diego", city.lower()).replace("San Diego", city) for kw in target_keywords]
        kw_sentences = []
        for kw in localised[:3]:
            kw_sentences.append(
                f"Whether you're searching for \"{kw}\" or need a trusted local expert, "
                f"our {bt_lower} team in {city} is ready to help."
            )
        if kw_sentences:
            body_sections.append(" ".join(kw_sentences))

    content = "\n\n".join(body_sections)
    cta = _fill(rng.choice(CTA_VARIANTS), bt, city, state)

    faq_pool = rng.sample(FAQ_POOLS, min(7, len(FAQ_POOLS)))
    faqs = [
        FAQItem(
            question=_fill(q, bt, city, state),
            answer=_fill(a, bt, city, state)
        )
        for q, a in faq_pool
    ]

    schema = _build_schema(bt, city, state, faqs)
    seo_score = _seo_score(intro + " " + content, title, meta, h2s, faqs, keywords.primary, city, slug)
    density = _keyword_density(intro + " " + content, keywords.primary)

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
    )
