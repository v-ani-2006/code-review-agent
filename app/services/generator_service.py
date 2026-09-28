from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.generators import (
    ArchitectureGenerator,
    ChangelogGenerator,
    DocstringGenerator,
    DocumentationGenerator,
    ReadmeGenerator,
    RefactorGenerator,
    SummaryGenerator,
    UnitTestGenerator,
)
from app.core.logging import logger
from app.models.user import User
from app.repositories.review_repository import review_repository
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


class GeneratorService:
    """Service orchestrating AI documentation, test, readme, refactor, architecture, changelog, and summary generation."""

    # 1. Documentation
    async def generate_documentation(
        self,
        request: DocumentationRequest,
        db: Optional[AsyncSession] = None,
        current_user: Optional[User] = None,
    ) -> DocumentationResponse:
        generator = DocumentationGenerator(model=request.model)
        result = await generator.generate(
            code=request.code,
            filename=request.filename or "main.py",
            language=request.language or "python",
            include_api_doc=request.include_api_doc,
        )
        return DocumentationResponse(
            success=result["success"],
            message="Technical documentation generated successfully." if result["success"] else "Generation encountered warnings",
            generated_content=result["markdown"],
            format="markdown",
            model_used=result["model_used"],
            processing_time=result["processing_time"],
            data=result["data"],
        )

    # 2. Docstrings
    async def generate_docstrings(
        self,
        request: DocstringRequest,
        db: Optional[AsyncSession] = None,
        current_user: Optional[User] = None,
    ) -> DocstringResponse:
        generator = DocstringGenerator(model=request.model)
        result = await generator.generate(
            code=request.code,
            style=request.style,
            include_inline_comments=request.include_inline_comments,
            filename=request.filename or "main.py",
            language=request.language or "python",
        )
        return DocstringResponse(
            success=result["success"],
            message=f"Code annotated with {result['style_used']} docstrings.",
            generated_content=result["annotated_code"],
            annotated_code=result["annotated_code"],
            style_used=result["style_used"],
            summary=result["summary"],
            format=request.language or "python",
            model_used=result["model_used"],
            processing_time=result["processing_time"],
        )

    # 3. Unit Tests
    async def generate_tests(
        self,
        request: TestGeneratorRequest,
        db: Optional[AsyncSession] = None,
        current_user: Optional[User] = None,
    ) -> TestGeneratorResponse:
        generator = UnitTestGenerator(model=request.model)
        result = await generator.generate(
            code=request.code,
            filename=request.filename or "main.py",
            language=request.language or "python",
            include_edge_cases=request.include_edge_cases,
            include_async_tests=request.include_async_tests,
            include_security_tests=request.include_security_tests,
        )
        return TestGeneratorResponse(
            success=result["success"],
            message="Pytest test suite generated successfully.",
            generated_content=result["test_code"],
            test_code=result["test_code"],
            framework=result["framework"],
            fixtures=result["fixtures"],
            edge_cases=result["edge_cases"],
            security_cases=result["security_cases"],
            format="python",
            model_used=result["model_used"],
            processing_time=result["processing_time"],
        )

    # 4. README
    async def generate_readme(
        self,
        request: ReadmeRequest,
        db: Optional[AsyncSession] = None,
        current_user: Optional[User] = None,
    ) -> ReadmeResponse:
        generator = ReadmeGenerator(model=request.model)
        result = await generator.generate(
            project_name=request.project_name,
            description=request.description,
            code_context=request.code_context,
            endpoints=request.endpoints,
            tech_stack=request.tech_stack,
        )
        return ReadmeResponse(
            success=result["success"],
            message="GitHub README.md generated successfully.",
            generated_content=result["markdown"],
            format="markdown",
            model_used=result["model_used"],
            processing_time=result["processing_time"],
        )

    # 5. Refactor
    async def generate_refactor(
        self,
        request: RefactorRequest,
        db: Optional[AsyncSession] = None,
        current_user: Optional[User] = None,
    ) -> RefactorResponse:
        generator = RefactorGenerator(model=request.model)
        result = await generator.generate(
            code=request.code,
            filename=request.filename or "main.py",
            language=request.language or "python",
            focus_areas=request.focus_areas,
        )
        return RefactorResponse(
            success=result["success"],
            message="Code refactored successfully.",
            generated_content=result["refactored_code"],
            original_code=result["original_code"],
            refactored_code=result["refactored_code"],
            improvements=result["improvements"],
            format=request.language or "python",
            model_used=result["model_used"],
            processing_time=result["processing_time"],
        )

    # 6. Architecture
    async def generate_architecture(
        self,
        request: ArchitectureRequest,
        db: Optional[AsyncSession] = None,
        current_user: Optional[User] = None,
    ) -> ArchitectureResponse:
        generator = ArchitectureGenerator(model=request.model)
        result = await generator.generate(
            system_name=request.system_name,
            description=request.description,
            context_notes=request.context_notes,
        )
        return ArchitectureResponse(
            success=result["success"],
            message="System architecture specification generated successfully.",
            generated_content=result["markdown"],
            format="markdown",
            model_used=result["model_used"],
            processing_time=result["processing_time"],
        )

    # 7. Changelog
    async def generate_changelog(
        self,
        request: ChangelogRequest,
        db: Optional[AsyncSession] = None,
        current_user: Optional[User] = None,
    ) -> ChangelogResponse:
        generator = ChangelogGenerator(model=request.model)
        result = await generator.generate(
            original_code=request.original_code,
            updated_code=request.updated_code,
            filename=request.filename or "main.py",
            version=request.version or "1.0.0",
        )
        data = result.get("data", {})
        return ChangelogResponse(
            success=result["success"],
            message="Keep a Changelog release notes generated successfully.",
            generated_content=result["markdown"],
            format="markdown",
            added=data.get("added", []),
            changed=data.get("changed", []),
            removed=data.get("removed", []),
            fixed=data.get("fixed", []),
            security=data.get("security", []),
            model_used=result["model_used"],
            processing_time=result["processing_time"],
        )

    # 8. Summary
    async def generate_summary(
        self,
        request: SummaryRequest,
        db: Optional[AsyncSession] = None,
        current_user: Optional[User] = None,
    ) -> SummaryResponse:
        generator = SummaryGenerator(model=request.model)
        result = await generator.generate(
            code=request.code,
            filename=request.filename or "main.py",
            language=request.language or "python",
            static_summary=request.static_summary,
        )
        return SummaryResponse(
            success=result["success"],
            message="Executive code review summary generated successfully.",
            generated_content=result["markdown"],
            format="markdown",
            overall_quality=result["overall_quality"],
            major_risks=result["major_risks"],
            major_strengths=result["major_strengths"],
            improvement_roadmap=result["improvement_roadmap"],
            model_used=result["model_used"],
            processing_time=result["processing_time"],
        )


# Singleton generator service
generator_service = GeneratorService()
