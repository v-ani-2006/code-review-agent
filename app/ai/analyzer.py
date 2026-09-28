import ast
from datetime import datetime, timezone
import time
from typing import Optional

from fastapi import HTTPException, status

from app.ai.constants import SUPPORTED_LANGUAGES, Category, Severity
from app.ai.report import build_review_report
from app.core.logging import logger
from app.schemas.review import (
    CodeIssue,
    CodeMetrics,
    ComplexityMetrics,
    ReviewReport,
    ReviewScores,
)


def analyze_code(
    code: str,
    filename: Optional[str] = "main.py",
    language: str = "python",
) -> ReviewReport:
    """Entry point for the static code analysis engine.

    Parses source code into a Python Abstract Syntax Tree (AST), executes all modular
    analyzers, and aggregates scores, issues, complexity metrics, and suggestions.
    """
    start_time = time.perf_counter()

    # 1. Validate Language
    normalized_lang = language.lower().strip()
    if normalized_lang not in SUPPORTED_LANGUAGES:
        logger.warning("Unsupported language requested: '%s'", language)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported language '{language}'. Currently supported languages: {', '.join(SUPPORTED_LANGUAGES)}.",
        )

    # 2. Validate Code Content
    if not code or not code.strip():
        logger.warning("Empty source code submitted for analysis")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Source code cannot be empty.",
        )

    clean_filename = (filename or "main.py").strip()
    line_count = len(code.splitlines())
    logger.info("Analysis started: '%s' (%s, %d lines)", clean_filename, normalized_lang, line_count)

    # 3. Parse AST and gracefully handle Syntax Errors
    try:
        tree = ast.parse(code, filename=clean_filename)
    except SyntaxError as exc:
        duration = time.perf_counter() - start_time
        logger.warning("Syntax failure in '%s' at line %s: %s", clean_filename, exc.lineno, exc.msg)

        syntax_issue = CodeIssue(
            id="SYNTAX-001",
            title=f"Python Syntax Error: {exc.msg}",
            description=f"Invalid syntax detected on line {exc.lineno}, column {exc.offset}: '{exc.text.strip() if exc.text else ''}'.",
            severity=Severity.CRITICAL.value,
            category=Category.BUG.value,
            line_number=exc.lineno,
            column=exc.offset,
            suggestion="Correct the syntax error so the Python interpreter can parse and compile your code.",
        )

        # Return a structured failure report with 0 scores
        return ReviewReport(
            summary=f"Analysis aborted due to Syntax Error on line {exc.lineno}: {exc.msg}.",
            scores=ReviewScores(
                readability=0.0,
                maintainability=0.0,
                security=0.0,
                complexity=0.0,
                documentation=0.0,
                overall=0.0,
            ),
            issues=[syntax_issue],
            top_issues=[syntax_issue],
            metrics=CodeMetrics(
                line_count=line_count,
                character_count=len(code),
            ),
            suggestions={"SYNTAX": ["Fix the syntax error to allow full AST analysis."]},
            security_findings=[],
            complexity=ComplexityMetrics(
                cyclomatic_complexity=0.0,
                maintainability_index=0.0,
                rank="F",
            ),
            style={"syntax_valid": False},
            metadata={"filename": clean_filename, "language": normalized_lang, "syntax_error": True},
            timestamp=datetime.now(timezone.utc).isoformat(),
            processing_time=round(duration, 4),
            version="0.1.0",
        )

    # 4. Build Full Review Report
    duration = time.perf_counter() - start_time
    report = build_review_report(
        code=code,
        tree=tree,
        filename=clean_filename,
        language=normalized_lang,
        duration=duration,
    )

    # 5. Log Telemetry
    sec_count = len(report.security_findings)
    logger.info(
        "Analysis completed: '%s' | Overall Score: %s | Security Issues: %d | Time: %.4fs",
        clean_filename,
        report.scores.overall,
        sec_count,
        report.processing_time,
    )

    return report
