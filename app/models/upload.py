import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional
from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.review import Review
    from app.models.user import User


class Upload(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Upload entity representing metadata for uploaded files and archive packages."""

    __tablename__ = "uploads"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    original_filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    stored_filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    file_size: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    file_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True,
    )
    mime_type: Mapped[str] = mapped_column(
        String(100),
        default="text/x-python",
        nullable=False,
    )
    language: Mapped[str] = mapped_column(
        String(50),
        default="python",
        nullable=False,
    )
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    review_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("reviews.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        lazy="joined",
    )
    review: Mapped[Optional["Review"]] = relationship(
        "Review",
        lazy="joined",
    )

    def __repr__(self) -> str:
        return f"<Upload id={self.id} filename='{self.original_filename}' hash='{self.file_hash[:8]}...'>"
