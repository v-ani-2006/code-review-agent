from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class HeatmapDay(BaseModel):
    """Daily activity unit for GitHub-style contribution heatmaps."""

    date: str = Field(..., description="Date formatted as YYYY-MM-DD")
    count: int = Field(default=0, description="Number of reviews completed on this date")
    level: int = Field(default=0, ge=0, le=4, description="Activity intensity tier from 0 (none) to 4 (high)")


class HeatmapResponse(BaseModel):
    """Annual activity distribution response."""

    success: bool = True
    total_reviews_year: int
    days_recorded: int
    heatmap: List[HeatmapDay]


class LanguageDistributionItem(BaseModel):
    """Per-language distribution metric."""

    language: str
    count: int
    percentage: float
    average_score: float
    average_security: float


class LanguageAnalyticsResponse(BaseModel):
    """Comprehensive language portfolio breakdown."""

    success: bool = True
    favorite_language: Optional[str] = None
    total_languages: int
    distribution: List[LanguageDistributionItem]


class CategoryBreakdownItem(BaseModel):
    """Issue category volume and percentage."""

    category: str
    count: int
    percentage: float


class IssueAnalyticsResponse(BaseModel):
    """Categorized findings and defect distribution."""

    success: bool = True
    total_issues: int
    severity_distribution: Dict[str, int]
    category_breakdown: List[CategoryBreakdownItem]
    most_frequent_issues: List[Dict[str, Any]]


class SecurityAnalyticsResponse(BaseModel):
    """Security vulnerability trends and critical finding breakdown."""

    success: bool = True
    total_security_findings: int
    average_security_score: float
    vulnerabilities_by_severity: Dict[str, int]
    top_vulnerabilities: List[Dict[str, Any]]
    security_posture: str


class ComplexityAnalyticsResponse(BaseModel):
    """Radon and cyclomatic complexity distributions."""

    success: bool = True
    average_cyclomatic_complexity: float
    average_maintainability_index: float
    rank_distribution: Dict[str, int]
    highest_complexity_reviews: List[Dict[str, Any]]


class ReadabilityAnalyticsResponse(BaseModel):
    """PEP 8 style compliance and readability metrics."""

    success: bool = True
    average_readability_score: float
    style_issue_count: int
    average_line_length_compliance: float
    naming_convention_score: float


class TrendAnalyticsResponse(BaseModel):
    """Velocity, score improvements, and defect resolution trends over time."""

    success: bool = True
    weekly_trend: Dict[str, Any]
    monthly_trend: Dict[str, Any]
    score_improvement_trend: str
    issue_reduction_trend: str
    security_improvement_trend: str
    trajectory_verdict: str
