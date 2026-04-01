from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # PostgreSQL
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/seo_automation"

    OPENCAGE_API_KEY: str = ""
    GEODB_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    GOOGLE_PLACES_API_KEY: str = ""

    # WordPress integration
    WP_URL: str = ""
    WP_USERNAME: str = ""
    WP_APP_PASSWORD: str = ""
    WP_SEO_PLUGIN: str = "rankmath"
    FRONTEND_URL: str = ""  # "rankmath" | "aioseo" | "yoast"

    class Config:
        env_file = ".env"

settings = Settings()
