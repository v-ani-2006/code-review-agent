"""Services package encapsulating core business logic."""

from app.services.ai_review_service import AIReviewService, ai_review_service
from app.services.auth_service import AuthService, auth_service
from app.services.export_service import ExportService, app_export_service
from app.services.generator_service import GeneratorService, generator_service
from app.services.review_service import ReviewService, review_service
from app.services.user_service import UserService, user_service
from app.services.history_service import HistoryService, history_service
from app.services.dashboard_service import DashboardService, dashboard_service
from app.services.analytics_service import AnalyticsService, analytics_service
from app.services.upload_service import UploadService, upload_service
from app.services.batch_service import BatchService, batch_service
from app.services.project_scan_service import ProjectScanService, project_scan_service
from app.services.task_service import TaskService, task_service
from app.services.report_service import ReportService, report_service
from app.services.cache_service import CacheService, cache_service
from app.services.monitoring_service import MonitoringService, monitoring_service
from app.services.audit_service import AuditService, audit_service
from app.services.webhook_service import WebhookService, webhook_service
from app.services.api_key_service import APIKeyService, api_key_service

__all__ = [
    "AuthService",
    "auth_service",
    "UserService",
    "user_service",
    "ReviewService",
    "review_service",
    "AIReviewService",
    "ai_review_service",
    "GeneratorService",
    "generator_service",
    "ExportService",
    "app_export_service",
    "HistoryService",
    "history_service",
    "DashboardService",
    "dashboard_service",
    "AnalyticsService",
    "analytics_service",
    "UploadService",
    "upload_service",
    "BatchService",
    "batch_service",
    "ProjectScanService",
    "project_scan_service",
    "TaskService",
    "task_service",
    "ReportService",
    "report_service",
    "CacheService",
    "cache_service",
    "MonitoringService",
    "monitoring_service",
    "AuditService",
    "audit_service",
    "WebhookService",
    "webhook_service",
    "APIKeyService",
    "api_key_service",
]
