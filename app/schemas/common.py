from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class RootResponse(BaseModel):
    """Schema for root welcome endpoint response."""

    message: str = Field(
        ...,
        description="Friendly greeting message",
        examples=["Welcome to the code-review-agent API"],
    )
    app_name: str = Field(
        ...,
        description="Name of the running application",
        examples=["code-review-agent"],
    )
    version: str = Field(
        ...,
        description="Current application version",
        examples=["0.1.0"],
    )
    docs_url: str = Field(
        ...,
        description="Path to interactive Swagger documentation",
        examples=["/docs"],
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "message": "Welcome to the code-review-agent API",
                "app_name": "code-review-agent",
                "version": "0.1.0",
                "docs_url": "/docs",
            }
        }
    }


class HealthResponse(BaseModel):
    """Schema for service health check response."""

    status: str = Field(
        default="ok",
        description="Operational health status of the service",
        examples=["ok"],
    )
    app_name: str = Field(
        ...,
        description="Name of the running application",
        examples=["code-review-agent"],
    )
    version: str = Field(
        ...,
        description="Current application version",
        examples=["0.1.0"],
    )
    environment: str = Field(
        ...,
        description="Current running environment (development/production)",
        examples=["development"],
    )
    uptime: Optional[str] = Field(
        default=None,
        description="Human-readable server uptime duration",
    )
    timestamp: Optional[str] = Field(
        default=None,
        description="ISO timestamp of health probe",
    )
    database: Optional[dict] = Field(
        default=None,
        description="PostgreSQL connectivity diagnostics",
    )
    redis: Optional[dict] = Field(
        default=None,
        description="Redis cache connectivity diagnostics",
    )
    gemini: Optional[dict] = Field(
        default=None,
        description="Google Gemini AI connectivity status",
    )
    storage: Optional[dict] = Field(
        default=None,
        description="Storage system disk capacity",
    )
    application: Optional[str] = Field(
        default=None,
        description="Standardized application identifier",
        examples=["code-review-agent"],
    )
    api_status: Optional[str] = Field(
        default=None,
        description="Operational API status string",
        examples=["ok"],
    )
    ai_provider: Optional[str] = Field(
        default=None,
        description="Active AI provider backend",
        examples=["Google Gemini (gemini-2.5-flash)"],
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "status": "ok",
                "api_status": "ok",
                "application": "code-review-agent",
                "app_name": "code-review-agent",
                "version": "1.0.0",
                "environment": "development",
                "ai_provider": "Google Gemini (gemini-2.5-flash)",
            }
        }
    }


class VersionResponse(BaseModel):
    """Schema for version information endpoint response."""

    app_name: str = Field(
        ...,
        description="Name of the application",
        examples=["code-review-agent"],
    )
    version: str = Field(
        ...,
        description="Semantic version string",
        examples=["0.1.0"],
    )
    api_prefix: str = Field(
        ...,
        description="Active API path prefix",
        examples=[""],
    )
    debug: bool = Field(
        ...,
        description="Whether debug mode is currently enabled",
        examples=[True],
    )
    build_commit: Optional[str] = Field(
        default=None,
        description="Git commit hash of the deployed release",
        examples=["935afac"],
    )
    build_timestamp: Optional[str] = Field(
        default=None,
        description="Timestamp when the release artifact was compiled",
        examples=["2026-09-28T14:00:00Z"],
    )
    ai_provider: Optional[str] = Field(
        default=None,
        description="Active AI reasoning backend",
        examples=["Google Gemini (gemini-2.5-flash)"],
    )
    database_provider: Optional[str] = Field(
        default=None,
        description="Active database engine",
        examples=["PostgreSQL 16 (asyncpg)"],
    )
    cache_provider: Optional[str] = Field(
        default=None,
        description="Active caching backend",
        examples=["Redis 7 (redis-py)"],
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "app_name": "code-review-agent",
                "version": "1.0.0",
                "api_prefix": "",
                "debug": True,
                "build_commit": "main-v1.0.0",
                "build_timestamp": "2026-09-28T14:00:00Z",
                "ai_provider": "Google Gemini (gemini-2.5-flash)",
                "database_provider": "PostgreSQL 16 (asyncpg)",
                "cache_provider": "Redis 7 (redis-py)",
            }
        }
    }


class ErrorResponse(BaseModel):
    """Unified schema for standardized error responses across the entire API."""

    success: bool = Field(
        default=False,
        description="Indicates operation failure",
        examples=[False],
    )
    message: str = Field(
        ...,
        description="Human-readable error explanation",
        examples=["The requested resource was not found."],
    )
    error_code: str = Field(
        ...,
        description="Machine-readable error classification code",
        examples=["NOT_FOUND"],
    )
    timestamp: str = Field(
        ...,
        description="ISO 8601 UTC timestamp of when the error occurred",
        examples=["2026-09-27T20:30:00Z"],
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "success": False,
                "message": "Resource not found",
                "error_code": "NOT_FOUND",
                "timestamp": "2026-09-27T20:30:00Z",
            }
        }
    }
