import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class CodeIssue(BaseModel):
    """Specific code quality, style, bug, or security finding."""

    id: str = Field(..., description="Unique issue rule identifier (e.g. SEC-001, BUG-001)")
    title: str = Field(..., description="Concise title of the issue")
    description: str = Field(..., description="Detailed explanation of the issue")
    severity: str = Field(..., description="Severity level: LOW, MEDIUM, HIGH, CRITICAL")
    category: str = Field(..., description="Category: STYLE, BUG, SECURITY, COMPLEXITY, READABILITY, DOCUMENTATION")
    line_number: Optional[int] = Field(default=None, description="1-indexed line number in source code")
    column: Optional[int] = Field(default=None, description="1-indexed column offset in source code")
    suggestion: Optional[str] = Field(default=None, description="Recommended remediation action")


class CodeMetrics(BaseModel):
    """Quantitative source code composition metrics."""

    line_count: int = Field(default=0, description="Total number of physical lines")
    function_count: int = Field(default=0, description="Total functions defined")
    class_count: int = Field(default=0, description="Total classes defined")
    import_count: int = Field(default=0, description="Total import statements")
    comment_count: int = Field(default=0, description="Total comment lines")
    blank_line_count: int = Field(default=0, description="Total blank whitespace lines")
    character_count: int = Field(default=0, description="Total characters in source code")
    token_count: int = Field(default=0, description="Total parsed Python tokens")


class ComplexityMetrics(BaseModel):
    """Radon and AST cyclomatic complexity measurements."""

    cyclomatic_complexity: float = Field(default=1.0, description="Average cyclomatic complexity across blocks")
    maintainability_index: float = Field(default=100.0, description="Radon Maintainability Index (0-100)")
    halstead_volume: Optional[float] = Field(default=None, description="Halstead Volume score")
    halstead_difficulty: Optional[float] = Field(default=None, description="Halstead Difficulty score")
    rank: str = Field(default="A", description="Radon complexity grade rank (A-F)")
    functions_complexity: List[Dict[str, Any]] = Field(default_factory=list, description="Per-function complexity breakdown")


class ReviewScores(BaseModel):
    """Normalized scoring rubric (0 to 100, where 100 is optimal)."""

    readability: float = Field(..., ge=0.0, le=100.0, description="Readability score")
    maintainability: float = Field(..., ge=0.0, le=100.0, description="Maintainability score")
    security: float = Field(..., ge=0.0, le=100.0, description="Security vulnerability score")
    complexity: float = Field(..., ge=0.0, le=100.0, description="Structural simplicity score")
    documentation: float = Field(..., ge=0.0, le=100.0, description="Docstring and comment coverage score")
    overall: float = Field(..., ge=0.0, le=100.0, description="Weighted composite code quality score")


class ReviewRequest(BaseModel):
    """Input payload for comprehensive code review."""

    language: str = Field(
        default="python",
        description="Programming language (currently 'python' is supported)",
        examples=["python"],
    )
    code: str = Field(
        ...,
        min_length=1,
        description="Raw source code to analyze",
        examples=["def calculate_total(price, tax):\n    return price + (price * tax)\n"],
    )
    filename: Optional[str] = Field(
        default="main.py",
        description="Optional filename used for context and language detection",
        examples=["payment_service.py"],
    )


class TextReviewRequest(BaseModel):
    """Lightweight plain text code review request."""

    code: str = Field(..., min_length=1, description="Raw source code snippet")


class ReviewReport(BaseModel):
    """Complete static code analysis report."""

    summary: str = Field(..., description="Executive summary of the code review")
    scores: ReviewScores = Field(..., description="Categorized score breakdown")
    issues: List[CodeIssue] = Field(default_factory=list, description="All detected issues and findings")
    top_issues: List[CodeIssue] = Field(default_factory=list, description="Prioritized high and critical issues")
    metrics: CodeMetrics = Field(..., description="Quantitative code metrics")
    suggestions: Dict[str, List[str]] = Field(default_factory=dict, description="Actionable recommendations grouped by category")
    security_findings: List[CodeIssue] = Field(default_factory=list, description="Filtered security-specific findings")
    complexity: ComplexityMetrics = Field(..., description="Complexity metrics and Radon ratings")
    style: Dict[str, Any] = Field(default_factory=dict, description="Stylistic conventions and formatting metrics")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Language, AST statistics, and review parameters")
    timestamp: str = Field(..., description="UTC ISO 8601 timestamp of analysis")
    processing_time: float = Field(..., description="Total analysis duration in seconds")
    version: str = Field(default="0.1.0", description="Analyzer engine version")


class LanguageInfo(BaseModel):
    """Supported language descriptor."""

    name: str = Field(..., examples=["python"])
    supported: bool = Field(default=True)
    engine: str = Field(..., examples=["Python AST + Radon Engine"])


class RuleInfo(BaseModel):
    """Static analysis rule documentation."""

    id: str = Field(..., examples=["SEC-001"])
    name: str = Field(..., examples=["eval/exec Execution"])
    category: str = Field(..., examples=["SECURITY"])
    severity: str = Field(..., examples=["CRITICAL"])
    description: str = Field(..., examples=["Direct execution of arbitrary code via eval() or exec()."])
    suggestion: str = Field(..., examples=["Use safe parsing like ast.literal_eval()."])


# Retain Phase 3 ORM Database schemas for compatibility
class ReviewBase(BaseModel):
    language: str = Field(..., max_length=50)
    filename: str = Field(..., max_length=255)
    source_code: str


class ReviewCreate(ReviewBase):
    user_id: uuid.UUID
    summary: Optional[str] = None
    readability_score: Optional[float] = None
    security_score: Optional[float] = None
    complexity_score: Optional[float] = None
    maintainability_score: Optional[float] = None
    overall_score: Optional[float] = None
    favorite: bool = False
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


class ReviewResponse(ReviewBase):
    id: uuid.UUID
    user_id: uuid.UUID
    summary: Optional[str] = None
    readability_score: Optional[float] = None
    security_score: Optional[float] = None
    complexity_score: Optional[float] = None
    maintainability_score: Optional[float] = None
    overall_score: Optional[float] = None
    favorite: bool = False
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
