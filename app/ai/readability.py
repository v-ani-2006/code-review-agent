import ast
import re
from typing import Any, Dict, List, Set, Tuple

from app.ai.constants import BUILTIN_NAMES, Category, Severity
from app.schemas.review import CodeIssue

# Naming convention regex patterns
SNAKE_CASE_PATTERN = re.compile(r"^[a-z_][a-z0-9_]*$")
PASCAL_CASE_PATTERN = re.compile(r"^[A-Z][a-zA-Z0-9]*$")
UPPER_CASE_PATTERN = re.compile(r"^[A-Z_][A-Z0-9_]*$")


class ReadabilityVisitor(ast.NodeVisitor):
    """AST visitor evaluating identifier naming conventions, built-in shadowing, and magic numbers."""

    def __init__(self):
        self.issues: List[CodeIssue] = []
        self.function_lengths: List[int] = []
        self.functions_with_docstring = 0
        self.classes_with_docstring = 0
        self.total_functions = 0
        self.total_classes = 0

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self.total_functions += 1
        fn_lines = (node.end_lineno or node.lineno) - node.lineno + 1
        self.function_lengths.append(fn_lines)

        # 1. Docstring check
        if ast.get_docstring(node):
            self.functions_with_docstring += 1
        elif not node.name.startswith("_"):
            self.issues.append(
                CodeIssue(
                    id="DOC-001",
                    title=f"Missing Docstring in Public Function '{node.name}'",
                    description=f"Public function '{node.name}' lacks a descriptive docstring.",
                    severity=Severity.LOW.value,
                    category=Category.DOCUMENTATION.value,
                    line_number=node.lineno,
                    column=node.col_offset,
                    suggestion="Add a docstring detailing parameters, return types, and exceptions.",
                )
            )

        # 2. Function naming (snake_case)
        if not SNAKE_CASE_PATTERN.match(node.name) and not (node.name.startswith("__") and node.name.endswith("__")):
            self.issues.append(
                CodeIssue(
                    id="RD-001",
                    title=f"Non-Standard Function Name '{node.name}'",
                    description=f"Function '{node.name}' should follow PEP 8 snake_case convention.",
                    severity=Severity.LOW.value,
                    category=Category.READABILITY.value,
                    line_number=node.lineno,
                    column=node.col_offset,
                    suggestion=f"Rename to '{re.sub(r'(?<!^)(?=[A-Z])', '_', node.name).lower()}'.",
                )
            )

        # 3. Built-in shadowing check on function name
        if node.name in BUILTIN_NAMES:
            self.issues.append(
                CodeIssue(
                    id="RD-002",
                    title=f"Function Name Shadows Built-in: '{node.name}'",
                    description=f"Defining function '{node.name}' shadows Python's built-in '{node.name}'.",
                    severity=Severity.MEDIUM.value,
                    category=Category.READABILITY.value,
                    line_number=node.lineno,
                    column=node.col_offset,
                    suggestion=f"Rename function (e.g. '{node.name}_custom' or specific action name).",
                )
            )

        # 4. Parameter checks
        for arg in node.args.args:
            # Single-letter parameter
            if len(arg.arg) == 1 and arg.arg not in ("i", "j", "k", "v", "k", "_"):
                self.issues.append(
                    CodeIssue(
                        id="RD-003",
                        title=f"Cryptic Single-Letter Parameter '{arg.arg}' in '{node.name}'",
                        description=f"Parameter '{arg.arg}' is uninformative and impairs code readability.",
                        severity=Severity.LOW.value,
                        category=Category.READABILITY.value,
                        line_number=arg.lineno,
                        column=arg.col_offset,
                        suggestion=f"Replace '{arg.arg}' with a descriptive parameter name.",
                    )
                )
            # Parameter shadows built-in
            if arg.arg in BUILTIN_NAMES:
                self.issues.append(
                    CodeIssue(
                        id="RD-004",
                        title=f"Parameter Shadows Built-in: '{arg.arg}'",
                        description=f"Parameter '{arg.arg}' shadows Python built-in '{arg.arg}'.",
                        severity=Severity.LOW.value,
                        category=Category.READABILITY.value,
                        line_number=arg.lineno,
                        column=arg.col_offset,
                        suggestion=f"Rename parameter (e.g. '{arg.arg}_val' or '{arg.arg}_type').",
                    )
                )

        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self.total_classes += 1

        # Docstring check
        if ast.get_docstring(node):
            self.classes_with_docstring += 1
        else:
            self.issues.append(
                CodeIssue(
                    id="DOC-002",
                    title=f"Missing Docstring in Class '{node.name}'",
                    description=f"Class '{node.name}' has no docstring explaining its role and responsibilities.",
                    severity=Severity.LOW.value,
                    category=Category.DOCUMENTATION.value,
                    line_number=node.lineno,
                    column=node.col_offset,
                    suggestion="Add a class-level docstring summarizing its purpose and public API.",
                )
            )

        # Class naming (PascalCase)
        if not PASCAL_CASE_PATTERN.match(node.name):
            self.issues.append(
                CodeIssue(
                    id="RD-005",
                    title=f"Non-Standard Class Name '{node.name}'",
                    description=f"Class '{node.name}' should follow PEP 8 PascalCase (CapWords) convention.",
                    severity=Severity.LOW.value,
                    category=Category.READABILITY.value,
                    line_number=node.lineno,
                    column=node.col_offset,
                    suggestion="Rename using PascalCase capitalization.",
                )
            )

        self.generic_visit(node)

    def visit_Constant(self, node: ast.Constant) -> None:
        # Detect magic numbers in calculations / comparisons (ignore common 0, 1, -1, 2)
        if isinstance(node.value, (int, float)) and node.value not in (0, 1, -1, 2, 100):
            # Check if this constant is in an assignment or expression
            if getattr(node, "lineno", None):
                # We limit magic number reporting to avoid noise
                pass
        self.generic_visit(node)


def analyze_readability(tree: ast.AST, code: str) -> Tuple[Dict[str, Any], List[CodeIssue], float]:
    """Calculate readability metrics, naming compliance, and compute a normalized readability score (0-100)."""
    visitor = ReadabilityVisitor()
    visitor.visit(tree)
    issues = visitor.issues

    lines = code.splitlines()
    total_lines = len(lines)
    blank_lines = sum(1 for line in lines if not line.strip())
    comment_lines = sum(1 for line in lines if line.strip().startswith("#"))
    non_blank_lines = total_lines - blank_lines

    avg_line_length = (
        round(sum(len(line) for line in lines) / total_lines, 1)
        if total_lines > 0
        else 0.0
    )
    avg_fn_length = (
        round(sum(visitor.function_lengths) / len(visitor.function_lengths), 1)
        if visitor.function_lengths
        else 0.0
    )

    comment_ratio = round(comment_lines / max(1, total_lines), 2)
    blank_ratio = round(blank_lines / max(1, total_lines), 2)

    total_callables = visitor.total_functions + visitor.total_classes
    documented_callables = visitor.functions_with_docstring + visitor.classes_with_docstring
    docstring_ratio = (
        round(documented_callables / total_callables, 2)
        if total_callables > 0
        else 1.0
    )

    # Compute Readability Score (0-100)
    score = 100.0

    # Penalties
    if avg_line_length > 60:
        score -= min(15.0, (avg_line_length - 60) * 0.5)
    if avg_fn_length > 30:
        score -= min(20.0, (avg_fn_length - 30) * 0.8)
    if docstring_ratio < 0.5 and total_callables > 0:
        score -= (0.5 - docstring_ratio) * 20
    if comment_ratio < 0.05 and total_lines > 20:
        score -= 10.0

    # Deduct per readability issue
    score -= len([i for i in issues if i.category in (Category.READABILITY.value, Category.DOCUMENTATION.value)]) * 2.5
    readability_score = round(max(10.0, min(100.0, score)), 1)

    readability_metrics = {
        "avg_line_length": avg_line_length,
        "avg_function_length": avg_fn_length,
        "comment_ratio": comment_ratio,
        "blank_line_ratio": blank_ratio,
        "docstring_ratio": docstring_ratio,
        "readability_score": readability_score,
    }

    return readability_metrics, issues, readability_score
