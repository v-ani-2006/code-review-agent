from typing import Annotated, Any, Dict, Optional
import uuid
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_active_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.task import TaskListResponse, TaskResponse
from app.services.task_service import task_service

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.get(
    "",
    response_model=TaskListResponse,
    status_code=status.HTTP_200_OK,
    summary="List All Background Tasks",
    description="Retrieve all background processing jobs submitted by the user.",
)
async def list_all_tasks(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    task_status: Optional[str] = Query(None, alias="status", description="Filter by status (PENDING, RUNNING, COMPLETED, FAILED, CANCELLED)"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
) -> TaskListResponse:
    """List tasks."""
    return await task_service.list_tasks(
        db=db,
        user=current_user,
        task_status=task_status,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/active",
    response_model=TaskListResponse,
    status_code=status.HTTP_200_OK,
    summary="List Active Tasks",
    description="Retrieve background tasks currently in PENDING or RUNNING status.",
)
async def list_active_tasks(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
) -> TaskListResponse:
    """List active tasks."""
    return await task_service.list_tasks(
        db=db,
        user=current_user,
        task_status="RUNNING",
        page=page,
        page_size=page_size,
    )


@router.get(
    "/completed",
    response_model=TaskListResponse,
    status_code=status.HTTP_200_OK,
    summary="List Completed Tasks",
    description="Retrieve successfully finished background review tasks.",
)
async def list_completed_tasks(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
) -> TaskListResponse:
    """List completed tasks."""
    return await task_service.list_tasks(
        db=db,
        user=current_user,
        task_status="COMPLETED",
        page=page,
        page_size=page_size,
    )


@router.get(
    "/failed",
    response_model=TaskListResponse,
    status_code=status.HTTP_200_OK,
    summary="List Failed Tasks",
    description="Retrieve tasks that encountered an error during analysis.",
)
async def list_failed_tasks(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
) -> TaskListResponse:
    """List failed tasks."""
    return await task_service.list_tasks(
        db=db,
        user=current_user,
        task_status="FAILED",
        page=page,
        page_size=page_size,
    )


@router.get(
    "/{task_id}",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Task by ID",
    description="Retrieve execution state, progress percentage, and timestamps for a specific task.",
)
async def get_task_by_id(
    task_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> TaskResponse:
    """Get single task."""
    return await task_service.get_task(db=db, task_id=task_id, user=current_user)


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete or Cancel Task",
    description="Delete a task record from tracking history.",
)
async def delete_task(
    task_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> Dict[str, Any]:
    """Delete task."""
    return await task_service.delete_task(db=db, task_id=task_id, user=current_user)
