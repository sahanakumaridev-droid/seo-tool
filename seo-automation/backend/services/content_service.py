import hashlib
import random
from typing import List, Dict, Any
from models.schemas import SEOBlock, FAQItem, KeywordSet
from services.keyword_service import generate_keywords

# ---------------------------------------------------------------------------
# TITLE variants — keyword-rich, conversion-focused, location-specific
# ---------------------------------------------------------------------------
TITLE_VARIANTS = [
    "#1 {BT} Services in {city}, {state} | Licensed & Insured Experts",
    "Best {BT} Company in {city}, {state} — Free Estimates, Same-Day Service",
    "Top-Rated {BT} Services in {city} | Trusted by 500+ Local Homeowners",
    "Expert {BT} in {city}, {state} | Affordable Rates · 24/7 Emergency Service",
    "Professional {BT} Services {city}, {state} | Licensed · Bonded · Insured",
]

META_VARIANTS = [
    "Need a trusted {bt} in {city}, {state}? Our licensed team offers same-day service, upfront pricing, and a 100% satisfaction guarantee. Call now for a FREE estimate!",
    "Looking for the best {bt} company in {city}? We're locally owned, fully insured, and available 24/7. Serving {city} homeowners and businesses since 2010. Get a free quote today.",
    "Affordable {bt} services in {city}, {state}. Licensed professionals, no hidden fees, and emergency response within 60 minutes. Rated 5 stars by {city} residents. Call us now.",
    "{city}'s most trusted {bt} company. We handle residential and commercial jobs of all sizes. Transparent pricing, certified technicians, and guaranteed workmanship. Free estimates available.",
]

# ---------------------------------------------------------------------------
# H1 variants — strong, benefit-driven, geo-targeted
# ---------------------------------------------------------------------------
H1_VARIANTS = [
    "Trusted {BT} Services in {city}, {state} — Licensed, Insured & Ready Today",
    "Expert {BT} Company Serving {city}, {state} | Same-Day Service Available",
    "{city}'s #1 {BT} Professionals — Affordable, Reliable & Locally Owned",
    "Professional {BT} Services in {city} | 5-Star Rated · Free Estimates",
    "Your Local {BT} Experts in {city}, {state} — Available 24/7",
]

# ---------------------------------------------------------------------------
# H2 pools — conversion-focused section headings (pick 4 per page)
# ---------------------------------------------------------------------------
H2_POOL = [
    "Why {city} Homeowners Choose Us for {BT} — Every Time",
    "Complete {BT} Solutions for {city} Residents & Businesses",
    "What Sets Our {BT} Team Apart in {city}, {state}",
    "Our {BT} Services in {city} — Everything You Need Under One Roof",
    "Serving Every Neighborhood in {city} with 5-Star {BT} Service",
    "How Much Does {BT} Cost in {city}? Honest, Upfront Pricing",
    "Emergency {BT} in {city}? We're On-Site in 60 Minutes or Less",
    "Residential & Commercial {BT} Services Across {city}, {state}",
    "Don't Risk It — Hire a Licensed {BT} Professional in {city}",
    "Get Your Free {BT} Estimate in {city} — No Obligation, No Surprises",
]

# ---------------------------------------------------------------------------
# H3 pools — supporting detail headings (pick 4 per page)
# ---------------------------------------------------------------------------
H3_POOL = [
    "Licensed, Bonded & Insured {BT} Technicians",
    "Same-Day & Emergency {BT} Appointments in {city}",
    "Transparent Pricing — No Hidden Fees, Ever",
    "5-Star Reviews from {city} Homeowners",
    "Residential {BT} Services for {city} Homes",
    "Commercial {BT} Solutions for {city} Businesses",
    "Financing Options Available for {city} Customers",
    "Satisfaction Guaranteed on Every {BT} Job",
    "Background-Checked, Drug-Tested {BT} Professionals",
    "Serving {city} and All Surrounding {state} Communities",
]

# ---------------------------------------------------------------------------
# Body content — 3 full paragraphs per variant, geo + keyword rich
# ---------------------------------------------------------------------------
BODY_VARIANTS = [
    """\
When {city} homeowners and business owners need reliable {bt} services, they call us first. \
We've built our reputation across {city}, {state} by showing up on time, communicating clearly, \
and delivering work that lasts. Every technician on our team is fully licensed, background-checked, \
and trained to handle jobs of any size — from routine maintenance to complex emergency repairs.

We understand that {bt} problems don't wait for a convenient time. That's why we offer same-day \
appointments and 24/7 emergency response throughout {city} and the surrounding areas. \
When you call us, a real person answers — not a voicemail. We'll dispatch a certified {bt} \
professional to your {city} location fast, with all the tools and parts needed to get the job done right.

Our pricing is always upfront and transparent. Before any work begins, we provide a detailed written \
estimate so {city} customers know exactly what to expect. No surprise charges, no upselling — \
just honest {bt} service at a fair price. That's why we've earned hundreds of 5-star reviews \
from homeowners and businesses across {city}, {state}.""",

    """\
Finding a trustworthy {bt} company in {city} shouldn't be stressful. At our company, we've made \
it simple: one call connects you with a licensed {bt} expert who knows {city}'s infrastructure, \
local building codes, and the specific challenges that come with properties in this area. \
Whether you own a home in a historic {city} neighborhood or manage a commercial property downtown, \
we have the experience and equipment to handle it.

Our {bt} team in {city} is equipped with the latest diagnostic tools and industry-certified \
techniques. We don't just fix the symptom — we identify the root cause and provide a lasting \
solution. Every job we complete in {city} is backed by our workmanship warranty, so you can \
have complete confidence in the quality of our work.

We're proud to be a locally owned {bt} company serving {city}, {state}. That means we're \
invested in this community — we live here, our kids go to school here, and we care deeply \
about the reputation we've built. When you hire us, you're not calling a national chain. \
You're working with neighbors who treat your {city} property like their own.""",

    """\
{city} residents deserve {bt} service that's fast, professional, and priced fairly. \
Our team has been delivering exactly that across {city} and {state} for years. \
We handle everything from small repairs to full-scale installations, and we bring the \
same level of care and precision to every single job — no matter the size.

What makes us the go-to {bt} company in {city}? It starts with our people. Every technician \
is thoroughly vetted, continuously trained, and held to the highest professional standards. \
We invest in ongoing education so our {city} team stays current with the latest {bt} \
technologies, safety protocols, and code requirements specific to {state}.

We also believe in making {bt} services accessible to every {city} homeowner. That's why \
we offer flexible scheduling — including evenings and weekends — and financing options for \
larger projects. Getting quality {bt} work done in {city} shouldn't mean breaking the bank. \
Call us today and discover why thousands of {city} customers trust us year after year.""",
]

# ---------------------------------------------------------------------------
# FAQ pools — real questions US homeowners search for
# ---------------------------------------------------------------------------
FAQ_POOLS = [
    (
        "How fast can you get a {bt} technician to my {city} home?",
        "For standard appointments in {city}, we typically arrive within 2–4 hours of your call. "
        "For emergency {bt} situations, we guarantee on-site response within 60 minutes throughout {city} and {state}."
    ),
    (
        "Are your {bt} technicians licensed and insured in {state}?",
        "Yes. Every {bt} professional we send to your {city} property is fully licensed in {state}, "
        "bonded, and carries comprehensive liability insurance. We never use unlicensed subcontractors."
    ),
    (
        "Do you provide free estimates for {bt} work in {city}?",
        "Absolutely. We offer free, no-obligation written estimates for all {bt} projects in {city}. "
        "Our technician will assess the job, explain the scope of work, and give you an exact price before anything starts."
    ),
    (
        "What {bt} services do you offer in {city}, {state}?",
        "We provide a full range of {bt} services in {city} including residential repairs, commercial installations, "
        "emergency response, preventive maintenance, inspections, and complete system replacements. "
        "If it involves {bt} in {city}, we handle it."
    ),
    (
        "How much does {bt} service typically cost in {city}?",
        "Costs vary based on the scope of work, but our {city} pricing is always competitive and transparent. "
        "Minor repairs typically start at $150–$300, while larger projects are quoted individually. "
        "We never charge hidden fees and always provide a written estimate upfront."
    ),
    (
        "Do you guarantee your {bt} work in {city}?",
        "Yes. All {bt} work we perform in {city} is backed by our workmanship guarantee. "
        "If anything we've done fails within the warranty period, we return and fix it at no additional cost to you."
    ),
    (
        "Can you handle commercial {bt} projects in {city}?",
        "Absolutely. We serve both residential homeowners and commercial clients throughout {city}, {state}. "
        "Our commercial {bt} team is experienced with office buildings, retail spaces, restaurants, "
        "multi-family properties, and industrial facilities in the {city} area."
    ),
    (
        "What should I do before the {bt} technician arrives at my {city} home?",
        "Clear access to the area where work is needed and note any symptoms or issues you've observed. "
        "If it's an emergency {bt} situation in {city}, shut off the main supply if safe to do so "
        "and call us immediately — we'll walk you through next steps on the phone."
    ),
    (
        "Do you offer financing for large {bt} projects in {city}?",
        "Yes. We understand that major {bt} work can be a significant investment for {city} homeowners. "
        "We offer flexible financing options with approved credit, so you can get the work done now "
        "and pay over time. Ask our {city} team for details when you call."
    ),
    (
        "Are you available for {bt} emergencies on weekends and holidays in {city}?",
        "Yes — we provide 24/7 emergency {bt} service in {city}, including weekends, evenings, "
        "and all major holidays. {bt} emergencies don't follow a schedule, and neither do we."
    ),
]

# ---------------------------------------------------------------------------
# CTA variants — urgency + local trust signals
# ---------------------------------------------------------------------------
CTA_VARIANTS = [
    "Don't wait — {bt} problems in {city} get worse and more expensive over time. "
    "Call our {city} team now for a FREE estimate and same-day service. "
    "We're available 24/7 and ready to dispatch a licensed {bt} professional to your door.",

    "Ready to work with {city}'s most trusted {bt} company? "
    "Contact us today for a no-obligation estimate. Our {city} team is standing by — "
    "we offer same-day appointments, transparent pricing, and a 100% satisfaction guarantee.",

    "Join thousands of satisfied {city} homeowners who trust us for all their {bt} needs. "
    "Call now or book online for a FREE {bt} estimate in {city}, {state}. "
    "Same-day availability. Licensed professionals. Guaranteed results.",

    "Your search for a reliable {bt} company in {city} ends here. "
    "Call us today — we'll send a licensed, insured {bt} expert to your {city} property fast. "
    "Free estimates. Upfront pricing. No surprises.",
]


def _seed_random(city: str, business_type: str) -> random.Random:
    seed = int(hashlib.md5(f"{city}{business_type}".encode()).hexdigest(), 16) % (2**32)
    return random.Random(seed)

def _fill(template: str, bt: str, city: str, state: str) -> str:
    return template.format(bt=bt.lower(), BT=bt.title(), city=city, state=state)

def _readability_score(text: str) -> float:
    sentences = max(text.count('.') + text.count('!') + text.count('?'), 1)
    words = len(text.split())
    syllables = sum(max(1, len([c for c in w if c in 'aeiouAEIOU'])) for w in text.split())
    score = 206.835 - 1.015 * (words / sentences) - 84.6 * (syllables / words)
    return round(min(max(score, 0), 100), 1)

def _keyword_density(text: str, keyword: str) -> float:
    words = text.lower().split()
    kw_words = keyword.lower().split()
    count = sum(1 for i in range(len(words) - len(kw_words) + 1)
                if words[i:i+len(kw_words)] == kw_words)
    return round((count / max(len(words), 1)) * 100, 2)

def _build_schema(bt: str, city: str, state: str) -> Dict[str, Any]:
    slug = f"{bt.lower().replace(' ', '-')}-{city.lower().replace(' ', '-')}"
    return {
        "@context": "https://schema.org",
        "@type": "LocalBusiness",
        "name": f"{bt.title()} Services {city}",
        "description": f"Licensed and insured {bt.lower()} services in {city}, {state}. Same-day service, free estimates, 5-star rated.",
        "url": f"https://example.com/{slug}",
        "telephone": "+1-800-555-0000",
        "priceRange": "$$",
        "address": {
            "@type": "PostalAddress",
            "addressLocality": city,
            "addressRegion": state,
            "addressCountry": "US"
        },
        "areaServed": {
            "@type": "City",
            "name": city,
            "addressRegion": state,
            "addressCountry": "US"
        },
        "serviceType": bt.title(),
        "aggregateRating": {
            "@type": "AggregateRating",
            "ratingValue": "4.9",
            "reviewCount": "127",
            "bestRating": "5"
        },
        "openingHoursSpecification": {
            "@type": "OpeningHoursSpecification",
            "dayOfWeek": ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"],
            "opens": "00:00",
            "closes": "23:59"
        },
        "hasOfferCatalog": {
            "@type": "OfferCatalog",
            "name": f"{bt.title()} Services in {city}",
            "itemListElement": [
                {"@type": "Offer", "itemOffered": {"@type": "Service", "name": f"Residential {bt.title()} in {city}"}},
                {"@type": "Offer", "itemOffered": {"@type": "Service", "name": f"Commercial {bt.title()} in {city}"}},
                {"@type": "Offer", "itemOffered": {"@type": "Service", "name": f"Emergency {bt.title()} {city}"}},
                {"@type": "Offer", "itemOffered": {"@type": "Service", "name": f"{bt.title()} Repair {city}"}},
                {"@type": "Offer", "itemOffered": {"@type": "Service", "name": f"{bt.title()} Installation {city}"}},
            ]
        }
    }


async def generate_seo_block(business_type: str, city: str, state: str, target_keywords: list = []) -> SEOBlock:
    rng = _seed_random(city, business_type)
    bt = business_type.title()
    bt_lower = business_type.lower()

    keywords = await generate_keywords(business_type, city, state)

    # Inject target keywords into the keyword set so they appear in output
    if target_keywords:
        # Localise each target keyword to this city (replace generic city refs if present)
        localised = [kw.replace("san diego", city.lower()).replace("San Diego", city) for kw in target_keywords]
        # Prepend to secondary so they appear first
        keywords.secondary = localised + [k for k in keywords.secondary if k not in localised]
        # Also add to long_tail if not already there
        for kw in localised:
            if kw not in keywords.long_tail:
                keywords.long_tail.insert(0, kw)

    title    = _fill(rng.choice(TITLE_VARIANTS), bt, city, state)
    meta     = _fill(rng.choice(META_VARIANTS), bt, city, state)
    h1       = _fill(rng.choice(H1_VARIANTS), bt, city, state)
    h2s      = [_fill(h, bt, city, state) for h in rng.sample(H2_POOL, 4)]
    h3s      = [_fill(h, bt, city, state) for h in rng.sample(H3_POOL, 4)]
    body     = _fill(rng.choice(BODY_VARIANTS), bt, city, state)

    # Weave target keywords naturally into the body content
    if target_keywords:
        localised = [kw.replace("san diego", city.lower()).replace("San Diego", city) for kw in target_keywords]
        # Append a natural sentence per keyword at the end of the body
        kw_sentences = []
        for kw in localised[:3]:  # max 3 to avoid stuffing
            kw_sentences.append(
                f"Whether you're searching for \"{kw}\" or need a trusted local expert, "
                f"our {bt_lower} team in {city} is ready to help."
            )
        if kw_sentences:
            body = body + "\n\n" + " ".join(kw_sentences)

    content  = body
    cta      = _fill(rng.choice(CTA_VARIANTS), bt, city, state)

    faq_pool = rng.sample(FAQ_POOLS, min(6, len(FAQ_POOLS)))
    faqs = [
        FAQItem(
            question=_fill(q, bt, city, state),
            answer=_fill(a, bt, city, state)
        )
        for q, a in faq_pool
    ]

    schema      = _build_schema(bt, city, state)
    readability = _readability_score(content)
    density     = _keyword_density(content, keywords.primary)

    return SEOBlock(
        city=city,
        state=state,
        business_type=bt,
        title=title,
        meta_description=meta,
        h1=h1,
        h2s=h2s,
        h3s=h3s,
        content=content,
        faqs=faqs,
        cta=cta,
        keywords=keywords,
        schema_markup=schema,
        readability_score=readability,
        keyword_density=density,
    )
