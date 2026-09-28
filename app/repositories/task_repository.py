from datetime import datetime, timezone
from typing import List, Optional, Tuple
import uuid
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import Task
from app.repositories.base_repository import BaseRepository


class TaskRepository(BaseRepository[Task]):
    """Repository handling asynchronous job state, progress metrics, and execution statuses."""

    def __init__(self):
        super().__init__(Task)

    async def create_task(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        task_type: str = "batch_upload",
        filename: Optional[str] = None,
        total_files: int = 0,
    ) -> Task:
        """Initialize a new pending background task."""
        return await self.create(
            db,
            user_id=user_id,
            task_type=task_type,
            status="PENDING",
            filename=filename,
            total_files=total_files,
            processed_files=0,
            failed_files=0,
            progress_percentage=0.0,
            started_at=None,
            completed_at=None,
        )

    async def get_task_by_id(
        self,
        db: AsyncSession,
        task_id: uuid.UUID,
        user_id: uuid.UUID,
        is_admin: bool = False,
    ) -> Optional[Task]:
        """Fetch task enforcing user ownership or admin authority."""
        stmt = select(Task).where(Task.id == task_id)
        if not is_admin:
            stmt = stmt.where(Task.user_id == user_id)
        result = await db.execute(stmt)
        return result.scalars().first()

    async def list_tasks(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        status: Optional[str] = None,
        is_admin: bool = False,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[Task], int]:
        """Query tasks filtered by user and status."""
        conditions = []
        if not is_admin:
            conditions.append(Task.user_id == user_id)
        if status:
            conditions.append(func.upper(Task.status) == status.upper().strip())

        count_stmt = select(func.count(Task.id))
        if conditions:
            count_stmt = count_stmt.where(and_(*conditions))
        total_res = await db.execute(count_stmt)
        total = total_res.scalar_one() or 0

        stmt = select(Task)
        if conditions:
            stmt = stmt.where(and_(*conditions))
        stmt = stmt.order_by(Task.created_at.desc()).offset((page - 1) * page_size).limit(page_size)

        result = await db.execute(stmt)
        return list(result.scalars().all()), total

    async def update_progress(
        self,
        db: AsyncSession,
        task: Task,
        processed_files: int,
        failed_files: int = 0,
        total_files: Optional[int] = None,
    ) -> Task:
        """Increment progress metrics for active task."""
        if total_files is not None:
            task.total_files = total_files
        task.processed_files = processed_files
        task.failed_files = failed_files
        if task.total_files > 0:
            task.progress_percentage = round((task.processed_files / task.total_files) * 100.0, 1)

        await db.flush()
        try:
            await db.refresh(task)
        except Exception:
            pass
        return task

    async def mark_running(
        self,
        db: AsyncSession,
        task: Task,
    ) -> Task:
        """Mark task as running with started_at timestamp."""
        task.status = "RUNNING"
        task.started_at = datetime.now(timezone.utc)
        await db.commit()
        await db.refresh(task)
        return task

    async def mark_completed(
        self,
        db: AsyncSession,
        task: Task,
        output_path: Optional[str] = None,
        processing_time: Optional[float] = None,
    ) -> Task:
        """Mark task as completed successfully."""
        task.status = "COMPLETED"
        task.completed_at = datetime.now(timezone.utc)
        task.progress_percentage = 100.0
        if output_path:
            task.output_path = output_path
        if processing_time is not None:
            task.processing_time = round(processing_time, 3)

        await db.commit()
        await db.refresh(task)
        return task

    async def mark_failed(
        self,
        db: AsyncSession,
        task: Task,
        error_message: str,
        processing_time: Optional[float] = None,
    ) -> Task:
        """Mark task as failed with diagnostic error message."""
        task.status = "FAILED"
        task.completed_at = datetime.now(timezone.utc)
        task.error_message = error_message
        if processing_time is not None:
            task.processing_time = round(processing_time, 3)

        await db.commit()
        await db.refresh(task)
        return task


task_repository = TaskRepository()
