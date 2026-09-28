import ast
from typing import Any, Dict, List, Tuple

from app.ai.constants import MAX_LINE_LENGTH, Category, Severity
from app.schemas.review import CodeIssue


class StyleAndBugVisitor(ast.NodeVisitor):
    """AST visitor detecting common Python bugs, anti-patterns, and code smells."""

    def __init__(self):
        self.issues: List[CodeIssue] = []

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._check_mutable_defaults(node)
        self._check_unreachable_code(node.body)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._check_mutable_defaults(node)
        self._check_unreachable_code(node.body)
        self.generic_visit(node)

    def _check_mutable_defaults(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        """Detect mutable objects (list, dict, set) as default parameter values."""
        for default in node.args.defaults + node.args.kw_defaults:
            if default is None:
                continue
            if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                self.issues.append(
                    CodeIssue(
                        id="BUG-001",
                        title=f"Mutable Default Argument in '{node.name}'",
                        description=f"Function '{node.name}' uses a mutable default argument. Default objects are instantiated once and shared across calls.",
                        severity=Severity.HIGH.value,
                        category=Category.BUG.value,
                        line_number=default.lineno,
                        column=default.col_offset,
                        suggestion="Set the default parameter value to None and initialize inside the function: if arg is None: arg = []",
                    )
                )

    def _check_unreachable_code(self, body: List[ast.stmt]) -> None:
        """Detect statements appearing after return, raise, break, or continue."""
        for i, stmt in enumerate(body[:-1]):
            if isinstance(stmt, (ast.Return, ast.Raise, ast.Break, ast.Continue)):
                next_stmt = body[i + 1]
                self.issues.append(
                    CodeIssue(
                        id="BUG-004",
                        title="Unreachable Code Detected",
                        description="Statements exist after a terminal control-flow statement (return, raise, break).",
                        severity=Severity.MEDIUM.value,
                        category=Category.BUG.value,
                        line_number=next_stmt.lineno,
                        column=next_stmt.col_offset,
                        suggestion="Remove or refactor the unreachable statements.",
                    )
                )
                break

    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> None:
        # 1. Bare except:
        if node.type is None:
            self.issues.append(
                CodeIssue(
                    id="BUG-002",
                    title="Bare Except Clause: 'except:'",
                    description="Bare except catches system exit signals (KeyboardInterrupt, SystemExit) and hides fatal bugs.",
                    severity=Severity.HIGH.value,
                    category=Category.BUG.value,
                    line_number=node.lineno,
                    column=node.col_offset,
                    suggestion="Catch specific exceptions like 'except ValueError:' or at minimum 'except Exception:'.",
                )
            )

        # 2. Empty except block: except ...: pass
        if len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
            self.issues.append(
                CodeIssue(
                    id="BUG-005",
                    title="Silenced Exception with 'except: pass'",
                    description="Exceptions are silently ignored, preventing error tracking and masking failures.",
                    severity=Severity.MEDIUM.value,
                    category=Category.BUG.value,
                    line_number=node.lineno,
                    column=node.col_offset,
                    suggestion="Log the exception using logger.exception() or handle it explicitly.",
                )
            )

        self.generic_visit(node)

    def visit_Compare(self, node: ast.Compare) -> None:
        """Detect comparison to None using == None or != None."""
        for op, comparator in zip(node.ops, node.comparators):
            if isinstance(op, (ast.Eq, ast.NotEq)):
                if isinstance(comparator, ast.Constant) and comparator.value is None:
                    correct_op = "is None" if isinstance(op, ast.Eq) else "is not None"
                    self.issues.append(
                        CodeIssue(
                            id="BUG-003",
                            title="Comparison to None using Equality Operator",
                            description="Singleton object 'None' should be compared using identity 'is', not equality '=='.",
                            severity=Severity.LOW.value,
                            category=Category.STYLE.value,
                            line_number=node.lineno,
                            column=node.col_offset,
                            suggestion=f"Replace with '{correct_op}'.",
                        )
                    )
        self.generic_visit(node)

    def visit_If(self, node: ast.If) -> None:
        """Detect duplicate branch conditions in if-elif chains."""
        conditions: List[str] = []
        current = node
        while isinstance(current, ast.If):
            cond_str = ast.dump(current.test)
            if cond_str in conditions:
                self.issues.append(
                    CodeIssue(
                        id="BUG-006",
                        title="Duplicate Conditional Branch in 'if/elif'",
                        description="Identical test expression appears multiple times in the conditional chain.",
                        severity=Severity.HIGH.value,
                        category=Category.BUG.value,
                        line_number=current.lineno,
                        column=current.col_offset,
                        suggestion="Remove the redundant elif condition or fix the intended test variable.",
                    )
                )
            conditions.append(cond_str)
            if len(current.orelse) == 1 and isinstance(current.orelse[0], ast.If):
                current = current.orelse[0]
            else:
                break
        self.generic_visit(node)


def analyze_style_and_bugs(tree: ast.AST, code: str) -> Tuple[Dict[str, Any], List[CodeIssue]]:
    """Perform stylistic, PEP 8, and bug detection checks."""
    # 1. AST-based bug checks
    visitor = StyleAndBugVisitor()
    visitor.visit(tree)
    issues = visitor.issues

    # 2. Line-by-line stylistic checks
    lines = code.splitlines()
    todo_count = 0
    long_lines_count = 0
    trailing_whitespace_count = 0
    tabs_detected = False

    for idx, line in enumerate(lines, start=1):
        # A. Line length
        if len(line) > MAX_LINE_LENGTH:
            long_lines_count += 1
            if long_lines_count <= 3:  # Report first few to avoid flooding
                issues.append(
                    CodeIssue(
                        id="STY-001",
                        title=f"Line Exceeds {MAX_LINE_LENGTH} Characters ({len(line)} chars)",
                        description="Line length exceeds the PEP 8 / Black standard limit of 88 characters.",
                        severity=Severity.LOW.value,
                        category=Category.STYLE.value,
                        line_number=idx,
                        column=MAX_LINE_LENGTH,
                        suggestion="Break long expressions, lists, or function arguments across multiple lines.",
                    )
                )

        # B. Trailing whitespace
        if line.endswith(" ") or line.endswith("\t"):
            trailing_whitespace_count += 1
            if trailing_whitespace_count <= 2:
                issues.append(
                    CodeIssue(
                        id="STY-002",
                        title="Trailing Whitespace",
                        description="Line contains unnecessary trailing whitespace.",
                        severity=Severity.LOW.value,
                        category=Category.STYLE.value,
                        line_number=idx,
                        column=len(line),
                        suggestion="Trim trailing spaces.",
                    )
                )

        # C. Tabs vs spaces
        if "\t" in line and not tabs_detected:
            tabs_detected = True
            issues.append(
                CodeIssue(
                    id="STY-003",
                    title="Tab Character Used for Indentation",
                    description="PEP 8 recommends 4 spaces per indentation level instead of tab characters.",
                    severity=Severity.LOW.value,
                    category=Category.STYLE.value,
                    line_number=idx,
                    column=line.find("\t"),
                    suggestion="Configure your editor to convert tabs to 4 spaces.",
                )
            )

        # D. Multiple statements on single line via semicolon
        if ";" in line and not line.strip().startswith("#"):
            issues.append(
                CodeIssue(
                    id="STY-004",
                    title="Multiple Statements on Single Line",
                    description="Using ';' to separate multiple statements on a single line harms code readability.",
                    severity=Severity.LOW.value,
                    category=Category.STYLE.value,
                    line_number=idx,
                    column=line.find(";"),
                    suggestion="Separate statements onto individual lines.",
                )
            )

        # E. TODO / FIXME markers
        upper_line = line.upper()
        if "#" in line:
            comment_part = line[line.find("#"):]
            if "TODO" in comment_part or "FIXME" in comment_part or "HACK" in comment_part or "XXX" in comment_part:
                todo_count += 1

    style_summary = {
        "long_lines_count": long_lines_count,
        "trailing_whitespace_count": trailing_whitespace_count,
        "tabs_detected": tabs_detected,
        "todo_markers_count": todo_count,
    }

    return style_summary, issues
