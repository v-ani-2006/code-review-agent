import json
from typing import Any, Dict, List, Optional, Union
import uuid

from app.core.cache import redis_manager
from app.core.config import settings
from app.core.logging import logger
from app.core.metrics import metrics_collector


class CacheService:
    """Enterprise caching service supporting Redis with automatic JSON serialization and in-memory fallback."""

    def __init__(self):
        self.default_ttl = settings.CACHE_TTL_SECONDS

    async def get(self, key: str, namespace: str = "general") -> Optional[Any]:
        """Fetch and deserialize a cached object by key."""
        client = redis_manager.get_client()
        try:
            raw_value = await client.get(key)
            if raw_value is None:
                metrics_collector.record_cache_miss(namespace)
                return None

            metrics_collector.record_cache_hit(namespace)
            try:
                return json.loads(raw_value)
            except Exception:
                return raw_value
        except Exception as exc:
            logger.warning("Cache GET failed for key '%s': %s", key, str(exc))
            metrics_collector.record_cache_miss(namespace)
            return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        namespace: str = "general",
    ) -> bool:
        """Serialize and store an object in cache with expiration."""
        client = redis_manager.get_client()
        expire = ttl if ttl is not None else self.default_ttl
        try:
            if isinstance(value, (dict, list, bool, int, float)) or hasattr(value, "model_dump"):
                if hasattr(value, "model_dump"):
                    payload = json.dumps(value.model_dump(mode="json"), default=str)
                else:
                    payload = json.dumps(value, default=str)
            elif isinstance(value, str):
                payload = value
            else:
                payload = json.dumps(value, default=str)

            await client.set(key, payload, ex=expire)
            return True
        except Exception as exc:
            logger.warning("Cache SET failed for key '%s': %s", key, str(exc))
            return False

    async def delete(self, *keys: str) -> int:
        """Evict one or more keys from cache."""
        if not keys:
            return 0
        client = redis_manager.get_client()
        try:
            return await client.delete(*keys)
        except Exception as exc:
            logger.warning("Cache DELETE failed for keys %s: %s", keys, str(exc))
            return 0

    async def exists(self, key: str) -> bool:
        """Check if a specific key exists and has not expired."""
        client = redis_manager.get_client()
        try:
            res = await client.exists(key)
            return bool(res)
        except Exception:
            return False

    async def clear_namespace(self, namespace: str) -> int:
        """Delete all cached keys matching a specific prefix namespace pattern."""
        client = redis_manager.get_client()
        pattern = f"{namespace}:*"
        keys_to_delete: List[str] = []
        try:
            if hasattr(client, "scan_iter"):
                async for key in client.scan_iter(match=pattern):
                    keys_to_delete.append(key)
            if keys_to_delete:
                return await client.delete(*keys_to_delete)
            return 0
        except Exception as exc:
            logger.warning("Failed clearing cache namespace '%s': %s", namespace, str(exc))
            return 0

    async def invalidate_review(
        self,
        review_id: Union[str, uuid.UUID],
        user_id: Union[str, uuid.UUID],
    ) -> None:
        """Evict cached review items, user timeline, and analytics after review mutations."""
        u_str = str(user_id)
        r_str = str(review_id)
        keys = [
            f"review:{r_str}",
            f"review:detail:{r_str}",
            f"history:{u_str}",
            f"dashboard:{u_str}",
            f"analytics:{u_str}",
        ]
        await self.delete(*keys)
        await self.clear_namespace(f"history:{u_str}")
        await self.clear_namespace(f"dashboard:{u_str}")
        await self.clear_namespace(f"analytics:{u_str}")
        logger.info("🗑️ Cache invalidated for review %s and user %s", r_str, u_str)

    async def invalidate_user(self, user_id: Union[str, uuid.UUID]) -> None:
        """Evict all cached resources associated with a user."""
        u_str = str(user_id)
        await self.clear_namespace(f"history:{u_str}")
        await self.clear_namespace(f"dashboard:{u_str}")
        await self.clear_namespace(f"analytics:{u_str}")
        logger.info("🗑️ Cache namespace invalidated for user %s", u_str)

    async def flush_all(self) -> bool:
        """Admin flush of all cache keys."""
        client = redis_manager.get_client()
        try:
            if hasattr(client, "flushdb"):
                await client.flushdb()
                logger.info("🧹 Cache storage flushed completely.")
                return True
            return False
        except Exception as exc:
            logger.error("Failed flushing cache: %s", str(exc))
            return False


cache_service = CacheService()
