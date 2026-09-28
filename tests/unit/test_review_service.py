"""Unit tests for ReviewService and AST static code analysis."""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.review import ReviewRequest
from app.services.review_service import review_service
from tests.sample_files import (
    CLEAN_CODE_PATH,
    COMPLEX_CODE_PATH,
    SYNTAX_ERROR_PATH,
    VULNERABLE_CODE_PATH,
)


@pytest.mark.unit
async def test_analyze_clean_code(db_session: AsyncSession, test_user: User):
    """Test AST static analysis on clean PEP 8 compliant code."""
    code = CLEAN_CODE_PATH.read_text(encoding="utf-8")
    req = ReviewRequest(code=code, filename="clean.py", language="python")

    report = await review_service.analyze_and_store(db_session, req, test_user)

    assert report is not None
    assert report.scores.overall >= 80
    assert report.metadata.get("language") == "python"
    assert "review_id" in report.metadata


@pytest.mark.unit
async def test_analyze_vulnerable_code(db_session: AsyncSession, test_user: User):
    """Test detection of security vulnerabilities (eval, hardcoded secret, shell)."""
    code = VULNERABLE_CODE_PATH.read_text(encoding="utf-8")
    req = ReviewRequest(code=code, filename="vuln.py", language="python")

    report = await review_service.analyze_and_store(db_session, req, test_user)

    assert report is not None
    # Security score should be penalized for critical findings
    assert report.scores.security < 80
    vuln_ids = [issue.id for issue in report.issues]
    assert any("SEC" in issue_id or "security" in issue.category.lower() for issue, issue_id in zip(report.issues, vuln_ids))


@pytest.mark.unit
async def test_analyze_complex_code(db_session: AsyncSession, test_user: User):
    """Test detection of high cyclomatic complexity."""
    code = COMPLEX_CODE_PATH.read_text(encoding="utf-8")
    req = ReviewRequest(code=code, filename="complex.py", language="python")

    report = await review_service.analyze_and_store(db_session, req, test_user)

    assert report is not None
    assert report.complexity.cyclomatic_complexity > 5
    assert report.scores.complexity < 95


@pytest.mark.unit
async def test_analyze_syntax_error_code(db_session: AsyncSession, test_user: User):
    """Test graceful handling of code containing Python syntax errors."""
    code = SYNTAX_ERROR_PATH.read_text(encoding="utf-8")
    req = ReviewRequest(code=code, filename="syntax.py", language="python")

    report = await review_service.analyze_and_store(db_session, req, test_user)

    assert report is not None
    # Syntax error produces an issue indicating parse error
    assert any("syntax" in issue.description.lower() for issue in report.issues)


@pytest.mark.unit
async def test_get_supported_languages():
    """Test retrieval of supported programming languages list."""
    langs = review_service.get_supported_languages()
    assert len(langs) > 0
    lang_keys = [l.name.lower() for l in langs]
    assert "python" in lang_keys


@pytest.mark.unit
async def test_get_active_rules():
    """Test retrieval of active analysis rule definitions."""
    rules = review_service.get_active_rules()
    assert len(rules) > 0
    assert any(str(r.category).lower() in ["security", "complexity", "style", "maintainability"] for r in rules)
