from datetime import datetime
from typing import Any, Dict, List, Optional
import uuid
from pydantic import BaseModel, ConfigDict, Field


class PaginationMeta(BaseModel):
    """Pagination metadata model."""

    page: int = Field(default=1, ge=1, description="Current page number")
    page_size: int = Field(default=20, ge=1, le=100, description="Number of items per page")
    total_items: int = Field(..., description="Total records matching query criteria")
    total_pages: int = Field(..., description="Total pages available")
    has_next: bool = Field(default=False, description="Whether a subsequent page exists")
    has_prev: bool = Field(default=False, description="Whether a preceding page exists")


class HistoryItem(BaseModel):
    """Condensed review summary item suitable for lists and dashboards."""

    id: uuid.UUID
    user_id: uuid.UUID
    language: str
    filename: str
    summary: Optional[str] = None
    overall_score: Optional[float] = None
    readability_score: Optional[float] = None
    security_score: Optional[float] = None
    complexity_score: Optional[float] = None
    maintainability_score: Optional[float] = None
    favorite: bool = False
    is_deleted: bool = False
    deleted_at: Optional[datetime] = None
    status: str = "completed"
    view_count: int = 0
    last_viewed: Optional[datetime] = None
    tags: Optional[List[str]] = Field(default_factory=list)
    ai_model: Optional[str] = None
    ai_processing_time: Optional[float] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class HistoryDetailResponse(BaseModel):
    """Exhaustive review entity payload including source code and generated artifacts."""

    id: uuid.UUID
    user_id: uuid.UUID
    language: str
    filename: str
    source_code: str
    summary: Optional[str] = None
    overall_score: Optional[float] = None
    readability_score: Optional[float] = None
    security_score: Optional[float] = None
    complexity_score: Optional[float] = None
    maintainability_score: Optional[float] = None
    favorite: bool = False
    is_deleted: bool = False
    deleted_at: Optional[datetime] = None
    status: str = "completed"
    view_count: int = 0
    last_viewed: Optional[datetime] = None
    tags: Optional[List[str]] = Field(default_factory=list)
    language_version: Optional[str] = None
    analysis_duration: Optional[float] = None
    review_version: int = 1

    # AI & Generator artifacts
    ai_summary: Optional[str] = None
    ai_strengths: Optional[str] = None
    ai_recommendations: Optional[str] = None
    ai_bugfix: Optional[str] = None
    ai_documentation: Optional[str] = None
    ai_test_code: Optional[str] = None
    ai_model: Optional[str] = None
    ai_processing_time: Optional[float] = None
    ai_created_at: Optional[datetime] = None
    documentation: Optional[str] = None
    docstrings: Optional[str] = None
    readme_markdown: Optional[str] = None
    unit_tests: Optional[str] = None
    refactored_code: Optional[str] = None
    architecture_summary: Optional[str] = None
    changelog: Optional[str] = None
    export_markdown: Optional[str] = None
    export_html: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class HistoryListResponse(BaseModel):
    """Paginated list of review history items."""

    success: bool = True
    items: List[HistoryItem] = Field(default_factory=list)
    meta: PaginationMeta


class ReviewCompareRequest(BaseModel):
    """Payload to initiate a structured side-by-side comparison between two reviews."""

    review_id_a: uuid.UUID = Field(..., description="Baseline review ID")
    review_id_b: uuid.UUID = Field(..., description="Target comparison review ID")


class ScoreDiff(BaseModel):
    """Score variance between two review snapshots."""

    metric: str
    score_a: Optional[float] = None
    score_b: Optional[float] = None
    difference: Optional[float] = None
    improved: Optional[bool] = None


class ComparisonResponse(BaseModel):
    """Structured analytical comparison between two code reviews."""

    success: bool = True
    review_a: HistoryItem
    review_b: HistoryItem
    score_diffs: List[ScoreDiff]
    summary_diff: Dict[str, Any]
    structural_diff: Dict[str, Any]
    verdict: str


class TimelineGroup(BaseModel):
    """Chronologically grouped reviews."""

    period: str
    count: int
    average_score: Optional[float] = None
    reviews: List[HistoryItem]


class TimelineResponse(BaseModel):
    """Chronological timeline of user reviews grouped by day, week, or month."""

    success: bool = True
    group_by: str
    total_reviews: int
    timeline: List[TimelineGroup]
