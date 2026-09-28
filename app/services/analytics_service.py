import csv
import io
import json
from typing import Any, Dict
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import logger
from app.models.user import User
from app.repositories.analytics_repository import analytics_repository
from app.schemas.analytics import (
    CategoryBreakdownItem,
    ComplexityAnalyticsResponse,
    HeatmapDay,
    HeatmapResponse,
    IssueAnalyticsResponse,
    LanguageAnalyticsResponse,
    LanguageDistributionItem,
    ReadabilityAnalyticsResponse,
    SecurityAnalyticsResponse,
    TrendAnalyticsResponse,
)


class AnalyticsService:
    """Service generating advanced code review analytics, metrics, heatmaps, and data exports."""

    async def get_overview(
        self,
        db: AsyncSession,
        user: User,
    ) -> Dict[str, Any]:
        """Fetch general analytics metrics overview with Redis caching."""
        from app.services.cache_service import cache_service

        cache_key = f"analytics:overview:{user.id}"
        cached = await cache_service.get(cache_key, namespace="analytics")
        if cached:
            return cached

        logger.info("Analytics overview calculated for user %s", user.username)
        stats = await analytics_repository.get_overview_stats(
            db=db,
            user_id=user.id,
            is_admin=user.is_admin,
        )
        payload = {"success": True, **stats}
        await cache_service.set(cache_key, payload, ttl=120, namespace="analytics")
        return payload


    async def get_scores(
        self,
        db: AsyncSession,
        user: User,
    ) -> Dict[str, Any]:
        """Fetch aggregated metrics across all scoring criteria."""
        overview = await analytics_repository.get_overview_stats(db=db, user_id=user.id, is_admin=user.is_admin)
        sec = await analytics_repository.get_security_analytics(db=db, user_id=user.id, is_admin=user.is_admin)
        comp = await analytics_repository.get_complexity_analytics(db=db, user_id=user.id, is_admin=user.is_admin)
        read = await analytics_repository.get_readability_analytics(db=db, user_id=user.id, is_admin=user.is_admin)

        return {
            "success": True,
            "overall_average": overview["average_score"],
            "highest_score": overview["highest_score"],
            "lowest_score": overview["lowest_score"],
            "security_score_average": sec["average_security_score"],
            "cyclomatic_complexity_index": comp["average_cyclomatic_complexity"],
            "maintainability_index": comp["average_maintainability_index"],
            "readability_score_average": read["average_readability_score"],
        }

    async def get_issues(
        self,
        db: AsyncSession,
        user: User,
    ) -> IssueAnalyticsResponse:
        """Fetch issue categorization and severity distribution."""
        data = await analytics_repository.get_issue_analytics(db=db, user_id=user.id, is_admin=user.is_admin)
        return IssueAnalyticsResponse(
            success=True,
            total_issues=data["total_issues"],
            severity_distribution=data["severity_distribution"],
            category_breakdown=[CategoryBreakdownItem(**c) for c in data["category_breakdown"]],
            most_frequent_issues=data["most_frequent_issues"],
        )

    async def get_security(
        self,
        db: AsyncSession,
        user: User,
    ) -> SecurityAnalyticsResponse:
        """Fetch security metrics, vulnerability counts, and posture."""
        data = await analytics_repository.get_security_analytics(db=db, user_id=user.id, is_admin=user.is_admin)
        return SecurityAnalyticsResponse(
            success=True,
            total_security_findings=data["total_security_findings"],
            average_security_score=data["average_security_score"],
            vulnerabilities_by_severity=data["vulnerabilities_by_severity"],
            top_vulnerabilities=data["top_vulnerabilities"],
            security_posture=data["security_posture"],
        )

    async def get_complexity(
        self,
        db: AsyncSession,
        user: User,
    ) -> ComplexityAnalyticsResponse:
        """Fetch cyclomatic complexity and Radon rank distribution."""
        data = await analytics_repository.get_complexity_analytics(db=db, user_id=user.id, is_admin=user.is_admin)
        return ComplexityAnalyticsResponse(
            success=True,
            average_cyclomatic_complexity=data["average_cyclomatic_complexity"],
            average_maintainability_index=data["average_maintainability_index"],
            rank_distribution=data["rank_distribution"],
            highest_complexity_reviews=data["highest_complexity_reviews"],
        )

    async def get_readability(
        self,
        db: AsyncSession,
        user: User,
    ) -> ReadabilityAnalyticsResponse:
        """Fetch PEP 8 style heuristics and formatting compliance."""
        data = await analytics_repository.get_readability_analytics(db=db, user_id=user.id, is_admin=user.is_admin)
        return ReadabilityAnalyticsResponse(
            success=True,
            average_readability_score=data["average_readability_score"],
            style_issue_count=data["style_issue_count"],
            average_line_length_compliance=data["average_line_length_compliance"],
            naming_convention_score=data["naming_convention_score"],
        )

    async def get_languages(
        self,
        db: AsyncSession,
        user: User,
    ) -> LanguageAnalyticsResponse:
        """Fetch language distribution analytics."""
        data = await analytics_repository.get_language_analytics(db=db, user_id=user.id, is_admin=user.is_admin)
        return LanguageAnalyticsResponse(
            success=True,
            favorite_language=data["favorite_language"],
            total_languages=data["total_languages"],
            distribution=[LanguageDistributionItem(**d) for d in data["distribution"]],
        )

    async def get_trends(
        self,
        db: AsyncSession,
        user: User,
    ) -> TrendAnalyticsResponse:
        """Calculate historical velocity and code quality improvements."""
        data = await analytics_repository.get_trend_analytics(db=db, user_id=user.id, is_admin=user.is_admin)
        return TrendAnalyticsResponse(
            success=True,
            weekly_trend=data["weekly_trend"],
            monthly_trend=data["monthly_trend"],
            score_improvement_trend=data["score_improvement_trend"],
            issue_reduction_trend=data["issue_reduction_trend"],
            security_improvement_trend=data["security_improvement_trend"],
            trajectory_verdict=data["trajectory_verdict"],
        )

    async def get_heatmap(
        self,
        db: AsyncSession,
        user: User,
    ) -> HeatmapResponse:
        """Generate 365-day activity heatmap data."""
        data = await analytics_repository.get_heatmap_data(db=db, user_id=user.id, is_admin=user.is_admin)
        return HeatmapResponse(
            success=True,
            total_reviews_year=data["total_reviews_year"],
            days_recorded=data["days_recorded"],
            heatmap=[HeatmapDay(**d) for d in data["heatmap"]],
        )

    async def export_analytics(
        self,
        db: AsyncSession,
        user: User,
        export_format: str = "json",
    ) -> Dict[str, Any]:
        """Export comprehensive analytics in JSON, CSV, or Markdown format."""
        logger.info("Analytics exported: format=%s user=%s", export_format, user.username)
        overview = await analytics_repository.get_overview_stats(db=db, user_id=user.id, is_admin=user.is_admin)
        sec = await analytics_repository.get_security_analytics(db=db, user_id=user.id, is_admin=user.is_admin)
        comp = await analytics_repository.get_complexity_analytics(db=db, user_id=user.id, is_admin=user.is_admin)
        read = await analytics_repository.get_readability_analytics(db=db, user_id=user.id, is_admin=user.is_admin)
        langs = await analytics_repository.get_language_analytics(db=db, user_id=user.id, is_admin=user.is_admin)

        bundle = {
            "user": user.username,
            "overview": overview,
            "security": sec,
            "complexity": comp,
            "readability": read,
            "languages": langs,
        }

        fmt = export_format.lower().strip()
        if fmt == "csv":
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(["Section", "Metric", "Value"])
            for k, v in overview.items():
                writer.writerow(["Overview", k, str(v)])
            for k, v in sec.items():
                if not isinstance(v, (dict, list)):
                    writer.writerow(["Security", k, str(v)])
            for k, v in comp.items():
                if not isinstance(v, (dict, list)):
                    writer.writerow(["Complexity", k, str(v)])
            for k, v in read.items():
                writer.writerow(["Readability", k, str(v)])

            content = output.getvalue()
            return {
                "format": "csv",
                "filename": f"analytics_{user.username}.csv",
                "mime_type": "text/csv",
                "content": content,
            }

        elif fmt == "markdown":
            md_lines = [
                f"# CodePilot AI Analytics Report for `{user.username}`",
                "",
                "## 1. Executive Overview",
                f"- **Total Reviews:** {overview['total_reviews']}",
                f"- **Average Quality Score:** {overview['average_score']}/100",
                f"- **Highest Score Recorded:** {overview['highest_score']}/100",
                f"- **Lowest Score Recorded:** {overview['lowest_score']}/100",
                f"- **Favorite Language:** {langs.get('favorite_language', 'N/A')}",
                "",
                "## 2. Security Posture",
                f"- **Security Score Average:** {sec['average_security_score']}/100",
                f"- **Overall Posture:** `{sec['security_posture']}`",
                f"- **Identified Findings:** {sec['total_security_findings']}",
                "",
                "## 3. Complexity & Maintainability",
                f"- **Cyclomatic Complexity (Avg):** {comp['average_cyclomatic_complexity']}",
                f"- **Maintainability Index:** {comp['average_maintainability_index']}/100",
                "",
                "## 4. Readability & Style",
                f"- **Readability Score:** {read['average_readability_score']}/100",
                f"- **Style Issues Logged:** {read['style_issue_count']}",
                "",
                "---",
                "*Generated automatically by CodePilot AI Analytics Engine.*",
            ]
            content = "\n".join(md_lines)
            return {
                "format": "markdown",
                "filename": f"analytics_{user.username}.md",
                "mime_type": "text/markdown",
                "content": content,
            }

        else:
            # Default JSON
            return {
                "format": "json",
                "filename": f"analytics_{user.username}.json",
                "mime_type": "application/json",
                "content": json.dumps(bundle, indent=2, default=str),
            }


analytics_service = AnalyticsService()
