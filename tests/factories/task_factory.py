"""Task model factory producing realistic background task records for testing."""
import uuid
from faker import Faker
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import Task

fake = Faker()


class TaskFactory:
    """Factory generating Task entity instances."""

    @classmethod
    def build(
        cls,
        id: uuid.UUID = None,
        user_id: uuid.UUID = None,
        task_type: str = "batch_upload",
        status: str = "COMPLETED",
        filename: str = "archive.zip",
        total_files: int = 5,
        processed_files: int = 5,
        failed_files: int = 0,
        progress_percentage: float = 100.0,
        error_message: str = None,
    ) -> Task:
        return Task(
            id=id or uuid.uuid4(),
            user_id=user_id or uuid.uuid4(),
            task_type=task_type,
            status=status,
            filename=filename,
            total_files=total_files,
            processed_files=processed_files,
            failed_files=failed_files,
            progress_percentage=progress_percentage,
            error_message=error_message,
            processing_time=1.25,
        )

    @classmethod
    async def create(cls, db: AsyncSession, **kwargs) -> Task:
        task = cls.build(**kwargs)
        db.add(task)
        await db.flush()
        await db.refresh(task)
        return task
