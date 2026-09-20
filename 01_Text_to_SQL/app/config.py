import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application Settings configured via environment variables or defaults.
    Follows 12-factor application design.
    """
    APP_NAME: str = "Talk to Your Data - Text-to-SQL Analytics Assistant"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    PORT: int = 8000
    HOST: str = "0.0.0.0"

    # Database Settings
    # Supports PostgreSQL (primary production target) or SQLite (fallback zero-config target)
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./ecommerce.db")
    DB_ECHO: bool = False

    # LLM Settings
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "gemini")  # gemini, openai, mock
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY", os.getenv("GOOGLE_API_KEY"))
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    # Guardrails & Safety Parameters
    MAX_QUERY_ROW_LIMIT: int = 100
    DEFAULT_QUERY_ROW_LIMIT: int = 50
    ALLOW_MUTATION_QUERIES: bool = False
    MAX_SELF_CORRECTION_RETRIES: int = 3
    STATEMENT_TIMEOUT_SECONDS: float = 10.0

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
