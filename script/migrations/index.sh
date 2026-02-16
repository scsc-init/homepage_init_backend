#!/bin/bash

set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check if DB file argument is provided
if [ -z "$1" ]; then
  echo "Usage: $0 <database_file>"
  exit 1
fi

DB_FILE="$(realpath "$1")"  # Convert to absolute path

# Check if the database file already exists
if [ -f "$DB_FILE" ]; then
    echo "Error: Database file '$DB_FILE' already exists. Aborting."
    exit 1
fi

echo "Initializing database at $DB_FILE..."

touch "$DB_FILE"

# Define a function to run when the script exits
cleanup() {
  exit_code=$?
  if [ $exit_code -ne 0 ]; then
    rm "$DB_FILE"
    echo "Initializing DB Script terminated with error code $exit_code"
    # Do some error handling here
  fi
}

# Trap EXIT signal to call cleanup function on exit (error or success)
trap cleanup EXIT

(cd "$SCRIPT_DIR" && sqlite3 "$DB_FILE" < "B7__baseline.sql")
(cd "$SCRIPT_DIR" && sqlite3 "$DB_FILE" < "V8__update_kv_footer-message.sql")
(cd "$SCRIPT_DIR" && sqlite3 "$DB_FILE" < "V9__set_standby_default_status.sql")
(cd "$SCRIPT_DIR" && sqlite3 "$DB_FILE" < "V10__create_attachment.sql")
(cd "$SCRIPT_DIR" && sqlite3 "$DB_FILE" < "V11__create_pig_website.sql")
(cd "$SCRIPT_DIR" && sqlite3 "$DB_FILE" < "V12__alter_pig_admission.sql")
(cd "$SCRIPT_DIR" && sqlite3 "$DB_FILE" < "V13_create_sigpig_createdyear.sql")

echo "Database initialization and inserts completed successfully."
