# I Used Hindsight to Extend Instead of Rewrite

*How I stopped rebuilding my FastAPI architecture every time I added a feature—and started evolving it instead.*

---

I thought adding one more feature to my code review platform would take an afternoon.

Instead, I ended up with two review services doing the same job, duplicate response schemas, routers that drifted apart, and AI logic leaking into parts of the application where it never belonged.

The code still worked. That was the dangerous part.

The problem wasn't bugs—it was **architecture drift**. Every new feature had slightly less context than the previous one. Small inconsistencies accumulated until the application became harder to extend than to build.

I eventually changed my workflow around one idea: **extend the existing architecture instead of rewriting it.** Hindsight became the mechanism that forced every implementation to understand the project before changing it.

This article is about that decision, the architecture behind **CodePilot AI**, and why context continuity mattered more than adding another framework or another AI model.

---

## The system I was actually trying to build

CodePilot AI isn't a chatbot that reviews Python code. It's a full-stack code review platform built around a strict separation of responsibilities.

**Static analysis finds problems. AI explains them.**

That distinction shaped the entire architecture.

The stack combines:

- **Next.js 15 + React 19** for the frontend.
- **FastAPI** for API orchestration.
- **Python AST analysis** for deterministic code inspection.
- **Google Gemini** for explanations, documentation, and refactoring suggestions.
- **PostgreSQL** for persistence.
- **Redis** for caching and analytics.
- **Docker + GitHub Actions** for deployment and CI/CD.

The frontend feels like an IDE. The backend behaves like a compiler pipeline with an AI explanation layer attached to it.

---

## Where Hindsight Sits in the Stack

> Insert architecture diagram here as `assets/hindsight-architecture.png`.

The architecture places **Hindsight** between the FastAPI orchestration layer and the implementation layers. Before generating code, it inspects the repository so new features extend existing routers, services, schemas, repositories, and AI modules instead of creating duplicate implementations.

### Architecture Flow

```text
Next.js Frontend (Monaco Editor)
            │
            ▼
      FastAPI API Layer
            │
            ▼
     Hindsight Context Layer
            │
   ┌────────┴─────────┐
   ▼                  ▼
Static AST Engine   Gemini Provider
   │                  │
   └────────┬─────────┘
            ▼
 PostgreSQL + Redis Cache
            ▼
 History • Analytics • Reports
```

---

## Interactive Code Review

> Insert screenshot: `assets/dashboard-review-editor.png`

The review experience starts inside a Monaco-powered editor where deterministic AST scans run independently from Gemini-powered explanations.

---

## The rewrite trap

The first version of the review service looked like this:

```python
class ReviewService:
    async def review(self, source_code: str):
        return analyzer.analyze(source_code)
```

Then AI summaries were added through a second service:

```python
class AIReviewService:
    async def review(self, source_code: str):
        report = analyzer.analyze(source_code)
        summary = gemini.review(report)
        return merge(report, summary)
```

Both services slowly became orchestration layers.

That duplication spread into routers, schemas, persistence logic, and exports.

---

## I stopped asking for code. I started asking for context.

Every implementation phase began with a single instruction:

> Inspect the existing project before making changes.

Instead of creating another review pipeline, Hindsight extended the existing architecture.

```python
class ReviewService:
    async def review(self, source_code: str):
        static_report = analyzer.analyze(source_code)
        ai_summary = await ai_provider.review(static_report)
        return merge(static_report, ai_summary)
```

The API contract stayed stable while new capabilities kept growing.

---

## Static Analysis Became the Source of Truth

> Insert screenshot: `assets/review-metrics.png`

Every review generates deterministic metrics:

- Overall Quality Score
- Security Score
- Maintainability Index
- Complexity Score
- Readability Score
- Documentation Score

The analyzer produces structured findings before any language model is involved.

Example output:

```json
{
  "complexity_score": 88,
  "security": [
    {
      "rule": "SEC-002",
      "severity": "HIGH",
      "line": 10,
      "issue": "Insecure os.system() usage"
    }
  ]
}
```

AI consumes this structured report instead of raw source code.

---

## AI Became an Explanation Layer

> Insert screenshot: `assets/gemini-insights.png`

Gemini receives verified findings and produces:

- Executive summaries.
- Code strengths.
- Actionable improvements.
- Refactoring suggestions.
- Documentation improvements.
- Unit test generation.

The static analyzer detects issues.

Gemini explains them.

---

## Provider Abstraction Mattered More Than Provider Choice

The backend depends on an abstract provider interface.

```python
class BaseProvider(ABC):

    async def review(self, report):
        ...

    async def generate_tests(self, report):
        ...
```

Gemini is one implementation.

The application architecture does not depend on Gemini itself.

---

## Documentation Became Its Own Pipeline

Instead of generating documentation inside review logic, dedicated generators were introduced:

```text
ai/
├── documentation_generator.py
├── readme_generator.py
├── unittest_generator.py
├── refactor_generator.py
└── architecture_generator.py
```

Every generator consumes review context and produces one artifact.

---

## Security Findings Became Interactive

> Insert screenshot: `assets/remediation-diff.png`

Rather than only reporting vulnerabilities, CodePilot AI generates hardened code diffs.

Example:

```python
# Original
os.system(f"echo User {username}")
```

becomes

```python
subprocess.run(
    ["logger", f"User {username} authenticated"],
    check=True
)
```

The review becomes actionable instead of descriptive.

---

## Batch Project Analysis Changed the Architecture

ZIP uploads follow a pipeline:

```text
ZIP Upload
   │
Extract Files
   │
Ignore venv/cache/build
   │
Queue Python Files
   │
AST Analysis
   │
Aggregate Metrics
```

Project-wide metrics include language distribution, complexity averages, security hotspots, duplicate imports, documentation coverage, and maintainability trends.

---

## Review History Became an Analytics Problem

> Insert screenshot: `assets/review-history.png`

Reviews are persisted with metadata for filtering, comparisons, exports, favorites, and analytics dashboards.

Versioned reviews became much more valuable than replacing previous results.

---

## Redis Solved Consistency Before Speed

Redis caches dashboard aggregates and analytics responses.

The harder problem wasn't caching—it was invalidation.

Creating or updating reviews invalidates dashboard and history summaries while keeping analytics deterministic.

---

## Background Tasks Changed Upload Behavior

Uploads now move through explicit states:

```text
Pending → Running → Completed / Failed
```

The frontend polls task status instead of blocking on long-running requests.

---

## Why AI Never Writes to the Database

Responsibilities remain separate.

| Layer | Responsibility |
|-------|----------------|
| AI Provider | Generate explanations and artifacts. |
| Service Layer | Merge deterministic and AI outputs. |
| Repository Layer | Persist reviews and metadata. |

This boundary keeps documentation generation, exports, and future providers modular.

---

## What Hindsight Actually Solved

Hindsight isn't runtime memory.

It's **architecture continuity**.

Before implementing a feature, it inspects the repository and extends existing services instead of creating new parallel implementations.

That prevented duplicate routers, conflicting schemas, and repeated business logic as the project grew.

Useful resources:

- Hindsight GitHub: https://github.com/vectorize-io/hindsight
- Hindsight Documentation: https://hindsight.vectorize.io/
- Vectorize Agent Memory: https://vectorize.io/what-is-agent-memory

---

## The Review Request Lifecycle

```text
POST /review/code
      │
JWT Authentication
      │
Review Service
      │
AST Analyzer
      │
Gemini Provider
      │
Persist Review
      │
Redis Cache + Analytics
      │
Response
```

Everything downstream—history, analytics, documentation, exports—reuses persisted review artifacts.

---

## Lessons I’ll Reuse

### 1. Deterministic systems should feed language models.

Static analysis is responsible for facts.

AI is responsible for explanations.

### 2. Provider abstractions age better than provider-specific services.

Changing providers should not change API contracts.

### 3. Cache invalidation belongs in services.

Repositories store data.

Services understand business events.

### 4. Version review artifacts instead of replacing them.

Historical reviews become analytics almost immediately.

### 5. Extending architecture is cheaper than rewriting architecture.

Hindsight didn't magically generate better code.

It forced every new implementation to understand the existing architecture before modifying it, reducing duplicate services, conflicting schemas, and architectural drift.

That became the biggest lesson from building CodePilot AI.
