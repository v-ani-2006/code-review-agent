"""Reusable testing utilities, assertion helpers, and benchmarking tools."""
import asyncio
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
import time
from typing import Any, Callable, Dict, List, Optional
import uuid
from jose import jwt

from app.core.config import settings


def create_test_jwt(
    user_id: Optional[uuid.UUID] = None,
    username: str = "testuser",
    email: str = "test@example.com",
    is_admin: bool = False,
    token_type: str = "access",
    expires_in_minutes: int = 60,
) -> str:
    """Generate a valid test JWT with specified claims."""
    uid = str(user_id or uuid.uuid4())
    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_in_minutes)
    claims = {
        "sub": uid,
        "user_id": uid,
        "username": username,
        "email": email,
        "is_admin": is_admin,
        "type": token_type,
        "exp": expire,
    }
    return jwt.encode(claims, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_expired_jwt(
    user_id: Optional[uuid.UUID] = None,
    username: str = "testuser",
) -> str:
    """Generate an expired test JWT."""
    return create_test_jwt(user_id=user_id, username=username, expires_in_minutes=-10)


def assert_error_response(
    response_json: Dict[str, Any],
    expected_status: int,
    keyword: Optional[str] = None,
) -> None:
    """Assert structured JSON error format conforms to platform standard."""
    assert "detail" in response_json or "error" in response_json or "message" in response_json
    detail = str(response_json.get("detail") or response_json.get("error") or response_json.get("message"))
    if keyword:
        assert keyword.lower() in detail.lower(), f"Expected '{keyword}' in '{detail}'"


@contextmanager
def measure_duration():
    """Context manager measuring execution duration in seconds."""
    state = {"duration": 0.0}
    start = time.perf_counter()
    try:
        yield state
    finally:
        state["duration"] = round(time.perf_counter() - start, 5)


async def execute_concurrent(
    async_fn: Callable[[], Any],
    concurrency: int = 10,
) -> List[Any]:
    """Execute an asynchronous callable concurrently across multiple tasks."""
    tasks = [async_fn() for _ in range(concurrency)]
    return await asyncio.gather(*tasks, return_exceptions=True)
