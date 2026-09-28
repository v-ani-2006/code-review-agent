import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional
from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.user import User


class Task(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Task entity representing asynchronous batch, project scan, and upload processing jobs."""

    __tablename__ = "tasks"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    task_type: Mapped[str] = mapped_column(
        String(50),
        default="batch_upload",
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(50),
        default="PENDING",
        nullable=False,
        index=True,
    )
    filename: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )
    total_files: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    processed_files: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    failed_files: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    progress_percentage: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )
    started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    error_message: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    output_path: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    processing_time: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        lazy="joined",
    )

    def __repr__(self) -> str:
        return f"<Task id={self.id} type={self.task_type} status={self.status} progress={self.progress_percentage}%>"
