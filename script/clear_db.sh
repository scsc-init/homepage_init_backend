#!/bin/bash

set -e

usage() {
  cat <<USAGE
Usage: $0 [--force] [--static-dir <dir>] <database_file>
  --force        Delete without interactive prompts
  --static-dir   Optional static directory to delete after removing DB
USAGE
  exit 1
}

FORCE=false
STATIC_DIR=""
DB_FILE=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --force)
      FORCE=true
      shift
      ;;
    --static-dir)
      STATIC_DIR="$2"
      shift 2
      ;;
    -*|--*)
      echo "Unknown option: $1"
      usage
      ;;
    *)
      DB_FILE="$1"
      shift
      ;;
  esac
done

if [[ -z "$DB_FILE" ]]; then
  usage
fi

DB_FILE="$(realpath "$DB_FILE")"

prompt_confirm() {
  local prompt="$1"
  if [[ "$FORCE" == "true" ]]; then
    return 0
  fi
  read -p "$prompt (yes/no): " reply
  [[ "$reply" == "yes" ]]
}

if [[ -f "$DB_FILE" ]]; then
  if prompt_confirm "Delete database file '$DB_FILE'?"; then
    rm "$DB_FILE"
    echo "Deleted database file '$DB_FILE'"
  else
    echo "Skipped deleting database file"
    exit 1
  fi
else
  echo "Database file '$DB_FILE' does not exist."
fi

if [[ -n "$STATIC_DIR" ]]; then
  STATIC_DIR="$(realpath "$STATIC_DIR" 2>/dev/null)"
  if [[ -n "$STATIC_DIR" && -d "$STATIC_DIR" ]]; then
    if prompt_confirm "Delete static directory '$STATIC_DIR'?"; then
      rm -rf "$STATIC_DIR"
      echo "Deleted static directory '$STATIC_DIR'"
    else
      echo "Skipped deleting static directory"
    fi
  else
    echo "Static directory '$STATIC_DIR' does not exist."
  fi
fi
