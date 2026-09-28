#!/usr/bin/env bash
# ==============================================================================
# scripts/healthcheck.sh — Comprehensive application health check
#
# Verifies:
#   1. FastAPI application (/health endpoint)
#   2. PostgreSQL connectivity (pg_isready)
#   3. Redis connectivity (redis-cli ping)
#   4. Uploads directory is writable
#   5. Reports directory is writable
#
# Returns:
#   Exit code 0 — all checks passed
#   Exit code 1 — one or more checks failed
#
# Used as Docker HEALTHCHECK CMD or invoked manually.
# ==============================================================================

set -uo pipefail

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

PASS=0
FAIL=0

check_pass() { echo -e "${GREEN}[PASS]${NC} $*"; PASS=$((PASS + 1)); }
check_fail() { echo -e "${RED}[FAIL]${NC} $*"; FAIL=$((FAIL + 1)); }
check_warn() { echo -e "${YELLOW}[WARN]${NC} $*"; }

echo "============================================"
echo " CodePilot AI Health Check"
echo "============================================"

# --- 1. Application HTTP health -------------------------------------------
APP_URL="${APP_URL:-http://localhost:8000/health}"
if curl -sf --max-time 5 "${APP_URL}" -o /dev/null; then
    check_pass "Application is responding at ${APP_URL}"
else
    check_fail "Application NOT responding at ${APP_URL}"
fi

# --- 2. PostgreSQL -----------------------------------------------------------
PG_HOST="${DATABASE_HOST:-postgres}"
PG_PORT="${DATABASE_PORT:-5432}"
PG_USER="${DATABASE_USER:-postgres}"
PG_DB="${DATABASE_NAME:-codepilot_db}"
check_pg() {
    if command -v pg_isready >/dev/null 2>&1; then
        pg_isready -h "${PG_HOST}" -p "${PG_PORT}" -U "${PG_USER}" -d "${PG_DB}" -q 2>/dev/null
    else
        python3 -c "import socket; s = socket.socket(socket.AF_INET, socket.SOCK_STREAM); s.settimeout(2); s.connect(('${PG_HOST}', int('${PG_PORT}'))); s.close()" >/dev/null 2>&1
    fi
}
if check_pg; then
    check_pass "PostgreSQL is ready at ${PG_HOST}:${PG_PORT}"
else
    check_fail "PostgreSQL NOT ready at ${PG_HOST}:${PG_PORT}"
fi

# --- 3. Redis ----------------------------------------------------------------
REDIS_HOST="${REDIS_HOST:-redis}"
REDIS_PORT="${REDIS_PORT:-6379}"
check_redis() {
    if command -v redis-cli >/dev/null 2>&1; then
        redis-cli -h "${REDIS_HOST}" -p "${REDIS_PORT}" ping 2>/dev/null | grep -q PONG
    else
        python3 -c "import socket; s = socket.socket(socket.AF_INET, socket.SOCK_STREAM); s.settimeout(2); s.connect(('${REDIS_HOST}', int('${REDIS_PORT}'))); s.close()" >/dev/null 2>&1
    fi
}
if check_redis; then
    check_pass "Redis is ready at ${REDIS_HOST}:${REDIS_PORT}"
else
    check_warn "Redis NOT responding at ${REDIS_HOST}:${REDIS_PORT} (degraded mode)"
    # Redis failure is warning only — app continues in degraded mode
fi

# --- 4. Uploads directory ---------------------------------------------------
UPLOAD_DIR="${UPLOAD_DIR:-/app/uploads}"
if [ -d "${UPLOAD_DIR}" ] && [ -w "${UPLOAD_DIR}" ]; then
    check_pass "Uploads directory is writable: ${UPLOAD_DIR}"
else
    check_fail "Uploads directory NOT writable: ${UPLOAD_DIR}"
fi

# --- 5. Reports directory ---------------------------------------------------
REPORTS_DIR="${REPORTS_DIR:-/app/reports}"
if [ -d "${REPORTS_DIR}" ] && [ -w "${REPORTS_DIR}" ]; then
    check_pass "Reports directory is writable: ${REPORTS_DIR}"
else
    check_fail "Reports directory NOT writable: ${REPORTS_DIR}"
fi

# --- Summary ----------------------------------------------------------------
echo "============================================"
echo " Results: ${PASS} passed, ${FAIL} failed"
echo "============================================"

if [ "${FAIL}" -gt 0 ]; then
    exit 1
fi
exit 0
