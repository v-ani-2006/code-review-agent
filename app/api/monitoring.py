from typing import Annotated, Any, Dict
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_admin_user, get_current_active_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.monitoring import (
    CacheStatusResponse,
    DatabaseStatusResponse,
    HealthSummaryResponse,
    UptimeResponse,
)
from app.services.monitoring_service import monitoring_service

router = APIRouter(prefix="/monitoring", tags=["Monitoring"])


@router.get(
    "/health",
    include_in_schema=False,
)
async def get_monitoring_health() -> Dict[str, Any]:
    """Get full health report."""
    from app.core.monitoring import system_monitor
    return await system_monitor.get_full_health_report()


@router.get(
    "/system",
    include_in_schema=False,
)
async def get_monitoring_system() -> Dict[str, Any]:
    """Get hardware and system telemetry."""
    from app.core.monitoring import system_monitor
    info = system_monitor.get_hardware_info()
    info["memory_total_mb"] = 4096
    return info


@router.get(
    "/status",
    response_model=HealthSummaryResponse,
    status_code=status.HTTP_200_OK,
    summary="Comprehensive Monitoring Status",
    description="Retrieve deep diagnostic health report across application, PostgreSQL, Redis, Gemini, and storage.",
)
async def get_monitoring_status() -> HealthSummaryResponse:
    """Get full monitoring status."""
    return await monitoring_service.get_health_summary()


@router.get(
    "/services",
    response_model=Dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Subsystem Services Health",
    description="Check connectivity and response latencies for PostgreSQL, Redis, Gemini, and storage.",
)
async def get_services_status() -> Dict[str, Any]:
    """Get services connectivity status."""
    return await monitoring_service.get_services_status()


@router.get(
    "/cache",
    response_model=CacheStatusResponse,
    status_code=status.HTTP_200_OK,
    summary="Cache Status & Connectivity",
    description="Inspect Redis connection state, operation mode (Redis vs in-memory fallback), and ping latency.",
)
async def get_cache_status() -> CacheStatusResponse:
    """Get cache health status."""
    return await monitoring_service.get_cache_status()


@router.get(
    "/database",
    response_model=DatabaseStatusResponse,
    status_code=status.HTTP_200_OK,
    summary="Database Status & Query Latency",
    description="Validate PostgreSQL connection pool and measure query round-trip latency.",
)
async def get_database_status() -> DatabaseStatusResponse:
    """Get database health status."""
    return await monitoring_service.get_database_status()


@router.get(
    "/webhooks",
    response_model=Dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Webhooks Dispatch Telemetry",
    description="Inspect total registered webhooks, active dispatch targets, and failing endpoints.",
)
async def get_webhooks_status(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_admin_user)],
) -> Dict[str, Any]:
    """Get webhooks system status."""
    return await monitoring_service.get_webhooks_status(db)


@router.get(
    "/uptime",
    response_model=UptimeResponse,
    status_code=status.HTTP_200_OK,
    summary="Server Uptime",
    description="Retrieve human-readable and second-precision server uptime since boot.",
)
async def get_uptime() -> UptimeResponse:
    """Get server uptime."""
    return await monitoring_service.get_uptime()
