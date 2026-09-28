from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ReportMetadata(BaseModel):
    """Metadata for an existing project review report."""

    report_id: str
    project_name: str
    formats_available: List[str] = Field(default_factory=lambda: ["json", "markdown", "html", "zip"])
    created_at: datetime
    overall_score: float
    total_files: int


class ReportListResponse(BaseModel):
    """Collection of saved project reports."""

    success: bool = True
    total_reports: int
    reports: List[ReportMetadata] = Field(default_factory=list)


class ReportResponse(BaseModel):
    """Detailed report payload with artifact download endpoints."""

    success: bool = True
    report_id: str
    project_name: str
    created_at: datetime
    overall_score: float
    total_files: int
    formats: Dict[str, str] = Field(default_factory=dict)
    summary_data: Optional[Dict[str, Any]] = None
