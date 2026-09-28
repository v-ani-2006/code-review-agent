# CodePilot AI — Developer & Contributor Guide

## 1. Local Environment Setup

### 1.1 Prerequisites
* **Python**: Version 3.12 or 3.13
* **PostgreSQL**: Version 15+ or 16+ (or running via Docker)
* **Redis**: Version 6+ or 7+ (or running via Docker)
* **Git**: Version 2.30+

### 1.2 Virtual Environment & Dependencies
```bash
# Clone the repository
git clone https://github.com/v-ani-2006/code-review-agent.git
cd code-review-agent

# Create and activate Python virtual environment
python -m venv venv

# On Linux / macOS:
source venv/bin/activate

# On Windows (PowerShell):
.\venv\Scripts\Activate.ps1

# Install core runtime dependencies
pip install -r requirements.txt

# Install development, testing, and linting toolchain
pip install -r requirements-dev.txt
```

### 1.3 Environment Variables Configuration
Copy the template and adjust secrets:
```bash
cp .env.example .env
```
Key settings to configure:
* `DATABASE_URL`: `postgresql+asyncpg://postgres:postgres_password@localhost:5432/codepilot_db`
* `REDIS_URL`: `redis://localhost:6379/0`
* `GEMINI_API_KEY`: Your Google AI Studio API key
* `SECRET_KEY`: A cryptographically secure random string (minimum 32 characters)

---

## 2. Project Directory Structure

```text
code-review-agent/
├── app/
│   ├── ai/                      # Static analyzers, AST visitors, LLM orchestration
│   │   ├── generators/          # Docstring, Readme, UnitTest, Changelog generators
│   │   ├── prompts/             # Jinja2 / Python structured prompt templates
│   │   ├── providers/           # Provider implementations (Gemini, mock, base)
│   │   ├── analyzer.py          # Primary AST & complexity orchestration entrypoint
│   │   └── scoring.py           # Weighted composite scoring engine
│   ├── api/                     # 20+ FastAPI APIRouter endpoint definitions
│   ├── core/                    # App configuration, security, logging, monitoring
│   ├── db/                      # SQLAlchemy async engine, session factory, base mixins
│   ├── models/                  # SQLAlchemy ORM entity classes (User, Review, etc.)
│   ├── repositories/            # Data Access Layer implementing Repository pattern
│   ├── schemas/                 # Pydantic v2 validation & serialization schemas
│   ├── services/                # Business logic layer
│   ├── uploads/                 # Storage management & archive extraction logic
│   └── main.py                  # FastAPI application instantiation & lifespan
├── docs/                        # Complete technical and operational documentation
├── scripts/                     # Automated PowerShell & Bash management scripts
├── tests/                       # Pytest test suite (unit, integration, security, perf)
├── Dockerfile                   # Multi-stage production container build
├── docker-compose.yml           # Local multi-service orchestration
└── pyproject.toml               # Unified project metadata & tool configurations
```

---

## 3. Architecture & Clean Layering Pattern

CodePilot AI enforces a strict unidirectional dependency graph:
$$\text{API Routers} \longrightarrow \text{Domain Services} \longrightarrow \text{Repositories} \longrightarrow \text{Database Models}$$

1. **APIs (`app/api/`)**: Accept HTTP payloads, perform preliminary schema validation, check authentication guards, and invoke domain services.
2. **Services (`app/services/`)**: Enforce business invariants, execute AI reasoning, compute scores, coordinate background tasks, and trigger webhooks.
3. **Repositories (`app/repositories/`)**: Abstract database queries, pagination, soft-deletes, and transaction boundaries using SQLAlchemy AsyncSession.
4. **Schemas (`app/schemas/`)**: Pydantic models for strict type contracts and input sanitization.
5. **Models (`app/models/`)**: Declarative SQLAlchemy relational tables.

---

## 4. How-To: Adding a New Route

1. Define or extend an APIRouter in `app/api/<feature>.py`:
   ```python
   from fastapi import APIRouter, Depends, status
   from app.core.dependencies import get_current_user
   from app.models.user import User
   from app.schemas.feature import FeatureRequest, FeatureResponse
   from app.services.feature_service import feature_service

   router = APIRouter(prefix="/feature", tags=["Feature Management"])

   @router.post("", response_model=FeatureResponse, status_code=status.HTTP_201_CREATED)
   async def create_feature(
       payload: FeatureRequest,
       current_user: User = Depends(get_current_user),
   ) -> FeatureResponse:
       """Create and process a new feature entity."""
       return await feature_service.process(payload, user_id=current_user.id)
   ```

2. Register the router in `app/main.py`:
   ```python
   from app.api.feature import router as feature_router
   app.include_router(feature_router)
   ```

---

## 5. How-To: Adding a Service

Create a service class in `app/services/<feature>_service.py`:
```python
from uuid import UUID
from app.repositories.feature_repository import feature_repository
from app.schemas.feature import FeatureRequest, FeatureResponse

class FeatureService:
    """Business logic coordinator for features."""

    async def process(self, payload: FeatureRequest, user_id: UUID) -> FeatureResponse:
        # Enforce domain validation
        data = payload.model_dump()
        data["user_id"] = user_id
        # Persist through repository
        record = await feature_repository.create(data)
        return FeatureResponse.model_validate(record)

feature_service = FeatureService()
```

---

## 6. How-To: Adding a Repository

Inherit from `BaseRepository` in `app/repositories/<feature>_repository.py`:
```python
from app.models.feature import Feature
from app.repositories.base_repository import BaseRepository

class FeatureRepository(BaseRepository[Feature]):
    """Data access repository for Feature entities."""

    def __init__(self):
        super().__init__(Feature)

    async def get_by_name(self, name: str) -> Optional[Feature]:
        async with self.get_session() as session:
            stmt = select(Feature).where(Feature.name == name)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()

feature_repository = FeatureRepository()
```

---

## 7. How-To: Adding a Pydantic Schema

Define schemas in `app/schemas/<feature>.py`:
```python
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime

class FeatureRequest(BaseModel):
    name: str = Field(..., min_length=3, max_length=100, description="Feature name")
    description: str = Field("", max_length=500)

class FeatureResponse(BaseModel):
    id: UUID
    name: str
    description: str
    created_at: datetime

    model_config = {"from_attributes": True}
```

---

## 8. How-To: Adding a New AI Provider

1. Subclass `BaseAIProvider` in `app/ai/providers/<provider_name>_provider.py`:
   ```python
   from app.ai.providers.base_provider import BaseAIProvider
   from app.ai.models import AIProviderResponse

   class ClaudeAIProvider(BaseAIProvider):
       """Anthropic Claude integration provider."""

       async def generate_review(self, prompt: str) -> AIProviderResponse:
           # Call Anthropic API
           ...
   ```

2. Register the provider in `app/ai/providers/provider_factory.py`:
   ```python
   def get_ai_provider(provider_type: str = "gemini") -> BaseAIProvider:
       if provider_type == "claude":
           return ClaudeAIProvider()
       return GeminiProvider()
   ```

---

## 9. Running Migrations

```bash
# Generate a new migration after editing SQLAlchemy models
alembic revision --autogenerate -m "add_features_table"

# Apply the migration to the database
alembic upgrade head

# Rollback one migration
alembic downgrade -1
```

---

## 10. Running Test Suites

Execute tests via PowerShell or Bash:
```powershell
# Run the complete test suite with coverage report
.\scripts\test.ps1 -Type all

# Run specific test suites
.\scripts\test.ps1 -Type unit
.\scripts\test.ps1 -Type integration
.\scripts\test.ps1 -Type security
.\scripts\test.ps1 -Type performance
```

Or using standard `pytest`:
```bash
pytest --cov=app --cov-report=term-missing tests/
```

---

*Document Version: 1.0.0 — Developer & Contributor Guide.*
