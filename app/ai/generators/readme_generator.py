import time
from typing import Any, Dict, List, Optional

from app.ai.markdown_formatter import render_markdown_template
from app.ai.parser import extract_json_fragment
from app.ai.providers.provider_factory import get_ai_provider
from app.core.logging import logger


class ReadmeGenerator:
    """Generates comprehensive, professional GitHub README.md files."""

    def __init__(self, model: Optional[str] = None):
        self.model = model
        self.provider = get_ai_provider(model=model)

    async def generate(
        self,
        project_name: str,
        description: str,
        code_context: Optional[str] = None,
        endpoints: Optional[List[Dict[str, str]]] = None,
        tech_stack: Optional[List[Dict[str, str]]] = None,
    ) -> Dict[str, Any]:
        """Generate full GitHub README markdown."""
        start_time = time.perf_counter()
        logger.info("ReadmeGenerator started for '%s'", project_name)

        code_snippet = f"\n### SAMPLE REPOSITORY CODE:\n```python\n{code_context[:2500]}\n```" if code_context else ""

        prompt = f"""You are a Developer Relations Engineer and Open Source Documentation Specialist.
Generate structured information for a comprehensive GitHub README for project: `{project_name}`.

### PROJECT OVERVIEW:
- Name: {project_name}
- Description: {description}
{code_snippet}

### INSTRUCTIONS:
Analyze the project and output your response in valid JSON matching this schema:
{{
  "features": [
    {{"name": "Feature Title", "description": "Concise value proposition"}}
  ],
  "architecture_summary": "Paragraph describing high-level architecture, modules, and component interactions",
  "folder_structure": "app/\\n├── api/\\n├── core/\\n├── models/\\n├── services/\\n└── main.py",
  "tech_stack": [
    {{"category": "Backend Framework", "name": "FastAPI", "description": "High performance async web framework"}},
    {{"category": "Database ORM", "name": "SQLAlchemy 2.x", "description": "Async relational database abstraction"}}
  ],
  "endpoints": [
    {{"method": "POST", "path": "/api/resource", "description": "Creates resource", "auth": "Bearer"}}
  ],
  "roadmap": [
    {{"title": "OAuth2 Social Login", "description": "Add GitHub and Google OAuth2 support", "done": false}},
    {{"title": "Core AI Reasoning", "description": "AST static analysis and LLM reviews", "done": true}}
  ]
}}

Output only the JSON block without markdown fences or outside commentary.
"""
        provider_resp = await self.provider._generate_response(prompt)
        duration = round(time.perf_counter() - start_time, 4)

        data = provider_resp.parsed_json or {}
        if not data:
            data = extract_json_fragment(provider_resp.raw_text) or {}

        slug = project_name.lower().replace(" ", "-").replace("_", "-")
        template_context = {
            "project_name": project_name,
            "project_slug": slug,
            "description": description,
            "features": data.get("features", [{"name": "Automated Analysis", "description": "Instant code review and scoring."}]),
            "architecture_summary": data.get("architecture_summary", "Modern modular microservice backend."),
            "folder_structure": data.get("folder_structure", "app/\n├── api/\n└── main.py"),
            "tech_stack": tech_stack or data.get("tech_stack", [
                {"category": "Framework", "name": "FastAPI", "description": "Python async framework"},
                {"category": "Database", "name": "PostgreSQL", "description": "Relational database"},
            ]),
            "endpoints": endpoints or data.get("endpoints", [
                {"method": "GET", "path": "/health", "description": "Health status probe", "auth": "No"}
            ]),
            "roadmap": data.get("roadmap", [
                {"title": "Phase 1: Foundation", "description": "Core architecture", "done": true},
                {"title": "Phase 2: Production Scale", "description": "Performance optimizations", "done": false},
            ]),
        }

        try:
            readme_markdown = render_markdown_template("readme_template.md", template_context)
        except Exception as exc:
            logger.warning("Failed to render readme_template.md: %s", str(exc))
            readme_markdown = provider_resp.raw_text

        return {
            "success": provider_resp.success,
            "markdown": readme_markdown,
            "model_used": provider_resp.model_used,
            "processing_time": duration,
        }
