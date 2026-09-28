import asyncio
from datetime import datetime, timezone
import json
from typing import Any, Dict, List, Optional
from app.core.config import settings
from app.core.logging import logger

try:
    import redis.asyncio as aioredis
    from redis.exceptions import ConnectionError as RedisConnectionError, RedisError
    REDIS_MODULE_AVAILABLE = True
except ImportError:
    aioredis = None
    RedisConnectionError = Exception
    RedisError = Exception
    REDIS_MODULE_AVAILABLE = False


class InMemoryCacheFallback:
    """Thread-safe in-memory cache fallback used when Redis server is offline or not installed."""

    def __init__(self):
        self._store: Dict[str, Dict[str, Any]] = {}
        self._lock = asyncio.Lock()

    async def get(self, key: str) -> Optional[str]:
        async with self._lock:
            entry = self._store.get(key)
            if not entry:
                return None
            expires_at = entry.get("expires_at")
            if expires_at and datetime.now(timezone.utc).timestamp() > expires_at:
                del self._store[key]
                return None
            return entry.get("value")

    async def set(self, key: str, value: str, ex: Optional[int] = None) -> bool:
        async with self._lock:
            expires_at = None
            if ex:
                expires_at = datetime.now(timezone.utc).timestamp() + ex
            self._store[key] = {"value": value, "expires_at": expires_at}
            return True

    async def delete(self, *keys: str) -> int:
        async with self._lock:
            count = 0
            for k in keys:
                if k in self._store:
                    del self._store[k]
                    count += 1
            return count

    async def exists(self, key: str) -> int:
        val = await self.get(key)
        return 1 if val is not None else 0

    async def scan_iter(self, match: str = "*"):
        import fnmatch
        async with self._lock:
            matched_keys = [k for k in self._store.keys() if fnmatch.fnmatch(k, match)]
        for k in matched_keys:
            yield k

    async def flushdb(self) -> bool:
        async with self._lock:
            self._store.clear()
            return True

    async def ping(self) -> bool:
        return True


class RedisClientManager:
    """Manages asynchronous Redis connection lifecycle with seamless in-memory fallback."""

    def __init__(self):
        self.client = None
        self.fallback = InMemoryCacheFallback()
        self.is_connected = False
        self._connect_lock = asyncio.Lock()

    async def init_redis(self) -> None:
        """Initialize connection to Redis with graceful failure handling."""
        if not REDIS_MODULE_AVAILABLE:
            logger.info("📦 redis-py library not installed; operating in memory-cache fallback mode.")
            self.client = self.fallback
            self.is_connected = False
            return

        try:
            self.client = aioredis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                socket_timeout=2.0,
                socket_connect_timeout=2.0,
            )
            await asyncio.wait_for(self.client.ping(), timeout=2.0)
            self.is_connected = True
            logger.info(" Connected to Redis cache service at %s", settings.REDIS_URL)
        except Exception as exc:
            logger.warning(
                "⚠️ Redis server connection unreachable at %s (%s). Engaging high-performance in-memory cache fallback.",
                settings.REDIS_URL,
                str(exc),
            )
            self.client = self.fallback
            self.is_connected = False

    async def close_redis(self) -> None:
        """Gracefully release Redis connections on application shutdown."""
        if self.client and hasattr(self.client, "aclose") and self.is_connected:
            try:
                await self.client.aclose()
                logger.info("🛑 Redis connection pool closed gracefully.")
            except Exception as exc:
                logger.warning("Error closing Redis client: %s", str(exc))
        self.is_connected = False

    def get_client(self):
        """Return the active Redis client or in-memory fallback instance."""
        if self.client is None:
            return self.fallback
        return self.client

    async def ping(self) -> bool:
        """Check cache backend responsiveness."""
        if self.client is None:
            return False
        try:
            await self.client.ping()
            return True
        except Exception:
            return False


redis_manager = RedisClientManager()


def get_cache_backend():
    """FastAPI dependency for accessing the cache client."""
    return redis_manager.get_client()
