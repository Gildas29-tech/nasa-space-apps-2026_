from pydantic_settings import BaseSettings
from typing import Optional
from functools import lru_cache


class Settings(BaseSettings):
    # App
    APP_NAME: str = "FieldShift API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    # NASA POWER API
    NASA_POWER_BASE_URL: str = "https://power.larc.nasa.gov/api/temporal/daily/point"
    NASA_POWER_TIMEOUT: int = 30

    # Supabase (optional)
    SUPABASE_URL: Optional[str] = None
    SUPABASE_ANON_KEY: Optional[str] = None
    SUPABASE_SERVICE_KEY: Optional[str] = None

    # Sentinel Hub (optional)
    SENTINEL_HUB_CLIENT_ID: Optional[str] = None
    SENTINEL_HUB_CLIENT_SECRET: Optional[str] = None

    # Cache
    CACHE_TTL_SECONDS: int = 3600

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()