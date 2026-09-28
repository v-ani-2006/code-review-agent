import asyncio
from datetime import datetime, timezone
import os
from pathlib import Path
import platform
import shutil
import time
from typing import Any, Dict
from sqlalchemy import text

from app.core.cache import redis_manager
from app.core.config import settings
from app.core.logging import logger
from app.db.session import engine

# Service process start timestamp
SERVER_START_TIME = time.time()


class SystemMonitor:
    """Collects and aggregates real-time infrastructure, connectivity, and hardware diagnostics."""

    @staticmethod
    def get_uptime_seconds() -> float:
        """Calculate server uptime in seconds."""
        return time.time() - SERVER_START_TIME

    @staticmethod
    def get_uptime_human() -> str:
        """Format server uptime into human-readable duration."""
        seconds = int(SystemMonitor.get_uptime_seconds())
        days, remainder = divmod(seconds, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, secs = divmod(remainder, 60)
        parts = []
        if days > 0:
            parts.append(f"{days}d")
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0:
            parts.append(f"{minutes}m")
        parts.append(f"{secs}s")
        return " ".join(parts)

    @staticmethod
    async def check_database_health() -> Dict[str, Any]:
        """Validate live PostgreSQL connectivity and measure query ping latency."""
        start = time.perf_counter()
        try:
            async with engine.connect() as conn:
                await asyncio.wait_for(conn.execute(text("SELECT 1")), timeout=3.0)
            latency_ms = round((time.perf_counter() - start) * 1000, 2)
            return {
                "status": "healthy",
                "connected": True,
                "latency_ms": latency_ms,
                "host": settings.DATABASE_HOST,
                "database": settings.DATABASE_NAME,
            }
        except Exception as exc:
            return {
                "status": "unhealthy",
                "connected": False,
                "error": str(exc),
                "host": settings.DATABASE_HOST,
                "database": settings.DATABASE_NAME,
            }

    @staticmethod
    async def check_redis_health() -> Dict[str, Any]:
        """Validate Redis cache server connectivity and ping latency."""
        start = time.perf_counter()
        try:
            is_alive = await asyncio.wait_for(redis_manager.ping(), timeout=2.0)
            latency_ms = round((time.perf_counter() - start) * 1000, 2)
            backend_mode = "redis" if redis_manager.is_connected else "in_memory_fallback"
            return {
                "status": "healthy" if is_alive else "degraded",
                "connected": redis_manager.is_connected,
                "mode": backend_mode,
                "latency_ms": latency_ms if redis_manager.is_connected else 0.0,
                "url": settings.REDIS_URL,
            }
        except Exception as exc:
            return {
                "status": "degraded",
                "connected": False,
                "mode": "in_memory_fallback",
                "error": str(exc),
            }

    @staticmethod
    def check_gemini_health() -> Dict[str, Any]:
        """Validate Gemini AI provider configuration and readiness."""
        has_key = bool(settings.GEMINI_API_KEY and len(settings.GEMINI_API_KEY.strip()) > 5)
        return {
            "status": "configured" if has_key else "unconfigured",
            "model": settings.GEMINI_MODEL,
            "has_api_key": has_key,
            "timeout_seconds": settings.AI_TIMEOUT_SECONDS,
        }

    @staticmethod
    def check_storage_health() -> Dict[str, Any]:
        """Inspect storage volumes and ensure temp/upload directories exist and have capacity."""
        upload_path = Path("app/uploads")
        try:
            upload_path.mkdir(parents=True, exist_ok=True)
            total, used, free = shutil.disk_usage(upload_path.resolve())
            free_gb = round(free / (1024**3), 2)
            total_gb = round(total / (1024**3), 2)
            return {
                "status": "healthy" if free_gb > 1.0 else "warning_low_disk",
                "writable": os.access(upload_path, os.W_OK),
                "free_gb": free_gb,
                "total_gb": total_gb,
                "storage_dir": str(upload_path.resolve()),
            }
        except Exception as exc:
            return {
                "status": "error",
                "writable": False,
                "error": str(exc),
            }

    @staticmethod
    def get_hardware_info() -> Dict[str, Any]:
        """Return system and hardware diagnostics."""
        return {
            "os": platform.system(),
            "os_release": platform.release(),
            "python_version": platform.python_version(),
            "architecture": platform.machine(),
            "cpu_cores": os.cpu_count() or 1,
        }

    @classmethod
    async def get_full_health_report(cls) -> Dict[str, Any]:
        """Generate comprehensive health report combining all subsystem diagnostics."""
        db_res = await cls.check_database_health()
        redis_res = await cls.check_redis_health()
        gemini_res = cls.check_gemini_health()
        storage_res = cls.check_storage_health()

        overall_status = "healthy"
        if db_res["status"] != "healthy":
            overall_status = "unhealthy"
        elif redis_res["status"] == "degraded" or storage_res.get("status") == "warning_low_disk":
            overall_status = "degraded"

        return {
            "status": overall_status,
            "app_name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "environment": "development" if settings.DEBUG else "production",
            "uptime_seconds": round(cls.get_uptime_seconds(), 2),
            "uptime_human": cls.get_uptime_human(),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "services": {
                "database": db_res,
                "redis": redis_res,
                "gemini": gemini_res,
                "storage": storage_res,
            },
            "system": cls.get_hardware_info(),
            "application": {
                "name": settings.APP_NAME,
                "version": settings.APP_VERSION,
                "environment": "development" if settings.DEBUG else "production",
            },
        }



system_monitor = SystemMonitor()
