"""Unit tests for CacheService, JSON serialization, and fallback behavior."""
import uuid
import pytest
from unittest.mock import AsyncMock, patch

from app.core.cache import redis_manager
from app.services.cache_service import cache_service


@pytest.mark.unit
async def test_cache_set_and_get():
    """Test standard cache key set, retention, and retrieval."""
    test_key = f"test_key_{uuid.uuid4().hex}"
    test_payload = {"user_id": 123, "active": True, "roles": ["developer", "reviewer"]}

    success = await cache_service.set(test_key, test_payload, ttl=60)
    assert success is True

    cached_val = await cache_service.get(test_key)
    assert cached_val is not None
    assert cached_val["user_id"] == 123
    assert cached_val["roles"] == ["developer", "reviewer"]


@pytest.mark.unit
async def test_cache_miss():
    """Test that querying a non-existent key returns None without error."""
    missing_key = f"missing_{uuid.uuid4().hex}"
    cached_val = await cache_service.get(missing_key)
    assert cached_val is None


@pytest.mark.unit
async def test_cache_delete():
    """Test explicit key eviction."""
    test_key = f"delete_test_{uuid.uuid4().hex}"
    await cache_service.set(test_key, "temp_value", ttl=60)

    assert await cache_service.get(test_key) == "temp_value"

    await cache_service.delete(test_key)
    assert await cache_service.get(test_key) is None


@pytest.mark.unit
async def test_cache_invalidation_helpers():
    """Test invalidate_review and invalidate_user helper functions."""
    uid = uuid.uuid4()
    rid = uuid.uuid4()

    await cache_service.set(f"review:{rid}", {"id": str(rid)}, ttl=60)
    await cache_service.set(f"dashboard:{uid}", {"overview": 1}, ttl=60)

    await cache_service.invalidate_review(rid, uid)
    assert await cache_service.get(f"review:{rid}") is None
    assert await cache_service.get(f"dashboard:{uid}") is None


@pytest.mark.unit
async def test_cache_redis_error_resilience():
    """Test that Redis read errors are caught gracefully and return None."""
    from unittest.mock import AsyncMock
    client = redis_manager.get_client()
    original_get = client.get
    client.get = AsyncMock(side_effect=ConnectionError("Redis offline"))
    try:
        result = await cache_service.get("any_key")
        assert result is None
    finally:
        client.get = original_get

