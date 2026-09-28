from pathlib import Path
from typing import Annotated, Any, Dict, List, Optional
import uuid
from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, Query, Request, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_active_user
from app.core.limiter import limiter
from app.db.session import get_db
from app.models.user import User
from app.repositories.task_repository import task_repository
from app.schemas.batch import BatchReviewResponse
from app.schemas.task import TaskListResponse, TaskResponse
from app.services.batch_service import batch_service
from app.services.report_service import report_service
from app.services.task_service import task_service
from app.utils.file_utils import async_write_bytes, sanitize_filename


router = APIRouter(prefix="/batch", tags=["Batch Review"])
TEMP_DIR = Path("app/uploads/temp")


@router.post(
    "/review",
    response_model=BatchReviewResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Batch Code Review",
    description="Analyze multiple source files or ZIP project archive in a concurrent batch execution pipeline.",
)
@limiter.limit("15/minute")
async def batch_review(
    request: Request,
    background_tasks: BackgroundTasks,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    file: UploadFile = File(..., description="Project ZIP archive or Python source code package"),
    project_name: Optional[str] = Query(None, description="Project label"),
    run_in_background: bool = Query(False, description="Run as background job"),
) -> BatchReviewResponse:

    """Execute batch code review."""
    raw_filename = sanitize_filename(file.filename or "batch.zip")
    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    temp_path = TEMP_DIR / f"{uuid.uuid4()}_{raw_filename}"
    file_bytes = await file.read()
    await async_write_bytes(temp_path, file_bytes)

    proj_name = project_name or Path(raw_filename).stem
    task = await task_repository.create_task(
        db,
        user_id=current_user.id,
        task_type="batch_review",
        filename=raw_filename,
    )

    if run_in_background:
        background_tasks.add_task(
            batch_service.run_project_analysis_background,
            user_id=current_user.id,
            zip_file_path=temp_path,
            project_name=proj_name,
            task_id=task.id,
        )
        return BatchReviewResponse(
            task_id=task.id,
            status="PENDING",
            overall_project_score=0.0,
            total_files_analyzed=0,
            total_issues=0,
            critical_issues=0,
            security_summary="Batch job queued in background.",
            complexity_summary="Pending background execution.",
            documentation_summary="Pending background execution.",
            average_readability=0.0,
            average_maintainability=0.0,
            project_metrics=None,  # type: ignore
        )

    return await batch_service.execute_project_pipeline(
        db=db,
        user=current_user,
        zip_file_path=temp_path,
        project_name=proj_name,
        task=task,
    )


@router.post(
    "/project",
    response_model=BatchReviewResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Batch Project Analysis",
    description="Analyze full repository project package.",
)
async def batch_project_analysis(
    background_tasks: BackgroundTasks,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    file: UploadFile = File(..., description="Project archive (.zip)"),
    project_name: Optional[str] = Query(None, description="Project name"),
    run_in_background: bool = Query(False, description="Run in background"),
) -> BatchReviewResponse:
    """Analyze project repository archive."""
    return await batch_review(
        background_tasks=background_tasks,
        db=db,
        current_user=current_user,
        file=file,
        project_name=project_name,
        run_in_background=run_in_background,
    )


@router.get(
    "/history",
    response_model=TaskListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Batch Analysis History",
    description="List all batch and project review jobs submitted by user.",
)
async def get_batch_history(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
) -> TaskListResponse:
    """List batch execution history."""
    return await task_service.list_tasks(db=db, user=current_user, page=page, page_size=page_size)


@router.get(
    "/{task_id}",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Batch Task Status",
    description="Check status, progress percentage, and metrics of a running or completed batch task.",
)
async def get_batch_task(
    task_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> TaskResponse:
    """Get batch task status."""
    return await task_service.get_task(db=db, task_id=task_id, user=current_user)


@router.get(
    "/{task_id}/results",
    status_code=status.HTTP_200_OK,
    summary="Get Batch Task Results",
    description="Retrieve generated review results and report for a completed batch job.",
)
async def get_batch_task_results(
    task_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> Dict[str, Any]:
    """Get results of completed batch review."""
    task = await task_repository.get_task_by_id(db, task_id=task_id, user_id=current_user.id, is_admin=current_user.is_admin)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Task '{task_id}' not found.")

    if task.status != "COMPLETED":
        return {
            "task_id": task.id,
            "status": task.status,
            "progress_percentage": task.progress_percentage,
            "message": "Task has not completed yet or failed.",
        }

    report_id = Path(task.output_path).name if task.output_path else None
    report_data = None
    if report_id:
        try:
            report_data = await report_service.get_report(report_id)
        except Exception:
            pass

    return {
        "task_id": task.id,
        "status": task.status,
        "processing_time": task.processing_time,
        "total_files": task.total_files,
        "processed_files": task.processed_files,
        "report_id": report_id,
        "report": report_data,
    }


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_200_OK,
    summary="Cancel or Delete Batch Task",
    description="Cancel or delete a batch review task.",
)
async def delete_or_cancel_batch_task(
    task_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> Dict[str, Any]:
    """Delete or cancel batch task."""
    return await task_service.delete_task(db=db, task_id=task_id, user=current_user)
