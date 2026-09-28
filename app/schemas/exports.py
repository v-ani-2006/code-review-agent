from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class ExportRequest(BaseModel):
    """Generic payload for exporting code reviews, analysis reports, or documents."""

    content: Optional[str] = Field(default=None, description="Raw markdown or text content to convert/export")
    data: Optional[Dict[str, Any]] = Field(default=None, description="Structured report or dictionary data")
    filename: Optional[str] = Field(default="report", description="Target base filename without extension")
    title: Optional[str] = Field(default="CodePilot AI Technical Report", description="Document title used in HTML/PDF views")
    pretty: bool = Field(default=True, description="Whether to format output with pretty-printing")


class ExportResponse(BaseModel):
    """Standardized response containing exported content and MIME headers."""

    success: bool = Field(default=True, description="Export status")
    format: str = Field(..., description="Export format: 'json', 'markdown', 'html', or 'text'")
    filename: str = Field(..., description="Suggested filename with appropriate file extension")
    mime_type: str = Field(..., description="HTTP Content-Type MIME descriptor")
    content: str = Field(..., description="Rendered file content string")
    processing_time: float = Field(..., description="Duration of export formatting in seconds")
