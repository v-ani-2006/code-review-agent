"""Performance benchmark measuring database query latency for history and analytics."""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.review import Review
from app.models.user import User
from app.repositories.analytics_repository import analytics_repository
from app.repositories.history_repository import history_repository
from tests.utils import measure_duration


@pytest.mark.performance
async def test_history_query_latency(
    db_session: AsyncSession,
    test_user: User,
    sample_review: Review,
):
    """Benchmark history list query execution speed."""
    with measure_duration() as metric:
        items, total, total_pages = await history_repository.get_history(
            db=db_session,
            user_id=test_user.id,
            page=1,
            page_size=20,
        )

    duration = metric["duration"]
    assert total >= 1
    # Single indexed pagination query should complete under 200ms
    assert duration < 0.2, f"History query took {duration}s"


@pytest.mark.performance
async def test_analytics_aggregation_latency(
    db_session: AsyncSession,
    test_user: User,
    sample_review: Review,
):
    """Benchmark dashboard overview analytics aggregation speed."""
    with measure_duration() as metric:
        stats = await analytics_repository.get_overview_stats(
            db=db_session,
            user_id=test_user.id,
            is_admin=False,
        )

    duration = metric["duration"]
    assert stats is not None
    # Aggregation query should complete under 300ms
    assert duration < 0.3, f"Analytics aggregation took {duration}s"
