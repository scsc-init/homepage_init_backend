#!/bin/bash

set -e

usage() {
  cat <<USAGE
Usage: $0 <backup.tar.gz> [--force]
  <backup.tar.gz>  Backup archive created by the backup API (contains db.sql and static/)
  --force          Restore without interactive prompts
USAGE
  exit 1
}

FORCE=false
BACKUP_FILE=""
STATIC_DIR="static"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --force)
      FORCE=true
      shift
      ;;
    -*|--*)
      echo "Unknown option: $1"
      usage
      ;;
    *)
      if [[ -n "$BACKUP_FILE" ]]; then
        usage
      fi
      BACKUP_FILE="$1"
      shift
      ;;
  esac
done

if [[ -z "$BACKUP_FILE" ]]; then
  usage
fi

if [[ ! -f "$BACKUP_FILE" ]]; then
  echo "Backup file '$BACKUP_FILE' does not exist."
  exit 1
fi

prompt_confirm() {
  local prompt="$1"
  if [[ "$FORCE" == "true" ]]; then
    return 0
  fi
  read -p "$prompt (yes/no): " reply
  [[ "$reply" == "yes" ]]
}

WORK_DIR="$(mktemp -d)"
trap 'rm -rf "$WORK_DIR"' EXIT

tar -xzf "$BACKUP_FILE" -C "$WORK_DIR"

if [[ ! -f "$WORK_DIR/db.sql" ]]; then
  echo "Invalid backup: 'db.sql' not found in '$BACKUP_FILE'."
  exit 1
fi

# Restore database
if prompt_confirm "Overwrite current database with '$BACKUP_FILE'?"; then
  docker compose exec -T db sh -c \
    'psql -q -v ON_ERROR_STOP=1 --single-transaction -U postgres -d "$POSTGRES_DB"' \
    < "$WORK_DIR/db.sql" > /dev/null
  echo "Restored database from '$BACKUP_FILE'"
else
  echo "Skipped restoring database"
  exit 1
fi

# Restore static files
if [[ -d "$WORK_DIR/static" ]]; then
  if prompt_confirm "Replace static directory '$STATIC_DIR' with the backup?"; then
    mkdir -p "$STATIC_DIR"
    PREV_STATIC_DIR="${STATIC_DIR}_before_restore_$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$PREV_STATIC_DIR"
    cp -a "$STATIC_DIR/." "$PREV_STATIC_DIR/"
    # Replace contents in place: static/ is bind-mounted into the backend container.
    find "$STATIC_DIR" -mindepth 1 -delete
    cp -a "$WORK_DIR/static/." "$STATIC_DIR/"
    echo "Restored static directory (previous files kept in '$PREV_STATIC_DIR')"
  else
    echo "Skipped restoring static directory"
  fi
else
  echo "No static directory in backup; skipped restoring static directory"
fi

echo "Done. Restart the backend container to apply: docker compose restart backend"
