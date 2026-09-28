import time
from typing import Optional
import uuid
from fastapi import FastAPI, Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from app.core.logging import logger
from app.core.metrics import metrics_collector

MAX_REQUEST_BODY_BYTES = 50 * 1024 * 1024  # 50 MB limit


class SecurityAndTracingMiddleware(BaseHTTPMiddleware):
    """Middleware applying UUID request correlation tracing, security response headers,
    payload size guards, execution timing, and Prometheus request telemetry.
    """

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        start_time = time.perf_counter()

        # 1. Request ID Tracing: Propagate existing or mint a new UUID
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request.state.request_id = request_id

        # 2. Payload size validation for Content-Length
        content_length_header = request.headers.get("content-length")
        if content_length_header:
            try:
                content_length = int(content_length_header)
                if content_length > MAX_REQUEST_BODY_BYTES:
                    metrics_collector.record_error("payload_too_large", request.url.path)
                    return JSONResponse(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        content={
                            "success": False,
                            "error": "Payload Too Large",
                            "detail": f"Request body exceeds maximum allowed limit of {MAX_REQUEST_BODY_BYTES // (1024 * 1024)}MB.",
                        },
                        headers={"X-Request-ID": request_id},
                    )
            except ValueError:
                pass

        # 3. Process the HTTP pipeline
        try:
            response: Response = await call_next(request)
        except Exception as exc:
            duration = time.perf_counter() - start_time
            metrics_collector.record_request(request.method, request.url.path, 500, duration)
            metrics_collector.record_error("server_exception", request.url.path)
            raise exc

        execution_time = time.perf_counter() - start_time

        # 4. Attach Security & Diagnostic Headers
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = f"{execution_time:.6f}s"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdn.jsdelivr.net; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data: https:; "
            "connect-src 'self'"
        )
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        # 5. Record telemetry metrics
        metrics_collector.record_request(
            method=request.method,
            endpoint=request.url.path,
            status_code=response.status_code,
            duration_seconds=execution_time,
        )

        logger.info(
            "HTTP %s %s | Status: %d | Time: %.4fs | ReqID: %s",
            request.method,
            request.url.path,
            response.status_code,
            execution_time,
            request_id[:8],
        )

        return response


def register_middleware(app: FastAPI) -> None:
    """Register custom middlewares on the FastAPI instance."""
    app.add_middleware(SecurityAndTracingMiddleware)
