#!/usr/bin/env bash
# ==============================================================================
# scripts/wait_for_db.sh — Poll PostgreSQL until it accepts connections
#
# Reads connection parameters from environment variables:
#   DATABASE_HOST     (default: postgres)
#   DATABASE_PORT     (default: 5432)
#   DATABASE_USER     (default: postgres)
#   DATABASE_NAME     (default: codepilot_db)
#   DB_WAIT_TIMEOUT   (default: 60s)
# ==============================================================================

set -euo pipefail

HOST="${DATABASE_HOST:-postgres}"
PORT="${DATABASE_PORT:-5432}"
USER="${DATABASE_USER:-postgres}"
DB="${DATABASE_NAME:-codepilot_db}"
TIMEOUT="${DB_WAIT_TIMEOUT:-60}"

CYAN='\033[0;36m'
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

log()   { echo -e "${CYAN}[DB-WAIT]${NC} $*"; }
ok()    { echo -e "${GREEN}[DB-WAIT]${NC} $*"; }
fail()  { echo -e "${RED}[DB-WAIT]${NC} $*" >&2; exit 1; }

log "Waiting for PostgreSQL at ${HOST}:${PORT} (timeout: ${TIMEOUT}s)..."

ELAPSED=0
INTERVAL=2

check_pg() {
    if command -v pg_isready >/dev/null 2>&1; then
        pg_isready -h "${HOST}" -p "${PORT}" -U "${USER}" -d "${DB}" -q 2>/dev/null
    else
        python3 -c "import socket; s = socket.socket(socket.AF_INET, socket.SOCK_STREAM); s.settimeout(2); s.connect(('${HOST}', int('${PORT}'))); s.close()" >/dev/null 2>&1
    fi
}

until check_pg; do
    ELAPSED=$((ELAPSED + INTERVAL))
    if [ "${ELAPSED}" -ge "${TIMEOUT}" ]; then
        fail "PostgreSQL did not become ready within ${TIMEOUT} seconds. Aborting."
    fi
    log "PostgreSQL not ready yet (${ELAPSED}s elapsed). Retrying in ${INTERVAL}s..."
    sleep "${INTERVAL}"
done

ok "PostgreSQL is accepting connections at ${HOST}:${PORT} (${DB})."
