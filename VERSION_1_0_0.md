# CodePilot AI — Release Notes v1.0.0

**Release Tag**: `v1.0.0`  
**Release Date**: September 28, 2026  
**Commit**: `36877fe` / `main`  
**Stability**: Production Ready (GA)

---

## 1. Executive Summary

**CodePilot AI v1.0.0** marks the first official production General Availability (GA) release of our automated AST code review, security analysis, and AI reasoning platform. This milestone consolidates 14 phases of engineering into a unified, enterprise-ready system featuring:

* Sub-millisecond deterministic Python Abstract Syntax Tree (AST) static analysis.
* Radon cyclomatic complexity and Maintainability Index computation.
* Bandit AST-level security heuristics scanning 25+ vulnerability patterns.
* Google Gemini 2.5 Flash integration for deep architectural reasoning and automated remediation.
* Asynchronous PostgreSQL 16 persistence with SQLAlchemy 2.0 and Alembic migrations.
* Redis 7 LRU caching and SlowAPI sliding-window rate limiting.
* Multi-stage Docker production deployment with Nginx reverse proxy.
* Comprehensive GitHub Actions CI/CD workflows and developer quality toolchain.

---

## 2. What's New in v1.0.0

### Core Engine & Architecture
* **Centralized Semantic Versioning**: Application version unified at `1.0.0` across FastAPI, OpenAPI schema, `/version` endpoint, `/health` endpoint, and CLI scripts.
* **Extended Diagnostic Probes**: The `/health` endpoint now exposes structured telemetry for PostgreSQL connection status, Redis cache latency, Gemini AI provider availability, and volume disk space.
* **Build Metadata Exposure**: Exposes Git commit hash (`build_commit`), container build timestamp (`build_timestamp`), AI provider name, and database engine type via `/version`.

### Multi-Modal AI & Code Generators
* **Google Gemini 2.5 Flash Integration**: Real-time generation of executive summaries, code strengths, prioritized recommendations, and automated code diffs.
* **Automated Scaffolding Generators**:
  * Injected Google/Sphinx formatted docstrings (`/generators/docstring`).
  * Executable `pytest` unit test suites (`/generators/tests`).
  * Standalone Markdown project READMEs (`/generators/readme`).
  * Architecture Mermaid flowcharts (`/generators/architecture`).
  * Semantic changelog generators (`/generators/changelog`).
  * Clean refactored code output (`/generators/refactor`).

### Ingestion, Archives & Batch Processing
* **Safe Archive Ingestion**: Supports `.zip` and `.tar.gz` archive uploads with built-in path canonicalization defense against ZipSlip directory traversal attacks.
* **Background Task Worker**: Asynchronous queue processing with real-time percentage progress tracking (`GET /batch/status/{task_id}`).
* **HMAC-SHA256 Webhooks**: Event-driven notification dispatches for completed batch reviews with replay attack defense.

### Comprehensive Documentation Suite
* Created full technical reference under `docs/`:
  * [`architecture.md`](file:///c:/Users/VANI/OneDrive/Documents/Desktop/code-review-agent/docs/architecture.md): 9 detailed Mermaid diagrams covering application architecture, request lifecycles, auth flows, AI pipelines, database schemas, and background tasks.
  * [`database-schema.md`](file:///c:/Users/VANI/OneDrive/Documents/Desktop/code-review-agent/docs/database-schema.md): Complete data dictionary and Mermaid ER diagram for all 7 PostgreSQL tables.
  * [`ai-pipeline.md`](file:///c:/Users/VANI/OneDrive/Documents/Desktop/code-review-agent/docs/ai-pipeline.md): Comprehensive guide to Phase 5 static analyzers, Gemini integration, and prompt flows.
  * [`api-reference.md`](file:///c:/Users/VANI/OneDrive/Documents/Desktop/code-review-agent/docs/api-reference.md): Complete catalog across all 20 API routers with schemas, tables, and examples.
  * [`deployment.md`](file:///c:/Users/VANI/OneDrive/Documents/Desktop/code-review-agent/docs/deployment.md): Docker, Docker Compose, Linux VPS, and Windows operational manuals.
  * [`development-guide.md`](file:///c:/Users/VANI/OneDrive/Documents/Desktop/code-review-agent/docs/development-guide.md): Onboarding guide, clean architecture patterns, and contribution workflows.
  * [`testing-guide.md`](file:///c:/Users/VANI/OneDrive/Documents/Desktop/code-review-agent/docs/testing-guide.md): Pytest hierarchy, mocks, and PowerShell test commands.
  * [`security.md`](file:///c:/Users/VANI/OneDrive/Documents/Desktop/code-review-agent/docs/security.md): Threat modeling, sandboxing, and OWASP Top 10 mitigation matrix.
  * [`troubleshooting.md`](file:///c:/Users/VANI/OneDrive/Documents/Desktop/code-review-agent/docs/troubleshooting.md): Recovery steps for database, Redis, Gemini, Docker, and ports.
  * [`portfolio.md`](file:///c:/Users/VANI/OneDrive/Documents/Desktop/code-review-agent/docs/portfolio.md) & [`interview-guide.md`](file:///c:/Users/VANI/OneDrive/Documents/Desktop/code-review-agent/docs/interview-guide.md): Elevator pitches, system design narratives, and technical Q&As.
  * [`screenshots.md`](file:///c:/Users/VANI/OneDrive/Documents/Desktop/code-review-agent/docs/screenshots.md): Visual UI mockups and terminal displays.

---

## 3. Breaking Changes

* **FastAPI Query Parameter Syntax**: Query parameters previously using `regex=` have been updated to `pattern=` across `app/api/analytics.py`, `app/api/history.py`, and `app/api/reports.py` to comply with FastAPI / Pydantic v2 deprecation policies.
* **Database Connection Mapping**: In `docker-compose.yml`, the host port for PostgreSQL is mapped to `5433` (container port `5432`) and Redis is mapped to `6380` (container port `6379`) to prevent conflicts with pre-existing local database installations. Ensure external clients point to these updated ports.
* **Authentication Header Requirement**: Protected endpoints strictly enforce Bearer JWT authentication or `X-API-Key` headers; unauthenticated requests receive `401 Unauthorized`.

---

## 4. Database Migration Notes

Upgrading from pre-release builds to v1.0.0 requires applying Alembic migrations:
```bash
# Verify current schema state
alembic current

# Upgrade database to head revision
alembic upgrade head
```
Revisions included in v1.0.0:
* `001_initial_users`: User table with bcrypt password hashing.
* `002_reviews`: Review entities with AST and AI metrics columns.
* `003_tasks`: Asynchronous task execution and progress tracking.
* `004_uploads`: Uploaded source files and archive metadata.
* `005_api_keys`: SHA-256 hashed API keys and permissions scopes.
* `006_audit_and_webhooks`: Immutable audit logs and HMAC webhook subscriptions.

---

## 5. Deployment Notes

### Production Docker Stack
* Use `docker-compose.prod.yml` or standard `docker compose up --build -d`.
* Ensure `.env` is populated with a cryptographically secure `SECRET_KEY` (minimum 32 characters) and a valid `GEMINI_API_KEY`.
* Container healthchecks are pre-tuned with `start_period: 60s` to accommodate database initialization and Alembic auto-migrations.

---

## 6. Known Limitations & Roadmap

* **Language Scope**: Currently, deterministic AST parsing is specialized for Python 3.8–3.13 source code. Support for JavaScript, TypeScript, and Go via Tree-Sitter is slated for the v1.1.0 milestone.
* **Single Archive Limit**: Maximum archive size is constrained to 50 MB (configurable via `MAX_UPLOAD_SIZE_MB`).
* **AI Provider**: Google Gemini 2.5 Flash is the primary AI backend; multi-provider routing (Anthropic Claude, OpenAI GPT-4o, local Ollama) is planned for v1.2.0.

---

*CodePilot AI Release Team — v1.0.0 Production Release.*
