# ==============================================================================
# gunicorn_conf.py — Production Gunicorn Configuration for CodePilot AI
#
# Launches FastAPI application using UvicornWorker processes.
# All operational settings are fully configurable via environment variables.
#
# Usage:
#   gunicorn -c gunicorn_conf.py app.main:app
# ==============================================================================

import multiprocessing
import os
import sys

# ------------------------------------------------------------------------------
# Server Socket & Binding
# ------------------------------------------------------------------------------
host = os.getenv("HOST", "0.0.0.0")
port = os.getenv("PORT", "8000")
bind = f"{host}:{port}"
backlog = int(os.getenv("BACKLOG", "2048"))

# ------------------------------------------------------------------------------
# Worker Processes & Concurrency
# ------------------------------------------------------------------------------
# Default to (2 * CPU cores + 1), clamped between 2 and 8 for container safety
default_workers = max(2, min(multiprocessing.cpu_count() * 2 + 1, 8))
workers = int(os.getenv("WORKERS", str(default_workers)))
worker_class = "uvicorn.workers.UvicornWorker"
threads = int(os.getenv("THREADS", "2"))
worker_connections = int(os.getenv("WORKER_CONNECTIONS", "1000"))

# ------------------------------------------------------------------------------
# Worker Lifespan & Memory Recycling
# ------------------------------------------------------------------------------
# Periodically restart workers after processing requests to prevent memory leaks
max_requests = int(os.getenv("MAX_REQUESTS", "1000"))
max_requests_jitter = int(os.getenv("MAX_REQUESTS_JITTER", "100"))

# ------------------------------------------------------------------------------
# Timeouts & Keep-Alive
# ------------------------------------------------------------------------------
# Generous timeout for AI analysis requests which may take up to 60s
timeout = int(os.getenv("GUNICORN_TIMEOUT", os.getenv("TIMEOUT", "120")))
keepalive = int(os.getenv("KEEPALIVE", "5"))
graceful_timeout = int(os.getenv("GRACEFUL_TIMEOUT", "30"))

# ------------------------------------------------------------------------------
# Logging & Observability
# ------------------------------------------------------------------------------
accesslog = os.getenv("ACCESS_LOG", "/app/logs/gunicorn_access.log")
errorlog = os.getenv("ERROR_LOG", "/app/logs/gunicorn_error.log")
loglevel = os.getenv("LOG_LEVEL", "info").lower()
access_log_format = (
    '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s µs'
)

# If log files are not writable or stdout is preferred in container environments
try:
    if not os.path.exists(os.path.dirname(accesslog)) or not os.access(os.path.dirname(accesslog), os.W_OK):
        accesslog = "-"
except Exception:
    accesslog = "-"

try:
    if not os.path.exists(os.path.dirname(errorlog)) or not os.access(os.path.dirname(errorlog), os.W_OK):
        errorlog = "-"
except Exception:
    errorlog = "-"

# ------------------------------------------------------------------------------
# Process Naming & Security
# ------------------------------------------------------------------------------
proc_name = "codepilot_api"
forwarded_allow_ips = os.getenv("FORWARDED_ALLOW_IPS", "*")
secure_scheme_headers = {
    "X-FORWARDED-PROTOCOL": "ssl",
    "X-FORWARDED-PROTO": "https",
    "X-FORWARDED-SSL": "on",
}

# ------------------------------------------------------------------------------
# Server Lifecycle Hooks
# ------------------------------------------------------------------------------
def on_starting(server):
    """Invoked just before the master process starts."""
    server.log.info("Starting CodePilot AI Gunicorn Master Process [pid=%s]", os.getpid())
    server.log.info("Configuration: %s worker(s), timeout=%ss, bind=%s", workers, timeout, bind)


def on_reload(server):
    """Invoked when worker reload is signaled."""
    server.log.info("CodePilot AI Gunicorn Master reloaded.")


def worker_int(worker):
    """Invoked when a worker received SIGINT or SIGQUIT."""
    worker.log.info("Worker received SIGINT/SIGQUIT (pid=%s). Initiating graceful shutdown.", worker.pid)


def worker_abort(worker):
    """Invoked when a worker received SIGABRT (e.g. on timeout)."""
    worker.log.error("Worker received SIGABRT (pid=%s). Worker timed out or aborted.", worker.pid)
