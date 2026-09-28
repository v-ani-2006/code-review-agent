import html
from typing import Any, Dict, List, Optional
import orjson


def format_plain_json(data: Any, pretty: bool = True) -> str:
    """Format data as a standard JSON string."""
    option = orjson.OPT_INDENT_2 if pretty else 0
    return orjson.dumps(data, option=option).decode("utf-8")


def format_markdown_code_block(code: str, language: str = "python") -> str:
    """Wrap code inside markdown syntax highlighting fences."""
    clean_code = code.strip()
    return f"```{language}\n{clean_code}\n```"


def format_html_safe_markdown(text: str) -> str:
    """Escape unsafe HTML tags while preserving basic markdown readability."""
    if not text:
        return ""
    # Escape script and style tags specifically or html entities
    # To keep markdown legible while preventing XSS when rendered in HTML:
    return html.escape(text, quote=False)


def format_bullet_list(items: List[str], prefix: str = "-") -> str:
    """Format a list of strings into markdown bullet points."""
    if not items:
        return ""
    return "\n".join(f"{prefix} {item.strip()}" for item in items if item.strip())


def format_review_summary_markdown(
    summary: str,
    overall_assessment: Optional[str] = None,
    strengths: Optional[List[str]] = None,
    critical_issues: Optional[List[str]] = None,
    next_steps: Optional[List[str]] = None,
) -> str:
    """Assemble structured review findings into a unified executive markdown document."""
    parts = []
    if summary:
        parts.append(f"## Executive Summary\n\n{summary.strip()}")

    if overall_assessment:
        parts.append(f"## Overall Assessment\n\n{overall_assessment.strip()}")

    if strengths:
        parts.append("### Key Strengths\n\n" + format_bullet_list(strengths))

    if critical_issues:
        parts.append("### Critical Issues & Vulnerabilities\n\n" + format_bullet_list(critical_issues))

    if next_steps:
        parts.append("### Actionable Next Steps\n\n" + format_bullet_list(next_steps))

    return "\n\n".join(parts)
