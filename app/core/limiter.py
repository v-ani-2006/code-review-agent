import math
import time
from typing import Callable, Optional
from fastapi import HTTPException, Request, Response, status
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.core.logging import logger

try:
    from slowapi import Limiter, _rate_limit_exceeded_handler
    from slowapi.errors import RateLimitExceeded
    from slowapi.util import get_remote_address
    SLOWAPI_AVAILABLE = True
except ImportError:
    Limiter = None
    _rate_limit_exceeded_handler = None
    RateLimitExceeded = Exception
    get_remote_address = None
    SLOWAPI_AVAILABLE = False


def get_client_identifier(request: Request) -> str:
    """Extract client rate-limiting identifier from API key, Authorization header, or remote IP address."""
    # 1. API Key Header
    api_key = request.headers.get(settings.API_KEY_HEADER)
    if api_key:
        return f"apikey:{api_key[:12]}"

    # 2. Authorization Bearer Token
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ", 1)[1]
        return f"token:{token[:16]}"

    # 3. Client IP Address
    if request.client and request.client.host:
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return f"ip:{forwarded.split(',')[0].strip()}"
        return f"ip:{request.client.host}"

    return "ip:anonymous"


class FallbackLimiter:
    """Pass-through limiter when slowapi is not installed."""

    def __init__(self, key_func: Callable):
        self.key_func = key_func

    def limit(self, limit_value: str):
        def decorator(func: Callable):
            return func
        return decorator


def _get_limiter_storage() -> str:
    """Detect if Redis is actively reachable; otherwise fall back to memory storage."""
    import os
    import sys
    if "pytest" in sys.modules or os.environ.get("PYTEST_CURRENT_TEST") or os.environ.get("TESTING") == "true":
        return "memory://"

    redis_url = settings.REDIS_URL
    if not redis_url or not redis_url.startswith("redis"):
        return "memory://"
    try:
        import socket
        from urllib.parse import urlparse
        parsed = urlparse(redis_url)
        host = parsed.hostname or "localhost"
        port = parsed.port or 6379
        with socket.create_connection((host, port), timeout=0.3):
            return redis_url
    except Exception:
        logger.info("[INFO] Redis offline for rate limiter; using high-performance in-memory limiter.")
        return "memory://"



if SLOWAPI_AVAILABLE:
    limiter = Limiter(
        key_func=get_client_identifier,
        default_limits=[f"{settings.RATE_LIMIT_PER_MINUTE}/minute"],
        storage_uri=_get_limiter_storage(),
    )
else:
    limiter = FallbackLimiter(key_func=get_client_identifier)


def custom_rate_limit_exceeded_handler(request: Request, exc: Exception) -> Response:
    """Return standard HTTP 429 response with Retry-After header and structured JSON error."""
    retry_after = getattr(exc, "retry_after", 60)
    if isinstance(retry_after, (int, float)):
        retry_after_sec = math.ceil(retry_after)
    else:
        retry_after_sec = 60

    method = request.scope.get("method", "GET") if hasattr(request, "scope") and isinstance(request.scope, dict) else "GET"
    path = request.scope.get("path", "/") if hasattr(request, "scope") and isinstance(request.scope, dict) else "/"

    logger.warning(
        "🚫 Rate limit exceeded for client '%s' on %s %s. Retry after %ds",
        get_client_identifier(request),
        method,
        path,
        retry_after_sec,
    )

    response = JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={
            "success": False,
            "error": "Rate limit exceeded. Please wait before retrying.",
            "retry_after": retry_after_sec,
            "detail": f"Too many requests. Quota limit exceeded for {get_client_identifier(request)}.",
        },
        headers={
            "Retry-After": str(retry_after_sec),
            "X-RateLimit-Reset": str(int(time.time() + retry_after_sec)),
        },
    )
    return response
