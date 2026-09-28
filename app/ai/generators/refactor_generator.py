import time
from typing import Any, Dict, List, Optional

from app.ai.parser import extract_first_code_block, extract_json_fragment
from app.ai.providers.provider_factory import get_ai_provider
from app.core.logging import logger


class RefactorGenerator:
    """Generates clean, idiomatic, refactored code removing code smells and duplicates."""

    def __init__(self, model: Optional[str] = None):
        self.model = model
        self.provider = get_ai_provider(model=model)

    async def generate(
        self,
        code: str,
        filename: str = "main.py",
        language: str = "python",
        focus_areas: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Perform automated refactoring on provided source code."""
        start_time = time.perf_counter()
        logger.info("RefactorGenerator started for '%s' (%s)", filename, language)

        focus_str = ", ".join(focus_areas) if focus_areas else "cleanliness, readability, modularization, performance"

        prompt = f"""You are a Principal Software Refactoring Architect and Clean Code Evangelist.
Refactor the following {language} code for file `{filename}` focusing on: {focus_str}.

### OBJECTIVES:
1. Pythonic idioms (list comprehensions, walrus operator, pattern matching, context managers).
2. Descriptive, consistent naming adhering to PEP 8.
3. Modularization: break down monolith functions (>30 lines) into cohesive helper functions.
4. Remove duplicate code and extract reusable logic.
5. Algorithmic efficiency & memory optimization.
6. Preserve exact behavior, inputs, outputs, and public API.

### SOURCE CODE TO REFACTOR:
```{language}
{code}
```

### INSTRUCTIONS:
Output your response in valid JSON matching this schema:
{{
  "refactored_code": "Complete, production-ready, refactored source code",
  "improvements": [
    {{"category": "Naming", "description": "Renamed cryptic single-letter variables to descriptive identifiers"}},
    {{"category": "Modularization", "description": "Extracted calculation logic into helper function _calculate_rate"}},
    {{"category": "Performance", "description": "Replaced linear lookup with O(1) set membership"}}
  ],
  "summary": "High-level summary of architectural refactoring achievements"
}}

Output only the JSON block without markdown fences or outside commentary.
"""
        provider_resp = await self.provider._generate_response(prompt)
        duration = round(time.perf_counter() - start_time, 4)

        data = provider_resp.parsed_json or {}
        if not data:
            data = extract_json_fragment(provider_resp.raw_text) or {}

        refactored = data.get("refactored_code") or extract_first_code_block(provider_resp.raw_text) or code

        return {
            "success": provider_resp.success,
            "original_code": code,
            "refactored_code": refactored,
            "improvements": data.get("improvements", []),
            "summary": data.get("summary", "Code successfully refactored for clarity and performance."),
            "model_used": provider_resp.model_used,
            "processing_time": duration,
        }
