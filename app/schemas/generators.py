from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


# --- BASE GENERATOR SCHEMAS ---
class GeneratorBaseRequest(BaseModel):
    """Base request schema for code-related generator tasks."""

    code: str = Field(..., min_length=1, description="Raw source code to process")
    filename: Optional[str] = Field(default="main.py", description="Source code filename")
    language: Optional[str] = Field(default="python", description="Programming language")
    model: Optional[str] = Field(default=None, description="Optional Gemini model override")


class GeneratorBaseResponse(BaseModel):
    """Standardized response envelope for all AI generator endpoints."""

    success: bool = Field(default=True, description="Indicates whether the generation succeeded")
    message: str = Field(..., description="High-level status message")
    generated_content: str = Field(..., description="Primary generated text or code content")
    format: str = Field(default="markdown", description="Content format (e.g. markdown, python, text)")
    model_used: str = Field(..., description="Exact AI model used for generation")
    processing_time: float = Field(..., description="Duration in seconds")
    generated_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="UTC ISO 8601 generation timestamp",
    )
    version: str = Field(default="0.1.0", description="Backend service version")


# --- 1. DOCUMENTATION SCHEMAS ---
class DocumentationRequest(GeneratorBaseRequest):
    """Request schema for generating full module/package technical documentation."""

    include_api_doc: bool = Field(default=True, description="Whether to include API method and parameter tables")


class DocumentationResponse(GeneratorBaseResponse):
    """Response containing generated technical documentation."""

    data: Optional[Dict[str, Any]] = Field(default=None, description="Structured parsed class and function data")


# --- 2. DOCSTRING SCHEMAS ---
class DocstringRequest(GeneratorBaseRequest):
    """Request schema for generating standardized code docstrings."""

    style: str = Field(
        default="google",
        description="Docstring convention: 'google', 'numpy', or 'sphinx'",
        examples=["google"],
    )
    include_inline_comments: bool = Field(
        default=False,
        description="Whether to generate explanatory inline comments alongside docstrings",
    )


class DocstringResponse(GeneratorBaseResponse):
    """Response containing code with inserted docstrings."""

    annotated_code: str = Field(..., description="Complete source code with inserted docstrings")
    style_used: str = Field(..., description="Docstring convention applied")
    summary: Optional[str] = Field(default=None, description="Summary of docstring additions")


# --- 3. UNIT TEST SCHEMAS ---
class TestGeneratorRequest(GeneratorBaseRequest):
    """Request schema for generating a pytest test suite."""

    include_edge_cases: bool = Field(default=True, description="Include boundary and null edge cases")
    include_async_tests: bool = Field(default=True, description="Generate pytest-asyncio async tests")
    include_security_tests: bool = Field(default=True, description="Generate input validation and security checks")


class TestGeneratorResponse(GeneratorBaseResponse):
    """Response containing complete pytest test file."""

    test_code: str = Field(..., description="Complete runnable pytest test suite")
    framework: str = Field(default="pytest", description="Testing framework used")
    fixtures: List[str] = Field(default_factory=list, description="Fixtures created in test file")
    edge_cases: List[str] = Field(default_factory=list, description="Covered edge case descriptions")
    security_cases: List[str] = Field(default_factory=list, description="Covered security test descriptions")


# --- 4. README SCHEMAS ---
class ReadmeRequest(BaseModel):
    """Request schema for generating a GitHub README.md."""

    project_name: str = Field(..., min_length=1, description="Name of the open source or enterprise project")
    description: str = Field(..., min_length=1, description="Brief synopsis of what the project does")
    code_context: Optional[str] = Field(default=None, description="Sample source code or directory list for context")
    endpoints: Optional[List[Dict[str, str]]] = Field(default=None, description="List of API endpoints")
    tech_stack: Optional[List[Dict[str, str]]] = Field(default=None, description="List of technologies")
    model: Optional[str] = Field(default=None, description="Gemini model override")


class ReadmeResponse(GeneratorBaseResponse):
    """Response containing generated README.md."""
    pass


# --- 5. REFACTOR SCHEMAS ---
class RefactorRequest(GeneratorBaseRequest):
    """Request schema for refactoring source code."""

    focus_areas: Optional[List[str]] = Field(
        default=None,
        description="Specific optimization areas (e.g. ['performance', 'naming', 'modularization'])",
    )


class RefactorResponse(GeneratorBaseResponse):
    """Response containing original and refactored code."""

    original_code: str = Field(..., description="Original code submitted")
    refactored_code: str = Field(..., description="Cleaned, refactored, and modularized code")
    improvements: List[Dict[str, str]] = Field(default_factory=list, description="Categorized list of improvements made")


# --- 6. ARCHITECTURE SCHEMAS ---
class ArchitectureRequest(BaseModel):
    """Request schema for generating system architecture specifications."""

    system_name: str = Field(default="CodePilot AI", description="System or service name")
    description: Optional[str] = Field(default=None, description="Core purpose and domain of the system")
    context_notes: Optional[str] = Field(default=None, description="Architectural constraints, frameworks, or database choices")
    model: Optional[str] = Field(default=None, description="Gemini model override")


class ArchitectureResponse(GeneratorBaseResponse):
    """Response containing generated architecture specification."""
    pass


# --- 7. CHANGELOG SCHEMAS ---
class ChangelogRequest(BaseModel):
    """Request schema for generating release changelogs from code diffs."""

    original_code: str = Field(..., min_length=1, description="Prior version of source code")
    updated_code: str = Field(..., min_length=1, description="New version of source code")
    filename: Optional[str] = Field(default="main.py", description="Target filename")
    version: Optional[str] = Field(default="1.0.0", description="Semantic release version")
    model: Optional[str] = Field(default=None, description="Gemini model override")


class ChangelogResponse(GeneratorBaseResponse):
    """Response containing Keep a Changelog formatted markdown."""

    added: List[str] = Field(default_factory=list, description="New features added")
    changed: List[str] = Field(default_factory=list, description="Modified features")
    removed: List[str] = Field(default_factory=list, description="Removed features")
    fixed: List[str] = Field(default_factory=list, description="Fixed bugs")
    security: List[str] = Field(default_factory=list, description="Security patches")


# --- 8. SUMMARY SCHEMAS ---
class SummaryRequest(GeneratorBaseRequest):
    """Request schema for generating an executive code review summary."""

    static_summary: Optional[str] = Field(default=None, description="Optional Phase 5 static AST summary")


class SummaryResponse(GeneratorBaseResponse):
    """Response containing executive code review summary."""

    overall_quality: str = Field(..., description="Executive assessment of production readiness")
    major_risks: List[str] = Field(default_factory=list, description="Key vulnerabilities and code smells")
    major_strengths: List[str] = Field(default_factory=list, description="Key positive engineering patterns")
    improvement_roadmap: List[str] = Field(default_factory=list, description="Prioritized action steps")
