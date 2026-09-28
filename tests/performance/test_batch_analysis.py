"""Performance benchmark for concurrent multi-file static analysis."""
import asyncio
import pytest

from app.ai.analyzer import analyze_code
from tests.utils import execute_concurrent, measure_duration


@pytest.mark.performance
async def test_concurrent_batch_ast_analysis():
    """Benchmark executing 20 concurrent static code analysis requests."""
    code_snippet = """
def process_data(items):
    return [x * 2 for x in items if x > 0]
"""

    def _run_single():
        return analyze_code(code_snippet, "snippet.py", "python")

    with measure_duration() as metric:
        # Run 20 analyses concurrently using thread executor
        loop = asyncio.get_running_loop()
        tasks = [loop.run_in_executor(None, _run_single) for _ in range(20)]
        results = await asyncio.gather(*tasks)

    duration = metric["duration"]
    assert len(results) == 20
    assert all(r.scores.overall > 0 for r in results)
    # 20 concurrent AST analyses should complete under 4.0s
    assert duration < 4.0, f"Concurrent batch took {duration}s"
