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

    # Google Indexing API — path to the service-account JSON key. When set (and
    # the service account is an Owner in Search Console), published URLs are
    # auto-submitted to Google for fast crawling.
    GOOGLE_INDEXING_KEY_FILE: str = ""

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
    GBP_ACCOUNT_ID: str = ""
    GBP_LOCATION_ID: str = ""

    # ── Lead capture ─────────────────────────────────────────────
    BARK_API_KEY: str = ""
    THUMBTACK_API_KEY: str = ""

    class Config:
        env_file = ".env"

settings = Settings()
