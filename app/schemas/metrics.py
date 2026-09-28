from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class ApplicationMetricsResponse(BaseModel):
    """Aggregate HTTP application traffic and error rate telemetry."""

    success: bool = True
    total_requests: int
    total_errors: int
    error_rate_percentage: float
    status_2xx: int
    status_4xx: int
    status_5xx: int


class CacheMetricsResponse(BaseModel):
    """Cache efficiency, volume, and hit-ratio telemetry."""

    success: bool = True
    total_lookups: int
    cache_hits: int
    cache_misses: int
    hit_ratio_percentage: float


class AIMetricsResponse(BaseModel):
    """Google Gemini AI pipeline call volume and reliability telemetry."""

    success: bool = True
    total_ai_requests: int
    successful_requests: int
    failed_requests: int
    success_rate_percentage: float


class UploadMetricsResponse(BaseModel):
    """File upload processing and batch pipeline throughput telemetry."""

    success: bool = True
    total_uploads: int
    total_batch_jobs: int
    successful_uploads: int
    failed_uploads: int
