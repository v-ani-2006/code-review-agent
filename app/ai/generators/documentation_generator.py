from datetime import datetime, timezone
import time
from typing import Any, Dict, Optional

from app.ai.markdown_formatter import render_markdown_template
from app.ai.parser import extract_json_fragment, safe_parse_json
from app.ai.providers.provider_factory import get_ai_provider
from app.core.logging import logger


class DocumentationGenerator:
    """Generates complete technical and API Markdown documentation for modules and packages."""

    def __init__(self, model: Optional[str] = None):
        self.model = model
        self.provider = get_ai_provider(model=model)

    async def generate(
        self,
        code: str,
        filename: str = "main.py",
        language: str = "python",
        include_api_doc: bool = True,
    ) -> Dict[str, Any]:
        """Generate comprehensive module and API documentation."""
        start_time = time.perf_counter()
        logger.info("DocumentationGenerator started for '%s' (%s)", filename, language)

        prompt = f"""You are a Lead Technical Writer and Software Architect.
Generate complete technical documentation for the following {language} file: `{filename}`.

### SOURCE CODE:
```{language}
{code}
```

### INSTRUCTIONS:
Analyze the code and output your response in valid JSON matching this schema:
{{
  "module_overview": "Comprehensive explanation of package/module purpose, architecture, and roles",
  "classes": [
    {{
      "name": "ClassName",
      "docstring": "Detailed class documentation",
      "attributes": [{{"name": "attr_name", "type": "str", "description": "Purpose"}}],
      "methods": [{{"name": "method_name", "params": "self, a, b", "docstring": "Method summary"}}]
    }}
  ],
  "functions": [
    {{
      "name": "function_name",
      "signature": "param1: int, param2: str = 'default' -> bool",
      "docstring": "Purpose of function",
      "parameters": [{{"name": "param1", "type": "int", "default": null, "description": "Param purpose"}}],
      "return_type": "bool",
      "return_description": "What is returned",
      "raises": [{{"exception": "ValueError", "description": "When param1 is negative"}}],
      "example": "# Example snippet\\nresult = function_name(10)"
    }}
  ],
  "usage_examples": "# Practical usage workflow\\nfrom {filename.replace('.py', '')} import ...\\n"
}}

Output only the JSON block without markdown fences or outside commentary.
"""
        provider_resp = await self.provider._generate_response(prompt)
        duration = round(time.perf_counter() - start_time, 4)

        data = provider_resp.parsed_json or {}
        if not data:
            data = extract_json_fragment(provider_resp.raw_text) or {}

        # Render into markdown template
        template_context = {
            "module_name": filename.replace(".py", "").title(),
            "filename": filename,
            "language": language,
            "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
            "module_overview": data.get("module_overview", "Module technical documentation."),
            "classes": data.get("classes", []),
            "functions": data.get("functions", []),
            "usage_examples": data.get("usage_examples", "# See function documentation above"),
        }

        try:
            markdown_content = render_markdown_template("documentation_template.md", template_context)
        except Exception as exc:
            logger.warning("Failed to render documentation_template.md: %s", str(exc))
            markdown_content = provider_resp.raw_text

        return {
            "success": provider_resp.success,
            "markdown": markdown_content,
            "data": data,
            "model_used": provider_resp.model_used,
            "processing_time": duration,
        }
