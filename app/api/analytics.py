from typing import Annotated, Any, Dict
from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_active_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.analytics import (
    ComplexityAnalyticsResponse,
    HeatmapResponse,
    IssueAnalyticsResponse,
    LanguageAnalyticsResponse,
    ReadabilityAnalyticsResponse,
    SecurityAnalyticsResponse,
    TrendAnalyticsResponse,
)
from app.services.analytics_service import analytics_service

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get(
    "/overview",
    status_code=status.HTTP_200_OK,
    summary="Get Analytics Overview",
    description="High-level analytical metrics encompassing reviews, scores, AI runs, and top issues.",
)
async def get_analytics_overview(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> Dict[str, Any]:
    """Retrieve analytics overview."""
    return await analytics_service.get_overview(db=db, user=current_user)


@router.get(
    "/scores",
    status_code=status.HTTP_200_OK,
    summary="Get Score Analytics",
    description="Detailed breakdown of quality, security, complexity, maintainability, and readability scores.",
)
async def get_score_analytics(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> Dict[str, Any]:
    """Retrieve multi-metric score analytics."""
    return await analytics_service.get_scores(db=db, user=current_user)


@router.get(
    "/issues",
    response_model=IssueAnalyticsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Issue Distribution & Severity",
    description="Breakdown of code findings by category (BUG, STYLE, SECURITY, PERFORMANCE, READABILITY, DOCUMENTATION, BEST_PRACTICE) and severity tier.",
)
async def get_issue_analytics(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> IssueAnalyticsResponse:
    """Retrieve issue findings breakdown."""
    return await analytics_service.get_issues(db=db, user=current_user)


@router.get(
    "/security",
    response_model=SecurityAnalyticsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Security Posture & Vulnerabilities",
    description="Evaluate security posture, Bandit vulnerability classifications, and critical risk findings.",
)
async def get_security_analytics(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> SecurityAnalyticsResponse:
    """Retrieve security posture analytics."""
    return await analytics_service.get_security(db=db, user=current_user)


@router.get(
    "/complexity",
    response_model=ComplexityAnalyticsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Cyclomatic Complexity & Radon Metrics",
    description="Cyclomatic complexity distribution, Radon rank histogram (A-F), and highest complexity files.",
)
async def get_complexity_analytics(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> ComplexityAnalyticsResponse:
    """Retrieve complexity and Radon metrics."""
    return await analytics_service.get_complexity(db=db, user=current_user)


@router.get(
    "/readability",
    response_model=ReadabilityAnalyticsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Readability & PEP 8 Compliance",
    description="Analyze readability heuristics, style guideline compliance, and naming conventions.",
)
async def get_readability_analytics(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> ReadabilityAnalyticsResponse:
    """Retrieve readability metrics."""
    return await analytics_service.get_readability(db=db, user=current_user)


@router.get(
    "/languages",
    response_model=LanguageAnalyticsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Language Analytics",
    description="Exhaustive programming language breakdown with count percentages and average scores.",
)
async def get_language_analytics(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> LanguageAnalyticsResponse:
    """Retrieve language analytics."""
    return await analytics_service.get_languages(db=db, user=current_user)


@router.get(
    "/trends",
    response_model=TrendAnalyticsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Quality & Velocity Trends",
    description="Historical trends tracking score improvement, issue reduction, and overall trajectory verdict.",
)
async def get_trend_analytics(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> TrendAnalyticsResponse:
    """Retrieve quality improvement trends."""
    return await analytics_service.get_trends(db=db, user=current_user)


@router.get(
    "/heatmap",
    response_model=HeatmapResponse,
    status_code=status.HTTP_200_OK,
    summary="Get GitHub-Style Contribution Heatmap",
    description="365-day time-series activity map with intensity tiers (0 to 4) suitable for frontend calendar heatmaps.",
)
async def get_heatmap_data(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> HeatmapResponse:
    """Retrieve contribution heatmap data."""
    return await analytics_service.get_heatmap(db=db, user=current_user)


@router.get(
    "/export",
    status_code=status.HTTP_200_OK,
    summary="Export Analytics Data",
    description="Export comprehensive analytics dataset in JSON, CSV, or Markdown format.",
)
async def export_analytics(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    format: str = Query("json", pattern="^(json|csv|markdown)$", description="Export format: json, csv, or markdown"),
) -> Response:
    """Export analytics data in chosen format."""
    res = await analytics_service.export_analytics(db=db, user=current_user, export_format=format)
    return Response(
        content=res["content"],
        media_type=res["mime_type"],
        headers={"Content-Disposition": f"attachment; filename=\"{res['filename']}\""},
    )
