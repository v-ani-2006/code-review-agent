from typing import Any, Dict, List, Optional
import uuid
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import logger
from app.models.task import Task
from app.models.user import User
from app.repositories.task_repository import task_repository
from app.schemas.task import TaskListResponse, TaskResponse


class TaskService:
    """Service orchestrating background job state, status tracking, and cancellation."""

    async def get_task(
        self,
        db: AsyncSession,
        task_id: uuid.UUID,
        user: User,
    ) -> TaskResponse:
        """Fetch single task by ID."""
        task = await task_repository.get_task_by_id(db, task_id=task_id, user_id=user.id, is_admin=user.is_admin)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task '{task_id}' not found.",
            )
        return TaskResponse.model_validate(task)

    async def list_tasks(
        self,
        db: AsyncSession,
        user: User,
        task_status: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> TaskListResponse:
        """List tasks scoped to authenticated user."""
        tasks, total = await task_repository.list_tasks(
            db,
            user_id=user.id,
            status=task_status,
            is_admin=user.is_admin,
            page=page,
            page_size=page_size,
        )
        return TaskListResponse(
            success=True,
            total_tasks=total,
            tasks=[TaskResponse.model_validate(t) for t in tasks],
        )

    async def delete_task(
        self,
        db: AsyncSession,
        task_id: uuid.UUID,
        user: User,
    ) -> Dict[str, Any]:
        """Delete task from database."""
        task = await task_repository.get_task_by_id(db, task_id=task_id, user_id=user.id, is_admin=user.is_admin)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task '{task_id}' not found.",
            )
        await task_repository.delete(db, task.id)
        logger.info("Task %s deleted by user %s", task_id, user.username)
        return {"success": True, "message": f"Task '{task_id}' successfully deleted."}

    async def cancel_task(
        self,
        db: AsyncSession,
        task_id: uuid.UUID,
        user: User,
    ) -> TaskResponse:
        """Mark task as CANCELLED."""
        task = await task_repository.get_task_by_id(db, task_id=task_id, user_id=user.id, is_admin=user.is_admin)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task '{task_id}' not found.",
            )
        if task.status in {"COMPLETED", "FAILED"}:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot cancel task with status '{task.status}'.",
            )
        task.status = "CANCELLED"
        await db.commit()
        await db.refresh(task)
        logger.info("Task %s cancelled by user %s", task_id, user.username)
        return TaskResponse.model_validate(task)


task_service = TaskService()
