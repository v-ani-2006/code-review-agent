from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import (
    admin,
    ai_review,
    analytics,
    audit,
    auth,
    batch,
    dashboard,
    exports,
    generators,
    health,
    history,
    metrics,
    monitoring,
    reports,
    review,
    tasks,
    uploads,
    users,
    version,
    webhooks,
)
from app.core.cache import redis_manager
from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.limiter import RateLimitExceeded, custom_rate_limit_exceeded_handler, limiter
from app.core.logging import logger
from app.core.middleware import register_middleware
from app.db.init_db import init_db
from app.db.session import engine

# OpenAPI Tags Metadata for grouping and documenting endpoints in Swagger UI
tags_metadata = [
    {
        "name": "Admin",
        "description": "Administrator control panel: system telemetry, cache flushing, background task overview, and cryptographic API key provisioning.",
    },
    {
        "name": "Monitoring",
        "description": "Real-time infrastructure health probes, multi-service connectivity status (PostgreSQL, Redis, Gemini, storage), and uptime telemetry.",
    },
    {
        "name": "Metrics",
        "description": "Prometheus-compatible scraping endpoint and JSON telemetry for application traffic, error rates, AI requests, uploads, and cache hit ratios.",
    },
    {
        "name": "Audit",
        "description": "Immutable security and operational event trail: authentication events, review mutations, API key usage, and JSON/CSV audit log exports.",
    },
    {
        "name": "Webhooks",
        "description": "Outbound webhook subscription management, HMAC-SHA256 signature verification, and live test delivery dispatches.",
    },
    {
        "name": "Uploads",
        "description": "Single and multiple source file uploads, ZIP project packages, file deduplication, previews, and storage management.",
    },
    {
        "name": "Batch Review",
        "description": "Concurrent multi-file code reviews, project-wide scans, repository aggregation, and architectural metrics.",
    },
    {
        "name": "Tasks",
        "description": "Asynchronous background task status tracking, progress monitoring, and job cancellation.",
    },
    {
        "name": "Reports",
        "description": "Multi-format project review report generation, inspection, and downloadable deliverables (JSON, Markdown, HTML, ZIP).",
    },
    {
        "name": "History",
        "description": "Historical code review lifecycle management, multi-criteria search, favorites, soft delete/restore/trash, timeline aggregation, and review comparisons.",
    },
    {
        "name": "Dashboard",
        "description": "Developer dashboard metrics, time-series review activity, coding streak gamification, historical score progression, and actionable diagnostic insights.",
    },
    {
        "name": "Analytics",
        "description": "Advanced code quality metrics, security posture evaluation, cyclomatic complexity distributions, PEP 8 compliance, GitHub-style contribution heatmaps, and JSON/CSV/Markdown data exports.",
    },
    {
        "name": "AI Generation",
        "description": "Automated generation of technical documentation, standardized docstrings, pytest test suites, GitHub READMEs, code refactoring, architecture specs, changelogs, and executive summaries.",
    },
    {
        "name": "Export",
        "description": "Multi-format report export engine producing JSON, Markdown, styled responsive HTML, and plain text artifacts.",
    },
    {
        "name": "AI Review",
        "description": "Google Gemini AI reasoning layer for deep semantic reviews, code explanations, performance optimizations, automated bug fixes, docstrings, and pytest test suite generation.",
    },
    {
        "name": "Code Review & AST Analysis",
        "description": "Static code analysis engine powered by Python AST, Radon complexity, Bandit security checks, and PEP 8 style heuristics.",
    },
    {
        "name": "Authentication & Authorization",
        "description": "User registration, OAuth2 password flow login, JWT token issuance, refresh, and password management.",
    },
    {
        "name": "User Management",
        "description": "Authenticated user profile inspection, profile updates, account deactivation, and admin user queries.",
    },
    {
        "name": "Health & Status",
        "description": "Liveness probes, heartbeat, and general service status check endpoints.",
    },
    {
        "name": "System Info",
        "description": "Environment diagnostics, active configuration, and semantic versioning.",
    },
]


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manage application startup and shutdown lifecycle events."""
    # --- STARTUP LOGIC ---
    logger.info(
        "🚀 Application Started: %s (v%s) | Debug Mode: %s",
        settings.APP_NAME,
        settings.APP_VERSION,
        settings.DEBUG,
    )
    logger.info("📚 Interactive Docs: http://127.0.0.1:8000/docs")
    logger.info("📖 ReDoc Docs:       http://127.0.0.1:8000/redoc")

    # 1. Initialize and verify database connectivity
    await init_db()

    # 2. Initialize Redis connection pool (with graceful in-memory fallback)
    await redis_manager.init_redis()

    yield  # The application serves incoming requests while paused here

    # --- SHUTDOWN LOGIC ---
    logger.info("🛑 Application Shutdown: Closing Redis cache connection...")
    await redis_manager.close_redis()

    logger.info("🛑 Application Shutdown: Closing database connection pool...")
    await engine.dispose()
    logger.info("🛑 Application Shutdown: %s terminated gracefully.", settings.APP_NAME)


# Initialize FastAPI with production metadata, OpenAPI tags, and documentation paths
app = FastAPI(
    title=settings.APP_NAME,
    description="""
## AI Code Review Agent API 🤖

An enterprise-grade, memory-powered backend service designed to analyze source code diffs,
detect security vulnerabilities, enforce stylistic conventions, and provide automated review feedback.

### Key Capabilities:
* **Static Code Analysis**: Python AST parsing, Radon cyclomatic complexity & maintainability, Bandit-style security checks, PEP 8 heuristics.
* **Authentication & Authorization**: OAuth2 Password Flow, JWT access & refresh tokens, bcrypt hashing, and API Key authentication.
* **Role-Based Access Control**: Active account verification and administrator permissions.
* **Production Caching & Rate Limiting**: Redis asynchronous caching with graceful fallback and SlowAPI rate protection.
* **Telemetry & Webhooks**: Prometheus metric collection, HMAC-SHA256 signed event delivery, and deep health diagnostics.
* **Database Layer**: PostgreSQL + SQLAlchemy 2.x async ORM with Alembic migrations.
* **Production DevOps & CI/CD**: GitHub Actions workflows, Ruff & Black linting, MyPy static typing, Bandit security, and automated releases.
    """,
    version=settings.APP_VERSION,
    docs_url="/docs" if settings.ENABLE_DOCS else None,
    redoc_url="/redoc" if settings.ENABLE_DOCS else None,
    openapi_url="/openapi.json" if settings.ENABLE_DOCS else None,
    openapi_tags=tags_metadata,
    lifespan=lifespan,
)

# Attach SlowAPI limiter state and 429 exception handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, custom_rate_limit_exceeded_handler)

# 1. Register CORS Middleware (enables local frontend frameworks like React/Vite and production web clients)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Register Custom Diagnostics & Security Middleware (Tracing + Headers + Timing)
register_middleware(app)

# 3. Register Global Exception Handlers (404, 422, 409 Integrity, 500 formatted JSON)
register_exception_handlers(app)

# 4. Include API Routers with centralized configuration prefix
app.include_router(admin.router, prefix=settings.API_PREFIX)
app.include_router(monitoring.router, prefix=settings.API_PREFIX)
app.include_router(metrics.router, prefix=settings.API_PREFIX)
app.include_router(audit.router, prefix=settings.API_PREFIX)
app.include_router(webhooks.router, prefix=settings.API_PREFIX)
app.include_router(uploads.router, prefix=settings.API_PREFIX)
app.include_router(batch.router, prefix=settings.API_PREFIX)
app.include_router(tasks.router, prefix=settings.API_PREFIX)
app.include_router(reports.router, prefix=settings.API_PREFIX)
app.include_router(history.router, prefix=settings.API_PREFIX)
app.include_router(dashboard.router, prefix=settings.API_PREFIX)
app.include_router(analytics.router, prefix=settings.API_PREFIX)
app.include_router(generators.router, prefix=settings.API_PREFIX)
app.include_router(exports.router, prefix=settings.API_PREFIX)
app.include_router(ai_review.router, prefix=settings.API_PREFIX)
app.include_router(review.router, prefix=settings.API_PREFIX)
app.include_router(auth.router, prefix=settings.API_PREFIX)
app.include_router(users.router, prefix=settings.API_PREFIX)
app.include_router(health.router, prefix=settings.API_PREFIX)
app.include_router(version.router, prefix=settings.API_PREFIX)
