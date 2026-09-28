#!/usr/bin/env bash
# ==============================================================================
# scripts/start.sh — CodePilot AI container startup script
#
# Startup sequence:
#   1. Wait for PostgreSQL to be ready
#   2. Wait for Redis to be ready
#   3. Run Alembic database migrations
#   4. Start Gunicorn with UvicornWorkers
#
# Environment variables:
#   WORKERS       — Number of Gunicorn worker processes (default: 2)
#   TIMEOUT       — Worker timeout in seconds (default: 120)
#   PORT          — Application port (default: 8000)
#   DEBUG         — If "true", use uvicorn with --reload instead of Gunicorn
# ==============================================================================

set -euo pipefail

# --- Colours for readable output -------------------------------------------
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'  # No colour

log()    { echo -e "${CYAN}[START]${NC}  $*"; }
success(){ echo -e "${GREEN}[OK]${NC}     $*"; }
warn()   { echo -e "${YELLOW}[WARN]${NC}   $*"; }
error()  { echo -e "${RED}[ERROR]${NC}  $*" >&2; }

# ---------------------------------------------------------------------------
# Configuration defaults
# ---------------------------------------------------------------------------
WORKERS="${WORKERS:-2}"
TIMEOUT="${TIMEOUT:-120}"
PORT="${PORT:-8000}"
KEEPALIVE="${KEEPALIVE:-5}"
MAX_REQUESTS="${MAX_REQUESTS:-1000}"
MAX_REQUESTS_JITTER="${MAX_REQUESTS_JITTER:-100}"
GRACEFUL_TIMEOUT="${GRACEFUL_TIMEOUT:-30}"

log "============================================================"
log " CodePilot AI — Container Startup"
log " Workers: ${WORKERS} | Port: ${PORT} | Timeout: ${TIMEOUT}s"
log "============================================================"

# ---------------------------------------------------------------------------
# Step 1 — Wait for PostgreSQL
# ---------------------------------------------------------------------------
log "Step 1/4: Waiting for PostgreSQL..."
/app/scripts/wait_for_db.sh
success "PostgreSQL is ready."

# ---------------------------------------------------------------------------
# Step 2 — Wait for Redis
# ---------------------------------------------------------------------------
log "Step 2/4: Waiting for Redis..."
REDIS_HOST="${REDIS_HOST:-redis}"
REDIS_PORT="${REDIS_PORT:-6379}"
MAX_RETRIES=30
COUNT=0
check_redis() {
    if command -v redis-cli >/dev/null 2>&1; then
        redis-cli -h "${REDIS_HOST}" -p "${REDIS_PORT}" ping 2>/dev/null | grep -q PONG
    else
        python3 -c "import socket; s = socket.socket(socket.AF_INET, socket.SOCK_STREAM); s.settimeout(2); s.connect(('${REDIS_HOST}', int('${REDIS_PORT}'))); s.close()" >/dev/null 2>&1
    fi
}

until check_redis; do
    COUNT=$((COUNT + 1))
    if [ "${COUNT}" -ge "${MAX_RETRIES}" ]; then
        warn "Redis not reachable after ${MAX_RETRIES} attempts — continuing without Redis (cache degraded)."
        break
    fi
    log "Redis not ready yet (attempt ${COUNT}/${MAX_RETRIES}). Retrying in 2s..."
    sleep 2
done
if [ "${COUNT}" -lt "${MAX_RETRIES}" ]; then
    success "Redis is ready."
fi

# ---------------------------------------------------------------------------
# Step 3 — Run Alembic migrations
# ---------------------------------------------------------------------------
log "Step 3/4: Running database migrations..."
/app/scripts/migrate.sh
success "Migrations complete."

# ---------------------------------------------------------------------------
# Step 4 — Start application server
# ---------------------------------------------------------------------------
log "Step 4/4: Starting application server..."

if [ "${DEBUG:-false}" = "true" ]; then
    # Development: uvicorn with hot reload
    warn "DEBUG=true — Starting uvicorn with --reload (not for production!)"
    exec uvicorn app.main:app \
        --host 0.0.0.0 \
        --port "${PORT}" \
        --reload \
        --log-level info
else
    # Production: Gunicorn with UvicornWorker
    if [ -f "/app/gunicorn_conf.py" ]; then
        success "Starting Gunicorn with /app/gunicorn_conf.py..."
        exec gunicorn -c /app/gunicorn_conf.py app.main:app
    else
        success "Starting Gunicorn with ${WORKERS} UvicornWorker(s) on port ${PORT}..."
        exec gunicorn app.main:app \
            --worker-class uvicorn.workers.UvicornWorker \
            --workers "${WORKERS}" \
            --bind "0.0.0.0:${PORT}" \
            --timeout "${TIMEOUT}" \
            --keepalive "${KEEPALIVE}" \
            --max-requests "${MAX_REQUESTS}" \
            --max-requests-jitter "${MAX_REQUESTS_JITTER}" \
            --graceful-timeout "${GRACEFUL_TIMEOUT}" \
            --access-logfile /app/logs/gunicorn_access.log \
            --error-logfile /app/logs/gunicorn_error.log \
            --log-level info \
            --forwarded-allow-ips='*'
    fi
fi
