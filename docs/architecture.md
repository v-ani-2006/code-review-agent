# CodePilot AI — System Architecture Specification

## 1. Executive Architecture Overview

**CodePilot AI** is an enterprise-ready, hybrid static-analysis and Generative AI code review orchestration platform. It integrates deterministic AST parsing, cyclomatic complexity calculations (Radon), AST-level security auditing (Bandit), and PEP 8 conformance checking with high-reasoning Large Language Models (Google Gemini 2.5 Flash).

The backend is built on **FastAPI (Python 3.13)** with an asynchronous I/O paradigm, backed by **PostgreSQL 16** for relational state persistence, **Redis 7** for LRU caching and distributed rate limiting, and **Nginx** as an edge reverse proxy providing TLS termination, Gzip compression, and request buffering.

```mermaid
flowchart TB
    subgraph Clients["Edge Clients"]
        WebUI["💻 Browser / Web UI"]
        DevCLI["⌨️ CLI / IDE Extension"]
        GitWebhook["🐙 GitHub / GitLab Webhook"]
    end

    subgraph Edge["Reverse Proxy & Gateway"]
        Nginx["🛡️ Nginx Reverse Proxy\n(Port 80/443)\n• SSL Termination\n• Gzip Compression\n• Client Body Limit (50MB)\n• Security Headers"]
    end

    subgraph AppCluster["Application Tier (Docker: codepilot_backend)"]
        FastAPI["⚙️ FastAPI Core Engine\n(Gunicorn + Uvicorn Workers)"]
        
        subgraph Middlewares["Security & Telemetry Middleware"]
            SecHeaders["Security Headers Middleware"]
            SlowAPI["SlowAPI Rate Limiter (Redis-backed)"]
            AuditLogMid["Audit Logging Middleware"]
            CorsMid["CORS Middleware"]
        end

        subgraph Routers["API Routers (20+ Modular Endpoints)"]
            AuthR["/auth (JWT / OAuth2)"]
            KeyR["/api-keys (HMAC API Keys)"]
            RevR["/review (Single / Batch)"]
            AIR["/ai (Explain/Docs/Tests/Fix)"]
            UpR["/upload (Zip / Tar / Multi-file)"]
            RepR["/reports (JSON/MD/HTML/PDF)"]
            DashR["/dashboard & /analytics"]
            MonR["/monitoring & /health"]
        end

        subgraph CoreServices["Domain Services Layer"]
            AnalyzerSvc["AST & Complexity Analyzer"]
            GeminiSvc["Gemini 2.5 AI Reasoning Engine"]
            ReportGenSvc["Multi-Format Report Generator"]
            BatchWorker["Asynchronous Batch Orchestrator"]
            WebhookDispatcher["HMAC Webhook Dispatcher"]
        end

        subgraph Repos["Data Access Layer (Repository Pattern)"]
            UserRepo["User & Key Repository"]
            ReviewRepo["Review & Analysis Repository"]
            ReportRepo["Report Repository"]
            AuditRepo["Audit Log Repository"]
        end
    end

    subgraph DataCluster["Persistence & Cache Tier"]
        Postgres[("🐘 PostgreSQL 16\n(AsyncPG / SQLAlchemy ORM)\n• Relational Entity Persistence\n• Foreign Keys & Indexes")]
        RedisPool[("⚡ Redis 7 Cache & Store\n• Dynamic Query LRU Cache\n• SlowAPI Token Buckets\n• Temporary Job State")]
        Storage[("💾 Persistent Local Volumes\n• /app/uploads (Code Archives)\n• /app/reports (Deliverables)\n• /app/logs (Structured Logs)")]
    end

    subgraph External["External AI Provider"]
        GeminiCloud["🧠 Google Gemini API\n(gemini-2.5-flash)"]
    end

    %% Edge to Gateway
    WebUI -->|HTTPS / REST| Nginx
    DevCLI -->|HTTPS / REST| Nginx
    GitWebhook -->|POST /webhooks| Nginx

    %% Gateway to Backend
    Nginx -->|Reverse Proxy| FastAPI

    %% Middleware pipeline
    FastAPI --> SecHeaders
    SecHeaders --> SlowAPI
    SlowAPI --> AuditLogMid
    AuditLogMid --> CorsMid
    CorsMid --> Routers

    %% Routers to Services
    RevR --> AnalyzerSvc
    RevR --> GeminiSvc
    AIR --> GeminiSvc
    UpR --> BatchWorker
    RepR --> ReportGenSvc
    BatchWorker --> AnalyzerSvc
    BatchWorker --> GeminiSvc

    %% Services to Repositories & External
    AnalyzerSvc --> ReviewRepo
    GeminiSvc --> GeminiCloud
    GeminiSvc --> ReviewRepo
    BatchWorker --> WebhookDispatcher
    ReportGenSvc --> Storage

    %% Repositories to Databases
    UserRepo <--> Postgres
    ReviewRepo <--> Postgres
    ReportRepo <--> Postgres
    AuditRepo <--> Postgres

    %% Caching
    Routers <-->|Cache Hit / Miss| RedisPool
    SlowAPI <-->|Sliding Window Rate Check| RedisPool
```

---

## 2. Request Lifecycle

Every HTTP transaction flows through strict authentication, rate-limiting, audit-tracking, and error-handling filters before reaching domain controllers.

```mermaid
sequenceDiagram
    autonumber
    actor Client as Client / Dev
    participant Nginx as Nginx Proxy
    participant Mid as Middleware Stack
    participant Router as API Router
    participant Auth as Auth / API Key Guard
    participant Svc as Domain Service
    participant Cache as Redis Cache
    participant DB as PostgreSQL DB
    participant AI as Gemini 2.5 Flash

    Client->>Nginx: HTTP Request (e.g. POST /review/text)
    Nginx->>Nginx: Check Payload Size & Rate Limit Buffer
    Nginx->>Mid: Forward Request (Headers: X-Forwarded-For, X-Real-IP)
    
    Mid->>Mid: Inject Correlation ID (X-Request-ID)
    Mid->>Cache: Evaluate SlowAPI Rate Limit
    alt Rate Limit Exceeded
        Mid-->>Client: 429 Too Many Requests (Retry-After header)
    end

    Mid->>Router: Route Request
    Router->>Auth: Validate JWT Bearer or X-API-Key
    alt Invalid Credentials
        Auth-->>Client: 401 Unauthorized
    end

    Router->>Cache: Check Cached Review Hash
    alt Cache Hit
        Cache-->>Router: Return Cached Review JSON
        Router-->>Client: 200 OK (X-Cache: HIT)
    else Cache Miss
        Router->>Svc: Execute Hybrid Analysis
        Svc->>Svc: Run AST Syntax & Radon Complexity Checks
        Svc->>AI: Send Prompt with AST Context to Gemini API
        AI-->>Svc: Structured Suggestions & Quality Scores
        Svc->>DB: Persist Review Record & Findings
        Svc->>Cache: Set Cached Review (TTL 1 hour)
        Svc-->>Router: Analysis Result
        Router-->>Client: 200 OK (X-Cache: MISS)
    end

    Mid->>DB: Log Audit Event Asynchronously
```

---

## 3. Authentication & Authorization Flow

CodePilot AI supports dual authentication schemes: **JWT (JSON Web Tokens)** for interactive web users and **HMAC Hashed API Keys** for CI/CD pipelines and programmatic agents.

```mermaid
flowchart TD
    subgraph AuthInput["Credentials Provided"]
        JWTHeader["Authorization: Bearer <access_token>"]
        APIKeyHeader["X-API-Key: cp_live_..."]
        LoginReq["POST /auth/login (email + password)"]
    end

    subgraph AuthEngine["Security Engine (app/core/security.py)"]
        VerifyPassword["Verify bcrypt password hash"]
        GenTokens["Generate JWT Access (15m) & Refresh (7d) Tokens"]
        DecodeJWT["Decode & Verify JWT Signature (HS256)"]
        CheckBlacklist["Check Redis Token Blacklist"]
        HashKey["Hash Incoming API Key (SHA-256)"]
        LookupKey["Lookup Key in database (is_active=True)"]
    end

    subgraph ScopeGuard["Permission & Role Evaluation"]
        UserRole{"User Role"}
        KeyScope{"API Key Scope"}
    end

    subgraph AccessResult["Access Outcome"]
        AllowAdmin["Grant Admin Access"]
        AllowUser["Grant Standard User Access"]
        AllowReadOnly["Grant Read-Only Access"]
        DenyAuth["401 Unauthorized / 403 Forbidden"]
    end

    %% Login Path
    LoginReq --> VerifyPassword
    VerifyPassword -->|Valid| GenTokens
    VerifyPassword -->|Invalid| DenyAuth
    GenTokens --> TokenResponse["Return {access_token, refresh_token}"]

    %% JWT Path
    JWTHeader --> DecodeJWT
    DecodeJWT -->|Signature Valid| CheckBlacklist
    DecodeJWT -->|Expired / Invalid| DenyAuth
    CheckBlacklist -->|Not Blacklisted| UserRole
    CheckBlacklist -->|Revoked in Redis| DenyAuth

    %% API Key Path
    APIKeyHeader --> HashKey
    HashKey --> LookupKey
    LookupKey -->|Found & Active| KeyScope
    LookupKey -->|Not Found / Revoked| DenyAuth

    %% Role Resolution
    UserRole -->|admin| AllowAdmin
    UserRole -->|user| AllowUser
    KeyScope -->|full_access| AllowUser
    KeyScope -->|read_only| AllowReadOnly
```

---

## 4. AI Review Engine Pipeline

The AI analysis pipeline utilizes a multi-phase approach: deterministic Python Abstract Syntax Tree (AST) inspection evaluates mechanical correctness and complexity first, after which context-rich prompts feed the LLM to deliver architectural critique.

```mermaid
flowchart LR
    subgraph Input["Code Ingestion"]
        SourceCode["Raw Python Source Code"]
    end

    subgraph Phase1["Stage 1: Deterministic Static Analysis"]
        ASTParser["Python ast.parse()\n• Syntax Validation\n• Function/Class Extraction"]
        RadonEngine["Radon Metrics\n• Cyclomatic Complexity (CC)\n• Maintainability Index (MI)\n• Raw Halstead Metrics"]
        BanditScan["Security AST Rules\n• Hardcoded Secrets\n• Insecure Deserialization\n• SQL Injection Risks"]
        PEP8Checker["Style & Conformance\n• Line Length & Docstrings\n• Naming Conventions"]
    end

    subgraph Phase2["Stage 2: Contextual Prompt Assembly"]
        PromptBuilder["Prompt Template Engine (Jinja2)\n• Injects Code AST Summary\n• Injects Cyclomatic Metrics\n• Sets Strict Output JSON Schema"]
    end

    subgraph Phase3["Stage 3: LLM Reasoning"]
        GeminiModel["Google Gemini 2.5 Flash\n• Architectural Review\n• Anti-Pattern Detection\n• Concrete Refactoring Fixes"]
    end

    subgraph Phase4["Stage 4: Normalization & Quality Scoring"]
        Parser["Response Validator & Normalizer\n• JSON Extraction Guard\n• Schema Conformance Check"]
        Scorer["Composite Score Engine\nScore = 0.4(Quality) + 0.3(Security) +\n0.2(Complexity) + 0.1(Style)"]
    end

    subgraph Output["Review Deliverable"]
        ReviewResult["Standardized Review Object\n• Overall Score (0-100) & Grade (A-F)\n• Issues List with Line Numbers\n• Automated Code Diffs & Fixes"]
    end

    SourceCode --> ASTParser
    ASTParser --> RadonEngine
    ASTParser --> BanditScan
    ASTParser --> PEP8Checker

    RadonEngine --> PromptBuilder
    BanditScan --> PromptBuilder
    PEP8Checker --> PromptBuilder
    SourceCode --> PromptBuilder

    PromptBuilder --> GeminiModel
    GeminiModel --> Parser
    Parser --> Scorer
    Scorer --> ReviewResult
```

---

## 5. Upload & Batch Analysis Processing Flow

```mermaid
sequenceDiagram
    autonumber
    actor User as Developer / CI Runner
    participant Nginx as Nginx Edge
    participant API as Upload API (/upload)
    participant Sec as Path & ZIP Inspector
    participant Storage as Local Storage
    participant Batch as Batch Job Processor
    participant Engine as Review Engine
    participant DB as PostgreSQL DB
    participant Webhook as Webhook Dispatcher

    User->>Nginx: POST /upload/archive (ZIP / TAR file)
    Nginx->>API: Stream archive (Max 50MB)
    API->>Sec: Validate File Extension & MIME Type
    API->>Storage: Save archive to /app/uploads/raw/
    API->>Sec: Extract Archive with ZipSlip Defense
    Sec->>Sec: Filter out .git, __pycache__, binaries, >1MB files
    Sec->>Storage: Store valid source files to /app/uploads/extracted/{job_id}/
    API->>DB: Create BatchJob Record (status='queued', total_files=N)
    API-->>User: 202 Accepted {job_id, status: "queued", total_files: N}

    Note over Batch,Engine: Background Task Processing
    Batch->>DB: Update BatchJob (status='processing')
    loop For each file in extracted folder
        Batch->>Engine: Run AST + Gemini Review
        Engine-->>Batch: Single File Review Result
        Batch->>DB: Save individual Review entity & update processed_count
    end
    Batch->>DB: Compute Aggregated Batch Quality Score (status='completed')
    
    opt If Webhook URL registered
        Batch->>Webhook: Sign payload with HMAC-SHA256
        Webhook->>User: POST Webhook Notification {job_id, status, scores}
    end
```

---

## 6. Database Entity-Relationship Model

```mermaid
erDiagram
    USERS ||--o{ API_KEYS : owns
    USERS ||--o{ PROJECTS : manages
    USERS ||--o{ REVIEWS : initiates
    USERS ||--o{ REPORTS : generates
    USERS ||--o{ AUDIT_LOGS : triggers
    USERS ||--o{ WEBHOOKS : configures

    PROJECTS ||--o{ REVIEWS : contains
    PROJECTS ||--o{ BATCH_JOBS : executes
    
    BATCH_JOBS ||--o{ REVIEWS : produces
    REVIEWS ||--o{ REVIEW_ISSUES : details
    REVIEWS ||--o{ REPORTS : documented_in

    USERS {
        uuid id PK
        string email UK
        string hashed_password
        string full_name
        string role
        boolean is_active
        timestamp created_at
        timestamp updated_at
    }

    API_KEYS {
        uuid id PK
        uuid user_id FK
        string key_hash UK
        string key_prefix
        string name
        string scope
        boolean is_active
        timestamp expires_at
        timestamp created_at
    }

    PROJECTS {
        uuid id PK
        uuid user_id FK
        string name
        string description
        string repository_url
        string default_branch
        timestamp created_at
    }

    BATCH_JOBS {
        uuid id PK
        uuid project_id FK
        uuid user_id FK
        string status
        int total_files
        int processed_files
        float average_score
        timestamp created_at
        timestamp completed_at
    }

    REVIEWS {
        uuid id PK
        uuid user_id FK
        uuid project_id FK
        uuid batch_job_id FK
        string filename
        text source_code
        float overall_score
        string letter_grade
        float cyclomatic_complexity
        float maintainability_index
        jsonb raw_metrics
        text ai_summary
        string status
        timestamp created_at
    }

    REVIEW_ISSUES {
        uuid id PK
        uuid review_id FK
        string rule_id
        string category
        string severity
        int line_number
        text message
        text suggested_fix
    }

    REPORTS {
        uuid id PK
        uuid review_id FK
        uuid user_id FK
        string report_type
        string file_path
        timestamp generated_at
    }

    WEBHOOKS {
        uuid id PK
        uuid user_id FK
        string target_url
        string secret_token
        string event_types
        boolean is_active
        timestamp created_at
    }

    AUDIT_LOGS {
        uuid id PK
        uuid user_id FK
        string action
        string resource_type
        string resource_id
        string ip_address
        string user_agent
        timestamp timestamp
    }
```

---

## 7. Background Task Execution Architecture

CodePilot AI utilizes asynchronous non-blocking background task workers managed through FastAPI's `BackgroundTasks` orchestration and Redis tracking.

```mermaid
flowchart TD
    ClientReq["Client POST Request\n(e.g., /upload/archive or /review/batch)"]
    FastAPIEndpoint["FastAPI Router Endpoint"]
    ScheduleTask["BackgroundTasks.add_task(worker_fn)"]
    ReturnAccepted["HTTP 202 Accepted Response\n(Immediate return with tracking task_id)"]
    
    subgraph BackgroundExecution["Background Worker Pool"]
        WorkerInit["Worker Dequeues Task"]
        StateUpdate1["Update DB / Redis: status = 'running'"]
        ProcessChunks["Chunked Analysis Execution\n(Process N files concurrently)"]
        StateUpdate2["Update DB / Redis: status = 'completed'"]
        TriggerWebhook["Notify Webhook Receivers (HMAC Signed)"]
        CleanupArtifacts["Purge Temporary Staging Files"]
    end

    ClientReq --> FastAPIEndpoint
    FastAPIEndpoint --> ScheduleTask
    FastAPIEndpoint --> ReturnAccepted
    ScheduleTask -.->|Async Fire & Forget| WorkerInit
    WorkerInit --> StateUpdate1
    StateUpdate1 --> ProcessChunks
    ProcessChunks --> StateUpdate2
    StateUpdate2 --> TriggerWebhook
    TriggerWebhook --> CleanupArtifacts
```

---

## 8. Caching Strategy & Invalidation Flow

CodePilot AI uses Redis 7 as an intelligent multi-layer cache:

1. **Deterministic Review Cache**: Python source codes are normalized and hashed via SHA-256. If identical code is reviewed again with identical parameters, results are returned in <2ms.
2. **Dashboard & Analytics Cache**: Complex aggregate SQL queries across thousands of historical reviews are cached for 5 minutes.
3. **Session & Rate-Limit Tracking**: Token bucket sliding windows prevent API abuse.

```mermaid
flowchart TD
    StartCheck["Incoming Request (GET /review/{id} or POST /review/text)"]
    ComputeKey["Calculate Cache Key\n(Key: review:{sha256_hash} or analytics:{user_id})"]
    QueryRedis["Query Redis Cache Engine"]
    
    HitCheck{"Cache Key Exists?"}
    ReturnCached["Retrieve Deserialized JSON from Redis\nInject X-Cache: HIT Header\nReturn Response (<2ms)"]
    
    ExecuteQuery["Execute AST Pipeline / Query PostgreSQL Database"]
    StoreRedis["Serialize Output to JSON\nSet Redis Key with TTL (e.g. 3600s)\nInject X-Cache: MISS Header"]
    ReturnFresh["Return Newly Computed Result"]

    StartCheck --> ComputeKey
    ComputeKey --> QueryRedis
    QueryRedis --> HitCheck
    HitCheck -->|Yes (HIT)| ReturnCached
    HitCheck -->|No (MISS)| ExecuteQuery
    ExecuteQuery --> StoreRedis
    StoreRedis --> ReturnFresh
```

---

## 9. Observability, Monitoring & Audit Flow

```mermaid
flowchart LR
    subgraph Probes["Diagnostic Probes"]
        LivenessProbe["K8s / Docker Liveness\nGET /health"]
        ReadinessProbe["K8s Readiness\nGET /monitoring/health"]
        SysMetrics["System Resources\nGET /monitoring/system"]
    end

    subgraph Collector["System Monitor Engine (app/core/monitoring.py)"]
        DBProbe["Postgres pg_isready & SELECT 1"]
        RedisProbe["Redis PING & memory check"]
        DiskProbe["Disk Storage utilization"]
        GeminiProbe["AI Provider API probe"]
    end

    subgraph AuditCollector["Audit Logger (app/core/audit.py)"]
        ReqFilter["Capture User, IP, Endpoint, Timestamp"]
        AsyncWriter["Async DB AuditLog Batch Writer"]
    end

    subgraph ObservabilityOut["Monitoring Dashboards"]
        Prometheus["Prometheus / Grafana"]
        AdminAudit["Admin Audit Explorer\nGET /audit-logs"]
    end

    LivenessProbe --> Collector
    ReadinessProbe --> Collector
    SysMetrics --> Collector

    Collector --> DBProbe
    Collector --> RedisProbe
    Collector --> DiskProbe
    Collector --> GeminiProbe

    ReqFilter --> AsyncWriter
    AsyncWriter --> AdminAudit
    Collector -.-> Prometheus
```

---

*Document Version: 1.0.0 — Phase 14 Complete Architecture Specification.*
