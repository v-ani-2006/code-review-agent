from typing import Annotated
import uuid
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_active_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.webhook import (
    WebhookCreate,
    WebhookListResponse,
    WebhookResponse,
    WebhookTestResponse,
    WebhookUpdate,
)
from app.services.webhook_service import webhook_service

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])


@router.post(
    "",
    response_model=WebhookResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register Webhook Endpoint",
    description="Subscribe an HTTP URL to receive cryptographically signed event notifications.",
)
async def create_webhook(
    data: WebhookCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> WebhookResponse:
    """Create a new webhook subscription."""
    return await webhook_service.register_webhook(db=db, user=current_user, data=data)


@router.get(
    "",
    response_model=WebhookListResponse,
    status_code=status.HTTP_200_OK,
    summary="List Registered Webhooks",
    description="Retrieve all webhook subscriptions configured by the authenticated user.",
)
async def list_webhooks(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
) -> WebhookListResponse:
    """List user webhooks."""
    return await webhook_service.list_user_webhooks(
        db=db,
        user=current_user,
        page=page,
        page_size=page_size,
    )


@router.patch(
    "/{webhook_id}",
    response_model=WebhookResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Webhook Endpoint",
    description="Update the target URL, event subscription, or toggle active status of a webhook.",
)
async def update_webhook(
    webhook_id: uuid.UUID,
    data: WebhookUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> WebhookResponse:
    """Update a webhook."""
    return await webhook_service.update_webhook(
        db=db,
        webhook_id=webhook_id,
        user=current_user,
        data=data,
    )


@router.delete(
    "/{webhook_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete Webhook",
    description="Permanently remove a webhook subscription.",
)
async def delete_webhook(
    webhook_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> dict:
    """Delete a webhook."""
    await webhook_service.delete_webhook(db=db, webhook_id=webhook_id, user=current_user)
    return {"success": True, "message": f"Webhook '{webhook_id}' deleted successfully."}


@router.post(
    "/test/{webhook_id}",
    response_model=WebhookTestResponse,
    status_code=status.HTTP_200_OK,
    summary="Test Webhook Delivery",
    description="Send a real HMAC-signed test ping payload to verify destination reachability and signature computation.",
)
async def test_webhook(
    webhook_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> WebhookTestResponse:
    """Test webhook delivery."""
    return await webhook_service.test_webhook(db=db, webhook_id=webhook_id, user=current_user)
