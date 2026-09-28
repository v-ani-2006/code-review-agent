# Contributing to CodePilot AI

Thank you for your interest in contributing to **CodePilot AI**! We welcome bug reports, feature proposals, documentation improvements, architectural reviews, and code contributions.

Please review this guide before submitting your Pull Request.

---

## 🚀 Quick Setup Guide

### 1. Fork & Clone
```bash
git clone https://github.com/<your-username>/code-review-agent.git
cd code-review-agent
```

### 2. Set Up Virtual Environment (Python 3.13)
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
pre-commit install
```

### 3. Launch Development Infrastructure (Docker)
```powershell
docker compose up -d
docker compose ps
```

---

## 🌿 Branch Naming Conventions

Prefix your branches with the nature of the change:
* `feat/` — New feature or major enhancement (e.g. `feat/ast-rust-support`)
* `fix/` — Bug fix (e.g. `fix/alembic-lock-timeout`)
* `docs/` — Documentation updates (e.g. `docs/api-guide`)
* `refactor/` — Code refactoring without behavioral alterations (e.g. `refactor/cache-pool`)
* `test/` — Adding or improving automated tests (e.g. `test/rate-limiter`)
* `ci/` — GitHub Actions and DevOps pipeline changes (e.g. `ci/docker-buildx`)

---

## 📝 Commit Conventions (Conventional Commits)

Commit messages must adhere to the [Conventional Commits](https://www.conventionalcommits.org/) format:

$$\text{<type>}(\text{<scope>}): \text{<description>}$$

### Examples:
* `feat(analyzer): add Halstead volume metrics to code report`
* `fix(auth): prevent timing attack in password hash verification`
* `docs(readme): add interactive swagger and docker setup guides`
* `test(history): add timeline aggregation unit tests`
* `ci(workflows): add weekly security scan cron trigger`

---

## 🧪 Quality Gates & Local Verification

Before opening your Pull Request, ensure all local checks pass:

```powershell
# 1. Format code (Black, isort, Ruff fix)
.\scripts\format.ps1

# 2. Run lint and security checks (Ruff, MyPy, Bandit)
.\scripts\lint.ps1

# 3. Run automated tests with coverage
.\scripts\test.ps1 -Target all
```

---

## 🔀 Pull Request Process

1. Ensure all new functions, classes, and endpoints include descriptive docstrings and type hints.
2. If changing database schemas, include a versioned Alembic migration script under `alembic/versions/`.
3. Open a Pull Request against the `main` branch.
4. Fill out the [PULL_REQUEST_TEMPLATE.md](file:///.github/PULL_REQUEST_TEMPLATE.md).
5. Ensure all GitHub Actions workflows (`CI Pipeline`, `Code Quality`, `Docker Build`) pass with green status.
6. A project maintainer will review your submission and provide feedback.
