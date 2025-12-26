#!/bin/sh
set -eu

DB_PATH="/volume1/web_apps/eli-care-log-data/eli_care_log.db"
BACKUP_DIR="/volume1/web_apps/eli-care-log-backups"

mkdir -p "$BACKUP_DIR"

TS="$(date +%Y-%m-%d_%H%M%S)"
OUT_DB="${BACKUP_DIR}/eli_care_log_${TS}.db"

# Make consistent snapshot
sqlite3 "$DB_PATH" ".backup '$OUT_DB'"

# Compress
gzip "$OUT_DB"

# Keep last 60 backups
ls -1t "${BACKUP_DIR}"/eli_care_log_*.db.gz | tail -n +61 | xargs -r rm --
