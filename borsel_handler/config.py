"""
Application Configuration and Environment Settings
"""
import os
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Borsel Handler Data Collection Platform"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"

    # Database connection string: PostgreSQL in production, SQLite in local/test
    DATABASE_URL: str = "sqlite:///./borsel_handler.db"

    # Security & CORS
    API_SECRET_KEY: str = ""
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    # Ingestion & Scraping Settings
    DEFAULT_LOOKBACK_HOURS: int = 48
    HTTP_TIMEOUT_SECONDS: int = 15
    MAX_RETRIES: int = 3
    RETRY_BACKOFF_SECONDS: float = 2.0
    COLLECTION_INTERVAL_MINUTES: int = 60

    # Optional 3rd party API keys
    MARKETAUX_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""

    # Optional Headless Browser (Playwright) Settings
    ENABLE_PLAYWRIGHT: bool = False
    PLAYWRIGHT_TIMEOUT_SECONDS: int = 30

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
