# System Architecture & Technical Specification

> **System**: {{ system_name | default("CodePilot AI") }} | **Version**: {{ version | default("0.1.0") }} | **Generated At**: {{ generated_at }}

---

## 1. High-Level Backend Architecture

{{ backend_architecture }}

```text
{{ architecture_diagram | default("Client ──> FastAPI Application ──> Middlewares ──> API Routers ──> Services ──> [AI Provider | PostgreSQL DB]") }}
```

---

## 2. API Architecture & Routing Layer

{{ api_architecture }}

- **Prefix / Mounts**: All endpoints adhere to versioned, RESTful conventions.
- **Dependency Injection**: Centralized session management and authentication guards (`get_db`, `get_current_user`, `get_optional_user`).

---

## 3. Authentication & Authorization Flow

{{ auth_flow }}

1. **Client Credentials**: Client submits username and password via OAuth2 password flow (`/auth/login`).
2. **Cryptographic Validation**: Password verified with salted bcrypt hashing.
3. **Token Issuance**: Server returns JWT Access Token (HS256) and optional Refresh Token.
4. **Protected Resource Access**: Authorization header Bearer token validated on each authenticated endpoint.

---

## 4. AI Reasoning & Static Analysis Pipeline

{{ ai_pipeline }}

```text
Source Code ──> AST Parser ──> Radon Complexity ──> Bandit Security ──> PEP 8 Style Heuristics
                     │
                     ▼
          Consolidated Context ──> Google Gemini Reasoning Engine
                     │
                     ▼
         Enriched Review / Generated Code / Pytest Tests / Documentation
```

---

## 5. Database Schema & Data Models

{{ database_structure }}

Key ORM entities:
- **`User`**: Account credentials, profile, active status, administrator flags.
- **`Review`**: Code reviews, static scores, and generated AI documentation/test artifacts.

---

## 6. Services & Repositories Layer

{{ services_and_repos }}

- **Repository Layer**: Encapsulates database queries using SQLAlchemy 2.x AsyncSession.
- **Service Layer**: Coordinates business workflows, static analysis execution, and Gemini reasoning.

---

## 7. Middleware & Request Lifecycle

{{ request_lifecycle }}

```text
Incoming Request ──> ProcessTimeMiddleware (Records start timestamp)
                  ──> Exception Handling Layer
                  ──> Authentication & Dependencies
                  ──> Business Route Handler
                  ──> Database Commit / Rollback
                  ──> Response with 'X-Process-Time' header
```
