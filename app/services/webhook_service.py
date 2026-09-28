import asyncio
import secrets
from typing import Any, Dict, List, Optional
import uuid
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.logging import logger
from app.core.webhook import dispatch_webhook_request
from app.db.session import AsyncSessionLocal
from app.models.user import User
from app.models.webhook import Webhook
from app.repositories.webhook_repository import webhook_repository
from app.schemas.webhook import (
    WebhookCreate,
    WebhookListResponse,
    WebhookResponse,
    WebhookTestResponse,
    WebhookUpdate,
)


class WebhookService:
    """Service managing webhook registrations, test dispatches, and asynchronous fan-out broadcasts."""

    async def register_webhook(
        self,
        db: AsyncSession,
        user: User,
        data: WebhookCreate,
    ) -> WebhookResponse:
        """Register a new webhook subscription endpoint."""
        secret = data.secret or secrets.token_hex(24)
        webhook = await webhook_repository.create_webhook(
            db=db,
            user_id=user.id,
            url=data.url,
            secret=secret,
            event_type=data.event_type,
        )
        logger.info(" Registered new webhook %s for user %s [Event: %s]", webhook.id, user.username, data.event_type)
        return WebhookResponse.model_validate(webhook)

    async def list_user_webhooks(
        self,
        db: AsyncSession,
        user: User,
        page: int = 1,
        page_size: int = 20,
    ) -> WebhookListResponse:
        """List webhooks owned by the user."""
        items, total = await webhook_repository.list_by_user(db=db, user_id=user.id, page=page, page_size=page_size)
        return WebhookListResponse(
            total=total,
            webhooks=[WebhookResponse.model_validate(wh) for wh in items],
        )

    async def update_webhook(
        self,
        db: AsyncSession,
        webhook_id: uuid.UUID,
        user: User,
        data: WebhookUpdate,
    ) -> WebhookResponse:
        """Update webhook endpoint URL or subscription settings."""
        webhook = await webhook_repository.update_webhook(
            db=db,
            webhook_id=webhook_id,
            user_id=user.id,
            is_admin=user.is_admin,
            url=data.url,
            event_type=data.event_type,
            is_active=data.is_active,
        )
        if not webhook:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Webhook '{webhook_id}' not found.",
            )
        return WebhookResponse.model_validate(webhook)

    async def delete_webhook(
        self,
        db: AsyncSession,
        webhook_id: uuid.UUID,
        user: User,
    ) -> bool:
        """Delete a registered webhook."""
        deleted = await webhook_repository.delete_webhook(
            db=db,
            webhook_id=webhook_id,
            user_id=user.id,
            is_admin=user.is_admin,
        )
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Webhook '{webhook_id}' not found.",
            )
        return True

    async def test_webhook(
        self,
        db: AsyncSession,
        webhook_id: uuid.UUID,
        user: User,
    ) -> WebhookTestResponse:
        """Send a test ping payload to a webhook destination."""
        webhook = await webhook_repository.get_webhook_by_id(
            db=db,
            webhook_id=webhook_id,
            user_id=user.id,
            is_admin=user.is_admin,
        )
        if not webhook:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Webhook '{webhook_id}' not found.",
            )

        test_payload = {
            "ping": "pong",
            "message": "CodePilot AI webhook connectivity test",
            "subscription_id": str(webhook.id),
        }

        success, status_code, body = await dispatch_webhook_request(
            url=webhook.url,
            secret=webhook.secret,
            event_type="test.ping",
            payload_data=test_payload,
            max_retries=1,
            timeout_seconds=5.0,
        )

        if success:
            await webhook_repository.record_delivery_success(db, webhook.id)
            return WebhookTestResponse(
                success=True,
                status_code=status_code,
                message="Test webhook delivered successfully.",
                response_body=body,
            )
        else:
            await webhook_repository.record_delivery_failure(db, webhook.id)
            return WebhookTestResponse(
                success=False,
                status_code=status_code,
                message="Test webhook delivery failed.",
                error=body or "Destination server did not return 2xx status code.",
            )

    async def broadcast_event_background(
        self,
        event_type: str,
        payload_data: Dict[str, Any],
    ) -> None:
        """Fan-out event broadcast to all subscribed active webhooks in background."""
        if not settings.ENABLE_WEBHOOKS:
            return

        try:
            async with AsyncSessionLocal() as db:
                subscribers = await webhook_repository.get_active_webhooks_for_event(db, event_type)
                if not subscribers:
                    return

                logger.info("📡 Broadcasting webhook event '%s' to %d subscribers", event_type, len(subscribers))
                tasks = [
                    dispatch_webhook_request(
                        url=wh.url,
                        secret=wh.secret,
                        event_type=event_type,
                        payload_data=payload_data,
                    )
                    for wh in subscribers
                ]
                results = await asyncio.gather(*tasks, return_exceptions=True)
                for wh, res in zip(subscribers, results):
                    if isinstance(res, tuple) and res[0] is True:
                        await webhook_repository.record_delivery_success(db, wh.id)
                    else:
                        await webhook_repository.record_delivery_failure(db, wh.id)
        except Exception as exc:
            logger.warning("Error during background webhook broadcast: %s", str(exc))


webhook_service = WebhookService()
