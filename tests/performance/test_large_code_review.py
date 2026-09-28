"""Performance benchmark for AST analysis on large codebases (>1,000 LOC)."""
import pytest

from app.ai.analyzer import analyze_code
from tests.utils import measure_duration


@pytest.mark.performance
def test_large_codebase_ast_analysis():
    """Benchmark AST parsing, complexity, and security scans on 1,500 LOC Python source."""
    # Generate 1,500 lines of modular Python code
    functions = []
    for i in range(150):
        fn = f"""
def compute_dataset_segment_{i}(records, multiplier=1.5):
    \"\"\"Module processing function {i}.\"\"\"
    total = 0.0
    for record in records:
        if record is not None and record > {i}:
            total += record * multiplier
    return total
"""
        functions.append(fn)

    large_code = "\n".join(functions)
    assert len(large_code.splitlines()) > 1000

    with measure_duration() as metric:
        report = analyze_code(code=large_code, filename="benchmark_large.py", language="python")

    duration = metric["duration"]
    assert report is not None
    assert report.scores.overall > 0
    # AST analysis for 1,500 LOC should execute within 3 seconds
    assert duration < 3.0, f"Analysis took {duration}s, exceeding 3.0s threshold"
