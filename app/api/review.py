from typing import Annotated, List, Optional
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_optional_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import ApiResponse
from app.schemas.review import (
    LanguageInfo,
    ReviewReport,
    ReviewRequest,
    RuleInfo,
    TextReviewRequest,
)
from app.services.review_service import review_service

router = APIRouter(prefix="/review", tags=["Code Review & AST Analysis"])


@router.post(
    "/code",
    response_model=ReviewReport,
    status_code=status.HTTP_200_OK,
    summary="Analyze Source Code via Python AST & Radon",
    description="Performs complete static analysis on submitted code: syntax validation, complexity scoring, Bandit security checks, PEP 8 style heuristics, and maintainability metrics.",
)
async def analyze_source_code(
    request: ReviewRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[Optional[User], Depends(get_optional_user)] = None,
) -> ReviewReport:
    """Analyze source code with full AST inspection and persist report if user is authenticated."""
    return await review_service.analyze_and_store(db, request, current_user)


@router.post(
    "/text",
    response_model=ReviewReport,
    status_code=status.HTTP_200_OK,
    summary="Analyze Raw Code Snippet",
    description="Lightweight review endpoint accepting plain source code strings.",
)
async def analyze_snippet(
    request: TextReviewRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[Optional[User], Depends(get_optional_user)] = None,
) -> ReviewReport:
    """Review raw code snippet without extra metadata."""
    full_request = ReviewRequest(
        language="python",
        code=request.code,
        filename="snippet.py",
    )
    return await review_service.analyze_and_store(db, full_request, current_user)


@router.get(
    "/languages",
    response_model=ApiResponse[List[LanguageInfo]],
    summary="List Supported Programming Languages",
    description="Returns all programming languages currently supported by the static analysis engine.",
)
async def get_supported_languages() -> ApiResponse[List[LanguageInfo]]:
    """Return list of supported languages."""
    languages = review_service.get_supported_languages()
    return ApiResponse(
        success=True,
        message="Supported languages retrieved.",
        data=languages,
    )


@router.get(
    "/rules",
    response_model=ApiResponse[List[RuleInfo]],
    summary="Catalog of Static Analysis Rules",
    description="Returns full catalog of active security, complexity, bug detection, and style analysis rules.",
)
async def get_analysis_rules() -> ApiResponse[List[RuleInfo]]:
    """Return master catalog of analysis rules."""
    rules = review_service.get_analysis_rules()
    return ApiResponse(
        success=True,
        message=f"Retrieved {len(rules)} analysis rules.",
        data=rules,
    )
