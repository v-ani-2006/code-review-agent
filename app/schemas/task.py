from datetime import datetime
from typing import List, Optional
import uuid
from pydantic import BaseModel, ConfigDict, Field


class TaskResponse(BaseModel):
    """Status, metrics, and progress info for an asynchronous job."""

    id: uuid.UUID
    user_id: uuid.UUID
    task_type: str
    status: str
    filename: Optional[str] = None
    total_files: int = 0
    processed_files: int = 0
    failed_files: int = 0
    progress_percentage: float = 0.0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    output_path: Optional[str] = None
    processing_time: Optional[float] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TaskListResponse(BaseModel):
    """Collection of background task records."""

    success: bool = True
    total_tasks: int
    tasks: List[TaskResponse] = Field(default_factory=list)
