from fastapi import APIRouter, Response, status

from app.core.metrics import CONTENT_TYPE_LATEST, metrics_collector
from app.schemas.metrics import (
    AIMetricsResponse,
    ApplicationMetricsResponse,
    CacheMetricsResponse,
    UploadMetricsResponse,
)

router = APIRouter(prefix="/metrics", tags=["Metrics"])


@router.get(
    "",
    summary="Prometheus Metrics Scrape Endpoint",
    description="Export metrics in standard Prometheus text format for Prometheus/Grafana scrapers.",
    response_class=Response,
)
async def get_prometheus_metrics() -> Response:
    """Export Prometheus text formatted metrics."""
    data = metrics_collector.generate_prometheus_export()
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)


@router.get(
    "/application",
    response_model=ApplicationMetricsResponse,
    status_code=status.HTTP_200_OK,
    summary="Application Traffic & Error Metrics",
    description="Retrieve HTTP request counts, response code distributions, and error rates.",
)
async def get_application_metrics() -> ApplicationMetricsResponse:
    """Get application traffic telemetry."""
    data = metrics_collector.get_application_metrics_summary()
    return ApplicationMetricsResponse(**data)


@router.get(
    "/cache",
    response_model=CacheMetricsResponse,
    status_code=status.HTTP_200_OK,
    summary="Cache Hit-Rate & Lookups Metrics",
    description="Retrieve total cache lookups, hit count, miss count, and hit ratio percentage.",
)
async def get_cache_metrics() -> CacheMetricsResponse:
    """Get cache efficiency telemetry."""
    data = metrics_collector.get_cache_metrics_summary()
    return CacheMetricsResponse(**data)


@router.get(
    "/ai",
    response_model=AIMetricsResponse,
    status_code=status.HTTP_200_OK,
    summary="AI Provider Telemetry",
    description="Retrieve total Gemini AI calls, success rate, and failure rate.",
)
async def get_ai_metrics() -> AIMetricsResponse:
    """Get AI pipeline telemetry."""
    data = metrics_collector.get_ai_metrics_summary()
    return AIMetricsResponse(**data)


@router.get(
    "/uploads",
    response_model=UploadMetricsResponse,
    status_code=status.HTTP_200_OK,
    summary="Upload & Batch Pipeline Metrics",
    description="Retrieve counts of single-file uploads, multi-file batches, and background analysis executions.",
)
async def get_uploads_metrics() -> UploadMetricsResponse:
    """Get uploads telemetry."""
    data = metrics_collector.get_uploads_metrics_summary()
    return UploadMetricsResponse(**data)
