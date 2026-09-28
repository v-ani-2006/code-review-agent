from functools import lru_cache
from typing import Optional
from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration settings loaded from environment variables or .env file."""

    APP_NAME: str = Field(
        default="code-review-agent",
        description="Name of the application",
    )
    APP_VERSION: str = Field(
        default="1.0.0",
        description="Current semantic version of the application",
    )
    DEBUG: bool = Field(
        default=True,
        description="Debug mode toggle for detailed logs and diagnostics",
    )
    API_PREFIX: str = Field(
        default="",
        description="Optional prefix path for all API routes (e.g., /api/v1)",
    )
    BUILD_COMMIT: Optional[str] = Field(
        default="main-v1.0.0",
        description="Git commit hash corresponding to the deployed artifact",
    )
    BUILD_TIMESTAMP: Optional[str] = Field(
        default="2026-09-28T14:00:00Z",
        description="Build timestamp of the deployed container image",
    )
    AI_PROVIDER: str = Field(
        default="Google Gemini (gemini-2.5-flash)",
        description="Active AI provider backend",
    )
    DATABASE_PROVIDER: str = Field(
        default="PostgreSQL 16 (asyncpg)",
        description="Active relational database backend",
    )
    CACHE_PROVIDER: str = Field(
        default="Redis 7 (redis-py)",
        description="Active cache & rate limiting backend",
    )

    # PostgreSQL Database Credentials
    DATABASE_HOST: str = Field(default="localhost", description="PostgreSQL host server")
    DATABASE_PORT: int = Field(default=5432, description="PostgreSQL port")
    DATABASE_NAME: str = Field(default="codepilot_db", description="Database name")
    DATABASE_USER: str = Field(default="postgres", description="Database username")
    DATABASE_PASSWORD: str = Field(default="postgres_password", description="Database password")
    DATABASE_URL: Optional[str] = Field(
        default=None,
        description="Explicit full connection URL (overrides individual credentials if provided)",
    )

    # JWT Authentication & OAuth2 Settings
    SECRET_KEY: str = Field(
        default="replace-this-with-a-very-secure-random-secret-key-in-production-min-32-chars",
        description="Cryptographic secret key for signing JWT tokens",
    )
    ALGORITHM: str = Field(
        default="HS256",
        description="JWT signing algorithm",
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30,
        description="Access token lifespan in minutes",
    )
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(
        default=7,
        description="Refresh token lifespan in days",
    )

    # Google Gemini AI Settings (Phase 6)
    GEMINI_API_KEY: Optional[str] = Field(
        default=None,
        description="Google Gemini API key for AI reasoning",
    )
    GEMINI_MODEL: str = Field(
        default="gemini-3.8-flash",
        description="Default Gemini model identifier",
    )
    AI_TIMEOUT_SECONDS: int = Field(
        default=60,
        description="Maximum execution timeout for AI requests in seconds",
    )
    AI_MAX_RETRIES: int = Field(
        default=3,
        description="Maximum retry attempts on transient network or rate-limit failures",
    )

    # Phase 10 — Redis, Caching, Rate Limiting & Monitoring
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0",
        description="Redis server connection string (redis://host:port/db)",
    )
    CACHE_TTL_SECONDS: int = Field(
        default=300,
        description="Default cache time-to-live in seconds",
    )
    RATE_LIMIT_PER_MINUTE: int = Field(
        default=60,
        description="Default client rate limit per minute",
    )
    API_KEY_HEADER: str = Field(
        default="X-API-Key",
        description="HTTP header name used for API Key authentication",
    )
    ENABLE_METRICS: bool = Field(
        default=True,
        description="Toggle Prometheus metrics collection across requests",
    )
    PROMETHEUS_ENABLED: bool = Field(
        default=True,
        description="Toggle /metrics endpoint export",
    )
    ENABLE_WEBHOOKS: bool = Field(
        default=True,
        description="Toggle outbound webhook dispatching",
    )
    WEBHOOK_SECRET: str = Field(
        default="codepilot-super-secret-webhook-key-32chars",
        description="HMAC secret used to cryptographically sign webhook payloads",
    )
    UPLOAD_DIR: str = Field(
        default="app/uploads/temp",
        description="Directory path for file uploads",
    )

    # Hindsight Agent Memory & Retrospective Learning Engine (25% Evaluation Requirement)
    HINDSIGHT_ENABLED: bool = Field(
        default=True,
        description="Toggle Hindsight semantic memory layer and retrospective learning",
    )
    HINDSIGHT_BASE_URL: str = Field(
        default="http://localhost:8888",
        description="Base URL for Hindsight client server or embedded fallback",
    )
    HINDSIGHT_BANK_ID: str = Field(
        default="codepilot-memory-bank",
        description="Default Hindsight memory bank identifier for code review learnings",
    )
    HINDSIGHT_AUTO_RECALL: bool = Field(
        default=True,
        description="Automatically recall relevant past conventions and bugs before AI review",
    )
    HINDSIGHT_AUTO_RETAIN: bool = Field(
        default=True,
        description="Automatically retain review observations and security findings into Hindsight memory",
    )
    HINDSIGHT_TOP_K: int = Field(
        default=5,
        description="Number of top relevant memories to recall per review request",
    )
    HINDSIGHT_MIN_CONFIDENCE: float = Field(
        default=0.2,
        description="Minimum similarity confidence threshold for recalled memories",
    )
    REPORTS_DIR: str = Field(
        default="app/reports",
        description="Directory path for generated review reports",
    )

    # Phase 12 — Deployment & Production Management
    ENABLE_DOCS: bool = Field(
        default=True,
        description="Toggle interactive API documentation (/docs and /redoc)",
    )
    CORS_ORIGINS: str = Field(
        default="http://localhost:3000,http://127.0.0.1:3000,http://localhost:5173,http://127.0.0.1:5173,http://localhost,http://127.0.0.1",
        description="Comma-separated list of allowed CORS origins",
    )
    UPLOAD_LIMIT_MB: int = Field(
        default=25,
        description="Maximum file upload limit in megabytes",
    )
    WORKERS: int = Field(
        default=2,
        description="Number of Gunicorn worker processes",
    )

    @property
    def cors_origins_list(self) -> list[str]:
        """Return CORS_ORIGINS parsed as a clean list of allowed origins."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


    @computed_field
    @property
    def ASYNC_DATABASE_URL(self) -> str:
        """Construct the asynchronous PostgreSQL connection URL for SQLAlchemy + asyncpg."""
        if self.DATABASE_URL:
            # If user provided a raw postgresql:// or postgresql+psycopg:// url, adapt it for asyncpg
            if self.DATABASE_URL.startswith("postgresql://"):
                return self.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
            return self.DATABASE_URL
        return (
            f"postgresql+asyncpg://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}@"
            f"{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
        )

    @computed_field
    @property
    def SYNC_DATABASE_URL(self) -> str:
        """Construct the synchronous PostgreSQL connection URL for Alembic migrations + psycopg."""
        if self.DATABASE_URL:
            if self.DATABASE_URL.startswith("postgresql+asyncpg://"):
                return self.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql+psycopg://", 1)
            if self.DATABASE_URL.startswith("postgresql://"):
                return self.DATABASE_URL.replace("postgresql://", "postgresql+psycopg://", 1)
            return self.DATABASE_URL
        return (
            f"postgresql+psycopg://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}@"
            f"{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
        )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """Return a cached singleton instance of Settings."""
    return Settings()


# Global settings instance for easy access across the project
settings = get_settings()
