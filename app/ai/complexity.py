from typing import Any, Dict, List, Tuple
from radon.complexity import cc_rank, cc_visit
from radon.metrics import h_visit, mi_visit

from app.ai.constants import Category, Severity
from app.schemas.review import CodeIssue, ComplexityMetrics


def analyze_complexity(code: str) -> Tuple[ComplexityMetrics, List[CodeIssue]]:
    """Analyze cyclomatic complexity, Maintainability Index, and Halstead metrics using Radon."""
    issues: List[CodeIssue] = []
    functions_info: List[Dict[str, Any]] = []

    try:
        # 1. Cyclomatic Complexity
        blocks = cc_visit(code)
        total_cc = 0
        block_count = 0

        for block in blocks:
            cc = getattr(block, "complexity", 1)
            name = getattr(block, "name", "anonymous")
            lineno = getattr(block, "lineno", 1)
            col_offset = getattr(block, "col_offset", 0)
            block_type = getattr(block, "letter", "F")  # F: Function, C: Class, M: Method

            total_cc += cc
            block_count += 1

            functions_info.append({
                "name": name,
                "type": "Method" if block_type == "M" else "Function" if block_type == "F" else "Class",
                "complexity": cc,
                "rank": cc_rank(cc),
                "line": lineno,
            })

            # Check for high cyclomatic complexity
            if cc > 20:
                issues.append(
                    CodeIssue(
                        id="CMP-002",
                        title=f"Critical Cyclomatic Complexity in '{name}'",
                        description=f"'{name}' has cyclomatic complexity of {cc} (Rank {cc_rank(cc)}). Highly error-prone and untestable.",
                        severity=Severity.CRITICAL.value,
                        category=Category.COMPLEXITY.value,
                        line_number=lineno,
                        column=col_offset,
                        suggestion="Break this function down into smaller single-responsibility sub-functions or state machines.",
                    )
                )
            elif cc > 10:
                issues.append(
                    CodeIssue(
                        id="CMP-001",
                        title=f"High Cyclomatic Complexity in '{name}'",
                        description=f"'{name}' has cyclomatic complexity of {cc} (Rank {cc_rank(cc)}). Exceeds recommended threshold of 10.",
                        severity=Severity.HIGH.value,
                        category=Category.COMPLEXITY.value,
                        line_number=lineno,
                        column=col_offset,
                        suggestion="Simplify branch conditions, use guard clauses, or dispatch via a dictionary/strategy pattern.",
                    )
                )

        avg_cc = round(total_cc / block_count, 2) if block_count > 0 else 1.0
        overall_rank = cc_rank(int(avg_cc))

        # 2. Maintainability Index
        # Radon mi_visit returns a score typically from 0 to 100
        try:
            raw_mi = mi_visit(code, multi=True)
            mi = round(max(0.0, min(100.0, float(raw_mi))), 1)
        except Exception:
            mi = 85.0

        # 3. Halstead Metrics
        halstead_volume = None
        halstead_diff = None
        try:
            h_metrics = h_visit(code)
            if hasattr(h_metrics, "total"):
                halstead_volume = round(float(h_metrics.total.volume), 2)
                halstead_diff = round(float(h_metrics.total.difficulty), 2)
        except Exception:
            pass

        metrics = ComplexityMetrics(
            cyclomatic_complexity=avg_cc,
            maintainability_index=mi,
            halstead_volume=halstead_volume,
            halstead_difficulty=halstead_diff,
            rank=overall_rank,
            functions_complexity=functions_info,
        )

        return metrics, issues

    except Exception:
        # Fallback if code cannot be analyzed by Radon
        return ComplexityMetrics(
            cyclomatic_complexity=1.0,
            maintainability_index=75.0,
            rank="A",
            functions_complexity=[],
        ), issues
