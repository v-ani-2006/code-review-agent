from typing import Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.analyzer import analyze_code
from app.ai.constants import ANALYSIS_RULES, SUPPORTED_LANGUAGES
from app.core.logging import logger
from app.models.user import User
from app.repositories.review_repository import review_repository
from app.schemas.review import LanguageInfo, ReviewReport, ReviewRequest, RuleInfo


class ReviewService:
    """Service orchestrating static code analysis, score generation, and database persistence."""

    async def analyze_and_store(
        self,
        db: AsyncSession,
        request: ReviewRequest,
        current_user: Optional[User] = None,
    ) -> ReviewReport:
        """Execute AST analysis engine on submitted source code, and persist to database if user is authenticated."""
        filename = request.filename or "main.py"

        # 1. Run static code analyzer
        report = analyze_code(
            code=request.code,
            filename=filename,
            language=request.language,
        )

        # 2. Persist to PostgreSQL database if submitted by an authenticated user
        if current_user:
            try:
                saved_review = await review_repository.create_review(
                    db=db,
                    user_id=current_user.id,
                    language=request.language,
                    filename=filename,
                    source_code=request.code,
                    summary=report.summary,
                    readability_score=report.scores.readability,
                    security_score=report.scores.security,
                    complexity_score=report.scores.complexity,
                    maintainability_score=report.scores.maintainability,
                    overall_score=report.scores.overall,
                    favorite=False,
                )
                logger.info(
                    "Review saved to database: Review ID %s for user '%s'",
                    saved_review.id,
                    current_user.username,
                )
                report.metadata["review_id"] = str(saved_review.id)
                report.metadata["user_id"] = str(current_user.id)

                # Phase 10: Invalidate cache, broadcast webhook, and write audit log
                try:
                    import asyncio
                    from app.core.audit import log_audit_background
                    from app.services.cache_service import cache_service
                    from app.services.webhook_service import webhook_service

                    await cache_service.invalidate_user(current_user.id)
                    asyncio.create_task(
                        webhook_service.broadcast_event_background(
                            event_type="review.completed",
                            payload_data={
                                "review_id": str(saved_review.id),
                                "filename": saved_review.filename,
                                "overall_score": saved_review.overall_score,
                                "user_id": str(current_user.id),
                            },
                        )
                    )
                    asyncio.create_task(
                        log_audit_background(
                            action="review.created",
                            resource="review",
                            user_id=current_user.id,
                            resource_id=str(saved_review.id),
                            status="success",
                            metadata={"filename": saved_review.filename, "score": saved_review.overall_score},
                        )
                    )
                except Exception as hook_err:
                    logger.warning("Post-review hooks warning: %s", str(hook_err))
            except Exception as exc:
                logger.error("Failed to persist review record to database: %s", str(exc))

        return report


    def get_supported_languages(self) -> List[LanguageInfo]:
        """Return information regarding supported programming languages."""
        return [
            LanguageInfo(
                name=lang,
                supported=True,
                engine="Python AST + Radon Complexity + Bandit Security Engine",
            )
            for lang in SUPPORTED_LANGUAGES
        ]

    def get_analysis_rules(self) -> List[RuleInfo]:
        """Return list of active static analysis rules."""
        return [RuleInfo(**rule) for rule in ANALYSIS_RULES]

    get_active_rules = get_analysis_rules


# Singleton review service instance
review_service = ReviewService()
