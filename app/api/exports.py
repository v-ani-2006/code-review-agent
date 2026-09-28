from fastapi import APIRouter, status
from app.schemas.exports import ExportRequest, ExportResponse
from app.services.export_service import app_export_service

router = APIRouter(prefix="/export", tags=["Export"])


@router.post(
    "/json",
    response_model=ExportResponse,
    status_code=status.HTTP_200_OK,
    summary="Export as JSON",
    description="Format and export review data or structured artifacts into standardized JSON format.",
)
async def export_json(request: ExportRequest) -> ExportResponse:
    return app_export_service.export_json(request)


@router.post(
    "/markdown",
    response_model=ExportResponse,
    status_code=status.HTTP_200_OK,
    summary="Export as Markdown",
    description="Render review data or documents into clean GitHub-flavored markdown with code fences and tables.",
)
async def export_markdown(request: ExportRequest) -> ExportResponse:
    return app_export_service.export_markdown(request)


@router.post(
    "/html",
    response_model=ExportResponse,
    status_code=status.HTTP_200_OK,
    summary="Export as Responsive HTML",
    description="Convert markdown reports into modern, responsive, styled HTML documents with typography, tables, and code formatting.",
)
async def export_html(request: ExportRequest) -> ExportResponse:
    return app_export_service.export_html(request)


@router.post(
    "/text",
    response_model=ExportResponse,
    status_code=status.HTTP_200_OK,
    summary="Export as Plain Text",
    description="Strip markdown syntax and export documents into clean, human-readable plain text.",
)
async def export_text(request: ExportRequest) -> ExportResponse:
    return app_export_service.export_text(request)
