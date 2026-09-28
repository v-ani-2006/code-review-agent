import html
import re
from typing import Any, Dict, Optional
import orjson

from app.ai.html_formatter import convert_markdown_to_html
from app.ai.markdown_formatter import format_to_clean_markdown, render_markdown_template
from app.core.logging import logger


class ExportEngine:
    """Core export engine for transforming reviews and analysis artifacts into downloadable formats."""

    @staticmethod
    def to_json(data: Any, pretty: bool = True) -> str:
        """Export data as serialized JSON string."""
        option = orjson.OPT_INDENT_2 if pretty else 0
        return orjson.dumps(data, option=option).decode("utf-8")

    @staticmethod
    def to_markdown(report_data: Dict[str, Any], template_name: str = "report_template.md") -> str:
        """Render report data into clean GitHub-flavored markdown."""
        try:
            return render_markdown_template(template_name, report_data)
        except Exception as exc:
            logger.warning("Template rendering failed, formatting raw report: %s", str(exc))
            # Fallback basic markdown
            lines = [f"# Code Review Report: {report_data.get('filename', 'Source Code')}\n"]
            if "summary" in report_data:
                lines.append(f"## Summary\n{report_data['summary']}\n")
            if "scores" in report_data:
                lines.append(f"## Scores\n```json\n{orjson.dumps(report_data['scores'], option=orjson.OPT_INDENT_2).decode('utf-8')}\n```\n")
            return format_to_clean_markdown("\n".join(lines))

    @staticmethod
    def to_html(markdown_content: str, title: str = "CodePilot AI Code Review Report") -> str:
        """Render markdown into complete, modern, responsive HTML."""
        return convert_markdown_to_html(markdown_content, title=title)

    @staticmethod
    def to_plain_text(markdown_content: str) -> str:
        """Strip markdown syntax to create clean plain text."""
        # Strip header markers (#, ##)
        text = re.sub(r"^#{1,6}\s+", "", markdown_content, flags=re.MULTILINE)
        # Strip bold/italic (*, _)
        text = re.sub(r"[\*_]{1,2}(.*?)[_\*]{1,2}", r"\1", text)
        # Strip code blocks
        text = re.sub(r"```[a-zA-Z0-9_-]*\n?(.*?)\n?```", r"\1", text, flags=re.DOTALL)
        # Strip inline code
        text = re.sub(r"`([^`]+)`", r"\1", text)
        # Strip images/links [text](url) -> text
        text = re.sub(r"!\[(.*?)\]\(.*?\)", r"\1", text)
        text = re.sub(r"\[(.*?)\]\(.*?\)", r"\1", text)
        return text.strip() + "\n"


# Singleton export engine
export_engine = ExportEngine()
