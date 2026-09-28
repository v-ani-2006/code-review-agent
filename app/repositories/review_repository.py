from datetime import datetime
import uuid
from typing import List, Optional
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.review import Review
from app.repositories.base_repository import BaseRepository


class ReviewRepository(BaseRepository[Review]):
    """Repository handling database operations for code Review entities."""

    def __init__(self):
        super().__init__(Review)

    async def create_review(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        language: str,
        filename: str,
        source_code: str,
        summary: Optional[str] = None,
        readability_score: Optional[float] = None,
        security_score: Optional[float] = None,
        complexity_score: Optional[float] = None,
        maintainability_score: Optional[float] = None,
        overall_score: Optional[float] = None,
        favorite: bool = False,
        ai_summary: Optional[str] = None,
        ai_strengths: Optional[str] = None,
        ai_recommendations: Optional[str] = None,
        ai_bugfix: Optional[str] = None,
        ai_documentation: Optional[str] = None,
        ai_test_code: Optional[str] = None,
        ai_model: Optional[str] = None,
        ai_processing_time: Optional[float] = None,
        ai_created_at: Optional[datetime] = None,
        documentation: Optional[str] = None,
        docstrings: Optional[str] = None,
        readme_markdown: Optional[str] = None,
        unit_tests: Optional[str] = None,
        refactored_code: Optional[str] = None,
        architecture_summary: Optional[str] = None,
        changelog: Optional[str] = None,
        export_markdown: Optional[str] = None,
        export_html: Optional[str] = None,
    ) -> Review:
        """Create and persist a new review record."""
        return await self.create(
            db,
            user_id=user_id,
            language=language.lower().strip(),
            filename=filename.strip(),
            source_code=source_code,
            summary=summary,
            readability_score=readability_score,
            security_score=security_score,
            complexity_score=complexity_score,
            maintainability_score=maintainability_score,
            overall_score=overall_score,
            favorite=favorite,
            ai_summary=ai_summary,
            ai_strengths=ai_strengths,
            ai_recommendations=ai_recommendations,
            ai_bugfix=ai_bugfix,
            ai_documentation=ai_documentation,
            ai_test_code=ai_test_code,
            ai_model=ai_model,
            ai_processing_time=ai_processing_time,
            ai_created_at=ai_created_at,
            documentation=documentation,
            docstrings=docstrings,
            readme_markdown=readme_markdown,
            unit_tests=unit_tests,
            refactored_code=refactored_code,
            architecture_summary=architecture_summary,
            changelog=changelog,
            export_markdown=export_markdown,
            export_html=export_html,
        )

    async def update_artifacts(
        self,
        db: AsyncSession,
        review_id: uuid.UUID,
        **kwargs,
    ) -> Optional[Review]:
        """Update specific generated documentation, tests, or export artifacts on a review."""
        review = await self.get_by_id(db, review_id)
        if not review:
            return None
        for key, value in kwargs.items():
            if hasattr(review, key):
                setattr(review, key, value)
        await db.commit()
        await db.refresh(review)
        return review


    async def get_user_reviews(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        skip: int = 0,
        limit: int = 50,
    ) -> List[Review]:
        """Fetch paginated reviews belonging to a specific user ordered by latest."""
        statement = (
            select(Review)
            .where(Review.user_id == user_id)
            .order_by(Review.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(statement)
        return list(result.scalars().all())

    async def get_favorite_reviews(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        skip: int = 0,
        limit: int = 50,
    ) -> List[Review]:
        """Fetch favorited reviews for a specific user."""
        statement = (
            select(Review)
            .where(Review.user_id == user_id, Review.favorite.is_(True))
            .order_by(Review.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(statement)
        return list(result.scalars().all())

    async def search_reviews(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        keyword: str,
        skip: int = 0,
        limit: int = 50,
    ) -> List[Review]:
        """Search a user's reviews across filename, language, or summary."""
        search_pattern = f"%{keyword.strip()}%"
        statement = (
            select(Review)
            .where(
                Review.user_id == user_id,
                or_(
                    Review.filename.ilike(search_pattern),
                    Review.language.ilike(search_pattern),
                    Review.summary.ilike(search_pattern),
                ),
            )
            .order_by(Review.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(statement)
        return list(result.scalars().all())

    async def delete_review(
        self,
        db: AsyncSession,
        review_id: uuid.UUID,
        user_id: Optional[uuid.UUID] = None,
    ) -> bool:
        """Delete a review by ID, optionally verifying ownership."""
        review = await self.get_by_id(db, review_id)
        if not review:
            return False
        if user_id and review.user_id != user_id:
            return False
        await db.delete(review)
        await db.commit()
        return True

    async def toggle_favorite(
        self,
        db: AsyncSession,
        review_id: uuid.UUID,
    ) -> Optional[Review]:
        """Toggle the favorite boolean flag of a review."""
        review = await self.get_by_id(db, review_id)
        if not review:
            return None
        review.favorite = not review.favorite
        await db.commit()
        await db.refresh(review)
        return review


# Singleton repository instance
review_repository = ReviewRepository()
