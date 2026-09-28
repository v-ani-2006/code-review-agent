import time
from typing import Any, Dict, List, Optional

from app.ai.formatter import format_bullet_list
from app.ai.parser import extract_json_fragment
from app.ai.providers.provider_factory import get_ai_provider
from app.core.logging import logger


class SummaryGenerator:
    """Generates concise, high-impact executive summaries for code reviews and audits."""

    def __init__(self, model: Optional[str] = None):
        self.model = model
        self.provider = get_ai_provider(model=model)

    async def generate(
        self,
        code: str,
        filename: str = "main.py",
        language: str = "python",
        static_summary: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate executive summary containing overall quality, risks, strengths, and roadmap."""
        start_time = time.perf_counter()
        logger.info("SummaryGenerator started for '%s'", filename)

        static_hint = f"\nStatic Analysis Summary: {static_summary}" if static_summary else ""

        prompt = f"""You are a VP of Engineering and Technical Advisory Specialist.
Generate an executive briefing summary for the following {language} file: `{filename}`.{static_hint}

### SOURCE CODE:
```{language}
{code}
```

### INSTRUCTIONS:
Evaluate the code at an executive level.
Output your response in valid JSON matching this schema:
{{
  "overall_quality": "High-level rating and qualitative assessment of production readiness",
  "major_risks": [
    "Security vulnerability or critical reliability risk 1",
    ...
  ],
  "major_strengths": [
    "Key architectural strength or good engineering practice 1",
    ...
  ],
  "improvement_roadmap": [
    "Action item 1 to achieve production excellence",
    ...
  ]
}}

Output only the JSON block without markdown fences or outside commentary.
"""
        provider_resp = await self.provider._generate_response(prompt)
        duration = round(time.perf_counter() - start_time, 4)

        data = provider_resp.parsed_json or {}
        if not data:
            data = extract_json_fragment(provider_resp.raw_text) or {}

        overall_quality = data.get("overall_quality", "Code evaluated with moderate architectural maturity.")
        risks = data.get("major_risks", [])
        strengths = data.get("major_strengths", [])
        roadmap = data.get("improvement_roadmap", [])

        # Build clean markdown executive summary
        md_sections = [
            f"# Executive Code Review Summary: `{filename}`\n",
            f"### 🎯 Overall Quality\n{overall_quality}\n",
            f"### 🛡️ Major Risks\n" + (format_bullet_list(risks) or "- *No critical risks detected.*") + "\n",
            f"### ✨ Major Strengths\n" + (format_bullet_list(strengths) or "- *Standard implementation patterns.*") + "\n",
            f"### 🗺️ Improvement Roadmap\n" + (format_bullet_list(roadmap, prefix="1.") or "1. Maintain testing coverage."),
        ]
        markdown_summary = "\n".join(md_sections)

        return {
            "success": provider_resp.success,
            "markdown": markdown_summary,
            "overall_quality": overall_quality,
            "major_risks": risks,
            "major_strengths": strengths,
            "improvement_roadmap": roadmap,
            "model_used": provider_resp.model_used,
            "processing_time": duration,
        }
