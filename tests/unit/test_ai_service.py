"""Unit tests for AIService and AI provider orchestration with mocked Gemini."""
import pytest
from fastapi import HTTPException
from unittest.mock import patch

from app.ai.ai_service import ai_service
from app.schemas.ai_review import (
    AIBugFixRequest,
    AIDocumentationRequest,
    AIExplainRequest,
    AIOptimizeRequest,
    AIReviewRequest,
    AITestRequest,
)
from tests.mocks.gemini_mock import MockGeminiProvider

SAMPLE_CODE = "def add(a: int, b: int) -> int:\n    return a + b\n"


@pytest.mark.unit
async def test_ai_review_code_success(mock_gemini: MockGeminiProvider):
    """Test AI code review generation with mocked Gemini."""
    req = AIReviewRequest(code=SAMPLE_CODE, filename="math.py", language="python")
    res = await ai_service.review_code(req)

    assert res.success is True
    assert "well-structured" in res.review.summary.lower()
    assert res.static_report is not None


@pytest.mark.unit
async def test_ai_explain_code_success(mock_gemini: MockGeminiProvider):
    """Test AI code explanation with mocked Gemini."""
    req = AIExplainRequest(code=SAMPLE_CODE, language="python")
    res = await ai_service.explain_code(req)

    assert res.success is True
    assert res.data is not None
    assert "numerical calculation" in res.data.beginner_explanation.lower()
    assert len(res.data.execution_flow) > 0


@pytest.mark.unit
async def test_ai_optimize_code_success(mock_gemini: MockGeminiProvider):
    """Test AI code optimization with mocked Gemini."""
    req = AIOptimizeRequest(code=SAMPLE_CODE, language="python")
    res = await ai_service.optimize_code(req)

    assert res.success is True
    assert res.data is not None
    assert "optimized" in res.data.optimized_code.lower()
    assert len(res.data.performance_improvements) > 0


@pytest.mark.unit
async def test_ai_fix_code_success(mock_gemini: MockGeminiProvider):
    """Test AI automated bug fixing with mocked Gemini."""
    req = AIBugFixRequest(code=SAMPLE_CODE, language="python")
    res = await ai_service.fix_code(req)

    assert res.success is True
    assert res.data is not None
    assert len(res.data.identified_bugs) > 0
    assert res.data.corrected_code is not None


@pytest.mark.unit
async def test_ai_generate_docs_success(mock_gemini: MockGeminiProvider):
    """Test AI documentation generation with mocked Gemini."""
    req = AIDocumentationRequest(code=SAMPLE_CODE, language="python")
    res = await ai_service.generate_documentation(req)

    assert res.success is True
    assert res.data is not None
    assert "docstring" in str(res.data.module_docstring).lower()


@pytest.mark.unit
async def test_ai_generate_tests_success(mock_gemini: MockGeminiProvider):
    """Test AI pytest test suite generation with mocked Gemini."""
    req = AITestRequest(code=SAMPLE_CODE, language="python")
    res = await ai_service.generate_tests(req)

    assert res.success is True
    assert res.data is not None
    assert "pytest" in res.data.test_framework.lower()
    assert "def test_" in res.data.test_code


@pytest.mark.unit
async def test_ai_empty_code_rejection():
    """Test validation rejection on empty source code string."""
    req = AIReviewRequest(code="   ", filename="empty.py", language="python")
    with pytest.raises(HTTPException) as exc_info:
        await ai_service.review_code(req)
    assert exc_info.value.status_code == 400
    assert "cannot be empty" in exc_info.value.detail.lower()


@pytest.mark.unit
async def test_ai_unsupported_language_rejection():
    """Test validation rejection on unsupported language."""
    req = AIReviewRequest(code=SAMPLE_CODE, filename="math.xyz", language="unsupported_lang_xyz")
    with pytest.raises(HTTPException) as exc_info:
        await ai_service.review_code(req)
    assert exc_info.value.status_code == 400
    assert "unsupported language" in exc_info.value.detail.lower()


@pytest.mark.unit
async def test_ai_provider_quota_exceeded():
    """Test fallback and error encapsulation when Gemini quota is exceeded."""
    failing_provider = MockGeminiProvider(mode="quota_exceeded")
    with patch("app.ai.ai_service.get_ai_provider", return_value=failing_provider):
        req = AIReviewRequest(code=SAMPLE_CODE, filename="math.py", language="python")
        res = await ai_service.review_code(req)
        # Even when Gemini fails, static AST review is returned gracefully
        assert res.static_report is not None
        assert res.static_report.scores.overall > 0
