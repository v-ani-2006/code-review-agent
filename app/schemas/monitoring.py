from datetime import datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class ServiceHealth(BaseModel):
    """Health indicator for an individual integrated subsystem."""

    status: str
    connected: bool
    latency_ms: Optional[float] = None
    details: Optional[Dict[str, Any]] = None


class SystemInfo(BaseModel):
    """Host hardware and runtime environment telemetry."""

    os: str
    os_release: str
    python_version: str
    architecture: str
    cpu_cores: int


class HealthSummaryResponse(BaseModel):
    """Full operational health report across all subsystems."""

    status: str
    app_name: str
    version: str
    environment: str
    uptime_seconds: float
    uptime_human: str
    timestamp: datetime
    services: Dict[str, Any]
    system: Dict[str, Any]
    application: Optional[Dict[str, Any]] = None



class UptimeResponse(BaseModel):
    """Service uptime status metrics."""

    success: bool = True
    uptime_seconds: float
    uptime_human: str
    server_start_time: float


class CacheStatusResponse(BaseModel):
    """Real-time cache subsystem status."""

    success: bool = True
    status: str
    connected: bool
    mode: str
    latency_ms: float
    url: Optional[str] = None


class DatabaseStatusResponse(BaseModel):
    """Real-time database connectivity status."""

    success: bool = True
    status: str
    connected: bool
    latency_ms: float
    host: str
    database: str
