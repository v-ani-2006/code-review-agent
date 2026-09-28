from typing import Annotated, Any, Dict, List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_active_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.dashboard import (
    DashboardInsightsResponse,
    DashboardOverview,
    ScoreProgressResponse,
    UserActivity,
    UserStreak,
)
from app.schemas.history import HistoryItem
from app.services.dashboard_service import dashboard_service

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get(
    "/overview",
    response_model=DashboardOverview,
    status_code=status.HTTP_200_OK,
    summary="Get Dashboard Overview Metrics",
    description="Retrieve executive dashboard metrics: total reviews, favorites, average/highest/lowest scores, common issues, and language stats.",
)
async def get_dashboard_overview(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> DashboardOverview:
    """Retrieve high-level overview metrics."""
    return await dashboard_service.get_overview(db=db, user=current_user)


@router.get(
    "/activity",
    response_model=UserActivity,
    status_code=status.HTTP_200_OK,
    summary="Get User Review Activity",
    description="Retrieve activity counts aggregated by week, month, year, daily buckets (last 7 days), weekly buckets, and 24-hour distribution.",
)
async def get_user_activity(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> UserActivity:
    """Retrieve activity time-series."""
    return await dashboard_service.get_activity(db=db, user=current_user)


@router.get(
    "/streak",
    response_model=UserStreak,
    status_code=status.HTTP_200_OK,
    summary="Get Coding Review Streak",
    description="Calculate current consecutive days streak, all-time longest streak, total active days, and timestamp of last activity.",
)
async def get_user_streak(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> UserStreak:
    """Retrieve streak statistics."""
    return await dashboard_service.get_streak(db=db, user=current_user)


@router.get(
    "/progress",
    response_model=ScoreProgressResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Historical Score Progress",
    description="Retrieve chronological trajectory of quality, security, complexity, readability, and maintainability scores.",
)
async def get_score_progress(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    limit: int = Query(50, ge=1, le=200, description="Max historical data points to return"),
) -> ScoreProgressResponse:
    """Retrieve score progression trajectory."""
    return await dashboard_service.get_progress(db=db, user=current_user, limit=limit)


@router.get(
    "/recent",
    response_model=List[HistoryItem],
    status_code=status.HTTP_200_OK,
    summary="Get Recent Reviews for Dashboard Widget",
    description="Retrieve the latest 5 active reviews for quick dashboard display.",
)
async def get_dashboard_recent(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    limit: int = Query(5, ge=1, le=20, description="Max reviews to return"),
) -> List[HistoryItem]:
    """Retrieve recent reviews."""
    return await dashboard_service.get_recent_reviews(db=db, user=current_user, limit=limit)


@router.get(
    "/insights",
    response_model=DashboardInsightsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Automated Developer Insights",
    description="Generate diagnostic and preventative code hygiene recommendations tailored to user trends.",
)
async def get_dashboard_insights(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> DashboardInsightsResponse:
    """Retrieve personalized code insights."""
    return await dashboard_service.get_insights(db=db, user=current_user)


@router.get(
    "/languages",
    status_code=status.HTTP_200_OK,
    summary="Get Language Distribution",
    description="Retrieve language portfolio distribution, favorite language, and average scores per language.",
)
async def get_dashboard_languages(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> Dict[str, Any]:
    """Retrieve language distribution."""
    return await dashboard_service.get_languages(db=db, user=current_user)


@router.get(
    "/scores",
    status_code=status.HTTP_200_OK,
    summary="Get Comprehensive Score Breakdown",
    description="Retrieve multi-dimensional score statistics: overall, security, complexity, and readability averages.",
)
async def get_dashboard_scores(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> Dict[str, Any]:
    """Retrieve multi-dimensional score stats."""
    return await dashboard_service.get_scores(db=db, user=current_user)
