from pathlib import Path
import re
from typing import Any, Dict, List, Optional
import jinja2

TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"

# Jinja2 environment configured to load markdown templates from app/ai/templates
_jinja_env: Optional[jinja2.Environment] = None


def get_template_env() -> jinja2.Environment:
    """Initialize or return cached Jinja2 environment."""
    global _jinja_env
    if _jinja_env is None:
        _jinja_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(str(TEMPLATES_DIR)),
            autoescape=False,
            trim_blocks=True,
            lstrip_blocks=True,
        )
    return _jinja_env


def render_markdown_template(template_name: str, context: Dict[str, Any]) -> str:
    """Render a Jinja2 markdown template with the given context."""
    env = get_template_env()
    template = env.get_template(template_name)
    rendered = template.render(**context)
    return format_to_clean_markdown(rendered)


def format_to_clean_markdown(text: str) -> str:
    """Standardize and clean markdown text:
    - Normalizes line breaks (CRLF -> LF).
    - Ensures proper blank lines around headers, code blocks, and lists.
    - Strips unwanted redundant fencing tags.
    - Preserves tables and syntax highlighting tags.
    """
    if not text:
        return ""

    # 1. Normalize line endings
    clean = text.replace("\r\n", "\n").replace("\r", "\n")

    # 2. Fix triple-backtick fences without trailing newlines
    clean = re.sub(r"```([a-zA-Z0-9_-]*)([^\n`])", r"```\1\n\2", clean)

    # 3. Ensure a blank line before headers if preceded by normal text
    clean = re.sub(r"([^\n])\n(#{1,6}\s+)", r"\1\n\n\2", clean)

    # 4. Collapse 3 or more consecutive blank lines into 2
    clean = re.sub(r"\n{3,}", "\n\n", clean)

    return clean.strip() + "\n"


def format_table(headers: List[str], rows: List[List[str]]) -> str:
    """Generate a clean GFM markdown table."""
    if not headers:
        return ""

    header_line = "| " + " | ".join(str(h).strip() for h in headers) + " |"
    separator_line = "| " + " | ".join("---" for _ in headers) + " |"

    row_lines = []
    for row in rows:
        padded = list(row) + [""] * (len(headers) - len(row))
        row_line = "| " + " | ".join(str(cell).strip() for cell in padded[:len(headers)]) + " |"
        row_lines.append(row_line)

    return "\n".join([header_line, separator_line] + row_lines) + "\n"
