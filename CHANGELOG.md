# Changelog

All notable changes to the **CodePilot AI (`code-review-agent`)** project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

<!-- NEXT_VERSION_HEADER -->

## [0.1.0] - 2026-09-28

### Added
- **Phase 1: Project Architecture**: Initial FastAPI application factory with lifespan management, CORS, structured logging, and unified exception handling.
- **Phase 2: AST Static Analysis Engine**: Python AST parsing with error recovery, Radon cyclomatic complexity and Maintainability Index computation, Halstead metrics, Bandit security checks, and PEP 8 heuristics.
- **Phase 3: Authentication & Security**: OAuth2 password flow, JWT access & refresh tokens, bcrypt password hashing, and active account verification.
- **Phase 4: Database Layer**: SQLAlchemy 2.0 async engine with PostgreSQL, Alembic migrations (revisions 001–006), and generic asynchronous CRUD repository pattern.
- **Phase 5: Review Persistence**: Endpoints for raw code snippets, code files, and structured review report storage with score calculation.
- **Phase 6: Gemini AI Reasoning Engine**: Google Gemini 2.5 Flash provider with retry logic, prompts for deep code reviews, beginner explanations, algorithmic optimizations, and automated bug fixes.
- **Phase 7: AI Code Generators & Multi-Format Exporters**: Automated generation of documentation, Google/Sphinx docstrings, pytest unit test suites, GitHub READMEs, refactoring proposals, system architecture specs, and changelogs. Multi-format export to JSON, Markdown, styled HTML, and TXT.
- **Phase 8: Review History & Comparison**: Paginated history, advanced search, favorites, soft delete/restore, timeline aggregation, and side-by-side review diff comparisons.
- **Phase 9: Dashboard & Analytics**: Executive overview metrics, coding streak tracking, historical score trajectories, language distributions, and 365-day contribution heatmaps.
- **Phase 10: Infrastructure, Caching & Telemetry**: Redis connection pool with memory fallback, SlowAPI rate limiting, Prometheus metrics collector (`/metrics`), HMAC-SHA256 signed outbound webhooks, cryptographic API keys, and deep multi-service health probes.
- **Phase 11: Automated Testing Suite**: 116 automated tests covering unit tests, integration workflows, security penetration tests, and performance benchmarks.
- **Phase 12: Docker & Production Containerization**: Multi-stage production Dockerfile (`python:3.13-slim`), Docker Compose development and production profiles, Nginx reverse proxy with gzip compression and rate limiting, and PowerShell management helpers.
- **Phase 13: CI/CD & Production DevOps**:
  - GitHub Actions workflows: `ci.yml`, `tests.yml`, `lint.yml`, `security.yml`, `docker.yml`, `release.yml`, and `deploy.yml`.
  - Quality toolchain: Ruff linter & formatter, Black formatter, isort import sorter, MyPy static type checker, Bandit security scanner, and Safety vulnerability auditor.
  - Pre-commit hooks (`.pre-commit-config.yaml`) and EditorConfig (`.editorconfig`).
  - Automated weekly dependency audits via Dependabot (`dependabot.yml`).
  - Community health templates: Bug report, Feature request, Support question, PR template, and CODEOWNERS.
  - Automated PowerShell scripts: `format.ps1`, `lint.ps1`, `test.ps1`, and `release.ps1`.
  - Comprehensive DevOps architecture manual (`docs/devops.md`).

### Changed
- Standardized code formatting to 88-character width conforming with Black and PEP 8.
- Updated FastAPI query parameters from deprecated `regex=` to `pattern=`.
- Enhanced database and Redis startup pollers with pure-Python TCP socket fallbacks.
- Exposed build metadata (`build_commit`, `build_timestamp`) in `/version` and OpenAPI metadata.

### Fixed
- Fixed container startup timeout race condition by tuning Docker health check `start_period` to 60s and `interval` to 10s.
- Fixed missing client binaries in lightweight production container by adding `postgresql-client` and `redis-tools` to Dockerfile.
- Fixed safe fallback to stdout logging in container environments when file logs are restricted.

### Security
- Enforced cryptographic secret key verification and HMAC-SHA256 signature dispatches for webhooks.
- Configured Bandit static analysis and Safety vulnerability checks in CI/CD pipeline.
- Added heuristic secret scanner in `security.yml` to prevent credential leakage.
