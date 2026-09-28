#!/usr/bin/env bash
# ==============================================================================
# scripts/cleanup_uploads.sh — Clean expired uploads and temporary files
#
# Deletes:
#   - Temporary uploads older than UPLOAD_MAX_AGE_HOURS (default: 24h)
#   - Extracted ZIP directories older than ZIP_MAX_AGE_HOURS (default: 4h)
#   - Application logs older than LOG_MAX_AGE_DAYS (default: 30d)
#   - Temporary report files older than TEMP_REPORT_MAX_AGE_HOURS (default: 24h)
#
# Preserves:
#   - Permanent review reports (reports/ directory root)
#   - Database backups
#   - .gitkeep files
#
# Usage:
#   ./scripts/cleanup_uploads.sh              # Normal cleanup
#   DRY_RUN=true ./scripts/cleanup_uploads.sh # Preview without deleting
# ==============================================================================

set -euo pipefail

CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log()  { echo -e "${CYAN}[CLEANUP]${NC} $*"; }
ok()   { echo -e "${GREEN}[CLEANUP]${NC} $*"; }
warn() { echo -e "${YELLOW}[CLEANUP]${NC} $*"; }

DRY_RUN="${DRY_RUN:-false}"
UPLOAD_DIR="${UPLOAD_DIR:-/app/uploads}"
TEMP_UPLOAD_DIR="${TEMP_UPLOAD_DIR:-/app/app/uploads/temp}"
REPORTS_DIR="${REPORTS_DIR:-/app/reports}"
LOGS_DIR="${LOGS_DIR:-/app/logs}"

UPLOAD_MAX_AGE_HOURS="${UPLOAD_MAX_AGE_HOURS:-24}"
ZIP_MAX_AGE_HOURS="${ZIP_MAX_AGE_HOURS:-4}"
LOG_MAX_AGE_DAYS="${LOG_MAX_AGE_DAYS:-30}"
TEMP_REPORT_MAX_AGE_HOURS="${TEMP_REPORT_MAX_AGE_HOURS:-24}"

if [ "${DRY_RUN}" = "true" ]; then
    warn "DRY RUN mode — no files will be deleted"
fi

_delete() {
    local target="$1"
    if [ "${DRY_RUN}" = "true" ]; then
        log "  [DRY RUN] Would delete: ${target}"
    else
        rm -rf "${target}"
    fi
}

TOTAL=0

# --- 1. Temporary uploads (uploaded but not yet processed) -------------------
log "Cleaning temp uploads older than ${UPLOAD_MAX_AGE_HOURS}h from ${TEMP_UPLOAD_DIR}..."
if [ -d "${TEMP_UPLOAD_DIR}" ]; then
    while IFS= read -r -d '' f; do
        _delete "${f}"
        TOTAL=$((TOTAL + 1))
    done < <(find "${TEMP_UPLOAD_DIR}" -type f ! -name ".gitkeep" \
             -mmin "+$((UPLOAD_MAX_AGE_HOURS * 60))" -print0 2>/dev/null)
fi

# --- 2. Extracted ZIP project directories ------------------------------------
log "Cleaning extracted ZIP directories older than ${ZIP_MAX_AGE_HOURS}h..."
if [ -d "${TEMP_UPLOAD_DIR}" ]; then
    while IFS= read -r -d '' d; do
        _delete "${d}"
        TOTAL=$((TOTAL + 1))
    done < <(find "${TEMP_UPLOAD_DIR}" -mindepth 1 -maxdepth 1 -type d \
             -mmin "+$((ZIP_MAX_AGE_HOURS * 60))" -print0 2>/dev/null)
fi

# --- 3. Old application logs --------------------------------------------------
log "Cleaning application logs older than ${LOG_MAX_AGE_DAYS} days from ${LOGS_DIR}..."
if [ -d "${LOGS_DIR}" ]; then
    while IFS= read -r -d '' f; do
        _delete "${f}"
        TOTAL=$((TOTAL + 1))
    done < <(find "${LOGS_DIR}" -type f -name "*.log" \
             -mtime "+${LOG_MAX_AGE_DAYS}" -print0 2>/dev/null)
fi

# --- 4. Temporary report files (prefixed with tmp_ or in temp/ subdir) ------
log "Cleaning temporary reports older than ${TEMP_REPORT_MAX_AGE_HOURS}h from ${REPORTS_DIR}..."
if [ -d "${REPORTS_DIR}" ]; then
    while IFS= read -r -d '' f; do
        _delete "${f}"
        TOTAL=$((TOTAL + 1))
    done < <(find "${REPORTS_DIR}" -type f -name "tmp_*" \
             -mmin "+$((TEMP_REPORT_MAX_AGE_HOURS * 60))" -print0 2>/dev/null)
fi

# --- Summary -----------------------------------------------------------------
if [ "${DRY_RUN}" = "true" ]; then
    ok "Dry run complete. ${TOTAL} file(s)/dir(s) would be removed."
else
    ok "Cleanup complete. ${TOTAL} file(s)/dir(s) removed."
fi
