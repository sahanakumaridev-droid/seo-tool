from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # ── Environment ──────────────────────────────────────────────
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # ── Database ─────────────────────────────────────────────────
    DATABASE_URL: str = "sqlite+aiosqlite:///./seo_automation.db"
    
    # ── Authentication ───────────────────────────────────────────
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # ── Observability ────────────────────────────────────────────
    SENTRY_DSN: str = ""
    LOG_LEVEL: str = "INFO"
    
    # ── Caching ──────────────────────────────────────────────────
    REDIS_URL: str = "redis://localhost:6379/0"
    CACHE_TTL: int = 3600  # 1 hour
    
    # ── Vector DB (Semantic Search) ──────────────────────────────
    PINECONE_API_KEY: str = ""
    PINECONE_ENVIRONMENT: str = "us-west1-gcp"
    PINECONE_INDEX_NAME: str = "seo-content"
    
    # ── AI APIs ──────────────────────────────────────────────────
    OPENCAGE_API_KEY: str = ""
    GEODB_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    GOOGLE_PLACES_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    COHERE_API_KEY: str = ""
    # ── Free-tier LLM providers (preferred for zero-cost content) ─
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-1.5-flash"
    # Which provider to prefer: auto | groq | gemini | openai
    LLM_PROVIDER: str = "auto"
    
    # ── WordPress integration ────────────────────────────────────
    WP_URL: str = ""
    WP_USERNAME: str = ""
    WP_APP_PASSWORD: str = ""
    WP_SEO_PLUGIN: str = "rankmath"
    FRONTEND_URL: str = ""
    # Base URL used to build public "Publish to Web" links. If empty, it is
    # derived from the incoming request. e.g. https://seo.159.198.79.219.nip.io
    PUBLIC_BASE_URL: str = ""

    # ── Marketing / Tracking ─────────────────────────────────────
    # Google Tag Manager container (e.g. "GTM-XXXXXXX"). Empty = no tag loaded,
    # so published /p/ pages ship inert until an ID is set. Manage GA4, Google
    # Ads conversions & remarketing inside GTM once populated.
    GTM_CONTAINER_ID: str = ""

    # Google AdSense publisher ID (e.g. "ca-pub-1234567890123456"). Empty = no
    # ad script loaded, so published /p/ pages ship without ads until it's
    # set. Once set, auto ads run site-wide and an in-article unit renders
    # inside each published page (optionally scoped to ADSENSE_SLOT_ID).
    ADSENSE_CLIENT_ID: str = ""
    ADSENSE_SLOT_ID: str = ""

    # Google Indexing API — path to the service-account JSON key. NOTE: Google
    # restricts this API to JobPosting/BroadcastEvent pages, so it is NOT
    # auto-invoked for ordinary blog posts (see routes/wordpress.py) — it
    # remains available only as a manual, opt-in endpoint (/api/indexing/submit).
    GOOGLE_INDEXING_KEY_FILE: str = ""

    # Google Search Console API (Sitemaps + URL Inspection) — the compliant
    # path for blog content. Reuses GOOGLE_INDEXING_KEY_FILE's service account
    # (same Google Cloud project, already an Owner on the property) with a
    # different OAuth scope. GSC_SITE_URL is the verified property, e.g.
    # "https://zeorbit.com/" or "sc-domain:zeorbit.com". WP_SITEMAP_URL is the
    # exact sitemap URL your SEO plugin (RankMath/AIOSEO) already publishes,
    # e.g. "https://zeorbit.com/sitemap_index.xml".
    GSC_SITE_URL: str = ""
    WP_SITEMAP_URL: str = ""
    # Optional: paste the google-site-verification content token from Search Console
    # (URL-prefix property → HTML tag). Injected into every /p/{slug} page <head>.
    GSC_VERIFICATION_META: str = ""
    # Optional: filename Google gives you for HTML-file verification, e.g.
    # "google123abc.html", served at /{filename} with GSC_VERIFICATION_FILE_BODY.
    GSC_VERIFICATION_FILENAME: str = ""
    GSC_VERIFICATION_FILE_BODY: str = ""
    # Auto-submit sitemap + track all /p/ pages after publish (default on).
    GSC_AUTO_PUSH_ON_PUBLISH: bool = True

    # ── Image APIs ───────────────────────────────────────────────
    UNSPLASH_ACCESS_KEY: str = ""
    PEXELS_API_KEY: str = ""
    
    # ── Social Media ─────────────────────────────────────────────
    FACEBOOK_ACCESS_TOKEN: str = ""
    FACEBOOK_PAGE_ID: str = ""
    TWITTER_API_KEY: str = ""
    TWITTER_API_SECRET: str = ""
    TWITTER_ACCESS_TOKEN: str = ""
    TWITTER_ACCESS_SECRET: str = ""
    LINKEDIN_ACCESS_TOKEN: str = ""
    LINKEDIN_PERSON_URN: str = ""
    INSTAGRAM_ACCESS_TOKEN: str = ""
    INSTAGRAM_ACCOUNT_ID: str = ""
    # Pinterest / Threads / Google Business Profile (credential-gated adapters)
    PINTEREST_ACCESS_TOKEN: str = ""
    PINTEREST_BOARD_ID: str = ""
    THREADS_ACCESS_TOKEN: str = ""
    THREADS_USER_ID: str = ""
    GBP_ACCESS_TOKEN: str = ""
    GBP_REFRESH_TOKEN: str = ""
    GBP_ACCOUNT_ID: str = ""
    GBP_LOCATION_ID: str = ""

    # ── Google Ads (campaign creation/publishing) ────────────────
    # From Google Ads API Center (console.cloud.google.com OAuth client +
    # ads.google.com API Center for the developer token). All five must be
    # set for campaign creation to run; otherwise it's credential-gated off.
    GOOGLE_ADS_DEVELOPER_TOKEN: str = ""
    GOOGLE_ADS_CLIENT_ID: str = ""
    GOOGLE_ADS_CLIENT_SECRET: str = ""
    GOOGLE_ADS_REFRESH_TOKEN: str = ""
    GOOGLE_ADS_CUSTOMER_ID: str = ""       # the ad account to create campaigns in (digits only, no dashes)
    GOOGLE_ADS_LOGIN_CUSTOMER_ID: str = "" # manager (MCC) account id, if the above is a client account under one
    # After /p/ publish: auto-create a Search campaign for that URL (paused unless AUTO_ENABLE).
    GOOGLE_ADS_AUTO_CREATE_ON_PUBLISH: bool = True
    # Dangerous for spend — leave false unless billing is intentional. Default keeps campaigns paused.
    GOOGLE_ADS_AUTO_ENABLE: bool = False

    # ── Website form notifications ────────────────────────────────
    # Emails website inquiries to the inbox below. Requires SMTP credentials
    # for a mailbox that is allowed to send (Google Workspace app password,
    # Microsoft 365, or the host's SMTP).
    LEAD_NOTIFY_TO: str = "info@zeorbit.com"
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = "info@zeorbit.com"
    SMTP_STARTTLS: bool = True

    # ── Demo mode (optional sales simulation ONLY when live APIs missing) ─
    # Production default: false. Prefer free live Google APIs + free Groq/Gemini.
    # When true AND credentials are missing, Indexing/GBP/Ads return demo data.
    DEMO_MODE: bool = False

    class Config:
        env_file = ".env"

settings = Settings()
