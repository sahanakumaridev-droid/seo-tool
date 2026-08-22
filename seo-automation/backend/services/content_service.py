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

def _kw_words_present(text: str, keyword: str) -> bool:
    """True if every significant word of `keyword` appears in `text`,
    regardless of order or adjacency. Real SEO copy rarely repeats a keyword
    as one exact contiguous phrase — "Web Design Services in San Diego" is
    better writing than the literal "web design san diego" and should still
    get full credit for covering the keyword, not be penalized for it."""
    text_l = text.lower()
    return all(word in text_l for word in keyword.lower().split())


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

    if _kw_words_present(title, keyword):                score += 15
    if _kw_words_present(meta, keyword):                 score += 10
    if kw.replace(" ", "-") in slug_l or kw.replace(" ", "") in slug_l: score += 10
    if _kw_words_present(first_100, keyword):            score += 15
    if sum(1 for h in h2s if _kw_words_present(h, keyword)) >= 2: score += 10
    if len(words) >= 300:                                score += 10
    if len(faqs) >= 5:                                   score += 10
    if city_l in title_l:                                score += 10
    if len(h2s) >= 4:                                    score += 5
    if 120 <= len(meta) <= 165:                          score += 5

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
"""

LAYOUT_VARIANTS = ("qa", "steps", "story", "cards", "split", "timeline")

LAYOUT_INSTRUCTIONS = {
    "qa": "Use question-style H2s a real customer would ask. Body answers in short paragraphs, then a 3-item list.",
    "steps": "Structure as a how-to: H2s are numbered steps (Step 1, Step 2…). Body is actionable, not a pitch.",
    "story": "Open with a local situation, then proof, then what working together looks like. One H2 should be a short anecdote.",
    "cards": "Each H2 is a distinct benefit/offer card (speed, local SEO, care plan, cost clarity). Keep each section 2-4 sentences.",
    "split": "Alternate problem vs solution: first H2 is the pain in this city, next is how you fix it, then who it's for, then timeline, then next step.",
    "timeline": "Walk the reader through a project timeline (week 1 discovery → design → build → launch → support).",
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
) -> SEOBlock:
    from services.image_service import resolve_campaign_niche
    city, state = _one_place(city, state)
    original_niche = normalize_niche_text(business_type or "")
    business_type = resolve_campaign_niche(
        original_niche,
        industry or "",
    )
    kind = "blog" if (content_kind or "page") == "post" else "service"
    layout = pick_layout_variant(city, business_type, kind)
    if use_ai:
        try:
            block = await _generate_ai_block(
                business_type, city, state, target_keywords, industry, llm_provider,
                custom_requirements=custom_requirements, content_kind=kind, audience=audience,
                layout_variant=layout,
            )
        except Exception as e:
            print(f"[AI] LLM generation failed, falling back to templates: {e}")
            block = await _generate_template_block(
                business_type, city, state, target_keywords, industry,
                custom_requirements=custom_requirements, content_kind=kind, audience=audience,
                layout_variant=layout,
            )
    else:
        block = await _generate_template_block(
            business_type, city, state, target_keywords, industry,
            custom_requirements=custom_requirements, content_kind=kind, audience=audience,
            layout_variant=layout,
        )

    from services.slug_utils import article_slug
    slug_seed = (custom_requirements or business_type) if kind == "blog" else business_type
    block.slug = article_slug(target_keywords, city, slug_seed)
    block.content_type = kind
    block.layout_variant = layout
    block.city = city
    block.state = state or block.state

    try:
        from services.image_service import generate_article_images
        focus_keyword = block.keywords.primary if block.keywords and block.keywords.primary else f"{business_type} {city}"
        images = await generate_article_images(
            focus_keyword, f"{city}, {state}".strip(", "), "", count=3,
            exclude_urls=exclude_image_urls,
            industry=industry or "",
            niche=original_niche,
        )
        block.in_content_images = images
        if images:
            block.featured_image_url = images[0].url
        else:
            block.featured_image_url = await _get_business_image(business_type, city)
        print(f"[Image] Set {len(images)} image(s) for {business_type} in {city}")
    except Exception as e:
        print(f"[Image] Failed to set image: {e}")
        block.featured_image_url = await _get_business_image(business_type, city)

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
) -> SEOBlock:
    """Generate SEO content using an LLM (GPT-4, Gemini, or Groq — whichever
    is configured/selected) for higher quality, unique content."""
    from services.llm_service import chat_json

    city, state = _one_place(city, state)
    brief = (custom_requirements or "").strip()
    place = f"{city}, {state}".strip(", ") if state else city
    audience_line = f"Speak to: {audience}." if audience else "Speak to a US business owner or operator."
    kw_line = ", ".join(target_keywords) if target_keywords else "None"
    layout = layout_variant if layout_variant in LAYOUT_INSTRUCTIONS else pick_layout_variant(city, business_type, content_kind)
    layout_note = LAYOUT_INSTRUCTIONS[layout]

    if content_kind == "blog":
        topic = brief or business_type
        primary_kw = (target_keywords[0] if target_keywords else topic).strip()
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
        prompt = f"""You are a US content writer creating ONE blog post / article.

THIS ARTICLE'S TOPIC (follow exactly — do not replace it with a generic service pitch):
{topic}

Business context (only if relevant): {business_type}
Industry: {industry or "General"}
{audience_line}
SEO keywords to weave in naturally: {kw_line}
BODY LAYOUT ({layout}): {layout_note}
Do not reuse a generic five-question local-service outline. This layout must be visibly different from a location landing page.
{loc_note}

{VOICE_RULES}

Write an informational / educational / how-to article that actually answers the topic.
If the topic is "How to set 301 redirects on a website", teach 301 redirects — steps, when to use them, common mistakes.
Do NOT turn it into "web design services in San Diego".

Generate a JSON response with EXACTLY this structure:
{{
  "title": "SEO title 50-60 chars, about the topic (not a list of cities)",
  "meta_description": "150-160 chars, promise the reader will learn the topic, include a soft CTA",
  "h1": "Clear article H1 that matches the topic (question or how-to is fine)",
  "h2s": ["5 H2s that outline the article: what it is, steps, mistakes, tools, when to get help"],
  "h3s": ["4 supporting H3s"],
  "intro": "2-3 sentences. Open with a user-focused question or situation, then say what this post covers.",
  "content": "4-6 paragraphs, 500+ words. Numbered or bulleted steps when teaching. Separate paragraphs with double newlines.",
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

Return ONLY valid JSON, no markdown."""
    else:
        keywords = await generate_keywords(business_type, city or "United States", state or "")
        if target_keywords:
            keywords.secondary = list(dict.fromkeys([k.lower() for k in target_keywords] + keywords.secondary))
        primary_kw = keywords.primary
        secondary_kws = ", ".join(keywords.secondary[:5])
        faq_questions = "\n".join([f"- {q}" for q in keywords.user_questions[:6]])
        brief_block = f"\nOFFER / PAGE BRIEF (this is the page purpose — honor it):\n{brief}\n" if brief else ""
        prompt = f"""You are a US SEO writer creating ONE website SERVICE / LOCATION PAGE (not a blog post).

Page purpose: {brief or business_type}
Business Type: {business_type}
Location (the ONLY place this page is about): {place or "the United States"}
Do NOT list other cities, neighborhoods, or communities in the title, H1, meta, or body.
Primary Keyword: {primary_kw}
Secondary Keywords: {secondary_kws}
Industry: {industry or "General"}
{audience_line}
Target Keywords: {kw_line}
{brief_block}
BODY LAYOUT ({layout}): {layout_note}
Vary H2s and body shape for this layout — never the same five “what/how much/why” local-service headings on every page.
{VOICE_RULES}

This is a conversion page. Open like:
- "Looking for WordPress website design for automobile businesses in San Diego?"
- "Thinking about a new site for your auto shop?"
Then explain how you help, what they get, and a calm next step.

Generate a JSON response with EXACTLY this structure:
{{
  "title": "Meta title (50-60 chars, include primary keyword and {city or 'your area'} only)",
  "meta_description": "Meta description (150-160 chars, include primary keyword and a helpful CTA)",
  "h1": "Main heading (include primary keyword and {city or 'your business'} only — never a list of places)",
  "h2s": ["5 H2 subheadings covering the service for this location"],
  "h3s": ["4 H3 subheadings for supporting sections"],
  "intro": "2-3 sentence intro. User-focused question, then what you do.",
  "content": "3-4 paragraphs of body content (400+ words total). Local context for {city or 'this market'} only. Separate paragraphs with double newlines.",
  "faqs": [
    {{"question": "FAQ question 1", "answer": "Detailed answer 1 (2-3 sentences)"}},
    {{"question": "FAQ question 2", "answer": "Detailed answer 2"}},
    {{"question": "FAQ question 3", "answer": "Detailed answer 3"}},
    {{"question": "FAQ question 4", "answer": "Detailed answer 4"}},
    {{"question": "FAQ question 5", "answer": "Detailed answer 5"}},
    {{"question": "FAQ question 6", "answer": "Detailed answer 6"}}
  ],
  "cta": "Warm call-to-action (2-3 sentences). 'Not sure where to start? We're here to help.'"
}}

FAQ questions to address:
{faq_questions}

Requirements:
- Unique, not generic
- One location only
- No keyword stuffing
- Each FAQ answer 2-3 sentences minimum
- Return ONLY valid JSON, no markdown"""

    data = await chat_json(prompt, temperature=0.7, max_tokens=3000, provider=llm_provider)
    if not data:
        raise RuntimeError("LLM generation failed or returned no data")
    bt = business_type.title()
    slug = _slugify(f"{business_type.lower()}-{city}")

    faqs = [FAQItem(question=f["question"], answer=f["answer"]) for f in data.get("faqs", [])]
    schema = _build_schema(bt, city, state, faqs)

    title = data.get("title", "")
    meta = data.get("meta_description", "")
    h2s = data.get("h2s", [])
    content_text = data.get("intro", "") + " " + data.get("content", "")

    seo_score = _seo_score(content_text, title, meta, h2s, faqs, primary_kw, city, slug)
    density = _keyword_density(content_text, primary_kw)

    return SEOBlock(
        city=city,
        state=state,
        business_type=bt,
        industry=industry,
        slug=slug,
        title=title,
        meta_description=meta,
        h1=data.get("h1", ""),
        h2s=h2s,
        h3s=data.get("h3s", []),
        intro=data.get("intro", ""),
        content=data.get("content", ""),
        faqs=faqs,
        cta=data.get("cta", ""),
        keywords=keywords,
        schema_markup=schema,
        readability_score=seo_score,
        keyword_density=density,
        content_type="blog" if content_kind == "blog" else "service",
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
) -> SEOBlock:
    brief = (custom_requirements or "").strip()
    if content_kind == "blog":
        topic = brief or business_type
        primary = (target_keywords[0] if target_keywords else topic).strip()
        slug = _slugify(primary)
        title = (topic[:58] + "…") if len(topic) > 60 else topic
        h1 = topic.rstrip("?") if topic.endswith("?") else topic
        intro = (
            f"Not sure where to start with {primary.lower()}? You're not alone. "
            f"This guide walks you through it in plain American English — what it is, how to do it, and when to get help."
        )
        content = (
            f"Looking for a clear answer on {primary.lower()}?\n\n"
            f"Here's the short version: {topic.rstrip('.')}. "
            f"We'll keep this practical so you can take the next step without the jargon.\n\n"
            f"1. Understand the goal.\n2. Follow the steps in order.\n3. Test the result.\n4. Ask for help if you get stuck.\n\n"
            f"We help you turn your idea into something that actually works — from concept to launch. "
            f"Not sure where to start? We're here to help."
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
            "A soft next step if you need a hand",
        ]
        faqs = [
            FAQItem(question=f"What is {primary.lower()}?", answer=f"{primary} is easier than it sounds. This post covers the basics so you can decide what to do next."),
            FAQItem(question="Can I do this myself?", answer="Many teams can handle the first pass. If the setup is messy or high-stakes, get a specialist involved."),
            FAQItem(question="How long does it take?", answer="A straightforward setup can take minutes. Larger sites take longer because you should test every path."),
            FAQItem(question="What if I get it wrong?", answer="Most issues are reversible if you catch them early. Test, keep a backup, and don't guess on production."),
            FAQItem(question="Do I need a developer?", answer="Not always. If you're changing live URLs or app flows, a developer (or us) can keep things from breaking."),
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
        seo_score = _seo_score(intro + " " + content, title, "", h2s, faqs, primary, city or "", slug)
        return SEOBlock(
            city=city, state=state, business_type=business_type.title(), industry=industry,
            slug=slug, title=title, meta_description=f"A practical US-English guide to {primary.lower()}. Clear steps, fewer mistakes, and a next step if you need help.",
            h1=h1, h2s=h2s, h3s=h3s, intro=intro, content=content, faqs=faqs,
            cta="Not sure where to start? We're here to help you turn this into a working plan — from concept to launch.",
            keywords=kw, schema_markup=schema, readability_score=seo_score,
            keyword_density=_keyword_density(intro + " " + content, primary),
            content_type="blog",
        )

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
    layout = layout_variant if layout_variant in LAYOUT_INSTRUCTIONS else pick_layout_variant(city, business_type, content_kind)
    if layout == "steps":
        h2s = [
            f"Step 1: Map what {city} visitors should do on your site",
            f"Step 2: Design pages that match how {city} customers search",
            f"Step 3: Build, test, and launch without the guesswork",
            f"Step 4: Measure leads from {city} after go-live",
            "Step 5: Keep the site current after launch",
        ]
    elif layout == "timeline":
        h2s = [
            f"Week 1 — discovery for your {city} business",
            "Weeks 2–3 — design and content",
            "Weeks 3–5 — build and reviews",
            f"Launch week in {city}",
            "30 days of support after you go live",
        ]
    elif layout == "split":
        h2s = [
            f"What's getting in the way for {city} businesses",
            f"A clearer {bt_lower} path",
            "Who this is a fit for",
            "What you can expect on timeline and cost",
            "A simple next step if you're ready",
        ]
    elif layout == "cards":
        h2s = [
            f"Local {bt_lower} that understands {city}",
            "Clear pricing — no surprise invoices",
            "Built to rank and convert, not just look pretty",
            "Care after launch",
            "Talk it through before you commit",
        ]
    elif layout == "story":
        h2s = [
            f"A familiar story for {city} owners",
            "What changed when the site started working",
            f"How we approach {bt_lower} here",
            "Proof over promises",
            "If this sounds like you",
        ]
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
        content_type="service",
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
    seo_score = _seo_score(full_text, title, meta, h2s, faqs, primary_keyword, city, slug)
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
