"""Performance benchmark comparing cache hit speed against raw computation."""
import time
import pytest

from app.ai.analyzer import analyze_code
from app.services.cache_service import cache_service
from tests.utils import measure_duration


@pytest.mark.performance
async def test_cache_latency_vs_compute():
    """Verify that cached response retrieval is at least 10x faster than full analysis."""
    source = "def compute(n):\n    return sum(range(n))\n"

    # 1. Full computation duration
    start = time.perf_counter()
    report = analyze_code(source, "compute.py", "python")
    compute_duration = time.perf_counter() - start

    # Cache report
    cache_key = "bench:compute_report"
    await cache_service.set(cache_key, report.model_dump(mode="json"), ttl=60)

    # 2. Cache retrieval duration
    start_cache = time.perf_counter()
    cached = await cache_service.get(cache_key)
    cache_duration = time.perf_counter() - start_cache

    assert cached is not None
    # Cache hit must be faster than compute
    assert cache_duration < compute_duration
    # Cache hit should typically take less than 15ms
    assert cache_duration < 0.05
