from collections import defaultdict
import time
from typing import Any, Dict

from app.core.config import settings
from app.core.logging import logger

try:
    from prometheus_client import (
        CONTENT_TYPE_LATEST,
        Counter,
        Gauge,
        Histogram,
        REGISTRY,
        generate_latest,
    )
    PROMETHEUS_AVAILABLE = True
except ImportError:
    CONTENT_TYPE_LATEST = "text/plain; version=0.0.4; charset=utf-8"
    PROMETHEUS_AVAILABLE = False
    Counter = None
    Gauge = None
    Histogram = None
    REGISTRY = None
    generate_latest = None


class MetricsCollector:
    """Collects and aggregates performance, throughput, error, and caching metrics."""

    def __init__(self):
        # Internal in-memory fallback counters
        self._counts: Dict[str, int] = defaultdict(int)
        self._timings: Dict[str, list] = defaultdict(list)

        if PROMETHEUS_AVAILABLE:
            # 1. HTTP Request Metrics
            self.http_requests_total = Counter(
                "codepilot_http_requests_total",
                "Total number of HTTP requests processed",
                ["method", "endpoint", "status"],
            )
            self.http_request_duration_seconds = Histogram(
                "codepilot_http_request_duration_seconds",
                "HTTP request latency in seconds",
                ["method", "endpoint"],
                buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
            )

            # 2. AI Operation Metrics
            self.ai_requests_total = Counter(
                "codepilot_ai_requests_total",
                "Total number of AI requests sent to Gemini/LLM",
                ["model", "operation", "status"],
            )

            # 3. Upload & Batch Metrics
            self.uploads_total = Counter(
                "codepilot_uploads_total",
                "Total files uploaded and validated",
                ["file_type", "status"],
            )
            self.batch_jobs_total = Counter(
                "codepilot_batch_jobs_total",
                "Total batch project scans and analyses executed",
                ["status"],
            )

            # 4. Error Metrics
            self.errors_total = Counter(
                "codepilot_errors_total",
                "Total unhandled or client/server errors encountered",
                ["error_type", "endpoint"],
            )

            # 5. Cache Metrics
            self.cache_hits_total = Counter(
                "codepilot_cache_hits_total",
                "Total number of cache read hits",
                ["namespace"],
            )
            self.cache_misses_total = Counter(
                "codepilot_cache_misses_total",
                "Total number of cache read misses",
                ["namespace"],
            )

    def record_request(self, method: str, endpoint: str, status_code: int, duration_seconds: float) -> None:
        """Record an inbound HTTP request completion."""
        self._counts["http_requests_total"] += 1
        status_key = f"http_status_{status_code}"
        self._counts[status_key] += 1
        self._timings[f"{method}_{endpoint}"].append(duration_seconds)
        if len(self._timings[f"{method}_{endpoint}"]) > 500:
            self._timings[f"{method}_{endpoint}"] = self._timings[f"{method}_{endpoint}"][-500:]

        if PROMETHEUS_AVAILABLE:
            try:
                self.http_requests_total.labels(
                    method=method,
                    endpoint=endpoint,
                    status=str(status_code),
                ).inc()
                self.http_request_duration_seconds.labels(
                    method=method,
                    endpoint=endpoint,
                ).observe(duration_seconds)
            except Exception:
                pass

    def record_ai_request(self, model: str, operation: str, status: str = "success") -> None:
        """Record an AI reasoning pipeline execution."""
        self._counts["ai_requests_total"] += 1
        self._counts[f"ai_status_{status}"] += 1
        if PROMETHEUS_AVAILABLE:
            try:
                self.ai_requests_total.labels(
                    model=model,
                    operation=operation,
                    status=status,
                ).inc()
            except Exception:
                pass

    def record_upload(self, file_type: str, status: str = "success") -> None:
        """Record a file upload event."""
        self._counts["uploads_total"] += 1
        self._counts[f"upload_{status}"] += 1
        if PROMETHEUS_AVAILABLE:
            try:
                self.uploads_total.labels(
                    file_type=file_type,
                    status=status,
                ).inc()
            except Exception:
                pass

    def record_batch_job(self, status: str) -> None:
        """Record a batch project analysis job."""
        self._counts["batch_jobs_total"] += 1
        if PROMETHEUS_AVAILABLE:
            try:
                self.batch_jobs_total.labels(status=status).inc()
            except Exception:
                pass

    def record_error(self, error_type: str, endpoint: str) -> None:
        """Record an error encounter."""
        self._counts["errors_total"] += 1
        self._counts[f"error_{error_type}"] += 1
        if PROMETHEUS_AVAILABLE:
            try:
                self.errors_total.labels(
                    error_type=error_type,
                    endpoint=endpoint,
                ).inc()
            except Exception:
                pass

    def record_cache_hit(self, namespace: str = "general") -> None:
        """Record a cache read hit."""
        self._counts["cache_hits_total"] += 1
        self._counts[f"cache_hit_{namespace}"] += 1
        if PROMETHEUS_AVAILABLE:
            try:
                self.cache_hits_total.labels(namespace=namespace).inc()
            except Exception:
                pass

    def record_cache_miss(self, namespace: str = "general") -> None:
        """Record a cache read miss."""
        self._counts["cache_misses_total"] += 1
        self._counts[f"cache_miss_{namespace}"] += 1
        if PROMETHEUS_AVAILABLE:
            try:
                self.cache_misses_total.labels(namespace=namespace).inc()
            except Exception:
                pass

    def generate_prometheus_export(self) -> bytes:
        """Generate official Prometheus text scrape response."""
        if PROMETHEUS_AVAILABLE and generate_latest is not None:
            return generate_latest(REGISTRY)
        
        # Simple plain-text fallback formatting
        lines = ["# HELP codepilot_metrics CodePilot in-memory metrics fallback"]
        for key, val in self._counts.items():
            lines.append(f"codepilot_{key} {val}")
        return "\n".join(lines).encode("utf-8")

    def get_application_metrics_summary(self) -> Dict[str, Any]:
        """Return structured dictionary of application execution metrics."""
        total_requests = self._counts.get("http_requests_total", 0)
        total_errors = self._counts.get("errors_total", 0)
        error_rate = round((total_errors / max(total_requests, 1)) * 100, 2)
        return {
            "total_requests": total_requests,
            "total_errors": total_errors,
            "error_rate_percentage": error_rate,
            "status_2xx": sum(v for k, v in self._counts.items() if k.startswith("http_status_2")),
            "status_4xx": sum(v for k, v in self._counts.items() if k.startswith("http_status_4")),
            "status_5xx": sum(v for k, v in self._counts.items() if k.startswith("http_status_5")),
        }

    def get_cache_metrics_summary(self) -> Dict[str, Any]:
        """Return structured dictionary of caching throughput and hit rates."""
        hits = self._counts.get("cache_hits_total", 0)
        misses = self._counts.get("cache_misses_total", 0)
        total_lookups = hits + misses
        hit_ratio = round((hits / max(total_lookups, 1)) * 100, 2)
        return {
            "total_lookups": total_lookups,
            "cache_hits": hits,
            "cache_misses": misses,
            "hit_ratio_percentage": hit_ratio,
        }

    def get_ai_metrics_summary(self) -> Dict[str, Any]:
        """Return structured dictionary of AI LLM requests and outcomes."""
        total_ai = self._counts.get("ai_requests_total", 0)
        ai_success = self._counts.get("ai_status_success", 0)
        ai_failure = self._counts.get("ai_status_failure", 0)
        return {
            "total_ai_requests": total_ai,
            "successful_requests": ai_success,
            "failed_requests": ai_failure,
            "success_rate_percentage": round((ai_success / max(total_ai, 1)) * 100, 2),
        }

    def get_uploads_metrics_summary(self) -> Dict[str, Any]:
        """Return structured dictionary of uploads and batch jobs."""
        return {
            "total_uploads": self._counts.get("uploads_total", 0),
            "total_batch_jobs": self._counts.get("batch_jobs_total", 0),
            "successful_uploads": self._counts.get("upload_success", 0),
            "failed_uploads": self._counts.get("upload_failure", 0),
        }


metrics_collector = MetricsCollector()
