"""
Application configuration — 12-Factor App pattern.
All sensitive values come from environment variables.
"""
from functools import lru_cache
from typing import Union
from pydantic import field_validator, ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # ── App ──
    APP_NAME: str = "SupportSight Live"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"
    CORRELATION_ID_HEADER: str = "X-Correlation-ID"

    # ── Gemini ──
    GEMINI_API_KEY: str
    GEMINI_MODEL: str = "gemini-3.1-flash-lite-preview"
    GEMINI_MAX_TOKENS: int = 4096
    GEMINI_TEMPERATURE: float = 0.2

    # ── PostgreSQL ──
    DATABASE_URL: str = "postgresql+asyncpg://user:pass@localhost:5432/supportsight"

    # ── Redis ──
    REDIS_URL: str = "redis://localhost:6379/0"

    # ── Services ──
    LOGS_SERVICE_URL: str = "http://localhost:8090"
    ACTIONS_SERVICE_URL: str = "http://localhost:8091"
    ACTIONS_SERVICE_API_KEY: str = ""

    # ── Security ──
    SECRET_KEY: str = "change-me-in-production"
    API_KEY_HEADER: str = "X-API-Key"
    ALLOWED_ORIGINS: Union[list[str], str] = ["http://localhost:3000", "http://localhost:8080"]

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, list[str]]) -> list[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # ── Session ──
    SESSION_TTL_SECONDS: int = 3600
    MAX_SESSION_HISTORY: int = 50


@lru_cache
def get_settings() -> Settings:
    return Settings()
