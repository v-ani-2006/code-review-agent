import re
from typing import Any, Dict, List, Optional
import orjson


def normalize_whitespace(text: str) -> str:
    """Normalize line endings, remove trailing whitespace, and collapse excessive blank lines."""
    if not text:
        return ""
    # Normalize CRLF to LF
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    # Remove trailing spaces on lines
    lines = [line.rstrip() for line in text.split("\n")]
    normalized = "\n".join(lines)
    # Collapse 3 or more consecutive newlines into 2
    return re.sub(r"\n{3,}", "\n\n", normalized).strip()


def clean_markdown_fences(text: str) -> str:
    """Remove outer markdown code fences (```json or ```python or ```) if wrapping the entire string."""
    cleaned = text.strip()
    fence_pattern = re.compile(r"^```[a-zA-Z0-9_-]*\s*\n?(.*?)\n?```$", re.DOTALL)
    match = fence_pattern.match(cleaned)
    if match:
        return match.group(1).strip()
    return cleaned


def extract_code_blocks(text: str) -> List[Dict[str, str]]:
    """Extract all fenced code blocks with language identifiers from markdown text."""
    pattern = re.compile(r"```([a-zA-Z0-9_-]*)\n(.*?)```", re.DOTALL)
    blocks = []
    for match in pattern.finditer(text):
        lang = match.group(1).strip() or "text"
        code = match.group(2).rstrip()
        blocks.append({"language": lang, "code": code})
    return blocks


def extract_first_code_block(text: str, default_lang: str = "python") -> str:
    """Extract code from the first markdown code block, or return sanitized text if no fences found."""
    blocks = extract_code_blocks(text)
    if blocks:
        return blocks[0]["code"]
    return clean_markdown_fences(text)


def extract_bullet_points(text: str) -> List[str]:
    """Extract bullet point items (- item, * item, 1. item) from markdown text."""
    bullets: List[str] = []
    for line in text.split("\n"):
        line = line.strip()
        # Match - item, * item, + item, or numbered list 1. item
        match = re.match(r"^(?:[\*\-\+]|\d+\.)\s+(.+)$", line)
        if match:
            item = match.group(1).strip()
            if item:
                bullets.append(item)
    return bullets


def extract_json_fragment(text: str) -> Optional[Dict[str, Any]]:
    """Extract and parse structured JSON from text, accommodating code fences, raw JSON, or substrings."""
    if not text or not text.strip():
        return None

    # Step 1: Strip surrounding markdown code blocks if present
    candidate = clean_markdown_fences(text)

    # Step 2: Try direct parse
    try:
        return orjson.loads(candidate.encode("utf-8"))
    except Exception:
        pass

    # Step 3: Search for outermost curly braces {...}
    brace_pattern = re.compile(r"(\{.*\})", re.DOTALL)
    match = brace_pattern.search(text)
    if match:
        json_str = match.group(1).strip()
        try:
            return orjson.loads(json_str.encode("utf-8"))
        except Exception:
            # Handle potential trailing commas or formatting quirks
            try:
                # Basic cleanup: remove trailing commas before closing braces/brackets
                cleaned_json = re.sub(r",\s*([\]}])", r"\1", json_str)
                return orjson.loads(cleaned_json.encode("utf-8"))
            except Exception:
                pass

    return None


def safe_parse_json(text: str, fallback: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Safely parse JSON or return a designated fallback dict when parsing fails."""
    parsed = extract_json_fragment(text)
    if parsed is not None:
        return parsed
    return fallback if fallback is not None else {}
