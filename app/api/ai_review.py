from typing import Annotated, Optional
from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_optional_user
from app.core.limiter import limiter
from app.db.session import get_db

from app.models.user import User
from app.schemas.ai_review import (
    AIBugFixRequest,
    AIBugFixResponse,
    AIDocumentationRequest,
    AIDocumentationResponse,
    AIExplainRequest,
    AIExplainResponse,
    AIModelListResponse,
    AIOptimizeRequest,
    AIOptimizeResponse,
    AIReviewRequest,
    AIReviewResponse,
    AIStatusResponse,
    AITestRequest,
    AITestResponse,
)
from app.services.ai_review_service import ai_review_service

router = APIRouter(prefix="/ai", tags=["AI Review"])


@router.post(
    "/review",
    response_model=AIReviewResponse,
    status_code=status.HTTP_200_OK,
    summary="Comprehensive AI Code Review",
    description="""
Execute the complete Phase 6 AI reasoning pipeline:
1. Performs Phase 5 AST, Radon complexity, Bandit security, and style static analysis.
2. Injects structured static findings into Google Gemini reasoning layer.
3. Generates high-level review, priority issues, strengths, weaknesses, and improvement roadmaps.
4. If an authenticated Bearer token is provided, persists the review and findings to the PostgreSQL database.
    """,
    responses={
        200: {
            "description": "Full AI and static analysis code review.",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "Comprehensive AI and static code review generated successfully.",
                        "processing_time": 1.25,
                        "model_used": "gemini-2.5-flash",
                        "generated_at": "2026-09-27T18:00:00Z",
                        "version": "0.1.0",
                        "review": {
                            "summary": "Clean calculation module with slight complexity in discount calculation.",
                            "overall_assessment": "The code adheres to PEP 8 standards with good modularity.",
                            "strengths": ["Clear parameter naming", "Consistent indentation"],
                            "critical_issues": ["Line 12: Insecure eval() call detected"],
                            "optimization_suggestions": ["Use dict dispatch instead of nested if-elif blocks"],
                            "next_steps": ["Replace eval with ast.literal_eval"]
                        }
                    }
                }
            }
        },
        400: {"description": "Invalid source code or unsupported programming language."}
    }
)
@limiter.limit("20/minute")
async def review_code(
    request: Request,
    review_in: AIReviewRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[Optional[User], Depends(get_optional_user)],
) -> AIReviewResponse:

    return await ai_review_service.review_and_store(db=db, request=review_in, current_user=current_user)


@router.post(
    "/explain",
    response_model=AIExplainResponse,
    status_code=status.HTTP_200_OK,
    summary="AI Code Explanation & Walkthrough",
    description="Generate beginner-friendly explanations, execution flows, and function/class structural breakdowns.",
)
async def explain_code(
    request: AIExplainRequest,
) -> AIExplainResponse:
    return await ai_review_service.explain(request=request)


@router.post(
    "/optimize",
    response_model=AIOptimizeResponse,
    status_code=status.HTTP_200_OK,
    summary="AI Code Optimization",
    description="Analyze source code for algorithmic efficiency, memory allocation, and Pythonic modern syntax.",
)
async def optimize_code(
    request: AIOptimizeRequest,
) -> AIOptimizeResponse:
    return await ai_review_service.optimize(request=request)


@router.post(
    "/fix",
    response_model=AIBugFixResponse,
    status_code=status.HTTP_200_OK,
    summary="AI Bug Detection & Fix",
    description="Detect logic bugs, syntax errors, and edge-case exceptions, and return fully corrected source code.",
)
async def fix_code(
    request: AIBugFixRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[Optional[User], Depends(get_optional_user)],
) -> AIBugFixResponse:
    return await ai_review_service.fix(db=db, request=request, current_user=current_user)


@router.post(
    "/documentation",
    response_model=AIDocumentationResponse,
    status_code=status.HTTP_200_OK,
    summary="AI Documentation & Docstrings",
    description="Generate Google/Sphinx style docstrings, parameter descriptions, usage examples, and annotated source code.",
)
@router.post("/docs", response_model=AIDocumentationResponse, include_in_schema=False)
async def generate_documentation(
    request: AIDocumentationRequest,
) -> AIDocumentationResponse:
    return await ai_review_service.document(request=request)


@router.post(
    "/tests",
    response_model=AITestResponse,
    status_code=status.HTTP_200_OK,
    summary="AI Unit Test Suite Generation",
    description="Generate an exhaustive pytest test suite with fixtures, parameterized tests, and edge case coverage.",
)
async def generate_tests(
    request: AITestRequest,
) -> AITestResponse:
    return await ai_review_service.generate_tests(request=request)


@router.get(
    "/models",
    response_model=AIModelListResponse,
    status_code=status.HTTP_200_OK,
    summary="List Supported AI Models",
    description="Retrieve the list of supported Google Gemini models available for code reasoning.",
)
async def list_models() -> AIModelListResponse:
    return await ai_review_service.get_models()


@router.get(
    "/status",
    response_model=AIStatusResponse,
    status_code=status.HTTP_200_OK,
    summary="AI Reasoning Layer Health & Status",
    description="Inspect Gemini client configuration, model availability, timeout thresholds, and retry policy.",
)
async def get_status() -> AIStatusResponse:
    return await ai_review_service.get_status()
