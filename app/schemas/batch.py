from datetime import datetime
from typing import Any, Dict, List, Optional
import uuid
from pydantic import BaseModel, Field

from app.schemas.history import HistoryItem


class ProjectMetricsResponse(BaseModel):
    """Aggregate structural metrics calculated across the analyzed project."""

    total_files: int = 0
    total_lines: int = 0
    total_functions: int = 0
    total_classes: int = 0
    average_complexity: float = 0.0
    average_security_score: float = 0.0
    average_readability: float = 0.0
    average_maintainability: float = 0.0
    duplicate_imports_count: int = 0
    critical_findings_count: int = 0


class ProjectSummaryResponse(BaseModel):
    """High-level architectural summary of the scanned repository."""

    project_name: str
    metrics: ProjectMetricsResponse
    directory_tree: str
    analyzed_files: List[str] = Field(default_factory=list)
    ignored_directories: List[str] = Field(default_factory=list)


class BatchReviewResponse(BaseModel):
    """Aggregated project-wide review report resulting from batch or ZIP analysis."""

    task_id: uuid.UUID
    status: str
    overall_project_score: float
    total_files_analyzed: int
    total_issues: int
    critical_issues: int
    security_summary: str
    complexity_summary: str
    documentation_summary: str
    average_readability: float
    average_maintainability: float
    project_metrics: ProjectMetricsResponse
    directory_tree: Optional[str] = None
    report_id: Optional[str] = None
    file_reviews: List[HistoryItem] = Field(default_factory=list)
