from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Literal
from datetime import datetime

class GenerateRequest(BaseModel):
    business_type: str = Field(..., example="Web Design")
    base_location: str = Field(..., example="San Diego, CA")
    num_cities: int = Field(default=10, ge=1, le=100)
    target_keywords: List[str] = Field(default=[], example=["web design san diego"])
    industry: str = Field(default="", example="Contractors")
    use_ai: bool = Field(default=False, description="Use an LLM for content generation")
    llm_provider: Optional[str] = Field(default=None, description="auto | groq | gemini | openai — overrides server default for this request")

class KeywordSet(BaseModel):
    primary: str
    secondary: List[str]
    long_tail: List[str]
    near_me: List[str]
    user_questions: List[str] = Field(default=[])

class FAQItem(BaseModel):
    question: str
    answer: str

class ImageAsset(BaseModel):
    """A generated image with full SEO metadata (used for featured + in-content images)."""
    url: str = ""                      # public/hosted URL if available
    filename: str = ""                 # SEO-friendly filename, e.g. web-design-austin-1.webp
    mime_type: str = "image/webp"
    alt_text: str = ""
    title: str = ""
    caption: str = ""
    description: str = ""
    is_featured: bool = False

class SEOBlock(BaseModel):
    city: str
    state: str
    business_type: str
    industry: str = ""
    title: str
    meta_description: str
    slug: str = ""
    h1: str
    h2s: List[str]
    h3s: List[str]
    intro: str = ""
    content: str
    faqs: List[FAQItem]
    cta: str
    keywords: KeywordSet
    schema_markup: Dict[str, Any]
    readability_score: Optional[float] = None
    keyword_density: Optional[float] = None
    wp_post_id: Optional[int] = None
    wp_post_url: Optional[str] = None
    featured_image_url: Optional[str] = None
    # ── Keyword-driven article extensions ────────────────────────
    focus_keyword: str = ""
    secondary_keywords: List[str] = Field(default=[])
    in_content_images: List[ImageAsset] = Field(default=[])
    source_url: str = ""               # the analyzed website this article was grounded on
    content_type: Literal["service", "blog"] = "service"  # pillar/service page vs. supporting blog post — drives WordPress category

# ── Website Analysis Models ──────────────────────────────────────
class SitePage(BaseModel):
    """A single page discovered on the analyzed website (used for internal linking)."""
    url: str
    title: str = ""
    page_type: str = "other"           # blog | service | location | contact | product | home | other

class WebsiteProfile(BaseModel):
    """Structured understanding of a business website used to ground content generation."""
    url: str
    business_name: str = ""
    services: List[str] = Field(default=[])
    products: List[str] = Field(default=[])
    target_audience: str = ""
    brand_tone: str = ""
    existing_blog_topics: List[str] = Field(default=[])
    summary: str = ""
    phone: str = ""
    page_inventory: List[SitePage] = Field(default=[])
    analyzed: bool = False             # False when analysis failed / degraded gracefully

class ArticleRequest(BaseModel):
    primary_keyword: str = Field(..., example="commercial roofing")
    location: str = Field(..., example="Austin, TX")
    website_url: str = Field(..., example="https://example-roofing.com")
    # Number of US locations (target + nearby) to cover — one article per city.
    num_cities: int = Field(default=5, ge=1, le=25)
    num_articles: int = Field(default=1, ge=1, le=10, description="Articles per city (angle variety)")
    industry: str = Field(default="")
    use_ai: bool = Field(default=True, description="Use an LLM when available; template fallback otherwise")
    llm_provider: Optional[str] = Field(default=None, description="auto | groq | gemini | openai — overrides server default for this request")

class WebsiteAnalysisRequest(BaseModel):
    website_url: str = Field(..., example="https://example.com")

class SEOPage(BaseModel):
    id: Optional[str] = None
    business_type: str
    base_location: str
    city: str
    state: str
    slug: str
    seo_block: SEOBlock
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class BulkGenerateResponse(BaseModel):
    total: int
    pages: List[SEOBlock]
    job_id: str

class CityInfo(BaseModel):
    name: str
    state: str
    country: str
    latitude: float
    longitude: float
    population: Optional[int] = None

# WordPress integration models
class WordPressConfig(BaseModel):
    # Blank/omitted → server falls back to the configured connection (env).
    wp_url: str = Field(default="", example="https://yoursite.com")
    wp_username: str = Field(default="")
    wp_app_password: str = Field(default="")
    seo_plugin: str = Field(default="aioseo", description="rankmath | aioseo | yoast")
    status: str = Field(default="draft", description="draft | publish")
    category_ids: List[int] = Field(default=[], description="WordPress category IDs")
    tag_ids: List[int] = Field(default=[], description="WordPress tag IDs")
    scheduled_at: Optional[str] = Field(default=None, description="ISO datetime for scheduled publish")
    fetch_image: bool = Field(default=True, description="Auto-fetch and upload featured image")

class PublishRequest(BaseModel):
    seo_block: SEOBlock
    wp_config: WordPressConfig

class BulkPublishRequest(BaseModel):
    pages: List[SEOBlock]
    wp_config: WordPressConfig

class PublishResult(BaseModel):
    city: str
    success: bool
    post_id: Optional[int] = None
    post_url: Optional[str] = None
    error: Optional[str] = None
    featured_image_id: Optional[int] = None

# ── Social Media Models ──────────────────────────────────────────
class SocialAccount(BaseModel):
    platform: str  # facebook | twitter | linkedin | instagram
    account_id: str
    account_name: str
    access_token: str
    extra: Dict[str, Any] = {}

class SocialPostRequest(BaseModel):
    post_url: str
    title: str
    meta_description: str
    city: str
    business_type: str
    keywords: List[str] = []
    platforms: List[str] = Field(default=["facebook", "twitter", "linkedin"])
    image_url: Optional[str] = None

class SocialPostResult(BaseModel):
    platform: str
    success: bool
    post_id: Optional[str] = None
    post_url: Optional[str] = None
    error: Optional[str] = None

# ── Google Ads ───────────────────────────────────────────────────
class GoogleAdsCampaignRequest(BaseModel):
    campaign_name: str = Field(..., example="Plumbing Services - Austin TX")
    daily_budget: float = Field(..., gt=0, description="Daily budget in the account's currency, e.g. 25.00")
    final_url: str = Field(..., example="https://example.com/plumbing-austin")
    headlines: List[str] = Field(..., min_length=3, max_length=15, description="3-15 headlines, each <= 30 chars")
    descriptions: List[str] = Field(..., min_length=2, max_length=4, description="2-4 descriptions, each <= 90 chars")
    keywords: List[str] = Field(..., min_length=1, description="Keywords to target (broad match)")
    enable: bool = Field(
        default=False,
        description="If true, create campaign ENABLED (can spend). Default false = PAUSED.",
    )

class GoogleAdsSuggestRequest(BaseModel):
    business_name: str = ""
    category: str = ""
    city: str = ""

class GoogleAdsLaunchRequest(BaseModel):
    """One-shot: AI copy + create campaign for an already-published public URL."""
    final_url: str
    business_name: str = ""
    category: str = ""
    city: str = ""
    daily_budget: float = Field(default=25.0, gt=0)
    enable: bool = False
    keywords: List[str] = []

class GoogleAdsCampaignResult(BaseModel):
    success: bool
    campaign_id: Optional[str] = None
    campaign_resource_name: Optional[str] = None
    ad_group_resource_name: Optional[str] = None
    manage_url: Optional[str] = None
    error: Optional[str] = None
    demo: bool = False

# ── Google Business Profile (free local posts) ────────────────────
class GBPPostRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1500)
    cta_type: str = Field(default="LEARN_MORE", description="LEARN_MORE | CALL | BOOK | ORDER | SHOP | SIGN_UP | GET_OFFER")
    cta_url: Optional[str] = None
    image_url: Optional[str] = None

class GBPPostResult(BaseModel):
    success: bool
    post_name: Optional[str] = None
    error: Optional[str] = None
    demo: bool = False

class GBPSuggestRequest(BaseModel):
    business_name: str = ""
    city: str = ""
    service: str = ""
    tone: str = "friendly"

# ── Lead Models ──────────────────────────────────────────────────
class Lead(BaseModel):
    id: Optional[int] = None
    source: str  # manual | prospecting | website | instant-quote | webhook
    name: str = ""            # customer / contact person name
    business_name: str = ""
    contact_name: str = ""
    email: Optional[str] = None
    phone: Optional[str] = None
    website: str = ""
    industry: str = ""
    service: str = ""
    location: str = ""
    budget: Optional[str] = None
    message: Optional[str] = None
    status: str = "new"  # new | contacted | qualified | closed
    created_at: Optional[datetime] = None

class LeadCreate(BaseModel):
    source: str = "manual"
    name: str = ""
    business_name: str = ""
    contact_name: str = ""
    email: Optional[str] = None
    phone: Optional[str] = None
    website: str = ""
    industry: str = ""
    service: str = ""
    location: str = ""
    budget: Optional[str] = None
    message: Optional[str] = None

class ProspectRequest(BaseModel):
    industry: str = Field(..., example="roofing")
    location: str = Field(..., example="Austin, TX")
    limit: int = Field(default=20, ge=1, le=60)

# ── Job Queue Models ─────────────────────────────────────────────
class JobStatus(BaseModel):
    job_id: str
    status: str  # pending | running | done | failed
    total: int
    completed: int
    failed: int
    results: List[Dict[str, Any]] = []
    error: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

# ── Site Audit ───────────────────────────────────────────────────
class AuditIssue(BaseModel):
    id: str
    title: str
    severity: str  # critical | warning | opportunity | passed
    category: str  # Technical SEO | On-Page SEO | Performance | Content | Links
    what: str
    why: str
    affected_pages: List[str] = []
    how_to_fix: str

class AuditCategory(BaseModel):
    name: str
    score: int  # 0-100

class AuditResult(BaseModel):
    url: str
    overall_score: int  # 0-100
    categories: List[AuditCategory]
    issues: List[AuditIssue]

# ── Keyword Research ─────────────────────────────────────────────
class KeywordMetric(BaseModel):
    keyword: str
    volume: int
    difficulty: int  # 0-100
    cpc: float
    intent: str  # Informational | Commercial | Transactional | Navigational
    trend: str   # e.g. "+12%"
    serp_features: List[str] = []

class KeywordResearchResult(BaseModel):
    location: str
    language: str
    primary: KeywordMetric
    related: List[KeywordMetric]

# ── Rank Tracking ────────────────────────────────────────────────
class RankingPoint(BaseModel):
    date: str
    position: int

class RankingMetric(BaseModel):
    keyword: str
    position: int
    previous_position: int
    volume: int
    url: str
    history: List[RankingPoint]

class RankingResult(BaseModel):
    business_type: str
    location: str
    keywords: List[RankingMetric]
