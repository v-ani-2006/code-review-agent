# CodePilot AI — Technical Portfolio & Project Showcase

## 1. Project Elevator Pitch (30 Seconds)

**CodePilot AI** is an enterprise-grade, asynchronous code analysis and AI review platform built with **FastAPI**, **PostgreSQL**, **Redis**, and **Google Gemini 2.5 Flash**. It bridges the gap between deterministic static analysis (AST parsing, cyclomatic complexity, Bandit security heuristics) and modern Generative AI reasoning.

By pre-processing code through an in-memory Abstract Syntax Tree before prompting the LLM, CodePilot AI eliminates AI hallucinations on syntactic metrics, slashes inference token costs by 40%, and provides sub-millisecond cached review reports alongside deep, context-aware architectural feedback and automated remediation diffs.

---

## 2. Resume & Professional Profile Description

### Short Bullet Points (Targeted for Software Engineer / Backend Engineer):
* **Architected CodePilot AI**, a distributed code review orchestration engine in **FastAPI** and **Python 3.13**, analyzing multi-file codebases in <5ms for static AST passes and under 1s for deep LLM reasoning.
* **Engineered a hybrid analysis pipeline** coupling deterministic AST parsing (Radon complexity, Bandit security patterns, PEP 8) with **Google Gemini 2.5 Flash**, automating bug fixes, test generation, and documentation.
* **Designed an asynchronous persistence & cache tier** utilizing **PostgreSQL 16** with SQLAlchemy 2.0 AsyncIO, **Redis 7** for LRU query caching and token-bucket rate limiting (SlowAPI), and **Alembic** migrations.
* **Hardened microservices infrastructure** with Docker multi-stage non-root containers, **Nginx** reverse proxy (TLS, rate-limiting, Gzip), and an end-to-end **GitHub Actions CI/CD** pipeline achieving >85% test coverage.

---

## 3. High-Impact Technical Narrative (Interview Explanation)

> *"When building CodePilot AI, I wanted to solve a major problem with purely LLM-based code review bots: **hallucinations and token waste**. If you ask an LLM 'What is the cyclomatic complexity or exact line length?', it will often guess or consume thousands of tokens on mechanical tasks.*
>
> *I designed a two-stage hybrid architecture: The first stage parses the code into an Abstract Syntax Tree in memory, calculating exact cyclomatic complexity, Halstead maintainability, and scanning for 25+ AST security vulnerability signatures deterministically.
>
> In the second stage, these structured metrics are assembled into a Jinja2 prompt context and dispatched to Google Gemini 2.5 Flash. The LLM focuses purely on what it excels at: architectural design patterns, logic edge cases, idiomatic refactoring, and generating pytest suites.
>
> The result is a robust backend with dual JWT/API-key authentication, Redis caching, async batch uploads, HMAC-signed webhooks, and full Docker containerization."*

---

## 4. Key Architectural Decisions & Trade-Offs

| Decision | Alternative Considered | Why CodePilot AI Chose This Path |
| :--- | :--- | :--- |
| **FastAPI + AsyncIO** | Django / Flask | High-throughput asynchronous I/O natively suited for concurrent LLM streaming, Redis cache lookups, and asyncpg database pools. |
| **Hybrid AST + Gemini** | Pure LLM Review | Deterministic AST calculations eliminate hallucinations on line numbers, complexity metrics, and known CVE signatures while reducing token spend. |
| **PostgreSQL 16 + Asyncpg** | MongoDB / NoSQL | Relational integrity for user ownership, role hierarchies, foreign key cascading, and ACID guarantees for audit logs and batch jobs. |
| **Redis 7 LRU Cache** | Local In-Memory Cache | Distributed cache shared across multiple Gunicorn worker processes and scalable across horizontal container replicas. |
| **Nginx Reverse Proxy** | Exposing Uvicorn Directly | Offloads TLS termination, gzip compression, request buffering, and static file delivery away from application Python workers. |

---

## 5. Complex Engineering Challenges Solved

### Challenge 1: Preventing ZipSlip and Malicious Code Ingestion
* **Problem**: Ingesting user archives (.zip, .tar.gz) can allow attackers to overwrite system files via directory traversal paths (`../../etc/passwd`).
* **Solution**: Implemented strict canonical path resolution in `app/uploads/` verifying that extracted file destinations stay within the designated temporary sandboxed directory. Furthermore, files are parsed strictly as AST data trees—never executed via `exec` or `eval`.

### Challenge 2: Eliminating LLM Rate Limit & Quota Outages
* **Problem**: External AI providers can experience rate limiting (HTTP 429) or transient outages, which could fail user review requests.
* **Solution**: Implemented a multi-tier fallback mechanism. When Gemini is unavailable, the pipeline falls back to deterministic AST rule evaluation, producing a full quality report and letter grade with an explicit degraded warning rather than crashing.

### Challenge 3: Orchestrating Zero-Downtime Docker Health Checks
* **Problem**: Backend containers on Windows/WSL2 cold starts required up to 40 seconds to wait for PostgreSQL, apply Alembic migrations, and boot Gunicorn workers, causing premature container restarts.
* **Solution**: Engineered a robust container health probe with a 60-second start period, 10-second interval, and direct loopback IP probing, ensuring smooth container readiness without flapping.

---

## 6. Scalability & Production Readiness

1. **Horizontal Backend Scaling**: The FastAPI application is completely stateless. Session state and rate limits reside in Redis, and relational data resides in PostgreSQL, allowing the backend to scale horizontally behind an Nginx or AWS ALB load balancer.
2. **Database Connection Pooling**: Utilizes SQLAlchemy AsyncSession with an asyncpg pool (default pool size: 20, max overflow: 10) to efficiently handle thousands of concurrent queries without database connection exhaustion.
3. **Optimized Caching**: Identical source code strings are hashed via SHA-256; subsequent requests for the same code hash are served directly from Redis in <2ms without querying PostgreSQL or invoking Gemini.

---

## 7. Future Enhancements Roadmap

* **Tree-Sitter Polyglot Expansion**: Extend AST parsing to TypeScript, Go, Rust, and Java using Tree-Sitter grammar engines.
* **IDE Extensions**: Direct integration with VS Code and JetBrains IDEs for real-time in-editor code reviews.
* **Local LLM Support (Ollama / vLLM)**: Enable on-premises air-gapped deployments using local DeepSeek-Coder or Llama-3 models.

---

*Document Version: 1.0.0 — Portfolio & Project Showcase.*
