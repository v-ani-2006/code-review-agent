from datetime import datetime, timezone
import time
from typing import Any, Dict, Optional

from app.ai.markdown_formatter import render_markdown_template
from app.ai.parser import extract_json_fragment
from app.ai.providers.provider_factory import get_ai_provider
from app.core.logging import logger


class ChangelogGenerator:
    """Generates Keep a Changelog formatted release notes by comparing two versions of source code."""

    def __init__(self, model: Optional[str] = None):
        self.model = model
        self.provider = get_ai_provider(model=model)

    async def generate(
        self,
        original_code: str,
        updated_code: str,
        filename: str = "main.py",
        version: str = "1.0.0",
    ) -> Dict[str, Any]:
        """Generate semantic changelog comparing code diffs."""
        start_time = time.perf_counter()
        logger.info("ChangelogGenerator comparing versions for '%s'", filename)

        prompt = f"""You are a Lead Software Release Engineer and Technical Communicator.
Compare the following two versions of `{filename}` and generate a precise changelog following the Keep a Changelog standard.

### ORIGINAL CODE:
```python
{original_code}
```

### UPDATED CODE:
```python
{updated_code}
```

### INSTRUCTIONS:
Categorize every difference into the 5 standard Keep a Changelog categories.
Output your response in valid JSON matching this schema:
{{
  "added": ["List of new functions, classes, arguments, or features added"],
  "changed": ["List of modified behaviors, signatures, or refactored logic"],
  "removed": ["List of deprecated or removed methods/variables"],
  "fixed": ["List of bugs, exceptions, or error handling resolved"],
  "security": ["List of security patches, sanitizations, or vulnerability fixes"]
}}

Output only the JSON block without markdown fences or outside commentary.
"""
        provider_resp = await self.provider._generate_response(prompt)
        duration = round(time.perf_counter() - start_time, 4)

        data = provider_resp.parsed_json or {}
        if not data:
            data = extract_json_fragment(provider_resp.raw_text) or {}

        template_context = {
            "filename": filename,
            "version": version,
            "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "added": data.get("added", []),
            "changed": data.get("changed", []),
            "removed": data.get("removed", []),
            "fixed": data.get("fixed", []),
            "security": data.get("security", []),
        }

        try:
            markdown_content = render_markdown_template("changelog_template.md", template_context)
        except Exception as exc:
            logger.warning("Failed to render changelog_template.md: %s", str(exc))
            markdown_content = provider_resp.raw_text

        return {
            "success": provider_resp.success,
            "markdown": markdown_content,
            "data": data,
            "model_used": provider_resp.model_used,
            "processing_time": duration,
        }
