import time
from typing import Any, Dict
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.monitoring import system_monitor
from app.models.task import Task
from app.models.upload import Upload
from app.models.webhook import Webhook
from app.schemas.monitoring import (
    CacheStatusResponse,
    DatabaseStatusResponse,
    HealthSummaryResponse,
    UptimeResponse,
)


class MonitoringService:
    """Service aggregating infrastructure diagnostics, subsystem health checks, and runtime telemetry."""

    async def get_health_summary(self) -> HealthSummaryResponse:
        """Fetch comprehensive health report combining all subsystem diagnostics."""
        report = await system_monitor.get_full_health_report()
        return HealthSummaryResponse(**report)

    async def get_uptime(self) -> UptimeResponse:
        """Fetch server uptime metrics."""
        return UptimeResponse(
            uptime_seconds=round(system_monitor.get_uptime_seconds(), 2),
            uptime_human=system_monitor.get_uptime_human(),
            server_start_time=time.time() - system_monitor.get_uptime_seconds(),
        )

    async def get_cache_status(self) -> CacheStatusResponse:
        """Fetch cache connectivity status and latency."""
        res = await system_monitor.check_redis_health()
        return CacheStatusResponse(
            status=res["status"],
            connected=res["connected"],
            mode=res.get("mode", "redis"),
            latency_ms=res.get("latency_ms", 0.0),
            url=res.get("url"),
        )

    async def get_database_status(self) -> DatabaseStatusResponse:
        """Fetch live PostgreSQL connectivity status and latency."""
        res = await system_monitor.check_database_health()
        return DatabaseStatusResponse(
            status=res["status"],
            connected=res["connected"],
            latency_ms=res.get("latency_ms", 0.0),
            host=res["host"],
            database=res["database"],
        )

    async def get_services_status(self) -> Dict[str, Any]:
        """Aggregate health status of all dependent services."""
        db_res = await system_monitor.check_database_health()
        redis_res = await system_monitor.check_redis_health()
        gemini_res = system_monitor.check_gemini_health()
        storage_res = system_monitor.check_storage_health()
        return {
            "database": db_res,
            "redis": redis_res,
            "gemini": gemini_res,
            "storage": storage_res,
        }

    async def get_webhooks_status(self, db: AsyncSession) -> Dict[str, Any]:
        """Query statistics on registered webhooks, active count, and failed delivery counters."""
        total = (await db.execute(select(func.count(Webhook.id)))).scalar() or 0
        active = (
            await db.execute(select(func.count(Webhook.id)).where(Webhook.is_active == True))
        ).scalar() or 0
        failed = (
            await db.execute(select(func.count(Webhook.id)).where(Webhook.failure_count > 0))
        ).scalar() or 0

        return {
            "total_webhooks": total,
            "active_webhooks": active,
            "failing_webhooks": failed,
        }

    async def get_system_overview(self, db: AsyncSession) -> Dict[str, Any]:
        """Admin overview of active tasks, uploads, and system health."""
        tasks_count = (await db.execute(select(func.count(Task.id)))).scalar() or 0
        uploads_count = (await db.execute(select(func.count(Upload.id)))).scalar() or 0
        health = await system_monitor.get_full_health_report()
        return {
            "health": health,
            "total_tasks_recorded": tasks_count,
            "total_uploads_recorded": uploads_count,
        }


monitoring_service = MonitoringService()
