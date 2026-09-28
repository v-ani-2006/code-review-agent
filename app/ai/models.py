from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class AIAnalysisContext(BaseModel):
    """Context object encapsulating source code and Phase 5 static analysis findings."""

    language: str = Field(default="python", description="Programming language")
    filename: str = Field(default="main.py", description="Source code filename")
    source_code: str = Field(..., description="Raw source code being analyzed")
    summary: Optional[str] = Field(default=None, description="Static analysis summary")
    overall_score: Optional[float] = Field(default=None, description="Overall static analysis quality score")
    readability_score: Optional[float] = Field(default=None, description="Readability score (0-100)")
    maintainability_score: Optional[float] = Field(default=None, description="Maintainability score (0-100)")
    security_score: Optional[float] = Field(default=None, description="Security vulnerability score (0-100)")
    complexity_score: Optional[float] = Field(default=None, description="Complexity simplicity score (0-100)")
    documentation_score: Optional[float] = Field(default=None, description="Documentation coverage score (0-100)")
    cyclomatic_complexity: Optional[float] = Field(default=None, description="Average cyclomatic complexity")
    complexity_rank: Optional[str] = Field(default="A", description="Radon complexity grade rank (A-F)")
    issues: List[Dict[str, Any]] = Field(default_factory=list, description="All static issues")
    security_findings: List[Dict[str, Any]] = Field(default_factory=list, description="Security findings")
    style_findings: Dict[str, Any] = Field(default_factory=dict, description="Style and formatting metrics")
    metrics: Dict[str, Any] = Field(default_factory=dict, description="Quantitative source metrics (lines, tokens, etc.)")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional context metadata")
    hindsight_memories: List[Dict[str, Any]] = Field(default_factory=list, description="Recalled Hindsight agent memories")
    hindsight_prompt_context: Optional[str] = Field(default=None, description="Formatted Hindsight markdown context")


class AIProviderResponse(BaseModel):
    """Normalized response returned from an AI provider execution."""

    raw_text: str = Field(..., description="Raw response text from the AI model")
    parsed_json: Optional[Dict[str, Any]] = Field(default=None, description="Parsed structured JSON if available")
    model_used: str = Field(..., description="Exact model name used for generation")
    processing_time: float = Field(..., description="Duration in seconds")
    tokens_used: Optional[int] = Field(default=None, description="Estimated or reported token count")
    success: bool = Field(default=True, description="Whether generation succeeded")
    error: Optional[str] = Field(default=None, description="Error message if generation failed")
