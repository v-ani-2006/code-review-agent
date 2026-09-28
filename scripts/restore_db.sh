#!/usr/bin/env bash
# ==============================================================================
# scripts/restore_db.sh — PostgreSQL database restore script
#
# Usage:
#   ./scripts/restore_db.sh                            # Restore latest backup
#   ./scripts/restore_db.sh <backup_file.sql.gz>       # Restore specific backup
#
# WARNING: This will DROP and RECREATE the target database.
#          Requires confirmation prompt in interactive mode.
# ==============================================================================

set -euo pipefail

CYAN='\033[0;36m'
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

log()  { echo -e "${CYAN}[RESTORE]${NC} $*"; }
ok()   { echo -e "${GREEN}[RESTORE]${NC} $*"; }
warn() { echo -e "${YELLOW}[RESTORE]${NC} $*"; }
fail() { echo -e "${RED}[RESTORE]${NC} $*" >&2; exit 1; }

# --- Configuration -----------------------------------------------------------
DB_HOST="${DATABASE_HOST:-postgres}"
DB_PORT="${DATABASE_PORT:-5432}"
DB_NAME="${DATABASE_NAME:-codepilot_db}"
DB_USER="${DATABASE_USER:-postgres}"
PGPASSWORD="${DATABASE_PASSWORD:-postgres_password}"
export PGPASSWORD

BACKUP_DIR="${BACKUP_DIR:-/app/backups}"

# --- Resolve which backup file to restore -----------------------------------
if [ "$#" -ge 1 ] && [ -n "$1" ]; then
    BACKUP_FILE="$1"
    if [ ! -f "${BACKUP_FILE}" ]; then
        fail "Specified backup file not found: ${BACKUP_FILE}"
    fi
    log "Using specified backup: ${BACKUP_FILE}"
else
    # Find the latest backup
    BACKUP_FILE=$(ls -t "${BACKUP_DIR}"/codepilot_*.sql.gz 2>/dev/null | head -n1 || true)
    if [ -z "${BACKUP_FILE}" ]; then
        fail "No backups found in ${BACKUP_DIR}"
    fi
    log "Using latest backup: ${BACKUP_FILE}"
fi

# --- Validate backup file ---------------------------------------------------
if ! gzip -t "${BACKUP_FILE}" 2>/dev/null; then
    fail "Backup file is corrupted or not a valid gzip archive: ${BACKUP_FILE}"
fi
BACKUP_SIZE=$(du -sh "${BACKUP_FILE}" | cut -f1)
ok "Backup file is valid (${BACKUP_SIZE})"

# --- Confirmation prompt (skip if FORCE=true) --------------------------------
if [ "${FORCE:-false}" != "true" ]; then
    warn "This will DROP and RECREATE database '${DB_NAME}' on ${DB_HOST}:${DB_PORT}."
    warn "ALL EXISTING DATA WILL BE LOST."
    read -rp "Type 'yes' to proceed: " CONFIRM
    if [ "${CONFIRM}" != "yes" ]; then
        log "Restore cancelled by user."
        exit 0
    fi
fi

# --- Drop and recreate the database -----------------------------------------
log "Dropping and recreating database '${DB_NAME}'..."
psql \
    --host="${DB_HOST}" \
    --port="${DB_PORT}" \
    --username="${DB_USER}" \
    --dbname="postgres" \
    --no-password \
    -c "DROP DATABASE IF EXISTS \"${DB_NAME}\";" \
    -c "CREATE DATABASE \"${DB_NAME}\" OWNER \"${DB_USER}\";"
ok "Database recreated."

# --- Restore from backup ----------------------------------------------------
log "Restoring from: ${BACKUP_FILE}"
if zcat "${BACKUP_FILE}" | psql \
    --host="${DB_HOST}" \
    --port="${DB_PORT}" \
    --username="${DB_USER}" \
    --dbname="${DB_NAME}" \
    --no-password \
    --quiet; then
    ok "Database restored successfully from ${BACKUP_FILE}"
else
    fail "Restore failed. Database may be in an inconsistent state."
fi

# --- Run migrations to ensure schema is current -----------------------------
log "Running migrations to synchronize schema..."
cd /app && alembic upgrade head
ok "Schema synchronized."

ok "Restore complete."
