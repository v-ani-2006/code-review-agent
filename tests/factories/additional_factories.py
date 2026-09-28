"""Factories for Webhook, APIKey, and AuditLog models."""
import hashlib
import uuid
from faker import Faker
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.api_key import APIKey
from app.models.audit_log import AuditLog
from app.models.webhook import Webhook

fake = Faker()


class WebhookFactory:
    """Factory generating Webhook entity instances."""

    @classmethod
    def build(
        cls,
        id: uuid.UUID = None,
        user_id: uuid.UUID = None,
        url: str = None,
        secret: str = "whsec_test_secret_key_12345",
        event_type: str = "*",
        is_active: bool = True,
    ) -> Webhook:
        return Webhook(
            id=id or uuid.uuid4(),
            user_id=user_id or uuid.uuid4(),
            url=url or f"https://example.com/webhook/{uuid.uuid4().hex[:8]}",
            secret=secret,
            event_type=event_type,
            is_active=is_active,
            failure_count=0,
        )

    @classmethod
    async def create(cls, db: AsyncSession, **kwargs) -> Webhook:
        webhook = cls.build(**kwargs)
        db.add(webhook)
        await db.flush()
        await db.refresh(webhook)
        return webhook


class APIKeyFactory:
    """Factory generating APIKey entity instances."""

    @classmethod
    def build(
        cls,
        id: uuid.UUID = None,
        user_id: uuid.UUID = None,
        name: str = "Test API Key",
        raw_key: str = "cp_test_api_key_1234567890abcdef",
        is_active: bool = True,
        permissions: list = None,
    ) -> APIKey:
        prefix = raw_key[:10]
        hashed = hashlib.sha256(raw_key.encode("utf-8")).hexdigest()
        return APIKey(
            id=id or uuid.uuid4(),
            user_id=user_id or uuid.uuid4(),
            name=name,
            hashed_key=hashed,
            prefix=prefix,
            is_active=is_active,
            permissions=permissions if permissions is not None else ["*"],
        )

    @classmethod
    async def create(cls, db: AsyncSession, **kwargs) -> APIKey:
        key = cls.build(**kwargs)
        db.add(key)
        await db.flush()
        await db.refresh(key)
        return key


class AuditLogFactory:
    """Factory generating AuditLog entity instances."""

    @classmethod
    def build(
        cls,
        id: uuid.UUID = None,
        user_id: uuid.UUID = None,
        action: str = "review.created",
        resource: str = "review",
        resource_id: str = None,
        status: str = "success",
    ) -> AuditLog:
        return AuditLog(
            id=id or uuid.uuid4(),
            user_id=user_id,
            action=action,
            resource=resource,
            resource_id=resource_id or str(uuid.uuid4()),
            ip_address="127.0.0.1",
            user_agent="Pytest-TestClient/1.0",
            status=status,
            metadata_json={"source": "test_suite"},
        )

    @classmethod
    async def create(cls, db: AsyncSession, **kwargs) -> AuditLog:
        log = cls.build(**kwargs)
        db.add(log)
        await db.flush()
        await db.refresh(log)
        return log
