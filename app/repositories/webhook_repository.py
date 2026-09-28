from datetime import datetime, timezone
from typing import List, Optional, Tuple
import uuid
from sqlalchemy import and_, func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.webhook import Webhook
from app.repositories.base_repository import BaseRepository


class WebhookRepository(BaseRepository[Webhook]):
    """Repository handling CRUD, query, and status state updates for Webhooks."""

    def __init__(self):
        super().__init__(Webhook)

    async def create_webhook(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        url: str,
        secret: str,
        event_type: str = "*",
    ) -> Webhook:
        """Register and persist a new user Webhook endpoint."""
        return await self.create(
            db,
            user_id=user_id,
            url=url,
            secret=secret,
            event_type=event_type,
            is_active=True,
            failure_count=0,
            last_success_at=None,
        )

    async def get_webhook_by_id(
        self,
        db: AsyncSession,
        webhook_id: uuid.UUID,
        user_id: Optional[uuid.UUID] = None,
        is_admin: bool = False,
    ) -> Optional[Webhook]:
        """Fetch single webhook checking user ownership unless admin."""
        filters = [Webhook.id == webhook_id]
        if not is_admin and user_id:
            filters.append(Webhook.user_id == user_id)

        stmt = select(Webhook).where(and_(*filters))
        result = await db.execute(stmt)
        return result.scalars().first()

    async def list_by_user(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[Webhook], int]:
        """Fetch webhooks created by a user."""
        count_stmt = select(func.count(Webhook.id)).where(Webhook.user_id == user_id)
        total = (await db.execute(count_stmt)).scalar() or 0

        stmt = (
            select(Webhook)
            .where(Webhook.user_id == user_id)
            .order_by(Webhook.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        result = await db.execute(stmt)
        return list(result.scalars().all()), total

    async def get_active_webhooks_for_event(
        self,
        db: AsyncSession,
        event_type: str,
    ) -> List[Webhook]:
        """Fetch all active webhooks subscribed to a specific event or wildcard '*'."""
        stmt = select(Webhook).where(
            and_(
                Webhook.is_active == True,
                or_(Webhook.event_type == event_type, Webhook.event_type == "*"),
            )
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def update_webhook(
        self,
        db: AsyncSession,
        webhook_id: uuid.UUID,
        user_id: Optional[uuid.UUID] = None,
        is_admin: bool = False,
        url: Optional[str] = None,
        event_type: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> Optional[Webhook]:
        """Update webhook endpoint URL, subscribed event type, or active state."""
        webhook = await self.get_webhook_by_id(db, webhook_id, user_id=user_id, is_admin=is_admin)
        if not webhook:
            return None

        if url is not None:
            webhook.url = url
        if event_type is not None:
            webhook.event_type = event_type
        if is_active is not None:
            webhook.is_active = is_active

        await db.commit()
        await db.refresh(webhook)
        return webhook

    async def delete_webhook(
        self,
        db: AsyncSession,
        webhook_id: uuid.UUID,
        user_id: Optional[uuid.UUID] = None,
        is_admin: bool = False,
    ) -> bool:
        """Permanently delete a webhook configuration."""
        webhook = await self.get_webhook_by_id(db, webhook_id, user_id=user_id, is_admin=is_admin)
        if not webhook:
            return False

        await db.delete(webhook)
        await db.commit()
        return True

    async def record_delivery_success(self, db: AsyncSession, webhook_id: uuid.UUID) -> None:
        """Record successful delivery and reset failure counter."""
        stmt = (
            update(Webhook)
            .where(Webhook.id == webhook_id)
            .values(last_success_at=datetime.now(timezone.utc), failure_count=0)
        )
        await db.execute(stmt)
        await db.commit()

    async def record_delivery_failure(self, db: AsyncSession, webhook_id: uuid.UUID) -> None:
        """Increment failure counter and auto-disable after 10 consecutive delivery failures."""
        webhook = await self.get_by_id(db, webhook_id)
        if webhook:
            webhook.failure_count += 1
            if webhook.failure_count >= 10:
                webhook.is_active = False
            await db.commit()


webhook_repository = WebhookRepository()
