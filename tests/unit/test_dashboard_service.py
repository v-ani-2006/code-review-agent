"""Unit tests for DashboardService and analytics metrics."""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.review import Review
from app.models.user import User
from app.services.dashboard_service import dashboard_service


@pytest.mark.unit
async def test_dashboard_overview(db_session: AsyncSession, test_user: User, sample_review: Review):
    """Test dashboard overview statistics generation."""
    overview = await dashboard_service.get_overview(db_session, test_user)

    assert overview is not None
    assert overview.total_reviews >= 1
    assert overview.average_score > 0


@pytest.mark.unit
async def test_dashboard_streak(db_session: AsyncSession, test_user: User, sample_review: Review):
    """Test developer activity streak metrics."""
    streak = await dashboard_service.get_streak(db_session, test_user)

    assert streak is not None
    assert hasattr(streak, "current_streak") or hasattr(streak, "current_streak_days")
    assert hasattr(streak, "longest_streak") or hasattr(streak, "longest_streak_days")


@pytest.mark.unit
async def test_dashboard_score_progression(db_session: AsyncSession, test_user: User, sample_review: Review):
    """Test chronological score progression data."""
    progression = await dashboard_service.get_progress(db_session, test_user)

    assert progression is not None
    assert hasattr(progression, "progression")


@pytest.mark.unit
async def test_dashboard_insights(db_session: AsyncSession, test_user: User, sample_review: Review):
    """Test automated actionable insights generation."""
    insights = await dashboard_service.get_insights(db_session, test_user)

    assert insights is not None
    assert hasattr(insights, "insights")
