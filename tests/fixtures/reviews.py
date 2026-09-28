"""Review entity fixtures for review, history, dashboard, and analytics tests."""
from typing import List
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.review import Review
from app.models.user import User
from tests.factories.review_factory import ReviewFactory


@pytest_asyncio.fixture(scope="function")
async def sample_review(db_session: AsyncSession, test_user: User) -> Review:
    """Create and persist single standard review record."""
    return await ReviewFactory.create(
        db=db_session,
        user_id=test_user.id,
        filename="service.py",
        language="python",
        score=88,
        summary="Well architected service layer component.",
        is_deleted=False,
        status="completed",
    )


@pytest_asyncio.fixture(scope="function")
async def sample_reviews_list(db_session: AsyncSession, test_user: User) -> List[Review]:
    """Create and persist a batch of reviews with diverse scores and filenames."""
    reviews = []
    metadata = [
        ("auth.py", 95, "python"),
        ("database.py", 78, "python"),
        ("client.ts", 82, "typescript"),
        ("worker.py", 65, "python"),
        ("main.py", 90, "python"),
    ]
    for fname, sc, lang in metadata:
        r = await ReviewFactory.create(
            db=db_session,
            user_id=test_user.id,
            filename=fname,
            language=lang,
            score=sc,
            is_deleted=False,
            status="completed",
        )
        reviews.append(r)
    return reviews
