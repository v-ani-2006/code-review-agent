from datetime import datetime, timezone
import time
from typing import Any, Dict, Optional

from app.ai.markdown_formatter import render_markdown_template
from app.ai.parser import extract_json_fragment
from app.ai.providers.provider_factory import get_ai_provider
from app.core.logging import logger


class ArchitectureGenerator:
    """Generates detailed, enterprise-grade system architecture and technical specifications."""

    def __init__(self, model: Optional[str] = None):
        self.model = model
        self.provider = get_ai_provider(model=model)

    async def generate(
        self,
        system_name: str = "CodePilot AI",
        description: Optional[str] = None,
        context_notes: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate full architecture specification document."""
        start_time = time.perf_counter()
        logger.info("ArchitectureGenerator started for system: '%s'", system_name)

        desc = description or "AI-Powered Automated Code Review and Reasoning Platform"

        prompt = f"""You are a Principal Enterprise Solutions Architect.
Generate a comprehensive technical architecture document for system: `{system_name}`.

### SYSTEM CONTEXT:
- Name: {system_name}
- Purpose: {desc}
- Additional Notes: {context_notes or 'Built with FastAPI, SQLAlchemy Async, PostgreSQL, Google Gemini, and Python AST Engine.'}

### INSTRUCTIONS:
Analyze the architectural requirements and output your response in valid JSON matching this schema:
{{
  "backend_architecture": "Detailed overview of the backend design patterns, modular boundaries, and scalability principles",
  "api_architecture": "Explanation of RESTful routing, dependency injection guards, versioning, and validation layers",
  "auth_flow": "Detailed walkthrough of OAuth2 password flow, JWT cryptographic signing, token lifespans, and role-based permissions",
  "ai_pipeline": "Step-by-step description of AST static analysis combined with Gemini LLM multi-modal semantic reasoning",
  "database_structure": "Relational schema explanation (User, Review entities), indexing strategy, and async session pool",
  "services_and_repos": "Explanation of separation of concerns between Controllers, Services, and Repositories",
  "request_lifecycle": "Step-by-step trace of a request through ProcessTimeMiddleware, exception handlers, and database commits"
}}

Output only the JSON block without markdown fences or outside commentary.
"""
        provider_resp = await self.provider._generate_response(prompt)
        duration = round(time.perf_counter() - start_time, 4)

        data = provider_resp.parsed_json or {}
        if not data:
            data = extract_json_fragment(provider_resp.raw_text) or {}

        template_context = {
            "system_name": system_name,
            "version": "0.1.0",
            "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
            "backend_architecture": data.get("backend_architecture", "Asynchronous layered microservice architecture."),
            "api_architecture": data.get("api_architecture", "FastAPI REST API with centralized routers and dependency injection."),
            "auth_flow": data.get("auth_flow", "OAuth2 Password Flow + HS256 JWT tokens."),
            "ai_pipeline": data.get("ai_pipeline", "Phase 5 Python AST analysis + Phase 6 Google Gemini reasoning layer."),
            "database_structure": data.get("database_structure", "PostgreSQL database using SQLAlchemy 2.x async ORM and Alembic."),
            "services_and_repos": data.get("services_and_repos", "Service layer encapsulates business workflows; repositories handle data access."),
            "request_lifecycle": data.get("request_lifecycle", "Middleware logs and instruments execution times across all requests."),
        }

        try:
            markdown_content = render_markdown_template("architecture_template.md", template_context)
        except Exception as exc:
            logger.warning("Failed to render architecture_template.md: %s", str(exc))
            markdown_content = provider_resp.raw_text

        return {
            "success": provider_resp.success,
            "markdown": markdown_content,
            "model_used": provider_resp.model_used,
            "processing_time": duration,
        }
