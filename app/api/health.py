from fastapi import APIRouter
from app.core.config import settings
from app.schemas.common import HealthResponse, RootResponse

# APIRouter instance for general health and status endpoints
router = APIRouter(tags=["Health & Status"])


@router.get(
    "/",
    response_model=RootResponse,
    summary="Root Welcome Endpoint",
    description="Provides basic service identification, current version, and links to documentation.",
)
async def root() -> RootResponse:
    """Return greeting message and basic application metadata."""
    return RootResponse(
        message="Welcome to the code-review-agent API",
        app_name=settings.APP_NAME,
        version=settings.APP_VERSION,
        docs_url="/docs",
    )


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health Check Endpoint",
    description="Validates that the API service is alive, responsive, and reports subsystem diagnostics.",
)
async def health_check() -> HealthResponse:
    """Return operational health status for monitoring and uptime probes."""
    from datetime import datetime, timezone
    from app.core.monitoring import system_monitor

    db_res = await system_monitor.check_database_health()
    redis_res = await system_monitor.check_redis_health()
    gemini_res = system_monitor.check_gemini_health()
    storage_res = system_monitor.check_storage_health()

    status_str = "ok"
    if db_res["status"] != "healthy":
        status_str = "unhealthy"
    elif redis_res["status"] == "degraded" or storage_res.get("status") == "warning_low_disk":
        status_str = "degraded"

    return HealthResponse(
        status=status_str,
        app_name=settings.APP_NAME,
        version=settings.APP_VERSION,
        environment="development" if settings.DEBUG else "production",
        uptime=system_monitor.get_uptime_human(),
        timestamp=datetime.now(timezone.utc).isoformat(),
        database=db_res,
        redis=redis_res,
        gemini=gemini_res,
        storage=storage_res,
    )

