from pathlib import Path
from typing import Optional

EXTENSION_LANGUAGE_MAP = {
    ".py": "python",
    ".pyw": "python",
    ".pyi": "python",
    # Extensible architecture for future phases
    ".js": "javascript",
    ".ts": "typescript",
    ".jsx": "javascript",
    ".tsx": "typescript",
    ".go": "go",
    ".rs": "rust",
    ".java": "java",
    ".cpp": "cpp",
    ".c": "c",
}

# Currently supported analysis languages
SUPPORTED_ANALYSIS_LANGUAGES = {"python"}


def detect_language_from_filename(filename: str) -> Optional[str]:
    """Determine programming language identifier from file extension."""
    suffix = Path(filename).suffix.lower()
    return EXTENSION_LANGUAGE_MAP.get(suffix)


def is_supported_language(language_or_ext: str) -> bool:
    """Validate whether language or extension is supported by the active code analysis engine."""
    clean = language_or_ext.lower().strip()
    if clean.startswith("."):
        detected = detect_language_from_filename(clean)
        return detected in SUPPORTED_ANALYSIS_LANGUAGES
    return clean in SUPPORTED_ANALYSIS_LANGUAGES
