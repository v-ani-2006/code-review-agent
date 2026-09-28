from app.ai.models import AIAnalysisContext


def build_unittest_prompt(context: AIAnalysisContext) -> str:
    """Build a prompt to generate comprehensive Pytest suites including fixtures, parameterized tests, and async support."""
    return f"""You are a Principal QA Engineer and Python Testing Specialist.
Generate an exhaustive, production-grade Pytest test suite for the following {context.language} code.

### SOURCE CODE METADATA
- Language: {context.language}
- Filename: {context.filename}

### SOURCE CODE TO TEST:
```{context.language}
{context.source_code}
```

### INSTRUCTIONS:
Create a complete test file using pytest, pytest-asyncio (if async functions exist), and unittest.mock.
Include:
1. Reusable `@pytest.fixture` functions.
2. Positive and negative test cases.
3. Edge cases (null/empty, boundary values, huge inputs, invalid types).
4. `@pytest.mark.parametrize` for table-driven test cases.
5. Async test functions with `@pytest.mark.asyncio` where appropriate.

You MUST output your response in valid JSON format matching this schema:
{{
  "test_code": "Complete runnable Python test file containing all tests, imports, fixtures, and assertions",
  "test_framework": "pytest",
  "fixtures": [
    {{"name": "fixture_name", "description": "What mock/state it prepares"}}
  ],
  "covered_edge_cases": [
    "Edge case description (e.g. Empty list handling, Negative price, Connection timeout)",
    ...
  ],
  "parameterized_cases": [
    "Description of parameterized matrix tests",
    ...
  ],
  "execution_command": "pytest -v test_{context.filename}"
}}

Output only the JSON block without markdown fences or outside commentary.
"""
