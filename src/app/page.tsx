import Link from "next/link";
import {
  ArrowRight,
  Award,
  Bot,
  CheckCircle2,
  Code2,
  Cpu,
  FileCode,
  Github,
  Layers,
  Lock,
  Play,
  ShieldCheck,
  Sparkles,
  Terminal,
  UploadCloud,
  Zap,
} from "lucide-react";
import { ThemeToggle } from "@/components/layout/theme-toggle";

export default function LandingPage() {
  return (
    <div className="relative min-h-screen bg-background overflow-hidden selection:bg-brand-500/20 selection:text-brand-300">
      {/* Background Glow Accents */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 h-[500px] w-full max-w-7xl bg-hero-glow pointer-events-none" />
      <div className="absolute top-1/4 -left-48 h-96 w-96 rounded-full bg-brand-600/10 blur-3xl pointer-events-none" />
      <div className="absolute top-1/3 -right-48 h-96 w-96 rounded-full bg-cyan-500/10 blur-3xl pointer-events-none" />

      {/* Top Navbar */}
      <header className="sticky top-0 z-40 border-b border-border/80 bg-background/70 backdrop-blur-xl">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-6">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-tr from-brand-600 via-indigo-500 to-cyan-400 text-white shadow-lg shadow-brand-500/20">
              <Bot className="h-5 w-5" />
            </div>
            <div className="flex flex-col">
              <span className="font-bold text-base text-foreground tracking-tight flex items-center gap-1.5">
                CodePilot AI
                <span className="rounded bg-brand-500/20 px-1.5 py-0.5 text-[10px] font-semibold text-brand-400">
                  v1.0.0
                </span>
              </span>
              <span className="text-[11px] text-muted-foreground">Autonomous Code Review</span>
            </div>
          </div>

          <nav className="hidden md:flex items-center gap-6 text-xs font-semibold text-muted-foreground">
            <a href="#features" className="hover:text-foreground transition-colors">Features</a>
            <a href="#architecture" className="hover:text-foreground transition-colors">Architecture</a>
            <a href="#stats" className="hover:text-foreground transition-colors">Metrics</a>
            <a href="#faq" className="hover:text-foreground transition-colors">FAQ</a>
            <a
              href="http://localhost:8000/docs"
              target="_blank"
              rel="noreferrer"
              className="hover:text-brand-300 transition-colors"
            >
              Swagger Docs
            </a>
          </nav>

          <div className="flex items-center gap-3">
            <ThemeToggle />
            <Link
              href="/login"
              className="text-xs font-semibold text-muted-foreground hover:text-foreground hidden sm:inline"
            >
              Sign In
            </Link>
            <Link
              href="/dashboard"
              className="inline-flex items-center gap-1.5 rounded-xl bg-gradient-to-r from-brand-600 to-indigo-600 px-4 py-2 text-xs font-semibold text-white shadow-lg shadow-brand-500/25 hover:from-brand-500 hover:to-indigo-500 transition-all"
            >
              <span>Launch App</span>
              <ArrowRight className="h-3.5 w-3.5" />
            </Link>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative pt-20 pb-16 md:pt-28 md:pb-24 text-center px-6">
        <div className="mx-auto max-w-4xl">
          <div className="inline-flex items-center gap-2 rounded-full border border-brand-500/30 bg-brand-500/10 px-3 py-1 text-xs font-semibold text-brand-300 mb-6 backdrop-blur-sm shadow-sm">
            <Sparkles className="h-3.5 w-3.5 text-cyan-300 animate-pulse" />
            <span>Phase 14 Production GA — Python AST + Gemini 2.5 Flash</span>
          </div>

          <h1 className="text-4xl font-extrabold tracking-tight text-foreground sm:text-6xl lg:text-7xl leading-tight">
            Stop Guessing Code Quality. <br />
            <span className="gradient-text">Audit Deterministically.</span>
          </h1>

          <p className="mt-6 text-base text-muted-foreground sm:text-lg max-w-2xl mx-auto leading-relaxed">
            CodePilot AI unifies in-memory Python AST analysis, Radon cyclomatic complexity, and Bandit security heuristics with Google Gemini 2.5 Flash reasoning.
          </p>

          <div className="mt-8 flex flex-wrap items-center justify-center gap-4">
            <Link
              href="/review"
              className="inline-flex items-center gap-2 rounded-xl bg-gradient-to-r from-brand-600 via-indigo-600 to-cyan-500 px-6 py-3.5 text-sm font-semibold text-white shadow-xl shadow-brand-500/30 hover:brightness-110 transition-all"
            >
              <Play className="h-4 w-4 fill-white" />
              <span>Try Interactive Review</span>
            </Link>
            <Link
              href="/dashboard"
              className="inline-flex items-center gap-2 rounded-xl border border-border bg-secondary/80 px-6 py-3.5 text-sm font-semibold text-foreground hover:bg-secondary transition-all"
            >
              <span>View Live Dashboard</span>
            </Link>
          </div>
        </div>

        {/* Hero Code & Report Mockup Card */}
        <div className="mx-auto mt-16 max-w-5xl rounded-2xl border border-border/80 bg-card/60 p-2 shadow-2xl backdrop-blur-xl">
          <div className="rounded-xl border border-border bg-[#0d1117] p-4 text-left font-mono text-xs">
            <div className="flex items-center justify-between border-b border-border/80 pb-3 mb-4">
              <div className="flex items-center gap-2">
                <span className="h-3 w-3 rounded-full bg-rose-500/80" />
                <span className="h-3 w-3 rounded-full bg-amber-500/80" />
                <span className="h-3 w-3 rounded-full bg-emerald-500/80" />
                <span className="ml-2 text-xs text-muted-foreground">security_auth.py — Review Output</span>
              </div>
              <span className="rounded bg-emerald-500/20 px-2 py-0.5 text-emerald-400 font-semibold">
                GRADE A (92.5/100)
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <div className="text-[11px] text-muted-foreground mb-1">Detected AST Vulnerability:</div>
                <div className="rounded-lg bg-rose-500/10 border border-rose-500/30 p-3 text-rose-300">
                  <span className="font-bold text-rose-400">[SEC-001]</span> Timing attack in password verification. Direct equality check is unsafe.
                </div>
              </div>
              <div>
                <div className="text-[11px] text-muted-foreground mb-1">Gemini AI Auto-Remediation:</div>
                <div className="rounded-lg bg-emerald-500/10 border border-emerald-500/30 p-3 text-emerald-300">
                  <code>+ if hmac.compare_digest(stored_hash, user_hash):</code>
                  <br />
                  <span className="text-[11px] text-emerald-400/80">Constant-time validation applied. Zero timing leaks.</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Statistics Banner */}
      <section id="stats" className="border-y border-border/80 bg-secondary/30 py-12 px-6">
        <div className="mx-auto max-w-7xl grid grid-cols-2 gap-6 sm:grid-cols-4 text-center">
          <div>
            <div className="text-3xl font-extrabold text-foreground sm:text-4xl">&lt; 2ms</div>
            <div className="mt-1 text-xs text-muted-foreground">Deterministic AST Latency</div>
          </div>
          <div>
            <div className="text-3xl font-extrabold text-cyan-400 sm:text-4xl">25+</div>
            <div className="mt-1 text-xs text-muted-foreground">Bandit Security Heuristics</div>
          </div>
          <div>
            <div className="text-3xl font-extrabold text-brand-400 sm:text-4xl">40%</div>
            <div className="mt-1 text-xs text-muted-foreground">Inference Token Cost Savings</div>
          </div>
          <div>
            <div className="text-3xl font-extrabold text-emerald-400 sm:text-4xl">100%</div>
            <div className="mt-1 text-xs text-muted-foreground">Zero Code Execution Safety</div>
          </div>
        </div>
      </section>

      {/* Features Grid */}
      <section id="features" className="py-20 px-6 max-w-7xl mx-auto">
        <div className="text-center max-w-2xl mx-auto mb-16">
          <h2 className="text-3xl font-bold tracking-tight text-foreground sm:text-4xl">
            Engineered for High-Velocity Engineering Teams
          </h2>
          <p className="mt-3 text-sm text-muted-foreground">
            Everything you need for automated quality gates, security auditing, and intelligent code refactoring.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="rounded-2xl border border-border bg-card p-6 shadow-sm hover:border-brand-500/40 transition-all">
            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-brand-500/10 text-brand-400 mb-4">
              <Cpu className="h-6 w-6" />
            </div>
            <h3 className="text-base font-semibold text-foreground">Python AST & Radon Engine</h3>
            <p className="mt-2 text-xs text-muted-foreground leading-relaxed">
              Calculates exact cyclomatic complexity, Halstead volume, and maintainability indices deterministically on Abstract Syntax Trees without executing code.
            </p>
          </div>

          <div className="rounded-2xl border border-border bg-card p-6 shadow-sm hover:border-cyan-500/40 transition-all">
            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-cyan-500/10 text-cyan-400 mb-4">
              <Sparkles className="h-6 w-6" />
            </div>
            <h3 className="text-base font-semibold text-foreground">Google Gemini 2.5 Reasoning</h3>
            <p className="mt-2 text-xs text-muted-foreground leading-relaxed">
              Provides architectural design feedback, idiomatic refactoring, automated bugfix patches, and complete executable pytest test suites.
            </p>
          </div>

          <div className="rounded-2xl border border-border bg-card p-6 shadow-sm hover:border-emerald-500/40 transition-all">
            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-emerald-500/10 text-emerald-400 mb-4">
              <ShieldCheck className="h-6 w-6" />
            </div>
            <h3 className="text-base font-semibold text-foreground">ZipSlip Defense & Sandboxing</h3>
            <p className="mt-2 text-xs text-muted-foreground leading-relaxed">
              Upload full ZIP/TAR archives with path canonicalization verification that prevents directory traversal exploits and arbitrary file overwriting.
            </p>
          </div>

          <div className="rounded-2xl border border-border bg-card p-6 shadow-sm hover:border-amber-500/40 transition-all">
            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-amber-500/10 text-amber-400 mb-4">
              <Zap className="h-6 w-6" />
            </div>
            <h3 className="text-base font-semibold text-foreground">Redis 7 Sub-2ms Caching</h3>
            <p className="mt-2 text-xs text-muted-foreground leading-relaxed">
              Normalized SHA-256 code hashing allows identical code reviews to be delivered in under 2 milliseconds without hitting the database or AI API.
            </p>
          </div>

          <div className="rounded-2xl border border-border bg-card p-6 shadow-sm hover:border-purple-500/40 transition-all">
            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-purple-500/10 text-purple-400 mb-4">
              <FileCode className="h-6 w-6" />
            </div>
            <h3 className="text-base font-semibold text-foreground">Automated Scaffolding</h3>
            <p className="mt-2 text-xs text-muted-foreground leading-relaxed">
              Generate Google docstrings, Markdown project READMEs, KeepAChangelog releases, and system architecture specifications with a single click.
            </p>
          </div>

          <div className="rounded-2xl border border-border bg-card p-6 shadow-sm hover:border-rose-500/40 transition-all">
            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-rose-500/10 text-rose-400 mb-4">
              <Lock className="h-6 w-6" />
            </div>
            <h3 className="text-base font-semibold text-foreground">HMAC Webhooks & API Keys</h3>
            <p className="mt-2 text-xs text-muted-foreground leading-relaxed">
              Event-driven notifications signed with HMAC-SHA256 and salted API keys for headless CI/CD pipeline automation in GitHub Actions.
            </p>
          </div>
        </div>
      </section>

      {/* Architecture Section */}
      <section id="architecture" className="py-20 border-t border-border/80 bg-secondary/20 px-6">
        <div className="mx-auto max-w-5xl text-center">
          <h2 className="text-3xl font-bold tracking-tight text-foreground sm:text-4xl">
            Built on Clean Asynchronous Architecture
          </h2>
          <p className="mt-3 text-sm text-muted-foreground max-w-xl mx-auto">
            Decoupled API routers, domain service coordinators, and SQLAlchemy AsyncSession repositories backed by PostgreSQL 16 and Redis 7.
          </p>

          <div className="mt-12 rounded-2xl border border-border bg-card p-8 shadow-xl text-left font-mono text-xs">
            <div className="flex items-center justify-between border-b border-border pb-3 mb-6">
              <span className="font-semibold text-brand-400">SYSTEM TOPOLOGY SPECIFICATION</span>
              <span className="text-muted-foreground">HTTP 200 PROBE OK</span>
            </div>
            <pre className="text-slate-300 leading-relaxed overflow-x-auto whitespace-pre">
{`Client (Next.js 15)  -->  Nginx Reverse Proxy (TLS, Gzip, 50MB Buffer)
                          |
                          v
FastAPI Core Engine (Gunicorn + Uvicorn Async Workers)
  |-- Security Middleware (SlowAPI Rate Limiter, JWT Auth, Security Headers)
  |-- Domain Services:
  |     |-- AST Parser & Radon Complexity Calculator (<2ms)
  |     |-- Bandit AST Vulnerability Inspector (25+ Rules)
  |     |-- Google Gemini 2.5 Flash Orchestration Layer
  |     +-- Multi-Format Report Exporter (MD, HTML, JSON, ZIP)
  |
  +-- Persistence & Distributed Caching:
        |-- PostgreSQL 16 (Asyncpg Connection Pool & Alembic Migrations)
        +-- Redis 7 (LRU Query Caching & Rate Limiting Token Buckets)`}
            </pre>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-6 text-center">
        <div className="mx-auto max-w-4xl rounded-3xl border border-brand-500/30 bg-gradient-to-b from-brand-500/10 to-transparent p-12 shadow-2xl">
          <h2 className="text-3xl font-bold tracking-tight text-foreground sm:text-4xl">
            Ready to Automate Your Code Reviews?
          </h2>
          <p className="mt-4 text-sm text-muted-foreground max-w-lg mx-auto">
            Launch the interactive dashboard, upload your repositories, and generate production-grade code reviews in seconds.
          </p>
          <div className="mt-8 flex flex-wrap justify-center gap-4">
            <Link
              href="/review"
              className="inline-flex items-center gap-2 rounded-xl bg-gradient-to-r from-brand-600 to-indigo-600 px-6 py-3 text-sm font-semibold text-white shadow-xl shadow-brand-500/30 hover:brightness-110 transition-all"
            >
              <span>Start Reviewing Now</span>
              <ArrowRight className="h-4 w-4" />
            </Link>
            <a
              href="http://localhost:8000/docs"
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center gap-2 rounded-xl border border-border bg-secondary px-6 py-3 text-sm font-semibold text-foreground hover:bg-accent transition-all"
            >
              <span>Explore Swagger API</span>
            </a>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-border/80 bg-background/50 px-6 py-8 text-xs text-muted-foreground">
        <div className="mx-auto max-w-7xl flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <Bot className="h-4 w-4 text-brand-400" />
            <span className="font-semibold text-foreground">CodePilot AI</span>
            <span>— MIT Open Source Portfolio Project</span>
          </div>
          <div className="flex items-center gap-6">
            <Link href="/dashboard" className="hover:text-foreground">Dashboard</Link>
            <Link href="/review" className="hover:text-foreground">Editor</Link>
            <Link href="/monitoring" className="hover:text-foreground">Status</Link>
            <a href="http://localhost:8000/docs" target="_blank" rel="noreferrer" className="hover:text-foreground">
              API Docs
            </a>
          </div>
        </div>
      </footer>
    </div>
  );
}
