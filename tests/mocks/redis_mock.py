"""Thread-safe, fully asynchronous in-memory Redis mock for test isolation."""
import asyncio
from datetime import datetime, timezone
import fnmatch
from typing import Any, AsyncGenerator, Dict, List, Optional


class MockRedisClient:
    """Mock async Redis client supporting TTL expiration, key matching, and error simulation."""

    def __init__(self, simulate_failure: bool = False):
        self._store: Dict[str, Dict[str, Any]] = {}
        self._lock = asyncio.Lock()
        self.simulate_failure = simulate_failure
        self.call_log: List[Dict[str, Any]] = []

    def _check_failure(self):
        if self.simulate_failure:
            raise ConnectionError("Simulated Redis connection failure")

    async def get(self, key: str) -> Optional[str]:
        self._check_failure()
        self.call_log.append({"op": "get", "key": key})
        async with self._lock:
            entry = self._store.get(key)
            if not entry:
                return None
            expires_at = entry.get("expires_at")
            if expires_at and datetime.now(timezone.utc).timestamp() > expires_at:
                del self._store[key]
                return None
            val = entry.get("value")
            return val if isinstance(val, str) else str(val)

    async def set(self, key: str, value: str, ex: Optional[int] = None) -> bool:
        self._check_failure()
        self.call_log.append({"op": "set", "key": key, "ex": ex})
        async with self._lock:
            expires_at = None
            if ex:
                expires_at = datetime.now(timezone.utc).timestamp() + ex
            self._store[key] = {"value": value, "expires_at": expires_at}
            return True

    async def delete(self, *keys: str) -> int:
        self._check_failure()
        self.call_log.append({"op": "delete", "keys": keys})
        async with self._lock:
            count = 0
            for k in keys:
                if k in self._store:
                    del self._store[k]
                    count += 1
            return count

    async def exists(self, key: str) -> int:
        self._check_failure()
        val = await self.get(key)
        return 1 if val is not None else 0

    async def scan_iter(self, match: str = "*") -> AsyncGenerator[str, None]:
        self._check_failure()
        async with self._lock:
            current_keys = list(self._store.keys())

        for key in current_keys:
            if match == "*" or fnmatch.fnmatch(key, match):
                # Verify TTL before yielding
                val = await self.get(key)
                if val is not None:
                    yield key

    async def ping(self) -> bool:
        self._check_failure()
        return True

    async def flushdb(self) -> bool:
        self._check_failure()
        async with self._lock:
            self._store.clear()
        return True

    async def aclose(self) -> None:
        pass
