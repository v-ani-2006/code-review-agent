from typing import Any, Dict, List
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import logger
from app.models.user import User
from app.repositories.analytics_repository import analytics_repository
from app.repositories.history_repository import history_repository
from app.schemas.dashboard import (
    ActivityBucket,
    DashboardInsight,
    DashboardInsightsResponse,
    DashboardOverview,
    ScoreProgressionPoint,
    ScoreProgressResponse,
    UserActivity,
    UserStreak,
)
from app.schemas.history import HistoryItem


class DashboardService:
    """Service generating user developer dashboard metrics, activity history, and progress analytics."""

    async def get_overview(
        self,
        db: AsyncSession,
        user: User,
    ) -> DashboardOverview:
        """Fetch dashboard executive overview metrics with Redis caching."""
        from app.services.cache_service import cache_service

        cache_key = f"dashboard:overview:{user.id}"
        cached = await cache_service.get(cache_key, namespace="dashboard")
        if cached:
            return DashboardOverview(**cached)

        stats = await analytics_repository.get_overview_stats(
            db=db,
            user_id=user.id,
            is_admin=user.is_admin,
        )
        logger.info("Dashboard overview calculated for user %s", user.username)
        overview = DashboardOverview(**stats)
        await cache_service.set(cache_key, overview.model_dump(mode="json"), ttl=120, namespace="dashboard")
        return overview


    async def get_activity(
        self,
        db: AsyncSession,
        user: User,
    ) -> UserActivity:
        """Fetch activity distributions across week, month, year, and 24h intervals."""
        activity_data = await analytics_repository.get_user_activity(
            db=db,
            user_id=user.id,
            is_admin=user.is_admin,
        )
        logger.info("User activity metrics requested by %s", user.username)
        return UserActivity(
            reviews_this_week=activity_data["reviews_this_week"],
            reviews_this_month=activity_data["reviews_this_month"],
            reviews_this_year=activity_data["reviews_this_year"],
            daily_activity=[ActivityBucket(**b) for b in activity_data["daily_activity"]],
            weekly_activity=[ActivityBucket(**b) for b in activity_data["weekly_activity"]],
            monthly_activity=[ActivityBucket(**b) for b in activity_data["monthly_activity"]],
            hourly_activity=[ActivityBucket(**b) for b in activity_data["hourly_activity"]],
        )

    async def get_streak(
        self,
        db: AsyncSession,
        user: User,
    ) -> UserStreak:
        """Calculate review streak metrics."""
        streak_data = await analytics_repository.get_user_streak(
            db=db,
            user_id=user.id,
            is_admin=user.is_admin,
        )
        return UserStreak(**streak_data)

    async def get_progress(
        self,
        db: AsyncSession,
        user: User,
        limit: int = 50,
    ) -> ScoreProgressResponse:
        """Fetch score progression points over time."""
        points = await analytics_repository.get_score_progression(
            db=db,
            user_id=user.id,
            limit=limit,
            is_admin=user.is_admin,
        )
        progression = [ScoreProgressionPoint(**p) for p in points]
        return ScoreProgressResponse(
            success=True,
            total_samples=len(progression),
            progression=progression,
        )

    async def get_recent_reviews(
        self,
        db: AsyncSession,
        user: User,
        limit: int = 5,
    ) -> List[HistoryItem]:
        """Fetch small list of recent reviews for dashboard widget."""
        reviews = await history_repository.get_recent_reviews(
            db=db,
            user_id=user.id,
            limit=limit,
            is_admin=user.is_admin,
        )
        return [HistoryItem.model_validate(r) for r in reviews]

    async def get_insights(
        self,
        db: AsyncSession,
        user: User,
    ) -> DashboardInsightsResponse:
        """Generate tailored diagnostic recommendations for improving developer velocity and code hygiene."""
        stats = await analytics_repository.get_overview_stats(db=db, user_id=user.id, is_admin=user.is_admin)
        avg_score = stats["average_score"]

        insights = []
        if avg_score < 75 and stats["total_reviews"] > 0:
            insights.append(
                DashboardInsight(
                    category="QUALITY",
                    title="Code Complexity Alert",
                    detail="Several submitted modules have high cyclomatic complexity. Break large functions into smaller composable units.",
                    priority="HIGH",
                )
            )
        else:
            insights.append(
                DashboardInsight(
                    category="MAINTAINABILITY",
                    title="Healthy Code Structure",
                    detail="Your average code quality score is strong. Continue adhering to single-responsibility principles.",
                    priority="LOW",
                )
            )

        insights.append(
            DashboardInsight(
                category="SECURITY",
                title="Input Validation Hygiene",
                detail="Ensure SQL queries and external process calls consistently use parameterized bindings rather than raw string interpolation.",
                priority="MEDIUM",
            )
        )
        insights.append(
            DashboardInsight(
                category="TESTING",
                title="Automated Test Coverage",
                detail="Leverage CodePilot's unit test generator (/generate/tests) on new modules to safeguard critical branches against regressions.",
                priority="LOW",
            )
        )

        return DashboardInsightsResponse(success=True, insights=insights)

    async def get_languages(
        self,
        db: AsyncSession,
        user: User,
    ) -> Dict[str, Any]:
        """Return language analytics breakdown for dashboard."""
        return await analytics_repository.get_language_analytics(
            db=db,
            user_id=user.id,
            is_admin=user.is_admin,
        )

    async def get_scores(
        self,
        db: AsyncSession,
        user: User,
    ) -> Dict[str, Any]:
        """Return comprehensive score breakdown for dashboard."""
        overview = await analytics_repository.get_overview_stats(db=db, user_id=user.id, is_admin=user.is_admin)
        sec = await analytics_repository.get_security_analytics(db=db, user_id=user.id, is_admin=user.is_admin)
        comp = await analytics_repository.get_complexity_analytics(db=db, user_id=user.id, is_admin=user.is_admin)
        read = await analytics_repository.get_readability_analytics(db=db, user_id=user.id, is_admin=user.is_admin)

        return {
            "success": True,
            "overall_average": overview["average_score"],
            "highest_score": overview["highest_score"],
            "lowest_score": overview["lowest_score"],
            "security_average": sec["average_security_score"],
            "complexity_index": comp["average_maintainability_index"],
            "readability_average": read["average_readability_score"],
        }


dashboard_service = DashboardService()
