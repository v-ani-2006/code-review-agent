import time
from typing import Any, Dict, List, Optional

from app.ai.parser import extract_first_code_block, extract_json_fragment
from app.ai.providers.provider_factory import get_ai_provider
from app.core.logging import logger


class UnitTestGenerator:
    """Generates complete, production-grade Pytest test suites including fixtures, mocks, and async support."""

    def __init__(self, model: Optional[str] = None):
        self.model = model
        self.provider = get_ai_provider(model=model)

    async def generate(
        self,
        code: str,
        filename: str = "main.py",
        language: str = "python",
        include_edge_cases: bool = True,
        include_async_tests: bool = True,
        include_security_tests: bool = True,
    ) -> Dict[str, Any]:
        """Generate comprehensive pytest test suite."""
        start_time = time.perf_counter()
        logger.info("UnitTestGenerator started for '%s' (%s)", filename, language)

        prompt = f"""You are a Principal QA Architect and Python Test Automation Specialist.
Generate an exhaustive, production-ready Pytest test suite for the following {language} file: `{filename}`.

### SOURCE CODE TO TEST:
```{language}
{code}
```

### REQUIREMENTS:
1. Framework: `pytest` (and `pytest-asyncio` if async functions are detected).
2. Use `@pytest.fixture` for reusable test dependencies, test data, and sample models.
3. Use `unittest.mock` / `pytest-mock` (`AsyncMock`, `MagicMock`, `patch`) for database or network calls.
4. Positive and negative testing for every function and method.
5. Edge cases: empty/null values, boundary numbers, unexpected data types.
6. Table-driven tests using `@pytest.mark.parametrize`.
7. Security / vulnerability tests (e.g. SQL injection attempts, malformed inputs, unhandled exceptions).

### INSTRUCTIONS:
Output your response in valid JSON matching this schema:
{{
  "test_code": "Complete runnable test_*.py source code including all imports, fixtures, assertions, and mocks",
  "framework": "pytest",
  "test_count": 8,
  "fixtures_included": ["fixture_db_session", "sample_payload"],
  "edge_cases_covered": ["Zero division boundary", "Null pointer argument", "Invalid type casting"],
  "security_cases_covered": ["SQL injection bypass test", "Buffer overflow input"]
}}

Output only the JSON block without markdown fences or outside commentary.
"""
        provider_resp = await self.provider._generate_response(prompt)
        duration = round(time.perf_counter() - start_time, 4)

        data = provider_resp.parsed_json or {}
        if not data:
            data = extract_json_fragment(provider_resp.raw_text) or {}

        test_code = data.get("test_code") or extract_first_code_block(provider_resp.raw_text) or "# No test suite generated"

        return {
            "success": provider_resp.success,
            "test_code": test_code,
            "framework": data.get("framework", "pytest"),
            "fixtures": data.get("fixtures_included", []),
            "edge_cases": data.get("edge_cases_covered", []),
            "security_cases": data.get("security_cases_covered", []),
            "model_used": provider_resp.model_used,
            "processing_time": duration,
        }
