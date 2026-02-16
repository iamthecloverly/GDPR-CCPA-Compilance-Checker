"""Configuration settings for GDPR/CCPA Compliance Checker."""

import os
from typing import Optional, Dict


class Config:
    """Application configuration."""
    
    # Application
    APP_NAME = "GDPR/CCPA Compliance Checker"
    DEBUG = os.getenv("APP_DEBUG", "").lower() in {"1", "true", "yes"}
    
    # User Agent
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    
    # Database
    DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL")
    DB_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "5"))
    DB_POOL_RECYCLE = int(os.getenv("DB_POOL_RECYCLE", "300"))
    
    # OpenAI
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    OPENAI_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
    OPENAI_MAX_TOKENS = int(os.getenv("OPENAI_MAX_TOKENS", "1500"))
    
    # Scanning
    REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "10"))
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
    BACKOFF_FACTOR = float(os.getenv("BACKOFF_FACTOR", "0.3"))
    MAX_POLICY_LENGTH = int(os.getenv("MAX_POLICY_LENGTH", "8000"))
    
    # Batch Scanning
    BATCH_SCAN_LIMIT = int(os.getenv("BATCH_SCAN_LIMIT", "10"))
    
    # Scoring Weights
    SCORING_WEIGHTS: Dict[str, int] = {
        "cookie_consent": int(os.getenv("SCORE_COOKIE_CONSENT", "25")),
        "privacy_policy": int(os.getenv("SCORE_PRIVACY_POLICY", "25")),
        "ccpa_compliance": int(os.getenv("SCORE_CCPA_COMPLIANCE", "10")),
        "contact_info": int(os.getenv("SCORE_CONTACT_INFO", "20")),
        "trackers": int(os.getenv("SCORE_TRACKERS_MAX", "20")),
    }
    
    # History
    DEFAULT_HISTORY_LIMIT = int(os.getenv("DEFAULT_HISTORY_LIMIT", "20"))
    
    @classmethod
    def validate(cls) -> None:
        """Validate critical configuration."""
        if cls.DATABASE_URL and cls.DATABASE_URL.startswith("postgresql"):
            try:
                import psycopg2
            except ImportError:
                raise ImportError("psycopg2-binary required for PostgreSQL")

