import time
from typing import Any, Dict, Optional

from app.ai.parser import extract_first_code_block, extract_json_fragment
from app.ai.providers.provider_factory import get_ai_provider
from app.core.logging import logger


class DocstringGenerator:
    """Generates standardized docstrings adhering to Google, NumPy, or Sphinx conventions."""

    def __init__(self, model: Optional[str] = None):
        self.model = model
        self.provider = get_ai_provider(model=model)

    async def generate(
        self,
        code: str,
        style: str = "google",
        include_inline_comments: bool = False,
        filename: str = "main.py",
        language: str = "python",
    ) -> Dict[str, Any]:
        """Generate annotated code with requested docstring style."""
        start_time = time.perf_counter()
        normalized_style = style.lower().strip()
        if normalized_style not in ("google", "numpy", "sphinx"):
            normalized_style = "google"

        logger.info("DocstringGenerator started for '%s' (Style: %s, Inline comments: %s)", filename, normalized_style, include_inline_comments)

        inline_instruction = (
            "Also add clear, concise inline comments explaining complex algorithm steps or critical logic."
            if include_inline_comments
            else "Do NOT add unnecessary inline comments; focus purely on comprehensive docstrings."
        )

        prompt = f"""You are a Python Documentation Architect and PEP 257 Specialist.
Annotate the following {language} code by generating complete `{normalized_style}` style docstrings for every module, class, method, and function.

### CONVENTIONS:
- Style: `{normalized_style}` convention (e.g. Args/Returns/Raises for Google, Parameters/Returns for NumPy, :param/:return: for Sphinx).
- {inline_instruction}
- Retain all original logic, variable names, and function bodies exactly as written.

### SOURCE CODE TO ANNOTATE:
```{language}
{code}
```

### INSTRUCTIONS:
Output your response in valid JSON matching this schema:
{{
  "annotated_code": "Full source code with all generated docstrings and annotations inserted",
  "style_used": "{normalized_style}",
  "docstring_count": 3,
  "summary": "Summary of docstrings added"
}}

Output only the JSON block without markdown fences or outside commentary.
"""
        provider_resp = await self.provider._generate_response(prompt)
        duration = round(time.perf_counter() - start_time, 4)

        data = provider_resp.parsed_json or {}
        if not data:
            data = extract_json_fragment(provider_resp.raw_text) or {}

        annotated_code = data.get("annotated_code") or extract_first_code_block(provider_resp.raw_text) or code

        return {
            "success": provider_resp.success,
            "annotated_code": annotated_code,
            "style_used": normalized_style,
            "summary": data.get("summary", f"Generated {normalized_style} docstrings."),
            "model_used": provider_resp.model_used,
            "processing_time": duration,
        }
