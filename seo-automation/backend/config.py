from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    MONGODB_URI: str = "mongodb://localhost:27017"
    DB_NAME: str = "seo_automation"
    OPENCAGE_API_KEY: str = ""
    GEODB_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    GOOGLE_PLACES_API_KEY: str = ""

    class Config:
        env_file = ".env"

settings = Settings()
