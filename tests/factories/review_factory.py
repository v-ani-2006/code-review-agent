"""Review model factory producing realistic review entities for testing."""
import uuid
from faker import Faker
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.review import Review

fake = Faker()


class ReviewFactory:
    """Factory generating Review entity instances."""

    @classmethod
    def build(
        cls,
        id: uuid.UUID = None,
        user_id: uuid.UUID = None,
        filename: str = None,
        language: str = "python",
        code: str = None,
        score: int = 85,
        summary: str = None,
        issues: list = None,
        metrics: dict = None,
        is_deleted: bool = False,
        status: str = "completed",
    ) -> Review:
        review_id = id or uuid.uuid4()
        uid = user_id or uuid.uuid4()
        code_snippet = code or "def calculate_total(items):\n    return sum(items)\n"

        return Review(
            id=review_id,
            user_id=uid,
            filename=filename or f"test_{str(review_id)[:6]}.py",
            language=language,
            source_code=code_snippet,
            summary=summary or fake.sentence(),
            overall_score=score,
            readability_score=score,
            security_score=score,
            complexity_score=score,
            maintainability_score=score,
            favorite=False,
            ai_summary="Solid and concise implementation.",
            is_deleted=is_deleted,
            status=status,
            view_count=1,
            tags=["tested", "python"],
            review_version=1,
        )

    @classmethod
    async def create(cls, db: AsyncSession, **kwargs) -> Review:
        review = cls.build(**kwargs)
        db.add(review)
        await db.flush()
        await db.refresh(review)
        return review
