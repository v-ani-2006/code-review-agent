#!/usr/bin/env bash
# ==============================================================================
# scripts/migrate.sh — Run Alembic database migrations
#
# Applies all pending migrations using `alembic upgrade head`.
# Exits non-zero on failure to halt container startup.
# ==============================================================================

set -euo pipefail

CYAN='\033[0;36m'
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

log()   { echo -e "${CYAN}[MIGRATE]${NC} $*"; }
ok()    { echo -e "${GREEN}[MIGRATE]${NC} $*"; }
fail()  { echo -e "${RED}[MIGRATE]${NC} $*" >&2; exit 1; }

cd /app

log "Running Alembic migrations..."

# Show current migration status before applying
log "Current revision:"
alembic current 2>&1 || true

log "Applying: alembic upgrade head"
if alembic upgrade head; then
    ok "All migrations applied successfully."
else
    fail "Migration failed! Check the Alembic output above."
fi

log "Revision after migration:"
alembic current 2>&1 || true
