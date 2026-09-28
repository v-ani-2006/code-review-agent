import ast
import tokenize
from datetime import datetime, timezone
import io
from typing import Any, Dict, List, Set, Tuple

from app.ai.constants import (
    MAX_CLASS_LINES,
    MAX_CLASS_METHODS,
    MAX_FUNCTION_LINES,
    MAX_FUNCTION_PARAMS,
    STDLIB_MODULES,
    Category,
    Severity,
)
from app.ai.complexity import analyze_complexity
from app.ai.readability import analyze_readability
from app.ai.scoring import calculate_scores
from app.ai.security import analyze_security
from app.ai.style import analyze_style_and_bugs
from app.schemas.review import (
    CodeIssue,
    CodeMetrics,
    ComplexityMetrics,
    ReviewReport,
    ReviewScores,
)


class StructuralVisitor(ast.NodeVisitor):
    """Gathers structural AST counts, function/class metrics, and import heuristics."""

    def __init__(self):
        self.issues: List[CodeIssue] = []
        self.function_count = 0
        self.async_function_count = 0
        self.class_count = 0
        self.import_count = 0
        self.loop_count = 0
        self.conditional_count = 0
        self.try_count = 0
        self.return_count = 0
        self.decorator_count = 0

        self.imported_names: Set[str] = set()
        self.used_names: Set[str] = set()
        self.seen_imports: Set[str] = set()

        self.stdlib_imports: List[str] = []
        self.third_party_imports: List[str] = []

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self.function_count += 1
        self._analyze_function(node)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self.function_count += 1
        self.async_function_count += 1
        self._analyze_function(node)
        self.generic_visit(node)

    def _analyze_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        fn_lines = (node.end_lineno or node.lineno) - node.lineno + 1
        num_args = len(node.args.args)

        # 1. Long functions
        if fn_lines > MAX_FUNCTION_LINES:
            self.issues.append(
                CodeIssue(
                    id="CMP-003",
                    title=f"Excessive Function Length in '{node.name}' ({fn_lines} lines)",
                    description=f"Function '{node.name}' spans {fn_lines} lines, exceeding the {MAX_FUNCTION_LINES}-line guideline.",
                    severity=Severity.MEDIUM.value,
                    category=Category.COMPLEXITY.value,
                    line_number=node.lineno,
                    column=node.col_offset,
                    suggestion="Decompose this function into smaller, single-responsibility helper functions.",
                )
            )

        # 2. Too many arguments
        if num_args > MAX_FUNCTION_PARAMS:
            self.issues.append(
                CodeIssue(
                    id="CMP-004",
                    title=f"Too Many Parameters in '{node.name}' ({num_args} params)",
                    description=f"Function '{node.name}' accepts {num_args} parameters, exceeding the threshold of {MAX_FUNCTION_PARAMS}.",
                    severity=Severity.LOW.value,
                    category=Category.COMPLEXITY.value,
                    line_number=node.lineno,
                    column=node.col_offset,
                    suggestion="Consolidate multiple arguments into a Pydantic model, dataclass, or configuration dictionary.",
                )
            )

        # 3. Decorator count
        self.decorator_count += len(node.decorator_list)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self.class_count += 1
        class_lines = (node.end_lineno or node.lineno) - node.lineno + 1
        methods = [stmt for stmt in node.body if isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef))]

        # 1. Large class lines
        if class_lines > MAX_CLASS_LINES:
            self.issues.append(
                CodeIssue(
                    id="CMP-005",
                    title=f"Large Class: '{node.name}' ({class_lines} lines)",
                    description=f"Class '{node.name}' exceeds recommended size of {MAX_CLASS_LINES} lines.",
                    severity=Severity.MEDIUM.value,
                    category=Category.COMPLEXITY.value,
                    line_number=node.lineno,
                    column=node.col_offset,
                    suggestion="Refactor using composition or split into focused sub-modules.",
                )
            )

        # 2. Too many methods
        if len(methods) > MAX_CLASS_METHODS:
            self.issues.append(
                CodeIssue(
                    id="CMP-006",
                    title=f"Too Many Methods in Class '{node.name}' ({len(methods)} methods)",
                    description=f"Class defines {len(methods)} methods, indicating high coupling or 'God Object' smell.",
                    severity=Severity.LOW.value,
                    category=Category.COMPLEXITY.value,
                    line_number=node.lineno,
                    column=node.col_offset,
                    suggestion="Separate auxiliary operations into dedicated service or helper classes.",
                )
            )

        # 3. Empty class without docstrings or methods
        if len(node.body) == 1 and isinstance(node.body[0], ast.Pass) and not ast.get_docstring(node):
            self.issues.append(
                CodeIssue(
                    id="BP-001",
                    title=f"Empty Class: '{node.name}'",
                    description=f"Class '{node.name}' contains only 'pass' without attributes or documentation.",
                    severity=Severity.LOW.value,
                    category=Category.BEST_PRACTICE.value,
                    line_number=node.lineno,
                    column=node.col_offset,
                    suggestion="Implement attributes/methods or add a docstring explaining its role.",
                )
            )

        self.generic_visit(node)

    def visit_Import(self, node: ast.Import) -> None:
        self.import_count += len(node.names)
        for alias in node.names:
            base_mod = alias.name.split(".")[0]
            if base_mod in STDLIB_MODULES:
                self.stdlib_imports.append(alias.name)
            else:
                self.third_party_imports.append(alias.name)

            # Duplicate import
            if alias.name in self.seen_imports:
                self.issues.append(
                    CodeIssue(
                        id="BP-002",
                        title=f"Duplicate Import: '{alias.name}'",
                        description=f"Module '{alias.name}' is imported more than once.",
                        severity=Severity.LOW.value,
                        category=Category.BEST_PRACTICE.value,
                        line_number=node.lineno,
                        column=node.col_offset,
                        suggestion=f"Remove the redundant import statement for '{alias.name}'.",
                    )
                )
            self.seen_imports.add(alias.name)
            self.imported_names.add(alias.asname or alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        self.import_count += len(node.names)
        module_name = node.module or ""
        base_mod = module_name.split(".")[0] if module_name else ""

        if base_mod in STDLIB_MODULES:
            self.stdlib_imports.append(module_name)
        else:
            self.third_party_imports.append(module_name)

        # 1. Wildcard import check (from x import *)
        for alias in node.names:
            if alias.name == "*":
                self.issues.append(
                    CodeIssue(
                        id="BP-003",
                        title=f"Wildcard Import: 'from {module_name} import *'",
                        description="Wildcard imports pollute the namespace and make symbol origin ambiguous.",
                        severity=Severity.MEDIUM.value,
                        category=Category.BEST_PRACTICE.value,
                        line_number=node.lineno,
                        column=node.col_offset,
                        suggestion="Explicitly import required symbols by name.",
                    )
                )
            else:
                self.imported_names.add(alias.asname or alias.name)

        # 2. Relative import check
        if node.level > 0:
            # Relative import (e.g. from . import utils)
            pass

        self.generic_visit(node)

    def visit_For(self, node: ast.For) -> None:
        self.loop_count += 1
        self.generic_visit(node)

    def visit_While(self, node: ast.While) -> None:
        self.loop_count += 1
        self.generic_visit(node)

    def visit_If(self, node: ast.If) -> None:
        self.conditional_count += 1
        self.generic_visit(node)

    def visit_Try(self, node: ast.Try) -> None:
        self.try_count += 1
        self.generic_visit(node)

    def visit_Return(self, node: ast.Return) -> None:
        self.return_count += 1
        self.generic_visit(node)

    def visit_Name(self, node: ast.Name) -> None:
        if isinstance(node.ctx, ast.Load):
            self.used_names.add(node.id)
        self.generic_visit(node)


def compute_token_count(code: str) -> int:
    """Safely count lexical tokens using Python's tokenize module."""
    try:
        tokens = list(tokenize.tokenize(io.BytesIO(code.encode("utf-8")).readline))
        return len(tokens)
    except Exception:
        return len(code.split())


def build_review_report(
    code: str,
    tree: ast.AST,
    filename: str = "main.py",
    language: str = "python",
    duration: float = 0.0,
) -> ReviewReport:
    """Execute all static analyzers and aggregate findings into a comprehensive ReviewReport."""
    lines = code.splitlines()
    line_count = len(lines)
    blank_lines = sum(1 for line in lines if not line.strip())
    comment_lines = sum(1 for line in lines if line.strip().startswith("#"))

    # 1. Structural & Import Visitor
    struct_visitor = StructuralVisitor()
    struct_visitor.visit(tree)

    # 2. Check for unused imports
    unused_imports = struct_visitor.imported_names - struct_visitor.used_names
    for unused in unused_imports:
        if unused not in ("__all__", "_"):
            struct_visitor.issues.append(
                CodeIssue(
                    id="BP-004",
                    title=f"Unused Imported Symbol: '{unused}'",
                    description=f"'{unused}' is imported but never referenced in the module.",
                    severity=Severity.LOW.value,
                    category=Category.BEST_PRACTICE.value,
                    suggestion=f"Remove the unused import '{unused}'.",
                )
            )

    # 3. Run Complexity Analysis
    complexity_metrics, complexity_issues = analyze_complexity(code)

    # 4. Run Security Analysis
    security_issues = analyze_security(tree, code)

    # 5. Run Style & Bug Analysis
    style_summary, style_issues = analyze_style_and_bugs(tree, code)

    # 6. Run Readability Analysis
    readability_summary, readability_issues, readability_score = analyze_readability(tree, code)

    # Combine all detected issues
    all_issues: List[CodeIssue] = (
        struct_visitor.issues
        + complexity_issues
        + security_issues
        + style_issues
        + readability_issues
    )

    # Sort issues by severity priority: CRITICAL -> HIGH -> MEDIUM -> LOW
    severity_order = {Severity.CRITICAL.value: 0, Severity.HIGH.value: 1, Severity.MEDIUM.value: 2, Severity.LOW.value: 3}
    all_issues.sort(key=lambda x: severity_order.get(x.severity, 4))

    top_issues = [i for i in all_issues if i.severity in (Severity.CRITICAL.value, Severity.HIGH.value)][:5]
    if not top_issues:
        top_issues = all_issues[:3]

    security_findings = [i for i in all_issues if i.category == Category.SECURITY.value]

    # 7. Compute Scores
    scores = calculate_scores(
        issues=all_issues,
        complexity_metrics=complexity_metrics,
        readability_score=readability_score,
        docstring_ratio=readability_summary.get("docstring_ratio", 1.0),
        comment_ratio=readability_summary.get("comment_ratio", 0.0),
    )

    # 8. Generate Suggestions grouped by Category
    suggestions: Dict[str, List[str]] = {}
    for issue in all_issues:
        if issue.suggestion:
            cat = issue.category
            if cat not in suggestions:
                suggestions[cat] = []
            if issue.suggestion not in suggestions[cat]:
                suggestions[cat].append(issue.suggestion)

    # 9. Quantitative Code Metrics
    token_count = compute_token_count(code)
    metrics = CodeMetrics(
        line_count=line_count,
        function_count=struct_visitor.function_count,
        class_count=struct_visitor.class_count,
        import_count=struct_visitor.import_count,
        comment_count=comment_lines,
        blank_line_count=blank_lines,
        character_count=len(code),
        token_count=token_count,
    )

    # 10. Executive Summary Synthesis
    critical_count = sum(1 for i in all_issues if i.severity == Severity.CRITICAL.value)
    high_count = sum(1 for i in all_issues if i.severity == Severity.HIGH.value)

    if critical_count > 0:
        status_text = f"CRITICAL: {critical_count} critical vulnerability detected! Immediate remediation required."
    elif high_count > 0:
        status_text = f"WARNING: {high_count} high-priority issues detected."
    elif scores.overall >= 85.0:
        status_text = "EXCELLENT: Code demonstrates high quality, clean maintainability, and conforms to Python best practices."
    elif scores.overall >= 70.0:
        status_text = "GOOD: Code is solid with minor improvements suggested in documentation, style, or structure."
    else:
        status_text = "NEEDS IMPROVEMENT: Code requires refactoring to reduce complexity and improve maintainability."

    summary = (
        f"Analyzed {line_count} lines across {metrics.function_count} functions and {metrics.class_count} classes. "
        f"Overall Quality Score: {scores.overall}/100 (Maintainability Index: {complexity_metrics.maintainability_index}, Rank: {complexity_metrics.rank}). "
        f"{status_text} Found {len(all_issues)} total observations."
    )

    metadata = {
        "filename": filename,
        "language": language,
        "loops": struct_visitor.loop_count,
        "conditionals": struct_visitor.conditional_count,
        "try_blocks": struct_visitor.try_count,
        "return_statements": struct_visitor.return_count,
        "decorators": struct_visitor.decorator_count,
        "async_functions": struct_visitor.async_function_count,
        "stdlib_imports": list(set(struct_visitor.stdlib_imports)),
        "third_party_imports": list(set(struct_visitor.third_party_imports)),
    }

    return ReviewReport(
        summary=summary,
        scores=scores,
        issues=all_issues,
        top_issues=top_issues,
        metrics=metrics,
        suggestions=suggestions,
        security_findings=security_findings,
        complexity=complexity_metrics,
        style=style_summary,
        metadata=metadata,
        timestamp=datetime.now(timezone.utc).isoformat(),
        processing_time=round(duration, 4),
        version="0.1.0",
    )
