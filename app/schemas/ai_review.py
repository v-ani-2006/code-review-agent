from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from app.schemas.review import ReviewReport


# --- BASE REQUEST & RESPONSE SCHEMAS ---
class AIBaseRequest(BaseModel):
    """Base request schema for code-related AI operations."""

    code: str = Field(
        ...,
        min_length=1,
        description="Raw source code to analyze and process",
        examples=["def add(a, b):\n    return a + b\n"],
    )
    language: str = Field(
        default="python",
        description="Programming language of the source code",
        examples=["python"],
    )
    filename: Optional[str] = Field(
        default="main.py",
        description="Optional filename of the code being processed",
        examples=["calculator.py"],
    )
    model: Optional[str] = Field(
        default=None,
        description="Override Gemini model identifier (e.g. gemini-2.5-flash)",
    )


class AIBaseResponse(BaseModel):
    """Standardized base response envelope for all AI operations."""

    success: bool = Field(default=True, description="Indicates whether the AI processing succeeded")
    message: str = Field(..., description="High-level status message or summary of the operation")
    processing_time: float = Field(..., description="Total execution duration in seconds")
    model_used: str = Field(..., description="Exact model version utilized for reasoning")
    generated_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="UTC ISO 8601 timestamp of response generation",
    )
    version: str = Field(default="0.1.0", description="Backend service version")


# --- 1. AI CODE REVIEW SCHEMAS ---
class AIReviewRequest(AIBaseRequest):
    """Request payload for full semantic and static code review."""
    pass


class AIReviewData(BaseModel):
    """Structured AI findings enriched from static AST analysis."""

    summary: str = Field(..., description="Executive summary of the review")
    overall_assessment: Optional[str] = Field(default=None, description="Detailed quality and architectural assessment")
    strengths: List[str] = Field(default_factory=list, description="Notable strengths of the code")
    critical_issues: List[str] = Field(default_factory=list, description="High-priority issues and bugs")
    security_analysis: Optional[str] = Field(default=None, description="Security vulnerability evaluation")
    complexity_analysis: Optional[str] = Field(default=None, description="Algorithmic and cognitive complexity analysis")
    readability_analysis: Optional[str] = Field(default=None, description="PEP 8 and style evaluation")
    maintainability_analysis: Optional[str] = Field(default=None, description="Maintainability and refactoring evaluation")
    optimization_suggestions: List[str] = Field(default_factory=list, description="Performance optimization tips")
    refactoring_suggestions: List[str] = Field(default_factory=list, description="Design pattern & refactoring opportunities")
    best_practices: List[str] = Field(default_factory=list, description="Recommended idiomatic practices")
    next_steps: List[str] = Field(default_factory=list, description="Actionable next steps")
    hindsight_context: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Historical conventions and lessons recalled from Hindsight Agent Memory",
    )
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadata and telemetry")


class AIReviewResponse(AIBaseResponse):
    """Combined response payload containing static AST report, AI reasoning, and Hindsight memory."""

    review: AIReviewData = Field(..., description="AI reasoning layer review")
    static_report: Optional[ReviewReport] = Field(
        default=None,
        description="Underlying Phase 5 static AST, complexity, and security report",
    )
    hindsight_context: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Recalled Hindsight agent memories actively applied to evaluate this review",
    )


# --- 2. AI CODE EXPLANATION SCHEMAS ---
class AIExplainRequest(AIBaseRequest):
    """Request payload to generate code explanation."""
    pass


class AIExplainData(BaseModel):
    """Detailed structural explanation and beginner walkthrough."""

    beginner_explanation: str = Field(..., description="Intuitive explanation in plain English")
    line_by_line_summary: List[Dict[str, Any]] = Field(default_factory=list, description="Line/block walkthrough")
    execution_flow: List[str] = Field(default_factory=list, description="Step-by-step program execution order")
    function_explanations: List[Dict[str, Any]] = Field(default_factory=list, description="Per-function breakdown")
    class_explanations: List[Dict[str, Any]] = Field(default_factory=list, description="Per-class breakdown")
    key_concepts: List[str] = Field(default_factory=list, description="Key computer science patterns and concepts")


class AIExplainResponse(AIBaseResponse):
    """Response containing code explanations."""

    data: AIExplainData = Field(..., description="Explanation payload")


# --- 3. AI CODE OPTIMIZATION SCHEMAS ---
class AIOptimizeRequest(AIBaseRequest):
    """Request payload to optimize source code."""
    pass


class AIOptimizeData(BaseModel):
    """Optimized code and complexity reduction breakdown."""

    optimized_code: str = Field(..., description="Optimized source code")
    performance_improvements: List[str] = Field(default_factory=list, description="Time complexity improvements")
    memory_improvements: List[str] = Field(default_factory=list, description="Memory footprint reductions")
    pythonic_improvements: List[str] = Field(default_factory=list, description="Pythonic idioms and modern syntax applied")
    time_complexity_before: Optional[str] = Field(default=None, description="Estimated time complexity before")
    time_complexity_after: Optional[str] = Field(default=None, description="Estimated time complexity after")
    space_complexity_before: Optional[str] = Field(default=None, description="Estimated space complexity before")
    space_complexity_after: Optional[str] = Field(default=None, description="Estimated space complexity after")


class AIOptimizeResponse(AIBaseResponse):
    """Response containing optimized code."""

    data: AIOptimizeData = Field(..., description="Optimization results")


# --- 4. AI BUG FIX SCHEMAS ---
class AIBugFixRequest(AIBaseRequest):
    """Request payload to diagnose and fix bugs."""
    pass


class AIBugFixData(BaseModel):
    """Corrected code and bug remediation details."""

    corrected_code: str = Field(..., description="Complete corrected source code")
    identified_bugs: List[Dict[str, Any]] = Field(default_factory=list, description="Identified bugs with locations")
    changed_sections: List[Dict[str, Any]] = Field(default_factory=list, description="Diff and modified sections")
    reasons_for_changes: List[str] = Field(default_factory=list, description="Detailed rationales for fixes")
    verification_steps: List[str] = Field(default_factory=list, description="Instructions to verify remediation")


class AIBugFixResponse(AIBaseResponse):
    """Response containing corrected code."""

    data: AIBugFixData = Field(..., description="Bug fix results")


# --- 5. AI DOCUMENTATION SCHEMAS ---
class AIDocumentationRequest(AIBaseRequest):
    """Request payload to generate docstrings and documentation."""
    pass


class AIDocumentationData(BaseModel):
    """Generated documentation and fully annotated code."""

    documented_code: str = Field(..., description="Source code with inserted docstrings")
    module_docstring: Optional[str] = Field(default=None, description="Module-level docstring")
    class_docstrings: List[Dict[str, Any]] = Field(default_factory=list, description="Class docstrings")
    function_docstrings: List[Dict[str, Any]] = Field(default_factory=list, description="Function/method docstrings")
    parameter_descriptions: List[Dict[str, Any]] = Field(default_factory=list, description="Parameter documentation")
    usage_examples: List[str] = Field(default_factory=list, description="Practical usage examples")


class AIDocumentationResponse(AIBaseResponse):
    """Response containing documentation artifacts."""

    data: AIDocumentationData = Field(..., description="Documentation results")


# --- 6. AI UNIT TEST SCHEMAS ---
class AITestRequest(AIBaseRequest):
    """Request payload to generate pytest test suite."""
    pass


class AITestData(BaseModel):
    """Generated pytest suite and test coverage metadata."""

    test_code: str = Field(..., description="Complete runnable pytest test code")
    test_framework: str = Field(default="pytest", description="Testing framework used")
    fixtures: List[Dict[str, Any]] = Field(default_factory=list, description="Defined pytest fixtures")
    covered_edge_cases: List[str] = Field(default_factory=list, description="Covered edge cases and boundary conditions")
    parameterized_cases: List[str] = Field(default_factory=list, description="Parameterized test scenarios")
    execution_command: str = Field(default="pytest -v", description="CLI command to run the generated suite")


class AITestResponse(AIBaseResponse):
    """Response containing generated test suite."""

    data: AITestData = Field(..., description="Test generation results")


# --- 7. STATUS & MODELS SCHEMAS ---
class AIModelListResponse(BaseModel):
    """List of available Gemini models."""

    success: bool = True
    provider: str = "gemini"
    default_model: str
    available_models: List[str]


class AIStatusResponse(BaseModel):
    """Operational status of the AI reasoning layer."""

    success: bool = True
    provider: str = "gemini"
    configured: bool
    status: str
    model: str
    timeout_seconds: int
    max_retries: int
