import ast
import re
from typing import List

from app.ai.constants import Category, Severity
from app.schemas.review import CodeIssue

# Regex patterns for detecting hardcoded secrets, credentials, and API keys
SECRET_PATTERNS = [
    (re.compile(r"""(?i)(?:password|passwd|pwd|secret|api_key|apikey|token|access_token)\s*=\s*['"][a-zA-Z0-9_\-.~!@#$%^&*+=]{6,}['"]"""), "Hardcoded Secret/Password", Severity.CRITICAL),
    (re.compile(r"""['"][a-zA-Z0-9_\-]{20,}['"]"""), "Possible High-Entropy Secret/API Token", Severity.HIGH),
    (re.compile(r"""(?i)(?:aws_secret_access_key|private_key|client_secret)\s*=\s*['"][^'"]+['"]"""), "Hardcoded Cloud Provider Secret", Severity.CRITICAL),
]


class SecurityVisitor(ast.NodeVisitor):
    """AST visitor implementing Bandit-style static security checks."""

    def __init__(self):
        self.issues: List[CodeIssue] = []

    def visit_Call(self, node: ast.Call) -> None:
        # 1. eval() / exec() detection
        if isinstance(node.func, ast.Name):
            if node.func.id in ("eval", "exec"):
                self.issues.append(
                    CodeIssue(
                        id="SEC-001",
                        title=f"Dangerous Execution Function: '{node.func.id}()'",
                        description=f"Direct invocation of '{node.func.id}()' allows arbitrary code execution.",
                        severity=Severity.CRITICAL.value,
                        category=Category.SECURITY.value,
                        line_number=node.lineno,
                        column=node.col_offset,
                        suggestion="Replace with safe parsers like ast.literal_eval() or structured serialization.",
                    )
                )

            # 2. os.system() / os.popen() detection
        elif isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name) and node.func.value.id == "os":
                if node.func.attr in ("system", "popen", "popen2", "popen3", "popen4"):
                    self.issues.append(
                        CodeIssue(
                            id="SEC-002",
                            title=f"Insecure OS Command Execution: 'os.{node.func.attr}()'",
                            description=f"Using 'os.{node.func.attr}()' is vulnerable to command injection.",
                            severity=Severity.HIGH.value,
                            category=Category.SECURITY.value,
                            line_number=node.lineno,
                            column=node.col_offset,
                            suggestion="Use the subprocess module with shell=False and pass arguments as an explicit list.",
                        )
                    )

            # 3. pickle.loads() detection
            if isinstance(node.func.value, ast.Name) and node.func.value.id == "pickle":
                if node.func.attr in ("loads", "load"):
                    self.issues.append(
                        CodeIssue(
                            id="SEC-003",
                            title="Unsafe Deserialization: 'pickle'",
                            description="Loading untrusted pickled objects can execute arbitrary Python bytecode.",
                            severity=Severity.HIGH.value,
                            category=Category.SECURITY.value,
                            line_number=node.lineno,
                            column=node.col_offset,
                            suggestion="Use safe data serialization formats such as JSON, Protocol Buffers, or MessagePack.",
                        )
                    )

            # 4. subprocess shell=True check
            if isinstance(node.func.value, ast.Name) and node.func.value.id in ("subprocess", "Popen"):
                for keyword in node.keywords:
                    if keyword.arg == "shell" and isinstance(keyword.value, ast.Constant) and keyword.value.value is True:
                        self.issues.append(
                            CodeIssue(
                                id="SEC-004",
                                title="Subprocess Shell Injection: 'shell=True'",
                                description="Running subprocess commands with shell=True invites command injection vulnerabilities.",
                                severity=Severity.CRITICAL.value,
                                category=Category.SECURITY.value,
                                line_number=node.lineno,
                                column=node.col_offset,
                                suggestion="Set shell=False and pass the command and its arguments as a list of strings.",
                            )
                        )

            # 5. Weak hashing algorithms: hashlib.md5 or hashlib.sha1
            if isinstance(node.func.value, ast.Name) and node.func.value.id == "hashlib":
                if node.func.attr in ("md5", "sha1"):
                    self.issues.append(
                        CodeIssue(
                            id="SEC-005",
                            title=f"Weak Cryptographic Hash: 'hashlib.{node.func.attr}()'",
                            description=f"Algorithm '{node.func.attr}' is cryptographically broken and vulnerable to collision attacks.",
                            severity=Severity.MEDIUM.value,
                            category=Category.SECURITY.value,
                            line_number=node.lineno,
                            column=node.col_offset,
                            suggestion="Upgrade to secure hashing algorithms such as SHA-256 or SHA-512.",
                        )
                    )

        self.generic_visit(node)

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            if alias.name == "telnetlib":
                self.issues.append(
                    CodeIssue(
                        id="SEC-006",
                        title="Insecure Protocol: 'telnetlib'",
                        description="Telnet transmits communications in cleartext without encryption.",
                        severity=Severity.HIGH.value,
                        category=Category.SECURITY.value,
                        line_number=node.lineno,
                        column=node.col_offset,
                        suggestion="Use encrypted protocols such as SSH (paramiko, asyncssh) or TLS.",
                    )
                )
        self.generic_visit(node)

    def visit_Assert(self, node: ast.Assert) -> None:
        self.issues.append(
            CodeIssue(
                id="SEC-007",
                title="Assert Used in Runtime Code",
                description="Assert statements are completely stripped when Python is run with optimizations (-O flag).",
                severity=Severity.LOW.value,
                category=Category.SECURITY.value,
                line_number=node.lineno,
                column=node.col_offset,
                suggestion="Use explicit conditional checks and raise appropriate exceptions (e.g. ValueError).",
            )
        )
        self.generic_visit(node)


def analyze_security(tree: ast.AST, code: str) -> List[CodeIssue]:
    """Run AST and pattern-based static security checks."""
    # 1. AST Security Visitor
    visitor = SecurityVisitor()
    visitor.visit(tree)
    issues = visitor.issues

    # 2. Regex Check for Hardcoded Secrets
    lines = code.splitlines()
    for idx, line in enumerate(lines, start=1):
        # Ignore comments
        stripped = line.strip()
        if stripped.startswith("#"):
            continue

        for pattern, title, severity in SECRET_PATTERNS:
            if pattern.search(line):
                # Ensure it's not a generic placeholder
                lower_line = line.lower()
                if any(placeholder in lower_line for placeholder in ["dummy", "placeholder", "your_", "example", "env", "os.getenv"]):
                    continue

                issues.append(
                    CodeIssue(
                        id="SEC-008",
                        title=f"Potential {title}",
                        description="Detected potential hardcoded secret or token assignment in source code.",
                        severity=severity.value,
                        category=Category.SECURITY.value,
                        line_number=idx,
                        column=0,
                        suggestion="Externalize secrets to environment variables (.env) or a secret manager.",
                    )
                )
                break

    return issues
