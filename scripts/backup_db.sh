#!/usr/bin/env bash
# ==============================================================================
# scripts/backup_db.sh — PostgreSQL database backup script
#
# Usage:
#   ./scripts/backup_db.sh                   # Backup to /app/backups/
#   BACKUP_DIR=/custom/path ./scripts/backup_db.sh
#
# Creates a timestamped, gzip-compressed pg_dump of the CodePilot database.
# Rotates backups older than BACKUP_RETENTION_DAYS (default: 7).
#
# Requires:
#   pg_dump   (installed via libpq-dev in container)
#   gzip
# ==============================================================================

set -euo pipefail

CYAN='\033[0;36m'
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

log()  { echo -e "${CYAN}[BACKUP]${NC}  $*"; }
ok()   { echo -e "${GREEN}[BACKUP]${NC}  $*"; }
warn() { echo -e "${YELLOW}[BACKUP]${NC}  $*"; }
fail() { echo -e "${RED}[BACKUP]${NC}  $*" >&2; exit 1; }

# --- Configuration -----------------------------------------------------------
DB_HOST="${DATABASE_HOST:-postgres}"
DB_PORT="${DATABASE_PORT:-5432}"
DB_NAME="${DATABASE_NAME:-codepilot_db}"
DB_USER="${DATABASE_USER:-postgres}"
PGPASSWORD="${DATABASE_PASSWORD:-postgres_password}"
export PGPASSWORD

BACKUP_DIR="${BACKUP_DIR:-/app/backups}"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="${BACKUP_DIR}/codepilot_${DB_NAME}_${TIMESTAMP}.sql.gz"
BACKUP_RETENTION_DAYS="${BACKUP_RETENTION_DAYS:-7}"

# --- Ensure backup directory exists ------------------------------------------
mkdir -p "${BACKUP_DIR}"

log "Starting backup of database '${DB_NAME}' from ${DB_HOST}:${DB_PORT}..."
log "Output: ${BACKUP_FILE}"

# --- Run pg_dump + gzip pipeline --------------------------------------------
if pg_dump \
    --host="${DB_HOST}" \
    --port="${DB_PORT}" \
    --username="${DB_USER}" \
    --dbname="${DB_NAME}" \
    --format=plain \
    --no-password \
    --verbose \
    2>/tmp/pg_dump.log | gzip -9 > "${BACKUP_FILE}"; then

    BACKUP_SIZE=$(du -sh "${BACKUP_FILE}" | cut -f1)
    ok "Backup completed: ${BACKUP_FILE} (${BACKUP_SIZE})"
else
    # Clean up partial file on failure
    rm -f "${BACKUP_FILE}"
    cat /tmp/pg_dump.log >&2
    fail "pg_dump failed! Partial backup removed."
fi

# --- Rotate old backups -------------------------------------------------------
log "Rotating backups older than ${BACKUP_RETENTION_DAYS} days..."
DELETED=$(find "${BACKUP_DIR}" -name "codepilot_*.sql.gz" -mtime "+${BACKUP_RETENTION_DAYS}" -print -delete | wc -l)
if [ "${DELETED}" -gt 0 ]; then
    ok "Removed ${DELETED} expired backup(s)."
else
    log "No expired backups to remove."
fi

# --- List current backups ---------------------------------------------------
log "Current backups in ${BACKUP_DIR}:"
ls -lh "${BACKUP_DIR}"/codepilot_*.sql.gz 2>/dev/null || warn "No backups found."

ok "Backup process complete."
