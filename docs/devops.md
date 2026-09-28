# CodePilot AI — Production DevOps & CI/CD Manual

Comprehensive guide to the **CodePilot AI** continuous integration, continuous delivery (CI/CD), static analysis, code quality gates, automated testing, security scanning, and semantic release pipeline.

---

## 🏗️ DevOps Architecture Overview

```mermaid
flowchart TD
    subgraph Developer["💻 Developer Workstation"]
        Code["Source Code Changes"]
        PreCommit["🪝 Pre-Commit Hooks\n(Ruff, Black, isort, MyPy, Bandit)"]
        LocalScripts["⚙️ PowerShell Toolchain\n(format.ps1, lint.ps1, test.ps1, release.ps1)"]
        Code --> PreCommit
        Code --> LocalScripts
    end

    subgraph GitHub["🐙 GitHub Enterprise / Actions"]
        PR(["🔀 Pull Request / Push"])
        PreCommit -.->|git push| PR

        subgraph Pipelines["Automated CI/CD Workflows"]
            CI["🔄 ci.yml\n• Linting (Ruff, Black, isort, MyPy)\n• Security (Bandit, Safety)\n• 116 Tests & Coverage Matrix"]
            Tests["🧪 tests.yml\n• Unit, Integration, Security\n• Performance Benchmarks\n• XML & HTML Artifacts"]
            Lint["🧹 lint.yml\n• Strict Style & Typing Checks\n• Artifact Reports on Failure"]
            Security["🛡️ security.yml\n• Scheduled Weekly Audits\n• Secret Leaks & Vulnerabilities"]
            Docker["🐳 docker.yml\n• Multi-Stage Buildx Build\n• Container Health Probe\n• In-Container Pytest"]
            Release["🏷️ release.yml\n• Semantic Version Tagging\n• Changelog Generation\n• GitHub Release & Artifacts"]
            Deploy["🚀 deploy.yml\n• Zero-Downtime Migrations\n• Rolling Restart\n• Smoke Health Probes"]
        end

        PR --> CI
        PR --> Lint
        PR --> Security
        PR --> Docker
        Release -.->|Triggered by v*.*.* tag| Deploy
    end

    subgraph Targets["🌐 Production Targets"]
        NginxProxy["🛡️ Nginx Reverse Proxy (Port 80/443)"]
        BackendContainer["⚙️ FastAPI Backend (Port 8000)"]
        PostgresDB[("🐘 PostgreSQL 16")]
        RedisCache[("⚡ Redis 7 Cache")]
        Deploy --> NginxProxy
        Deploy --> BackendContainer
        Deploy --> PostgresDB
        Deploy --> RedisCache
    end
```

---

## 📁 Repository CI/CD File Structure

```text
code-review-agent/
├── .github/
│   ├── workflows/
│   │   ├── ci.yml                 # Main CI pipeline (Lint + Security + Pytest Matrix)
│   │   ├── tests.yml              # Granular test suite execution & coverage reporting
│   │   ├── lint.yml               # Strict code formatting and static typing checks
│   │   ├── security.yml           # Bandit, Safety & credential scanning (weekly cron)
│   │   ├── docker.yml             # Docker Buildx verification & in-container test runner
│   │   ├── release.yml            # Automated GitHub releases, release notes & tagging
│   │   └── deploy.yml             # Production deployment orchestration & smoke tests
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.md          # Standardized bug reporting form
│   │   ├── feature_request.md     # Feature enhancement submission form
│   │   └── question.md            # Architecture & setup question template
│   ├── PULL_REQUEST_TEMPLATE.md   # PR checklist (tests, linter, docs, migrations)
│   ├── CODEOWNERS                 # Code ownership routing for reviews
│   └── dependabot.yml             # Automated weekly updates (pip, actions, docker)
├── scripts/
│   ├── format.ps1                 # Automated formatting (Black + isort + Ruff fix)
│   ├── lint.ps1                   # Static lint & security verification (Ruff + MyPy + Bandit)
│   ├── test.ps1                   # Automated test suite runner with HTML coverage
│   └── release.ps1                # Semantic release manager & changelog updater
├── .pre-commit-config.yaml        # Git pre-commit hook configuration
├── .editorconfig                  # Cross-editor formatting standards (UTF-8, LF, 4 spaces)
├── .ruff.toml / ruff.toml         # Fast linter and code quality rules
├── pyproject.toml                 # Project metadata, Black, isort, and Coverage settings
├── mypy.ini                       # Static type analysis rules and library overrides
├── .bandit                        # Bandit security scan target exclusions & rule skips
├── requirements-dev.txt           # Development, linting, and testing dependencies
└── CHANGELOG.md                   # Keep a Changelog history adhering to Semantic Versioning
```

---

## 🛠️ Local Developer Toolchain

### 1. Installing Development Dependencies
Install the complete development and quality assurance toolchain into your active virtual environment:

```powershell
pip install -r requirements-dev.txt
```

### 2. Setting Up Pre-Commit Git Hooks
Install pre-commit hooks so formatting and security checks run automatically before every commit:

```powershell
pre-commit install
```

Run hooks against all files manually at any time:
```powershell
pre-commit run --all-files
```

---

## 🚀 PowerShell Automation Scripts

CodePilot AI includes native Windows PowerShell automation scripts inside the `scripts/` directory:

### 1. Code Formatting (`.\scripts\format.ps1`)
Runs **isort** to sort imports, **Black** to format code to the 88-character standard, and **Ruff** to apply safe autofixes:
```powershell
.\scripts\format.ps1
```

### 2. Code Quality & Linting (`.\scripts\lint.ps1`)
Executes 5 static quality gates:
1. **Ruff** (PEP 8, complexity, unused imports)
2. **Black** (style check)
3. **isort** (import order check)
4. **MyPy** (static type verification)
5. **Bandit** (AST security scanning)

```powershell
# Run standard lint verification
.\scripts\lint.ps1

# Run in strict mode (fails with non-zero exit code on any warning)
.\scripts\lint.ps1 -Strict
```

### 3. Automated Test Suite & Coverage (`.\scripts\test.ps1`)
Runs tests and produces terminal, HTML, and XML coverage reports:
```powershell
# Run all 116 tests
.\scripts\test.ps1 -Target all

# Run isolated unit tests
.\scripts\test.ps1 -Target unit

# Run API integration tests
.\scripts\test.ps1 -Target integration

# Run security and exploit tests
.\scripts\test.ps1 -Target security

# Run performance latency benchmarks
.\scripts\test.ps1 -Target performance

# Generate full HTML and XML coverage reports
.\scripts\test.ps1 -Target coverage -MinCoverage 40
```
*Coverage report is saved directly to `coverage_html/index.html`.*

### 4. Automated Semantic Releases (`.\scripts\release.ps1`)
Calculates next semantic version, updates configuration files, updates `CHANGELOG.md`, and prepares release tags:
```powershell
# Bump patch version (0.1.0 -> 0.1.1)
.\scripts\release.ps1 -Bump patch

# Bump minor version (0.1.0 -> 0.2.0)
.\scripts\release.ps1 -Bump minor

# Bump major version (0.1.0 -> 1.0.0)
.\scripts\release.ps1 -Bump major

# Dry-run simulation (no files modified)
.\scripts\release.ps1 -Bump minor -DryRun
```

---

## 🔒 GitHub Actions Workflows & Quality Gates

| Workflow File | Trigger Events | Purpose & Deliverables |
|---|---|---|
| [ci.yml](file:///.github/workflows/ci.yml) | Push & PR (`main`, `develop`) | Linting, MyPy type analysis, Bandit security audit, full test suite execution, and coverage report upload. |
| [tests.yml](file:///.github/workflows/tests.yml) | Push & PR | Parallel matrix execution for `unit`, `integration`, `security`, and `performance` test suites. |
| [lint.yml](file:///.github/workflows/lint.yml) | Push & PR | Dedicated fast lint verification (Ruff, Black, isort, MyPy) with report artifacts uploaded on failure. |
| [security.yml](file:///.github/workflows/security.yml) | Weekly Cron (`0 2 * * 1`), Push & PR | Bandit AST scanner, Safety dependency vulnerability check, and heuristic secret leak scanner. |
| [docker.yml](file:///.github/workflows/docker.yml) | Push & PR (Docker files) | Buildx multi-stage build caching, compose validation, live `/health` container probe, and in-container pytest run. |
| [release.yml](file:///.github/workflows/release.yml) | Tags (`v*.*.*`) | Automated changelog extraction, GitHub Release creation, and coverage artifact publishing. |
| [deploy.yml](file:///.github/workflows/deploy.yml) | Manual dispatch (`workflow_dispatch`) | Production secrets verification, zero-downtime Alembic migrations, rolling container restarts, and health checks. |

---

## 🔑 GitHub Repository Secrets Configuration

To enable automated production deployments and CI testing, configure the following secrets under **GitHub Repository Settings ➔ Secrets and variables ➔ Actions**:

| Secret Name | Required | Description | Example / Fallback |
|---|---|---|---|
| `SECRET_KEY` | **Yes** | Cryptographic secret for signing JWT access & refresh tokens. | `e7b2514c3e8a...min-32-chars` |
| `DATABASE_URL` | Optional | Full PostgreSQL connection string (overrides individual parameters). | `postgresql+asyncpg://user:pass@host:5432/dbname` |
| `REDIS_URL` | Optional | Redis connection URL for caching and SlowAPI rate limiting. | `redis://redis:6379/0` |
| `GEMINI_API_KEY` | **Yes** | Google Gemini API key for deep semantic code reviews. | `AIzaSy...` |
| `WEBHOOK_SECRET` | Optional | Shared cryptographic secret for signing outbound webhook dispatches. | `codepilot-secret-webhook-key` |

> [!NOTE]
> Never commit actual secrets into Git. Use `.env.example` as a template and configure actual values via environment variables or GitHub Secrets.

---

## 🏷️ Semantic Versioning Standard

CodePilot AI adheres strictly to [Semantic Versioning 2.0.0](https://semver.org/):

$$\text{MAJOR}.\text{MINOR}.\text{PATCH}$$

1. **MAJOR (`1.0.0`)**: Incompatible API changes or major architectural redesigns.
2. **MINOR (`0.2.0`)**: Backwards-compatible new features, new endpoints, or added generators.
3. **PATCH (`0.1.1`)**: Backwards-compatible bug fixes, performance improvements, or security patches.

The active application version is dynamically exposed via:
- Configuration: `settings.APP_VERSION` in [app/core/config.py](file:///c:/Users/VANI/OneDrive/Documents/Desktop/code-review-agent/app/core/config.py)
- Packaging: `pyproject.toml`
- System Info API: `GET /version` returning `{"app_name": "code-review-agent", "version": "0.1.0", "build_commit": "...", "build_timestamp": "..."}`
- Interactive OpenAPI: `http://localhost:8000/docs`
