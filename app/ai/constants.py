from enum import Enum
from typing import Dict, List


class Severity(str, Enum):
    """Issue severity levels according to impact and urgency."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class Category(str, Enum):
    """Categorical classification of static code analysis findings."""
    STYLE = "STYLE"
    BUG = "BUG"
    SECURITY = "SECURITY"
    COMPLEXITY = "COMPLEXITY"
    READABILITY = "READABILITY"
    DOCUMENTATION = "DOCUMENTATION"
    PERFORMANCE = "PERFORMANCE"
    BEST_PRACTICE = "BEST_PRACTICE"


# Supported Programming Languages
SUPPORTED_LANGUAGES: List[str] = ["python"]

# Static Analysis Threshold Constants
MAX_LINE_LENGTH = 88
MAX_FUNCTION_LINES = 50
MAX_FUNCTION_PARAMS = 5
MAX_CYCLOMATIC_COMPLEXITY = 10
CRITICAL_CYCLOMATIC_COMPLEXITY = 20
MAX_CLASS_METHODS = 15
MAX_CLASS_LINES = 300

# Builtin names to detect shadowing
BUILTIN_NAMES = {
    "abs", "all", "any", "ascii", "bin", "bool", "bytearray", "bytes", "callable",
    "chr", "classmethod", "compile", "complex", "delattr", "dict", "dir", "divmod",
    "enumerate", "eval", "exec", "filter", "float", "format", "frozenset", "getattr",
    "globals", "hasattr", "hash", "help", "hex", "id", "input", "int", "isinstance",
    "issubclass", "iter", "len", "list", "locals", "map", "max", "memoryview", "min",
    "next", "object", "oct", "open", "ord", "pow", "print", "property", "range",
    "repr", "reversed", "round", "set", "setattr", "slice", "sorted", "staticmethod",
    "str", "sum", "super", "tuple", "type", "vars", "zip"
}

# Standard Library Modules for Import Categorization
STDLIB_MODULES = {
    "abc", "argparse", "array", "ast", "asyncio", "base64", "collections", "contextlib",
    "copy", "csv", "dataclasses", "datetime", "decimal", "difflib", "enum", "errno",
    "functools", "gc", "hashlib", "http", "io", "itertools", "json", "logging", "math",
    "multiprocessing", "os", "pathlib", "pickle", "random", "re", "secrets", "shutil",
    "socket", "sqlite3", "ssl", "string", "subprocess", "sys", "tempfile", "threading",
    "time", "traceback", "typing", "unittest", "urllib", "uuid", "warnings", "weakref", "xml"
}

# Master Rules Catalog for GET /review/rules
ANALYSIS_RULES: List[Dict[str, str]] = [
    {
        "id": "SEC-001",
        "name": "eval/exec Execution",
        "category": Category.SECURITY.value,
        "severity": Severity.CRITICAL.value,
        "description": "Direct execution of arbitrary code via eval() or exec().",
        "suggestion": "Replace dynamic code execution with safe parsing libraries like ast.literal_eval() or explicit mappings.",
    },
    {
        "id": "SEC-002",
        "name": "Insecure Deserialization (pickle)",
        "category": Category.SECURITY.value,
        "severity": Severity.HIGH.value,
        "description": "Deserializing untrusted data with pickle.loads() enables remote code execution.",
        "suggestion": "Use safe serialization formats like JSON, MessagePack, or Protocol Buffers.",
    },
    {
        "id": "SEC-003",
        "name": "Subprocess Shell Injection",
        "category": Category.SECURITY.value,
        "severity": Severity.CRITICAL.value,
        "description": "Calling subprocess with shell=True allows shell injection attacks.",
        "suggestion": "Pass command arguments as a list with shell=False.",
    },
    {
        "id": "SEC-004",
        "name": "Hardcoded Secrets / Tokens",
        "category": Category.SECURITY.value,
        "severity": Severity.CRITICAL.value,
        "description": "Detected potential hardcoded API keys, JWT tokens, or passwords in source code.",
        "suggestion": "Move credentials to environment variables or secret vaults like AWS Secrets Manager or HashiCorp Vault.",
    },
    {
        "id": "SEC-005",
        "name": "Weak Cryptographic Hashing",
        "category": Category.SECURITY.value,
        "severity": Severity.MEDIUM.value,
        "description": "Use of obsolete hash functions like MD5 or SHA1.",
        "suggestion": "Use SHA-256 or SHA-512 for integrity, and bcrypt or Argon2 for password hashing.",
    },
    {
        "id": "BUG-001",
        "name": "Mutable Default Argument",
        "category": Category.BUG.value,
        "severity": Severity.HIGH.value,
        "description": "Using mutable objects (list, dict, set) as default argument values causes shared state bugs.",
        "suggestion": "Use None as the default argument and initialize the mutable object inside the function body.",
    },
    {
        "id": "BUG-002",
        "name": "Bare Except Clause",
        "category": Category.BUG.value,
        "severity": Severity.HIGH.value,
        "description": "Bare except: catches system exit signals and hides programming errors.",
        "suggestion": "Catch specific exceptions like except ValueError: or at minimum except Exception:.",
    },
    {
        "id": "BUG-003",
        "name": "Comparison to None with Equality",
        "category": Category.BUG.value,
        "severity": Severity.MEDIUM.value,
        "description": "Using == None instead of is None for singleton comparison.",
        "suggestion": "Use 'is None' or 'is not None' for singleton checks.",
    },
    {
        "id": "CMP-001",
        "name": "High Cyclomatic Complexity",
        "category": Category.COMPLEXITY.value,
        "severity": Severity.HIGH.value,
        "description": "Function has cyclomatic complexity greater than threshold (10).",
        "suggestion": "Refactor deeply nested logic using early returns, polymorphism, or extract helper functions.",
    },
    {
        "id": "STY-001",
        "name": "Line Too Long",
        "category": Category.STYLE.value,
        "severity": Severity.LOW.value,
        "description": "Line length exceeds standard 88 characters (PEP 8 / Black standard).",
        "suggestion": "Split long expressions, function arguments, or strings across multiple lines.",
    },
    {
        "id": "DOC-001",
        "name": "Missing Docstring",
        "category": Category.DOCUMENTATION.value,
        "severity": Severity.LOW.value,
        "description": "Public class or function lacks an informative docstring.",
        "suggestion": "Add a descriptive docstring explaining purpose, parameters, and return types.",
    },
]
