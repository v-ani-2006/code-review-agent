"""Repositories package implementing the database access pattern."""

from app.repositories.base_repository import BaseRepository
from app.repositories.user_repository import UserRepository, user_repository
from app.repositories.review_repository import ReviewRepository, review_repository
from app.repositories.history_repository import HistoryRepository, history_repository
from app.repositories.analytics_repository import AnalyticsRepository, analytics_repository
from app.repositories.upload_repository import UploadRepository, upload_repository
from app.repositories.task_repository import TaskRepository, task_repository
from app.repositories.api_key_repository import APIKeyRepository, api_key_repository
from app.repositories.audit_repository import AuditRepository, audit_repository
from app.repositories.webhook_repository import WebhookRepository, webhook_repository

__all__ = [
    "BaseRepository",
    "UserRepository",
    "user_repository",
    "ReviewRepository",
    "review_repository",
    "HistoryRepository",
    "history_repository",
    "AnalyticsRepository",
    "analytics_repository",
    "UploadRepository",
    "upload_repository",
    "TaskRepository",
    "task_repository",
    "APIKeyRepository",
    "api_key_repository",
    "AuditRepository",
    "audit_repository",
    "WebhookRepository",
    "webhook_repository",
]
