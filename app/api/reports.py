from typing import Annotated, Any, Dict
from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_active_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.report import ReportListResponse, ReportResponse
from app.services.report_service import report_service

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get(
    "",
    response_model=ReportListResponse,
    status_code=status.HTTP_200_OK,
    summary="List Generated Reports",
    description="List all compiled project review reports available in storage.",
)
async def list_reports(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> ReportListResponse:
    """List available project reports."""
    return await report_service.list_reports()


@router.get(
    "/{report_id}",
    response_model=ReportResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Report Details",
    description="Fetch project audit summary and downloadable format URLs.",
)
async def get_report_details(
    report_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> ReportResponse:
    """Fetch report details."""
    return await report_service.get_report(report_id=report_id)


@router.get(
    "/{report_id}/download",
    status_code=status.HTTP_200_OK,
    summary="Download Project Report",
    description="Download project audit report in Markdown, JSON, responsive HTML, or complete ZIP package.",
)
async def download_report_artifact(
    report_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    format: str = Query("json", pattern="^(json|markdown|html|zip)$", description="Format: json, markdown, html, or zip"),
) -> FileResponse:
    """Download report file."""
    file_path, mime_type, filename = await report_service.get_report_file(
        report_id=report_id,
        export_format=format,
    )
    return FileResponse(
        path=str(file_path),
        media_type=mime_type,
        filename=filename,
    )


@router.delete(
    "/{report_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete Generated Report",
    description="Remove report artifacts and deliverables from storage.",
)
async def delete_report(
    report_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> Dict[str, Any]:
    """Delete report."""
    return await report_service.delete_report(report_id=report_id)
