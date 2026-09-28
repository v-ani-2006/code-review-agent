# CodePilot AI — REST API Reference Manual

## 1. Overview & Authentication Specification

All API endpoints are hosted at `/` or with an optional prefix defined by `API_PREFIX`.
* Interactive OpenAPI Swagger UI: `http://localhost:8000/docs`
* ReDoc UI: `http://localhost:8000/redoc`
* OpenAPI JSON Specification: `http://localhost:8000/openapi.json`

### Authentication Mechanisms
1. **JWT Bearer Token**: Pass via header:
   ```http
   Authorization: Bearer <access_token>
   ```
2. **API Key Authentication**: Pass via header:
   ```http
   X-API-Key: cp_live_<prefix>_<secret>
   ```

---

## 2. Health, Version & Diagnostics

### Endpoints Table
| Method | Path | Auth Required | Request Schema | Response Schema | Status Codes | Description |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `GET` | `/` | None | None | `RootResponse` | `200` | Service welcome & metadata |
| `GET` | `/health` | None | None | `HealthResponse` | `200`, `503` | Liveness & subsystem health |
| `GET` | `/version` | None | None | `VersionResponse` | `200` | Application build & version |

#### Example: `GET /health`
```http
GET /health HTTP/1.1
Host: localhost:8000
```
```json
{
  "status": "ok",
  "api_status": "ok",
  "application": "code-review-agent",
  "app_name": "code-review-agent",
  "version": "1.0.0",
  "environment": "production",
  "uptime": "14 days, 3 hours, 22 minutes",
  "timestamp": "2026-09-28T14:30:00.000000Z",
  "ai_provider": "Google Gemini (gemini-2.5-flash)",
  "database": {
    "status": "healthy",
    "latency_ms": 1.42
  },
  "redis": {
    "status": "healthy",
    "latency_ms": 0.38
  },
  "gemini": {
    "status": "healthy",
    "model": "gemini-2.5-flash"
  },
  "storage": {
    "status": "healthy",
    "free_space_gb": 42.8
  }
}
```

---

## 3. Authentication & User Management

### Endpoints Table
| Method | Path | Auth Required | Request Schema | Response Schema | Status Codes | Description |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `POST` | `/auth/register` | None | `UserRegisterRequest` | `UserResponse` | `201`, `400` | Register a new user |
| `POST` | `/auth/login` | None | `OAuth2PasswordRequestForm` | `TokenResponse` | `200`, `401` | Authenticate & get JWT |
| `POST` | `/auth/refresh` | None | `TokenRefreshRequest` | `TokenResponse` | `200`, `401` | Refresh expired access token |
| `GET` | `/auth/me` | JWT | None | `UserResponse` | `200`, `401` | Fetch current user profile |
| `POST` | `/auth/logout` | JWT | None | `MessageResponse` | `200`, `401` | Revoke active JWT session |
| `POST` | `/auth/change-password` | JWT | `PasswordChangeRequest` | `MessageResponse` | `200`, `400` | Update user password |

#### Example: `POST /auth/login`
```http
POST /auth/login HTTP/1.1
Content-Type: application/x-www-form-urlencoded

username=developer%40codepilot.ai&password=SuperSecurePassword123!
```
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 900
}
```

---

## 4. Code Review & Static Analysis

### Endpoints Table
| Method | Path | Auth Required | Request Schema | Response Schema | Status Codes | Description |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `POST` | `/review/text` | Optional | `ReviewCodeRequest` | `ReviewReport` | `200`, `400` | Fast AST & Radon review |
| `POST` | `/review/file` | Optional | `multipart/form-data` | `ReviewReport` | `200`, `400` | Review uploaded source file |

#### Example: `POST /review/text`
```http
POST /review/text HTTP/1.1
Content-Type: application/json

{
  "code": "def divide(a, b):\n    return a / b",
  "filename": "math_utils.py",
  "language": "python"
}
```
```json
{
  "summary": "Static analysis detected 1 issue in math_utils.py.",
  "scores": {
    "readability": 85.0,
    "maintainability": 92.0,
    "security": 70.0,
    "complexity": 95.0,
    "documentation": 50.0,
    "overall": 82.4
  },
  "issues": [
    {
      "id": "SEC-004",
      "title": "Unchecked Division by Zero",
      "description": "Function divide does not guard against b == 0.",
      "severity": "medium",
      "category": "bug_risk",
      "line_number": 2,
      "column": 11,
      "suggestion": "Check if b == 0 before division or handle ZeroDivisionError."
    }
  ],
  "complexity": {
    "cyclomatic_complexity": 1.0,
    "maintainability_index": 92.4,
    "rank": "A"
  },
  "processing_time": 0.0012,
  "version": "1.0.0"
}
```

---

## 5. Gemini AI Reasoning & Generation

### Endpoints Table
| Method | Path | Auth Required | Request Schema | Response Schema | Status Codes | Description |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `POST` | `/ai/review` | JWT / API Key | `AIReviewRequest` | `AIReviewResponse` | `200`, `400`, `500` | Deep Gemini AI code critique |
| `POST` | `/ai/explain` | JWT / API Key | `AIExplainRequest` | `AIExplainResponse` | `200`, `400` | Algorithm explanation |
| `POST` | `/ai/optimize` | JWT / API Key | `AIOptimizeRequest` | `AIOptimizeResponse` | `200`, `400` | Performance optimizations |
| `POST` | `/ai/bugfix` | JWT / API Key | `AIBugFixRequest` | `AIBugFixResponse` | `200`, `400` | Automated bug & CVE fix |
| `POST` | `/ai/documentation` | JWT / API Key | `AIDocumentationRequest`| `AIDocumentationResponse` | `200`, `400` | Generate Sphinx docstrings |
| `POST` | `/ai/tests` | JWT / API Key | `AITestRequest` | `AITestResponse` | `200`, `400` | Generate pytest test suite |
| `GET` | `/ai/status` | None | None | `AIStatusResponse` | `200` | AI provider connectivity |
| `GET` | `/ai/models` | None | None | `AIModelListResponse` | `200` | List available AI models |

#### Example: `POST /ai/review`
```http
POST /ai/review HTTP/1.1
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "code": "import os\ndef run_cmd(user_input):\n    return os.system('echo ' + user_input)",
  "language": "python",
  "detail_level": "comprehensive"
}
```
```json
{
  "summary": "Critical Command Injection vulnerability detected.",
  "strengths": [
    "Concise implementation logic"
  ],
  "recommendations": [
    "Use subprocess.run with a list of arguments and shell=False instead of os.system.",
    "Validate and sanitize all external user input before execution."
  ],
  "bugfix": "import subprocess\n\ndef run_cmd(user_input: str):\n    return subprocess.run(['echo', user_input], capture_output=True, text=True, check=True)",
  "model_used": "gemini-2.5-flash",
  "processing_time": 0.842
}
```

---

## 6. Generators & Scaffolding

### Endpoints Table
| Method | Path | Auth Required | Request Schema | Response Schema | Status Codes | Description |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `POST` | `/generators/readme` | JWT / API Key | `ReadmeGenRequest` | `ReadmeGenResponse` | `200` | Generate project README.md |
| `POST` | `/generators/docstring` | JWT / API Key | `DocstringGenRequest`| `DocstringGenResponse`| `200` | Injects Google docstrings |
| `POST` | `/generators/tests` | JWT / API Key | `TestGenRequest` | `TestGenResponse` | `200` | Generates pytest test cases |
| `POST` | `/generators/architecture` | JWT / API Key | `ArchGenRequest` | `ArchGenResponse` | `200` | Generates Mermaid architecture |
| `POST` | `/generators/changelog` | JWT / API Key | `ChangelogGenRequest` | `ChangelogGenResponse` | `200` | Generates release changelog |
| `POST` | `/generators/refactor` | JWT / API Key | `RefactorGenRequest` | `RefactorGenResponse` | `200` | Clean code refactoring |

---

## 7. Uploads & Batch Archive Processing

### Endpoints Table
| Method | Path | Auth Required | Request Schema | Response Schema | Status Codes | Description |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `POST` | `/upload/single` | JWT / API Key | `multipart/form-data` | `UploadResponse` | `201`, `400` | Upload single source file |
| `POST` | `/upload/archive`| JWT / API Key | `multipart/form-data` | `BatchTaskResponse`| `202`, `400` | Upload ZIP / TAR archive |
| `GET` | `/upload/files` | JWT / API Key | Query params | `PaginatedUploads` | `200` | List user uploaded files |
| `GET` | `/upload/status/{id}` | JWT / API Key | None | `TaskStatusResponse`| `200`, `404` | Check extraction status |

---

## 8. Batch & Async Task Orchestration

### Endpoints Table
| Method | Path | Auth Required | Request Schema | Response Schema | Status Codes | Description |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `POST` | `/batch/start` | JWT / API Key | `BatchStartRequest` | `BatchTaskResponse` | `202` | Trigger batch analysis job |
| `GET` | `/batch/status/{task_id}` | JWT / API Key | None | `TaskProgressResponse`| `200`, `404`| Poll progress percentage |
| `GET` | `/batch/results/{task_id}`| JWT / API Key | None | `BatchResultResponse` | `200`, `404`| Retrieve aggregated scores |

---

## 9. History, Reports & Exports

### Endpoints Table
| Method | Path | Auth Required | Request Schema | Response Schema | Status Codes | Description |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `GET` | `/history` | JWT / API Key | Pagination params | `PaginatedReviews` | `200` | List historical reviews |
| `GET` | `/history/{id}` | JWT / API Key | None | `ReviewDetailResponse`| `200`, `404` | Get specific review detail |
| `DELETE` | `/history/{id}` | JWT / API Key | None | `MessageResponse` | `200`, `404` | Soft-delete review record |
| `POST` | `/history/{id}/favorite` | JWT / API Key | None | `FavoriteResponse` | `200`, `404` | Toggle favorite flag |
| `GET` | `/reports/{id}/markdown` | JWT / API Key | None | `text/markdown` | `200`, `404` | Download report markdown |
| `GET` | `/reports/{id}/html` | JWT / API Key | None | `text/html` | `200`, `404` | Download report styled HTML |
| `GET` | `/reports/{id}/json` | JWT / API Key | None | `application/json` | `200`, `404` | Download report JSON |
| `POST` | `/exports/markdown` | JWT / API Key | `ExportRequest` | `ExportResponse` | `200` | Export ad-hoc markdown |
| `POST` | `/exports/html` | JWT / API Key | `ExportRequest` | `ExportResponse` | `200` | Export ad-hoc HTML |

---

## 10. Dashboard & Analytics

### Endpoints Table
| Method | Path | Auth Required | Request Schema | Response Schema | Status Codes | Description |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `GET` | `/dashboard/stats` | JWT / API Key | None | `DashboardStatsResponse`| `200` | Metrics aggregate overview |
| `GET` | `/dashboard/recent`| JWT / API Key | None | `List[ReviewSummary]` | `200` | Recent review activity |
| `GET` | `/analytics/summary` | JWT / API Key | Query params | `AnalyticsSummary` | `200` | High-level analytics |
| `GET` | `/analytics/trends` | JWT / API Key | `days=30` | `TrendsResponse` | `200` | Score trends over time |
| `GET` | `/analytics/languages` | JWT / API Key | None | `LanguageDistribution`| `200` | Language breakdown stats |
| `GET` | `/analytics/export` | JWT / API Key | `format=json\|csv\|markdown` | Download | `200` | Export analytics report |

---

## 11. Monitoring, Metrics & Audit Logs

### Endpoints Table
| Method | Path | Auth Required | Request Schema | Response Schema | Status Codes | Description |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `GET` | `/metrics` | Admin / Token | None | `MetricsResponse` | `200` | System throughput metrics |
| `GET` | `/metrics/prometheus`| None | None | Prometheus text | `200` | Prometheus scraping format |
| `GET` | `/monitoring/health` | None | None | `HealthDiagnostic` | `200`, `503`| Detailed subsystem probes |
| `GET` | `/monitoring/system` | Admin | None | `SystemResources` | `200` | CPU, RAM, Disk utilization |
| `GET` | `/monitoring/cache` | Admin | None | `CacheDiagnostics` | `200` | Redis hits, misses, memory |
| `GET` | `/audit-logs` | Admin | Query params | `PaginatedAuditLogs` | `200` | Filtered security audit trail |
| `GET` | `/audit-logs/export` | Admin | `format=json\|csv` | Download | `200` | Export immutable audit logs |

---

## 12. Webhooks & API Keys Administration

### Endpoints Table
| Method | Path | Auth Required | Request Schema | Response Schema | Status Codes | Description |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `POST` | `/webhooks` | JWT / API Key | `WebhookCreate` | `WebhookResponse` | `201` | Register new event webhook |
| `GET` | `/webhooks` | JWT / API Key | None | `List[WebhookResponse]`| `200` | List active webhook targets |
| `DELETE` | `/webhooks/{id}` | JWT / API Key | None | `MessageResponse` | `200`, `404` | Delete webhook subscription |
| `POST` | `/webhooks/{id}/test` | JWT / API Key | None | `WebhookDeliveryStatus`| `200`, `400` | Dispatch ping test event |
| `POST` | `/admin/api-keys` | Admin JWT | `APIKeyCreate` | `APIKeySecretResponse` | `201` | Provision new client API key |
| `GET` | `/admin/api-keys` | Admin JWT | None | `List[APIKeyResponse]` | `200` | List active client API keys |
| `DELETE` | `/admin/api-keys/{id}`| Admin JWT | None | `MessageResponse` | `200`, `404` | Revoke client API key |

---

*Document Version: 1.0.0 — REST API Reference Manual.*
