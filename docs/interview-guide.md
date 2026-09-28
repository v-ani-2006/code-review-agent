# CodePilot AI — Technical Interview Preparation Guide

This guide is designed for technical screening calls, system design interviews, and deep-dive technical rounds. It equips you with precise talking points, architectural rationales, and concise answers to challenging interviewer questions.

---

## 1. The 2-Minute Project Pitch

> *"CodePilot AI is an asynchronous code review and developer enablement platform built with FastAPI, PostgreSQL 16, Redis 7, and Google Gemini 2.5 Flash.
>
> The problem it solves is that traditional linters are too rigid and cannot explain high-level architectural flaws, while purely LLM-based tools hallucinate line numbers and waste massive amounts of tokens on basic mechanical checks like cyclomatic complexity and indentation.
>
> To solve this, I designed a hybrid analysis architecture:
> When code is submitted, our static engine compiles it into an Abstract Syntax Tree using Python's `ast` module, calculates exact cyclomatic complexity via Radon, and executes 25+ AST security rules adapted from Bandit—all in less than 2 milliseconds.
>
> Next, these structured findings are assembled into a Jinja2 prompt context and dispatched to Google Gemini 2.5 Flash, which focuses exclusively on architectural review, security remediation, and generating pytest suites.
>
> The entire backend is built with clean architecture—separating routers, domain services, and repositories—backed by PostgreSQL asyncpg pools, Redis LRU caching, SlowAPI rate limiting, and automated multi-stage Docker deployment with an 85%+ test coverage GitHub Actions CI/CD pipeline."*

---

## 2. The 5-Minute Technical Deep Dive

### Step 1: The Problem & Motivation (1 minute)
* "In enterprise CI/CD workflows, human code review is one of the biggest productivity bottlenecks. However, existing automated tools fall into two flawed extremes:
  1. Static Linters (Flake8, Pylint, SonarQube): Fast, but cannot understand business context, recommend architectural refactoring, or generate unit tests.
  2. Pure Generative AI bots: Powerful, but prone to hallucinations on complexity numbers, unreliable with exact line indexing, and costly in token consumption.
* CodePilot AI bridges this gap with a deterministic-first, AI-augmented pipeline."

### Step 2: System Architecture & Ingestion (1.5 minutes)
* "At the edge, Nginx acts as a reverse proxy, handling TLS termination, client body limit clamping (50MB for archives, 1MB for single files), and Gzip compression.
* The application runs on FastAPI under Gunicorn with Uvicorn worker processes.
* Authentication supports both JWT (for web users) and SHA-256 hashed API keys (for CI/CD runners).
* When a user uploads an archive, we extract it with strict path sanitization to defeat ZipSlip attacks, schedule an asynchronous batch background task, and return an immediate HTTP 202 Accepted with a task tracking ID."

### Step 3: Hybrid AI Pipeline (1.5 minutes)
* "The core engine parses the code into an in-memory Abstract Syntax Tree.
* We compute cyclomatic complexity, Halstead metrics, and a maintainability index from 0 to 100.
* Our security engine checks AST nodes for hardcoded secrets, `eval`/`exec`, unparameterized SQL queries, and unsafe deserialization.
* We aggregate these deterministic findings and supply them to Google Gemini 2.5 Flash with a temperature of 0.2. This produces structured JSON containing an executive summary, strengths, recommendations, bugfix patches, docstrings, and complete pytest test suites.
* If Gemini is unreachable or rate-limited, our fallback engine automatically constructs a complete report from the AST metrics alone, guaranteeing zero 500 errors."

### Step 4: Caching, Persistence & DevOps (1 minute)
* "We use PostgreSQL 16 managed by Alembic migrations for relational integrity, UUIDv4 keys, and cascading relationships.
* Redis 7 provides sub-2ms caching by indexing reviews by the SHA-256 hash of the normalized source code.
* The DevOps pipeline includes multi-stage Docker builds with non-root security and 7 GitHub Actions workflows running automated tests, Ruff linting, MyPy type checks, Bandit security scans, and auto-releases."

---

## 3. System Design Breakdown

### Component Topology
* **Edge Proxy**: Nginx (reverse proxy, rate-limit buffer, security headers)
* **Application Layer**: FastAPI (stateless, horizontally scalable)
* **Caching & Rate Limiting**: Redis 7 (in-memory LRU, sliding-window token bucket)
* **Relational Persistence**: PostgreSQL 16 (asyncpg driver, SQLAlchemy 2.0 AsyncSession)
* **Task Execution**: FastAPI `BackgroundTasks` with Redis job progress tracking
* **External Services**: Google Gemini API via asynchronous HTTP client

---

## 4. Top 12 Technical Interview Questions & Answers

### Q1: Why did you use AST parsing instead of letting the LLM do all the analysis?
**Answer**:
> *"Three reasons: Determinism, Speed, and Cost.
> 1. An LLM cannot reliably compute mathematical metrics like McCabe's Cyclomatic Complexity or exact character/line counts; it will often guess.
> 2. AST parsing takes under 2 milliseconds on a typical Python file, providing instant feedback.
> 3. By filtering out basic mechanical and syntactical bugs upfront, we send a much smaller, higher-value context to the LLM, reducing inference token costs by approximately 40%."*

### Q2: How do you prevent users from executing malicious code on your server?
**Answer**:
> *"We enforce a strict Zero Execution policy. The uploaded code is never executed via `exec()`, `eval()`, or imported as a module. It is parsed purely into an Abstract Syntax Tree data structure using Python's standard `ast.parse()`. Furthermore, all archive extractions validate that destination paths do not escape the designated sandboxed directory, preventing ZipSlip attacks."*

### Q3: How do you handle database concurrency and avoid connection exhaustion?
**Answer**:
> *"We use SQLAlchemy's AsyncSession backed by the `asyncpg` driver with an explicit connection pool (default pool size of 20, max overflow of 10). Connections are acquired per request using FastAPI's dependency injection (`get_db`) and closed immediately in a context manager, preventing connection leakage."*

### Q4: How does your Redis caching strategy handle cache invalidation?
**Answer**:
> *"For static code reviews, code is pure: the same source code string always produces the same deterministic AST analysis. We hash the normalized source code with SHA-256 to create the cache key (`review:<sha256>`) with a 1-hour TTL.
> For user dashboards and analytics, keys are scoped by user ID (`dashboard:<user_id>`) and invalidated whenever a new review is saved or deleted."*

### Q5: What happens if the Gemini AI API goes down or hits rate limits?
**Answer**:
> *"We built an automated fallback mechanism in `app/ai/providers/gemini_provider.py`. If Gemini returns an HTTP 429 quota exhaustion or network timeout, the application catches the exception, logs a warning, and assembles the review deliverable using the deterministic AST metrics, assigning an overall score and letter grade based on the static rules. The API returns HTTP 200 with a warning header indicating degraded mode."*

### Q6: Why did you choose UUIDv4 over autoincrementing integer IDs?
**Answer**:
> *"Autoincrementing integer IDs are vulnerable to enumeration attacks: an attacker can increment the ID in `/reports/1`, `/reports/2` to scrape all data in the system. UUIDv4 provides 128 bits of cryptographic randomness, making ID guessing statistically impossible. It also simplifies distributed database sharding and batch generation without sequence collisions."*

### Q7: How does your rate limiting work across multiple container instances?
**Answer**:
> *"We use SlowAPI backed by Redis. Instead of storing request counters in memory on a single machine, counters are maintained in Redis using a sliding window token bucket algorithm. When multiple backend containers run behind Nginx, all instances query the same Redis instance, ensuring global rate-limiting consistency."*

### Q8: How do you secure webhooks against forgery and replay attacks?
**Answer**:
> *"Each outbound webhook payload is signed with HMAC-SHA256 using a shared secret generated when the user registers the webhook. The signature is sent in the `X-CodePilot-Signature` header alongside a UTC timestamp in `X-CodePilot-Timestamp`. The receiving server validates the signature and verifies that the timestamp is within a 5-minute tolerance window to prevent replay attacks."*

### Q9: What is the difference between cyclomatic complexity and maintainability index?
**Answer**:
> *"Cyclomatic complexity measures the number of independent execution paths through a piece of code (decision points like `if`, `while`, `for`, `except`).
> Maintainability index is a composite formula (from 0 to 100) combining cyclomatic complexity, Halstead volume (measuring the number of operators and operands), and physical lines of code. It gives a holistic health score of how easy code is to maintain and modify."*

### Q10: How do you protect against SQL injection?
**Answer**:
> *"We use SQLAlchemy 2.0 ORM and SQLAlchemy select constructs exclusively, which compile into parameterized queries with bind variables in asyncpg. No dynamic raw SQL string interpolation is ever used in the application."*

### Q11: Why did you use Gunicorn with Uvicorn workers in Docker instead of running Uvicorn directly?
**Answer**:
> *"Running Uvicorn directly is suitable for development, but in production, Gunicorn serves as a robust process master. It monitors worker processes, automatically restarts crashed workers, handles graceful zero-downtime reloads, and distributes incoming requests across multiple CPU cores via pre-forked worker pools."*

### Q12: How do you test code that depends on Gemini AI without incurring costs?
**Answer**:
> *"We created `MockGeminiClient` in `tests/mocks/gemini_mock.py`. The pytest fixture overrides the AI provider dependency, returning deterministic, schema-compliant JSON payloads instantly. This guarantees our CI/CD pipeline runs fast, free of charge, and deterministically without external network flakiness."*

---

*Document Version: 1.0.0 — Technical Interview Preparation Guide.*
