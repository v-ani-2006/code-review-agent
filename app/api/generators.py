from typing import Annotated, Optional
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_optional_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.generators import (
    ArchitectureRequest,
    ArchitectureResponse,
    ChangelogRequest,
    ChangelogResponse,
    DocstringRequest,
    DocstringResponse,
    DocumentationRequest,
    DocumentationResponse,
    ReadmeRequest,
    ReadmeResponse,
    RefactorRequest,
    RefactorResponse,
    SummaryRequest,
    SummaryResponse,
    TestGeneratorRequest,
    TestGeneratorResponse,
)
from app.services.generator_service import generator_service

router = APIRouter(prefix="/generate", tags=["AI Generation"])


@router.post(
    "/documentation",
    response_model=DocumentationResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate Technical Documentation",
    description="Generate comprehensive module overview, class hierarchies, method signatures, parameter guides, and usage examples.",
)
async def generate_documentation(
    request: DocumentationRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[Optional[User], Depends(get_optional_user)],
) -> DocumentationResponse:
    return await generator_service.generate_documentation(request=request, db=db, current_user=current_user)


@router.post(
    "/docstrings",
    response_model=DocstringResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate Standardized Docstrings",
    description="Annotate source code with Google, NumPy, or Sphinx formatted docstrings and optional inline explanations.",
)
async def generate_docstrings(
    request: DocstringRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[Optional[User], Depends(get_optional_user)],
) -> DocstringResponse:
    return await generator_service.generate_docstrings(request=request, db=db, current_user=current_user)


@router.post(
    "/tests",
    response_model=TestGeneratorResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate Pytest Test Suite",
    description="Generate a production-ready pytest suite containing fixtures, mocks, async tests, boundary edge cases, and security assertions.",
)
async def generate_tests(
    request: TestGeneratorRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[Optional[User], Depends(get_optional_user)],
) -> TestGeneratorResponse:
    return await generator_service.generate_tests(request=request, db=db, current_user=current_user)


@router.post(
    "/readme",
    response_model=ReadmeResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate GitHub README",
    description="Generate an exhaustive GitHub README.md featuring architecture diagrams, badges, tech stack, API tables, and setup instructions.",
)
async def generate_readme(
    request: ReadmeRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[Optional[User], Depends(get_optional_user)],
) -> ReadmeResponse:
    return await generator_service.generate_readme(request=request, db=db, current_user=current_user)


@router.post(
    "/refactor",
    response_model=RefactorResponse,
    status_code=status.HTTP_200_OK,
    summary="Automated Code Refactoring",
    description="Analyze source code for modularization, duplicate elimination, naming improvements, and Pythonic modernization.",
)
async def generate_refactor(
    request: RefactorRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[Optional[User], Depends(get_optional_user)],
) -> RefactorResponse:
    return await generator_service.generate_refactor(request=request, db=db, current_user=current_user)


@router.post(
    "/architecture",
    response_model=ArchitectureResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate Architecture Specification",
    description="Generate comprehensive architectural documentation detailing routing, authentication flows, AI pipelines, database schemas, and request lifecycles.",
)
async def generate_architecture(
    request: ArchitectureRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[Optional[User], Depends(get_optional_user)],
) -> ArchitectureResponse:
    return await generator_service.generate_architecture(request=request, db=db, current_user=current_user)


@router.post(
    "/changelog",
    response_model=ChangelogResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate Release Changelog",
    description="Compare two source code versions and generate Keep a Changelog categorized release notes (Added, Changed, Removed, Fixed, Security).",
)
async def generate_changelog(
    request: ChangelogRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[Optional[User], Depends(get_optional_user)],
) -> ChangelogResponse:
    return await generator_service.generate_changelog(request=request, db=db, current_user=current_user)


@router.post(
    "/summary",
    response_model=SummaryResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate Executive Code Summary",
    description="Synthesize code quality, major risks, architectural strengths, and improvement roadmaps into an executive briefing.",
)
async def generate_summary(
    request: SummaryRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[Optional[User], Depends(get_optional_user)],
) -> SummaryResponse:
    return await generator_service.generate_summary(request=request, db=db, current_user=current_user)
