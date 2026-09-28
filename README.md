# code-review-agent

A production-ready FastAPI backend service for an AI-powered code review agent.

<!-- Description Placeholder: Add detailed overview, architecture, and goals here -->
> **Project Overview**: *An enterprise-grade, memory-powered backend service designed to analyze source code diffs, detect security vulnerabilities, enforce stylistic conventions, and provide automated review feedback.*

---

## Architecture Overview

```text
app/
├── __init__.py
├── main.py             # Application factory, lifespan, CORS, middleware, and router assembly
├── ai/                 # Static analysis, Gemini reasoning, and generation engine
│   ├── __init__.py     # Exports analyze_code, ai_service, and providers
│   ├── analyzer.py     # Main engine entry point, AST parser, and syntax error recovery
│   ├── complexity.py   # Radon cyclomatic complexity, Maintainability Index, Halstead metrics
│   ├── security.py     # Bandit-style AST checks and secret/token regex pattern scanner
│   ├── style.py        # PEP 8 heuristics, bug detection (mutable defaults, bare except, None checks)
│   ├── readability.py  # Identifier naming compliance, function/line lengths, docstring coverage
│   ├── scoring.py      # Weighted quality scoring rubric (0-100)
│   ├── report.py       # Structural AST visitor, metrics calculation, and report compilation
│   ├── constants.py    # Severities, Categories, thresholds, and master rule catalog
│   ├── models.py       # AI context and provider response data structures
│   ├── parser.py       # Markdown, bullet list, code block, and JSON fragment parser
│   ├── formatter.py    # Plain JSON, markdown, and HTML-safe code formatters
│   ├── markdown_formatter.py # Markdown standardization and Jinja2 rendering
│   ├── html_formatter.py     # Styled, responsive HTML report converter
│   ├── export_service.py     # Core multi-format export engine (JSON, MD, HTML, TXT)
│   ├── ai_service.py   # Multi-modal AI orchestrator integrating static analysis and Gemini
│   ├── generators/     # Independent AI generators
│   │   ├── __init__.py
│   │   ├── documentation_generator.py # Technical & API documentation generator
│   │   ├── docstring_generator.py     # Google, NumPy, Sphinx docstring generator
│   │   ├── unittest_generator.py      # Pytest test suite generator with fixtures & edge cases
│   │   ├── readme_generator.py        # GitHub README.md generator
│   │   ├── refactor_generator.py      # Automated code refactoring & modularization
│   │   ├── architecture_generator.py  # System architecture & specification generator
│   │   ├── changelog_generator.py     # Keep a Changelog diff generator
│   │   └── summary_generator.py       # Executive review summary generator
│   ├── templates/      # Jinja2 markdown templates
│   │   ├── readme_template.md
│   │   ├── documentation_template.md
│   │   ├── report_template.md
│   │   ├── changelog_template.md
│   │   └── architecture_template.md
│   ├── prompts/        # Prompt engineering layer
│   │   ├── __init__.py
│   │   ├── review_prompt.py         # Semantic review, strengths, critical issues, roadmap
│   │   ├── explain_prompt.py        # Beginner explanations, line-by-line summaries, execution flows
│   │   ├── optimize_prompt.py       # Algorithmic and memory optimization prompts
│   │   ├── bugfix_prompt.py         # Bug diagnosis and automated fix generation
│   │   ├── documentation_prompt.py  # Google/Sphinx style docstring and example generator
│   │   └── unittest_prompt.py       # Exhaustive pytest suites, fixtures, and edge cases
│   └── providers/      # Pluggable AI provider abstraction layer
│       ├── __init__.py
│       ├── base.py                  # BaseAIProvider abstract interface
│       ├── gemini_provider.py       # Google Gemini SDK & async HTTP provider with retry logic
│       └── provider_factory.py      # Extensible provider factory and registry
├── api/                # Modular API route controllers
│   ├── __init__.py
│   ├── admin.py        # GET /admin/system, /cache, /redis, /metrics, /tasks, /uploads, /reviews, POST/GET/PATCH/DELETE /admin/api-keys
│   ├── monitoring.py   # GET /monitoring/status, /services, /cache, /database, /webhooks, /uptime
│   ├── metrics.py      # GET /metrics (Prometheus text), /metrics/application, /cache, /ai, /uploads
│   ├── audit.py        # GET /audit, /audit/actions, /audit/export, /audit/{id}, /audit/user/{user_id}
│   ├── webhooks.py     # POST /webhooks, GET /webhooks, PATCH /webhooks/{id}, DELETE /webhooks/{id}, POST /webhooks/test/{id}
│   ├── uploads.py      # POST /upload/file, /code-file, /files, /project, GET /search, /{id}, /{id}/preview, DELETE /{id}
│   ├── batch.py        # POST /batch/review, /project, GET /{id}, /{id}/results, /history, DELETE /{id}
│   ├── tasks.py        # GET /tasks, /active, /completed, /failed, /{id}, DELETE /{id}
│   ├── reports.py      # GET /reports, /{id}, /{id}/download, DELETE /{id}
│   ├── history.py      # History, search, favorites, soft delete/restore, timeline, review comparison
│   ├── dashboard.py    # Executive overview, activity, coding streak, score progression, insights
│   ├── analytics.py    # Scores, issues, security posture, complexity, trends, heatmaps, export
│   ├── generators.py   # POST /generate/documentation, /docstrings, /tests, /readme, /refactor, /architecture, /changelog, /summary
│   ├── exports.py      # POST /export/json, /markdown, /html, /text
│   ├── ai_review.py    # POST /ai/review, /explain, /optimize, /fix, /documentation, /tests, GET /models, /status
│   ├── review.py       # POST /review/code, POST /review/text, GET /review/languages, GET /review/rules
│   ├── auth.py         # Registration, OAuth2 password login, token refresh, password change
│   ├── users.py        # User profile, update, deactivation, and admin user query
│   ├── health.py       # Extended multi-service health diagnostics & root endpoints
│   └── version.py      # Version & environment diagnostic endpoint
├── core/               # Cross-cutting core infrastructure
│   ├── __init__.py
│   ├── auth.py         # JWT generation, verification, and OAuth2PasswordBearer scheme
│   ├── cache.py        # Redis client manager with automatic in-memory fallback
│   ├── limiter.py      # SlowAPI token rate limiting with custom 429 Retry-After handler
│   ├── monitoring.py   # Multi-service health checker (PostgreSQL, Redis, Gemini, storage) & hardware stats
│   ├── audit.py        # Immutable audit logging helper and background task writer
│   ├── metrics.py      # Prometheus telemetry collector (counters, histograms, export generator)
│   ├── webhook.py      # Outbound signed webhook dispatcher with HMAC-SHA256 and exponential retries
│   ├── config.py       # Pydantic Settings (PostgreSQL, Redis, JWT, Gemini, Webhook, Metrics)
│   ├── database.py     # Database engine and session re-exports
│   ├── dependencies.py # Dual JWT + API Key auth dependencies (get_current_user, require_permission, get_admin_user)
│   ├── logging.py      # Structured console logging
│   ├── middleware.py   # UUID request tracing (X-Request-ID), security headers, timing (X-Process-Time)
│   ├── security.py     # bcrypt password hashing & verification utilities
│   └── exceptions.py   # Standardized JSON error handlers (404, 422, 409 Integrity, 500)
├── db/                 # Database engine & session management
│   ├── __init__.py
│   ├── session.py      # Async SQLAlchemy engine, AsyncSessionLocal, async_session_maker, and get_db dependency
│   └── init_db.py      # Database connectivity verification & development table synchronization
├── models/             # SQLAlchemy 2.x ORM models
│   ├── __init__.py
│   ├── base.py         # DeclarativeBase, TimestampMixin, and UUIDPrimaryKeyMixin
│   ├── user.py         # User model with UUID, unique indexes, and review relationship
│   ├── review.py       # Review model with static, AI, generator, export, history, tags, and lifecycle fields
│   ├── task.py         # Task model tracking asynchronous batch & upload jobs
│   ├── upload.py       # Upload model tracking uploaded source files, hashes, and deduplication
│   ├── api_key.py      # APIKey model with hashed secret, prefix, permissions, and expiration
│   ├── audit_log.py    # AuditLog model recording immutable security and operational events
│   └── webhook.py      # Webhook model managing subscriber endpoints, event types, and failure states
├── repositories/       # Generic and domain-specific repository data access layer
│   ├── __init__.py
│   ├── base_repository.py      # Generic async CRUD operations
│   ├── user_repository.py      # User-specific database operations & lookup
│   ├── review_repository.py    # Core review persistence and artifact updates
│   ├── history_repository.py   # History, pagination, multi-criteria search, timeline, and comparison queries
│   ├── analytics_repository.py # Aggregations, metrics, activity distributions, streaks, and heatmap datasets
│   ├── upload_repository.py    # File upload persistence, SHA-256 deduplication lookup, and search
│   ├── task_repository.py      # Background task state machine, progress tracking, and status queries
│   ├── api_key_repository.py   # APIKey storage, verification, and revocation queries
│   ├── audit_repository.py     # Immutable audit log search, filtering, and export queries
│   └── webhook_repository.py   # Webhook subscriber lookup, event fan-out, and failure tracking
├── schemas/            # Pydantic data models for requests & responses
│   ├── __init__.py
│   ├── monitoring.py   # HealthSummaryResponse, ServiceHealth, SystemInfo, UptimeResponse, CacheStatusResponse
│   ├── webhook.py      # WebhookCreate, WebhookUpdate, WebhookResponse, WebhookListResponse, WebhookTestResponse
│   ├── metrics.py      # ApplicationMetricsResponse, CacheMetricsResponse, AIMetricsResponse, UploadMetricsResponse
│   ├── api_key.py      # APIKeyCreate, APIKeyCreateResponse, APIKeyResponse, APIKeyListResponse, APIKeyUpdate
│   ├── audit.py        # AuditLogResponse, AuditLogListResponse, AuditActionsResponse
│   ├── upload.py       # UploadMetadata, UploadResponse, MultipleUploadResponse, FilePreviewResponse
│   ├── task.py         # TaskResponse, TaskListResponse
│   ├── batch.py        # ProjectMetricsResponse, ProjectSummaryResponse, BatchReviewResponse
│   ├── report.py       # ReportMetadata, ReportListResponse, ReportResponse
│   ├── history.py      # HistoryItem, HistoryDetailResponse, HistoryListResponse, ReviewCompareRequest, ComparisonResponse, TimelineResponse
│   ├── dashboard.py    # DashboardOverview, UserActivity, UserStreak, ScoreProgressResponse, DashboardInsightsResponse
│   ├── analytics.py    # HeatmapResponse, LanguageAnalyticsResponse, IssueAnalyticsResponse, SecurityAnalyticsResponse, TrendAnalyticsResponse
│   ├── generators.py   # Generator requests & responses (Documentation, Tests, Readme, etc.)
│   ├── exports.py      # ExportRequest, ExportResponse
│   ├── ai_review.py    # AIReviewRequest/Response, AIExplain, AIOptimize, AIBugFix, AIDocumentation, AITest
│   ├── review.py       # ReviewRequest, ReviewReport, CodeIssue, CodeMetrics, ComplexityMetrics
│   ├── auth.py         # Auth schemas (RegisterRequest, TokenResponse, RefreshRequest, etc.)
│   ├── common.py       # Reusable API response schemas
│   └── user.py         # User Pydantic schemas (UserCreate, UserResponse, UserProfileResponse)
├── services/           # Business logic layer
│   ├── __init__.py
│   ├── cache_service.py        # Redis caching, JSON serialization, eviction, and namespace clearing
│   ├── monitoring_service.py   # Infrastructure diagnostics, hardware telemetry, service health checks
│   ├── audit_service.py        # Audit trail querying, filtering, and CSV/JSON export
│   ├── webhook_service.py      # Webhook CRUD, HMAC signed test dispatch, fan-out event broadcasts
│   ├── api_key_service.py      # Cryptographic API key generation, SHA-256 hashing, scope verification
│   ├── upload_service.py       # Single & multiple file uploads, validation, SHA-256 deduplication, review triggers
│   ├── batch_service.py        # Concurrent multi-file reviews and full ZIP project analysis pipeline
│   ├── project_scan_service.py # Recursive directory scanner, AST metrics extraction, package detection, tree generation
│   ├── task_service.py         # Background job lifecycle management, status tracking, cancellation
│   ├── report_service.py       # Multi-format report generation (JSON, MD, HTML, ZIP) and artifact downloads
│   ├── history_service.py      # History pagination, search, favorites, soft delete/restore, comparison
│   ├── dashboard_service.py    # Executive dashboard aggregation, streaks, time-series, insights
│   ├── analytics_service.py    # Quality metrics, security posture, complexity, trends, heatmaps, export
│   ├── generator_service.py    # AI generation orchestration service
│   ├── export_service.py       # Multi-format report export service
│   ├── ai_review_service.py    # End-to-end AI reasoning pipeline and database persistence
│   ├── review_service.py       # Code analysis execution, score calculation, and review persistence
│   ├── auth_service.py         # User registration, credential authentication, JWT token issuance
│   └── user_service.py         # Profile management, account deactivation, and admin querying

├── uploads/            # Filesystem storage for uploads, archives, and compiled reports
│   ├── temp/           # Temporary uploaded files and archives
│   ├── extracted/      # Temporary workspace for extracted ZIP archives
│   └── reports/        # Compiled project audit reports (JSON, Markdown, HTML, ZIP)
└── utils/              # Helper utilities and shared tools
    ├── __init__.py
    ├── file_utils.py        # Safe file save, validation, path traversal prevention, async read/write
    ├── zip_utils.py         # Safe ZIP extraction, ZipSlip/ZipBomb prevention, directory tree generation
    ├── hash_utils.py        # SHA-256 byte and file hashing for deduplication
    └── language_detector.py # Language detection from file extensions

alembic/                # Database schema migrations
├── env.py              # Async migration runner targeting Base.metadata
├── script.py.mako      # Migration file template
└── versions/           # Versioned migration revision scripts
    ├── 001_initial_schema.py
    ├── 002_add_ai_fields.py
    ├── 003_add_generator_and_export_fields.py
    ├── 004_review_history_analytics.py
    ├── 005_uploads_batch_tasks.py
    └── 006_redis_monitoring_audit_webhooks.py

tests/                  # Phase 11 automated testing infrastructure
├── conftest.py         # Global test fixtures, DB isolation, and HTTP clients
├── pytest.ini          # Asyncio mode, marker configurations, coverage flags
├── utils.py            # JWT generators, response validators, benchmarking
├── fixtures/           # Database, user, review, upload, auth, and AI fixtures
├── factories/          # Factory Boy async models (User, Review, Task, Webhook, APIKey)
├── mocks/              # Deterministic Gemini AI, Redis cache, and Webhook mocks
├── sample_files/       # Clean, vulnerable, complex, and zipped repository archives
├── unit/               # Service-layer unit test suites
├── integration/        # API route end-to-end integration tests
├── performance/        # Code analysis, batch concurrency, and cache latency benchmarks
└── security/           # Rate limiting, API key, JWT auth, and exploit rejection tests
```

---

## API Endpoints

### File Uploads (`/upload`)

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `POST` | `/upload/file` | Upload and review a single Python source code file | Yes (Bearer) |
| `POST` | `/upload/code-file` | Upload single code file (alias) | Yes (Bearer) |
| `POST` | `/upload/files` | Upload and review multiple source code files | Yes (Bearer) |
| `POST` | `/upload/project` | Upload and extract ZIP repository archive for project scanning | Yes (Bearer) |
| `GET` | `/upload/search` | Search upload records by filename, language, hash, date, review ID | Yes (Bearer) |
| `GET` | `/upload/{upload_id}` | Get upload record metadata | Yes (Bearer) |
| `GET` | `/upload/{upload_id}/preview` | Preview the first N lines of an uploaded code file | Yes (Bearer) |
| `DELETE` | `/upload/{upload_id}` | Delete upload record and remove file from storage | Yes (Bearer) |

### Batch & Project Review (`/batch`)

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `POST` | `/batch/review` | Concurrent multi-file or archive project batch review | Yes (Bearer) |
| `POST` | `/batch/project` | Analyze entire repository project package | Yes (Bearer) |
| `GET` | `/batch/history` | List all batch review jobs submitted by user | Yes (Bearer) |
| `GET` | `/batch/{task_id}` | Check status, progress percentage, and metrics of a batch job | Yes (Bearer) |
| `GET` | `/batch/{task_id}/results` | Retrieve compiled findings and report for completed batch job | Yes (Bearer) |
| `DELETE` | `/batch/{task_id}` | Cancel or delete a batch task | Yes (Bearer) |

### Task Management (`/tasks`)

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/tasks` | List all background jobs submitted by the user | Yes (Bearer) |
| `GET` | `/tasks/active` | List tasks currently in PENDING or RUNNING status | Yes (Bearer) |
| `GET` | `/tasks/completed` | List successfully completed background tasks | Yes (Bearer) |
| `GET` | `/tasks/failed` | List tasks that encountered errors | Yes (Bearer) |
| `GET` | `/tasks/{task_id}` | Retrieve execution state and progress percentage for a task | Yes (Bearer) |
| `DELETE` | `/tasks/{task_id}` | Cancel or delete a background task | Yes (Bearer) |

### Project Reports (`/reports`)

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/reports` | List all compiled project audit reports available in storage | Yes (Bearer) |
| `GET` | `/reports/{report_id}` | Fetch project audit summary and downloadable format URLs | Yes (Bearer) |
| `GET` | `/reports/{report_id}/download` | Download report in JSON, Markdown, HTML, or compressed ZIP | Yes (Bearer) |
| `DELETE` | `/reports/{report_id}` | Remove project report and deliverables from storage | Yes (Bearer) |

### Review History (`/history`)


| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/history` | Paginated review history with filtering and sorting | Yes (Bearer) |
| `GET` | `/history/recent` | Recently analyzed reviews | Yes (Bearer) |
| `GET` | `/history/favorites` | Paginated favorite reviews | Yes (Bearer) |
| `GET` | `/history/trash` | Soft-deleted reviews currently in trash | Yes (Bearer) |
| `GET` | `/history/search` | Advanced partial match search across code, summaries, tags, IDs | Yes (Bearer) |
| `GET` | `/history/by-language/{language}` | Filter reviews by programming language | Yes (Bearer) |
| `GET` | `/history/by-score` | Filter reviews by score range | Yes (Bearer) |
| `GET` | `/history/by-date` | Filter reviews by creation date interval | Yes (Bearer) |
| `POST` | `/history/compare` | Structured side-by-side metric and diff comparison (JSON body) | Yes (Bearer) |
| `GET` | `/history/compare/{review_a}/{review_b}` | Structured side-by-side comparison (path IDs) | Yes (Bearer) |
| `GET` | `/history/timeline` | Chronological review history grouped by day/week/month | Yes (Bearer) |
| `GET` | `/history/{review_id}` | Detailed review with source code & AI artifacts (increments views) | Yes (Bearer) |
| `DELETE` | `/history/{review_id}` | Soft delete review (move to trash) | Yes (Bearer) |
| `PATCH` | `/history/{review_id}/favorite` | Toggle or set favorite status | Yes (Bearer) |
| `PATCH` | `/history/{review_id}/restore` | Restore review from trash | Yes (Bearer) |
| `PATCH` | `/history/{review_id}/archive` | Archive review | Yes (Bearer) |

### User Dashboard (`/dashboard`)

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/dashboard/overview` | Executive overview (counts, averages, scores, common issues) | Yes (Bearer) |
| `GET` | `/dashboard/activity` | Activity metrics (week, month, year, daily buckets, 24h distribution) | Yes (Bearer) |
| `GET` | `/dashboard/streak` | Active streak tracking, longest streak, active days, last activity | Yes (Bearer) |
| `GET` | `/dashboard/progress` | Historical score progression trajectory | Yes (Bearer) |
| `GET` | `/dashboard/recent` | Recent reviews widget dataset | Yes (Bearer) |
| `GET` | `/dashboard/insights` | Tailored code quality and diagnostic actionable recommendations | Yes (Bearer) |
| `GET` | `/dashboard/languages` | Language distribution portfolio and metrics | Yes (Bearer) |
| `GET` | `/dashboard/scores` | Multi-dimensional score breakdown | Yes (Bearer) |

### Advanced Analytics (`/analytics`)

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/analytics/overview` | High-level analytics metrics | Yes (Bearer) |
| `GET` | `/analytics/scores` | Comprehensive quality, security, complexity, readability stats | Yes (Bearer) |
| `GET` | `/analytics/issues` | Findings grouped by category and severity tiers | Yes (Bearer) |
| `GET` | `/analytics/security` | Security posture evaluation and Bandit vulnerability breakdown | Yes (Bearer) |
| `GET` | `/analytics/complexity` | Cyclomatic complexity distributions and Radon ranks | Yes (Bearer) |
| `GET` | `/analytics/readability` | PEP 8 style compliance, line length, naming conventions | Yes (Bearer) |
| `GET` | `/analytics/languages` | Language usage distribution and performance | Yes (Bearer) |
| `GET` | `/analytics/trends` | Weekly/monthly velocity, score progression, and issue reduction | Yes (Bearer) |
| `GET` | `/analytics/heatmap` | 365-day GitHub-style contribution activity heatmap dataset | Yes (Bearer) |
| `GET` | `/analytics/export` | Export analytics dataset in JSON, CSV, or Markdown format | Yes (Bearer) |

### AI Generation (`/generate`)


| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `POST` | `/generate/documentation` | Full technical module/package Markdown documentation | Optional |
| `POST` | `/generate/docstrings` | Code annotated with Google, NumPy, or Sphinx docstrings | Optional |
| `POST` | `/generate/tests` | Production-ready pytest test suite with fixtures & edge cases | Optional |
| `POST` | `/generate/readme` | Complete GitHub README.md with badges, tech stack, and setup | Optional |
| `POST` | `/generate/refactor` | Clean, modular, Pythonic refactoring with side-by-side improvements | Optional |
| `POST` | `/generate/architecture` | Enterprise system architecture and technical specification | Optional |
| `POST` | `/generate/changelog` | Keep a Changelog categorized release notes comparing code versions | Optional |
| `POST` | `/generate/summary` | Executive briefing summary (quality, risks, strengths, roadmap) | Optional |

### Document & Report Export (`/export`)

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `POST` | `/export/json` | Export report or data into serialized JSON | No |
| `POST` | `/export/markdown` | Export report or data into clean GitHub-flavored markdown | No |
| `POST` | `/export/html` | Export report into standalone, modern responsive styled HTML | No |
| `POST` | `/export/text` | Export report into clean plain text | No |

### AI Code Review & Reasoning (`/ai`)

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `POST` | `/ai/review` | Full semantic code review enriched with Phase 5 static AST analysis | Optional (Saves if logged in) |
| `POST` | `/ai/explain` | Beginner explanation, line-by-line summary, and execution flow | No |
| `POST` | `/ai/optimize` | Performance, memory, and idiomatic Pythonic optimization | No |
| `POST` | `/ai/fix` | Automated logic bug detection, remediation, and corrected code | Optional (Saves if logged in) |
| `POST` | `/ai/documentation` | Google/Sphinx style docstrings, parameter descriptions, examples | No |
| `POST` | `/ai/tests` | Automated pytest suite generation with fixtures and edge cases | No |
| `GET` | `/ai/models` | List of supported Google Gemini models | No |
| `GET` | `/ai/status` | AI reasoning layer health, configuration, and retry diagnostics | No |

### Code Review & AST Analysis (`/review`)

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `POST` | `/review/code` | Comprehensive static code analysis with AST, Radon & security checks | Optional (Saves if logged in) |
| `POST` | `/review/text` | Quick code review on plain text snippet | Optional (Saves if logged in) |
| `GET` | `/review/languages` | Supported programming languages | No |
| `GET` | `/review/rules` | Master catalog of static analysis rules and descriptions | No |

### Authentication & Authorization (`/auth`)

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `POST` | `/auth/register` | Register new user account with bcrypt password | No |
| `POST` | `/auth/login` | OAuth2 password flow login (Swagger Authorize compatible) | No |
| `POST` | `/auth/login/json` | JSON body login endpoint | No |
| `POST` | `/auth/refresh` | Issue new access token using refresh token | No |
| `POST` | `/auth/change-password` | Update account password | Yes (Bearer) |
| `GET` | `/auth/me` | Fetch authenticated user information | Yes (Bearer) |
| `POST` | `/auth/logout` | Terminate session | Yes (Bearer) |

### User Management (`/users`)

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/users/profile` | Detailed profile with review count statistics | Yes (Bearer) |
| `PUT` | `/users/profile` | Update profile fields (e.g. full name) | Yes (Bearer) |
| `DELETE` | `/users/profile` | Soft-deactivate user account | Yes (Bearer) |
| `GET` | `/users/{user_id}` | Look up user account metadata by UUID | Yes (Bearer) |
| `GET` | `/users` | List all registered users | Yes (Admin) |

### System & Health

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/` | Welcome message & links | No |
| `GET` | `/health` | Service health & liveness probe | No |
| `GET` | `/version` | System version & runtime config | No |

### Administration (`/admin`)

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/admin/system` | Comprehensive system telemetry, hardware stats, and service health | Yes (Admin) |
| `GET` | `/admin/cache` | Inspect cache operational mode, ping latency, and connection URL | Yes (Admin) |
| `DELETE` | `/admin/cache` | Flush all stored keys from Redis or in-memory cache backend | Yes (Admin) |
| `GET` | `/admin/redis` | Inspect Redis server connection state and latency | Yes (Admin) |
| `GET` | `/admin/metrics` | Retrieve application, AI, upload, and cache performance telemetry | Yes (Admin) |
| `GET` | `/admin/tasks` | List all background jobs executed across the platform | Yes (Admin) |
| `GET` | `/admin/uploads` | List all file uploads recorded across the platform | Yes (Admin) |
| `GET` | `/admin/reviews` | List recent reviews across all platform users | Yes (Admin) |
| `POST` | `/admin/api-keys` | Provision a new API key (returns raw secret key once!) | Yes (Admin) |
| `GET` | `/admin/api-keys` | List all provisioned API keys across the platform | Yes (Admin) |
| `PATCH` | `/admin/api-keys/{id}` | Update label, active status, or permissions of an API key | Yes (Admin) |
| `DELETE` | `/admin/api-keys/{id}` | Permanently revoke an API key | Yes (Admin) |

### Infrastructure Monitoring (`/monitoring`)

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/monitoring/status` | Deep diagnostic health report across PostgreSQL, Redis, Gemini, storage | No |
| `GET` | `/monitoring/services` | Check connectivity and response latencies for all subsystems | No |
| `GET` | `/monitoring/cache` | Inspect cache backend status, mode, and latency | No |
| `GET` | `/monitoring/database` | Validate PostgreSQL connection pool and query ping latency | No |
| `GET` | `/monitoring/webhooks` | Telemetry on total, active, and failing webhooks | Yes (Admin) |
| `GET` | `/monitoring/uptime` | Human-readable and second-precision server uptime | No |

### Prometheus & Telemetry (`/metrics`)

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/metrics` | Standard Prometheus text scrape endpoint for Prometheus/Grafana | No |
| `GET` | `/metrics/application` | HTTP request counts, response code distributions, and error rates | No |
| `GET` | `/metrics/cache` | Cache lookups, hit count, miss count, and hit ratio percentage | No |
| `GET` | `/metrics/ai` | Gemini AI call volume, success rates, and failure rates | No |
| `GET` | `/metrics/uploads` | File uploads and background batch job counts | No |

### Security & Operational Audit Trail (`/audit`)

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/audit` | Paginated security and operational audit trail with dynamic filters | Yes (Admin) |
| `GET` | `/audit/actions` | List all unique action identifiers recorded across audit history | Yes (Admin) |
| `GET` | `/audit/export` | Export filtered audit logs formatted as JSON or CSV | Yes (Admin) |
| `GET` | `/audit/user/{user_id}` | Retrieve operational audit trail for a specific user | Yes (Admin) |
| `GET` | `/audit/{log_id}` | Fetch a single audit log entry by UUID | Yes (Admin) |

### Webhook Subscriptions (`/webhooks`)

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `POST` | `/webhooks` | Subscribe an HTTP URL to receive HMAC-SHA256 signed event notifications | Yes (Bearer/API-Key) |
| `GET` | `/webhooks` | List all webhook subscriptions configured by the authenticated user | Yes (Bearer/API-Key) |
| `PATCH` | `/webhooks/{id}` | Update target URL, event subscription, or toggle active status | Yes (Bearer/API-Key) |
| `DELETE` | `/webhooks/{id}` | Permanently remove a webhook subscription | Yes (Bearer/API-Key) |
| `POST` | `/webhooks/test/{id}` | Send an HMAC-signed test ping payload to verify destination reachability | Yes (Bearer/API-Key) |

---

## Database Migrations

Apply Alembic migrations to synchronize the PostgreSQL database schema:

```bash
# 1. Apply Alembic migrations (including Phase 10: 006_redis_monitoring_audit_webhooks.py)
alembic upgrade head

# If existing tables were initialized in dev mode, align migration version:
# alembic stamp head

# 2. Start development server
uvicorn app.main:app --reload
```


---

## Automated Testing & Quality Assurance (Phase 11)

CodePilot AI includes an enterprise automated testing infrastructure covering unit tests, integration tests, security audits, performance benchmarks, and mocked AI/Redis/Webhook services.

### Test Categories & Directory Structure

* **Unit Tests (`tests/unit/`)**: Isolated unit tests for AuthService, ReviewService, AIService, CacheService, UploadService, DashboardService, and SecurityService.
* **Integration Tests (`tests/integration/`)**: Complete HTTP request/response workflows for Auth, Review, AI, Uploads, History, Dashboard, Analytics, Monitoring, and Webhooks.
* **Security & Auth Tests (`tests/security/`)**: Rate limiting, API key authentication, JWT validation, RBAC permissions, and exploit injection attempts (SQL injection, XSS, Path traversal).
* **Performance Benchmarks (`tests/performance/`)**: AST analysis latency on 1,500+ LOC files, concurrent batch processing, cache response speed vs computation, and database query timings.
* **Mocks (`tests/mocks/`)**: Offline deterministic Gemini AI provider (`MockGeminiProvider`), async in-memory Redis client (`MockRedisClient`), and HMAC-SHA256 signed webhook receiver (`MockWebhookReceiver`).
* **Sample Files (`tests/sample_files/`)**: Clean, vulnerable, complex, syntax-error Python scripts, and realistic multi-package `.zip` repositories.

### Executing Tests via PowerShell

Run all tests or target specific test suites:

```powershell
# 1. Run complete test suite
pytest

# 2. Run isolated unit tests
pytest tests/unit

# 3. Run API integration tests
pytest tests/integration

# 4. Run security and authorization tests
pytest tests/security

# 5. Run performance benchmarks
pytest tests/performance

# 6. Generate terminal, HTML, and XML coverage reports
pytest --cov=app --cov-report=term-missing --cov-report=html:coverage_html --cov-report=xml:coverage.xml

# 7. Using the PowerShell automation helper script
.\scripts\run_tests.ps1 -Target all
.\scripts\run_tests.ps1 -Target unit
.\scripts\run_tests.ps1 -Target integration
.\scripts\run_tests.ps1 -Target security
.\scripts\run_tests.ps1 -Target performance
.\scripts\run_tests.ps1 -Target coverage
```

---

## Docker & Production Deployment (Phase 12)

CodePilot AI includes enterprise containerization and deployment orchestration supporting **Docker Desktop on Windows**, **Linux VPS**, and cloud environments.

### Services Stack

* **Nginx Reverse Proxy (`nginx`)**: Port 80/443, SSL-ready, Gzip compression, rate limiting, and 50MB upload limits.
* **FastAPI Backend (`backend`)**: Multi-stage build on `python:3.13-slim`, unprivileged `appuser` (UID 1001), Gunicorn + `UvicornWorker` processes.
* **PostgreSQL 16 (`postgres`)**: Relational database with persistent volume, health checks, and automatic Alembic migrations.
* **Redis 7 (`redis`)**: In-memory cache and rate limiter with LRU eviction and data persistence.

### Quick Start with Docker

```bash
# 1. Build and start development stack (with bind mounts & hot-reload)
docker compose up --build -d

# 2. View running containers & health status
docker compose ps

# 3. Tail backend application logs
docker compose logs -f backend

# 4. Run Alembic migrations inside container
docker compose exec backend alembic upgrade head

# 5. Run complete 116-test suite inside container
docker compose exec backend pytest

# 6. Stop all containers
docker compose down
```

### Production Deployment

```bash
# Start production stack (hardened, internal ports isolated, restart always)
docker compose -f docker-compose.prod.yml up -d --build

# Inspect production logs
docker compose -f docker-compose.prod.yml logs -f backend
```

### Windows PowerShell Commands

```powershell
# Using the PowerShell Docker management helper:
.\scripts\docker_manage.ps1 -Action build
.\scripts\docker_manage.ps1 -Action up
.\scripts\docker_manage.ps1 -Action logs
.\scripts\docker_manage.ps1 -Action migrate
.\scripts\docker_manage.ps1 -Action test
.\scripts\docker_manage.ps1 -Action health
.\scripts\docker_manage.ps1 -Action down

# Database Backup & Restore:
.\scripts\backup_db.ps1 -RetentionDays 7
.\scripts\restore_db.ps1
```

For full production guides, VPS setup, backups, restores, and Nginx configurations, see **[docs/deployment.md](docs/deployment.md)**.

---

## Production DevOps, CI/CD & Code Quality (Phase 13)

CodePilot AI includes an enterprise automated CI/CD pipeline, code quality toolchain, static typing, and semantic release automation.

### Toolchain Stack
* **Linter & Formatter**: Ruff, Black, and isort configured for Python 3.13 and 88-character line length.
* **Static Typing**: MyPy with strict type analysis and library stubs.
* **Security & Auditing**: Bandit AST security scanner, Safety vulnerability checks, and credential leak detection.
* **Pre-Commit Automation**: Git pre-commit hooks (`.pre-commit-config.yaml`) for cross-editor enforcement.
* **GitHub Actions Workflows**:
  * `ci.yml`: Main CI matrix verifying linting, typing, security, and pytest test suite.
  * `tests.yml`: Granular test suite runner with coverage artifact uploads.
  * `lint.yml`: Dedicated fast lint and style checking.
  * `security.yml`: Weekly scheduled and on-push security scanning.
  * `docker.yml`: Buildx multi-stage image build, compose validation, and container health verification.
  * `release.yml`: Automated semantic tagging, release notes, and GitHub Releases.
  * `deploy.yml`: Production deployment orchestration with zero-downtime database migrations.
* **Automated Dependency Management**: Dependabot (`dependabot.yml`) for weekly pip, GitHub Actions, and Docker updates.
* **PowerShell Automation Helpers**:
  * `.\scripts\format.ps1`: Run Black, isort, and Ruff autofixes.
  * `.\scripts\lint.ps1`: Run 5-stage lint and security verification.
  * `.\scripts\test.ps1`: Run tests with terminal, HTML, and XML coverage.
  * `.\scripts\release.ps1`: Bump semantic versions and update changelog.

For full DevOps guides, local scripts, and secrets setup, see **[docs/devops.md](docs/devops.md)**.

---

## Interactive API Documentation

* **Swagger UI:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) (or [http://localhost/docs](http://localhost/docs) via Nginx)
* **ReDoc:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc) (or [http://localhost/redoc](http://localhost/redoc) via Nginx)
* **Deployment Guide:** [docs/deployment.md](docs/deployment.md)
* **DevOps & CI/CD Manual:** [docs/devops.md](docs/devops.md)


