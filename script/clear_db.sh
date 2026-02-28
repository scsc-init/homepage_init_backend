#!/bin/bash

set -e

usage() {
  cat <<USAGE
Usage: $0 [--force]
  --force        Delete without interactive prompts
USAGE
  exit 1
}

FORCE=false
STATIC_DIR="static"
DB_DIR="data"

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
  esac
done

DB_DIR="$(realpath -m "$DB_DIR")"

prompt_confirm() {
  local prompt="$1"
  if [[ "$FORCE" == "true" ]]; then
    return 0
  fi
  read -p "$prompt (yes/no): " reply
  [[ "$reply" == "yes" ]]
}

if [[ -d "$DB_DIR" ]]; then
  if prompt_confirm "Delete database directory '$DB_DIR'?"; then
    rm -r "$DB_DIR"
    echo "Deleted database directory '$DB_DIR'"
  else
    echo "Skipped deleting database directory"
    exit 1
  fi
else
  echo "Database directory '$DB_DIR' does not exist."
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
