from typing import List
from app.ai.constants import Severity
from app.schemas.review import CodeIssue, ComplexityMetrics, ReviewScores


def calculate_scores(
    issues: List[CodeIssue],
    complexity_metrics: ComplexityMetrics,
    readability_score: float,
    docstring_ratio: float,
    comment_ratio: float,
) -> ReviewScores:
    """Calculate normalized scores across all quality dimensions (0.0 to 100.0)."""

    # 1. Security Score
    sec_score = 100.0
    for issue in issues:
        if issue.category == "SECURITY":
            if issue.severity == Severity.CRITICAL.value:
                sec_score -= 35.0
            elif issue.severity == Severity.HIGH.value:
                sec_score -= 20.0
            elif issue.severity == Severity.MEDIUM.value:
                sec_score -= 10.0
            elif issue.severity == Severity.LOW.value:
                sec_score -= 3.0
    security_score = round(max(0.0, min(100.0, sec_score)), 1)

    # 2. Complexity Score
    cc = complexity_metrics.cyclomatic_complexity
    if cc <= 2.0:
        comp_score = 100.0
    elif cc <= 5.0:
        comp_score = 90.0 - (cc - 2.0) * 3.3
    elif cc <= 10.0:
        comp_score = 80.0 - (cc - 5.0) * 4.0
    elif cc <= 20.0:
        comp_score = 60.0 - (cc - 10.0) * 3.0
    else:
        comp_score = max(10.0, 30.0 - (cc - 20.0))

    # Deduct for specific complexity issues
    for issue in issues:
        if issue.category == "COMPLEXITY":
            comp_score -= 5.0
    complexity_score = round(max(10.0, min(100.0, comp_score)), 1)

    # 3. Maintainability Score
    # Blend Radon's MI with bug counts
    mi = complexity_metrics.maintainability_index
    bug_deduction = sum(8.0 for i in issues if i.category == "BUG")
    maintainability_score = round(max(10.0, min(100.0, mi - bug_deduction)), 1)

    # 4. Documentation Score
    doc_score = (docstring_ratio * 70.0) + min(30.0, comment_ratio * 300.0)
    documentation_score = round(max(10.0, min(100.0, doc_score)), 1)

    # 5. Overall Score (Weighted Composite)
    # Weights: Security 30%, Maintainability 25%, Complexity 20%, Readability 15%, Documentation 10%
    overall_score = round(
        (security_score * 0.30)
        + (maintainability_score * 0.25)
        + (complexity_score * 0.20)
        + (readability_score * 0.15)
        + (documentation_score * 0.10),
        1,
    )

    return ReviewScores(
        readability=round(max(0.0, min(100.0, readability_score)), 1),
        maintainability=round(max(0.0, min(100.0, maintainability_score)), 1),
        security=security_score,
        complexity=complexity_score,
        documentation=documentation_score,
        overall=round(max(0.0, min(100.0, overall_score)), 1),
    )
