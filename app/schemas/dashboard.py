from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from app.schemas.history import HistoryItem


class DashboardOverview(BaseModel):
    """Executive metrics summary for user dashboard."""

    total_reviews: int
    favorite_reviews: int
    average_score: float
    highest_score: float
    lowest_score: float
    languages_used: List[str]
    most_common_issue: Optional[str] = None
    most_common_security_issue: Optional[str] = None
    total_ai_reviews: int
    processing_time_average: float


class ActivityBucket(BaseModel):
    """Time-series activity count representation."""

    label: str
    count: int
    date: Optional[str] = None


class UserActivity(BaseModel):
    """Multi-tiered activity aggregation across time intervals."""

    reviews_this_week: int
    reviews_this_month: int
    reviews_this_year: int
    daily_activity: List[ActivityBucket]
    weekly_activity: List[ActivityBucket]
    monthly_activity: List[ActivityBucket]
    hourly_activity: List[ActivityBucket]


class UserStreak(BaseModel):
    """User coding review streak tracking metrics."""

    current_streak: int
    longest_streak: int
    days_active: int
    last_activity: Optional[datetime] = None


class ScoreProgressionPoint(BaseModel):
    """Historical score progression sample."""

    review_id: str
    date: str
    filename: str
    overall: Optional[float] = None
    security: Optional[float] = None
    complexity: Optional[float] = None
    readability: Optional[float] = None
    maintainability: Optional[float] = None
    ai_processing_time: Optional[float] = None


class ScoreProgressResponse(BaseModel):
    """Time-series score progression trajectory."""

    success: bool = True
    total_samples: int
    progression: List[ScoreProgressionPoint]


class DashboardInsight(BaseModel):
    """AI and rule-based diagnostic suggestion for developer improvement."""

    category: str
    title: str
    detail: str
    priority: str = "MEDIUM"


class DashboardInsightsResponse(BaseModel):
    """Aggregated insights and recommendations."""

    success: bool = True
    insights: List[DashboardInsight]
