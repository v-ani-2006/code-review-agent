from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.ai_service import ai_service
from app.ai.formatter import format_plain_json
from app.core.logging import logger
from app.models.user import User
from app.repositories.review_repository import review_repository
from app.schemas.ai_review import (
    AIBugFixRequest,
    AIBugFixResponse,
    AIDocumentationRequest,
    AIDocumentationResponse,
    AIExplainRequest,
    AIExplainResponse,
    AIModelListResponse,
    AIOptimizeRequest,
    AIOptimizeResponse,
    AIReviewRequest,
    AIReviewResponse,
    AIStatusResponse,
    AITestRequest,
    AITestResponse,
)


class AIReviewService:
    """High-level application service coordinating AI reasoning and database persistence."""

    async def review_and_store(
        self,
        db: AsyncSession,
        request: AIReviewRequest,
        current_user: Optional[User] = None,
    ) -> AIReviewResponse:
        """Run complete AI review pipeline and persist to database if user is authenticated."""
        # 1. Execute AI code review pipeline
        response = await ai_service.review_code(request)

        # 2. Persist to PostgreSQL if authenticated
        if current_user and response.static_report:
            try:
                review_data = response.review
                static_rep = response.static_report
                filename = request.filename or "main.py"

                saved_review = await review_repository.create_review(
                    db=db,
                    user_id=current_user.id,
                    language=request.language,
                    filename=filename,
                    source_code=request.code,
                    summary=review_data.summary or static_rep.summary,
                    readability_score=static_rep.scores.readability,
                    security_score=static_rep.scores.security,
                    complexity_score=static_rep.scores.complexity,
                    maintainability_score=static_rep.scores.maintainability,
                    overall_score=static_rep.scores.overall,
                    favorite=False,
                    ai_summary=review_data.summary,
                    ai_strengths=format_plain_json(review_data.strengths),
                    ai_recommendations=format_plain_json(review_data.optimization_suggestions + review_data.refactoring_suggestions),
                    ai_bugfix=None,
                    ai_documentation=None,
                    ai_test_code=None,
                    ai_model=response.model_used,
                    ai_processing_time=response.processing_time,
                    ai_created_at=datetime.now(timezone.utc),
                )

                logger.info(
                    "AI Review saved: Review ID %s for user '%s'",
                    saved_review.id,
                    current_user.username,
                )
                response.review.metadata["review_id"] = str(saved_review.id)
                response.review.metadata["user_id"] = str(current_user.id)
            except Exception as exc:
                logger.error("Failed to persist AI review record: %s", str(exc))

        return response

    async def explain(self, request: AIExplainRequest) -> AIExplainResponse:
        """Explain code structure and execution flow."""
        return await ai_service.explain_code(request)

    async def optimize(self, request: AIOptimizeRequest) -> AIOptimizeResponse:
        """Optimize code for performance, memory, and idiomatic quality."""
        return await ai_service.optimize_code(request)

    async def fix(
        self,
        db: AsyncSession,
        request: AIBugFixRequest,
        current_user: Optional[User] = None,
    ) -> AIBugFixResponse:
        """Fix bugs in code and optionally update review history."""
        response = await ai_service.fix_code(request)
        return response

    async def document(self, request: AIDocumentationRequest) -> AIDocumentationResponse:
        """Generate docstrings and documentation artifacts."""
        return await ai_service.generate_documentation(request)

    async def generate_tests(self, request: AITestRequest) -> AITestResponse:
        """Generate comprehensive pytest test suite."""
        return await ai_service.generate_tests(request)

    async def get_models(self) -> AIModelListResponse:
        """Retrieve available AI models with Redis caching."""
        from app.services.cache_service import cache_service

        cache_key = "models:available"
        cached = await cache_service.get(cache_key, namespace="models")
        if cached:
            return AIModelListResponse(**cached)

        res = await ai_service.get_models()
        await cache_service.set(cache_key, res.model_dump(mode="json"), ttl=600, namespace="models")
        return res


    async def get_status(self) -> AIStatusResponse:
        """Retrieve AI service operational status."""
        return await ai_service.get_status()


# Singleton AI review service
ai_review_service = AIReviewService()
