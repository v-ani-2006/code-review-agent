import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import Boolean, DateTime, ForeignKey, Index, JSON, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.user import User


class APIKey(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """APIKey entity representing provisioned client API keys with fine-grained access scopes."""

    __tablename__ = "api_keys"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    hashed_key: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        index=True,
    )
    prefix: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        index=True,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
    )
    last_used_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    permissions: Mapped[List[str]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        lazy="joined",
    )

    def __repr__(self) -> str:
        return f"<APIKey id={self.id} prefix='{self.prefix}' name='{self.name}' active={self.is_active}>"
