## Description
Briefly describe the purpose of this Pull Request and summarize the changes made.

Fixes #(issue)

## Type of Change
- [ ] 🐛 Bug fix (non-breaking change which fixes an issue)
- [ ] ✨ New feature (non-breaking change which adds functionality)
- [ ] 💥 Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] 🧹 Refactoring / Code cleanup
- [ ] 📝 Documentation update
- [ ] 🚀 DevOps / CI/CD pipeline update
- [ ] 🗄️ Database migration revision

## Architectural Impact
- [ ] Changes database schema (Alembic migration required)
- [ ] Changes API request/response contracts (OpenAPI schema modified)
- [ ] Adds new environment variables (`.env.example` updated)
- [ ] Affects Docker build or deployment scripts

## Quality Assurance Checklist
Please ensure all checks pass before requesting a review:

- [ ] **Formatting**: Ran `black .` and `isort .` (or `.\scripts\format.ps1`).
- [ ] **Linting**: Ran `ruff check .` and resolved all errors (or `.\scripts\lint.ps1`).
- [ ] **Type Checking**: Ran `mypy app` with 0 type errors.
- [ ] **Security**: Ran `bandit -c .bandit -r app` with 0 high/medium issues.
- [ ] **Automated Tests**: Ran `pytest` and all tests pass (or `.\scripts\test.ps1`).
- [ ] **Test Coverage**: Maintained or improved branch/statement coverage.
- [ ] **Alembic Migrations**: Added revision script under `alembic/versions/` (if schema changed).
- [ ] **Documentation**: Updated `README.md`, `docs/`, or docstrings.
- [ ] **Semantic Versioning**: Tagged/noted according to Conventional Commits.

## Testing Instructions
Describe how the reviewer can test and verify these changes:
```powershell
# 1. Run migrations (if applicable)
docker compose exec backend alembic upgrade head

# 2. Run targeted tests
pytest tests/unit -v
```

## Screenshots / Artifacts (if applicable)
Add any relevant screenshots, JSON responses, or test summary outputs here.
