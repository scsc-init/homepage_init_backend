#!/bin/bash

set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check if DB file argument is provided
if [ -z "$1" ]; then
  echo "Usage: $0 <database_file>"
  exit 1
fi

DB_FILE="$1"

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

"$SCRIPT_DIR/insert_tables.sh" "$DB_FILE"
"$SCRIPT_DIR/insert_scsc_global_status.sh" "$DB_FILE"
"$SCRIPT_DIR/insert_user_roles.sh" "$DB_FILE"
"$SCRIPT_DIR/insert_majors.sh" "$DB_FILE" "$SCRIPT_DIR/majors.csv"
"$SCRIPT_DIR/insert_boards.sh" "$DB_FILE"
"$SCRIPT_DIR/insert_kv.sh" "$DB_FILE"
"$SCRIPT_DIR/insert_president_users.sh" "$DB_FILE" "$SCRIPT_DIR/presidents.csv"
"$SCRIPT_DIR/insert_check_user_status_rules.sh" "$DB_FILE" "$SCRIPT_DIR/check_user_status_rules.csv"

echo "Database initialization and inserts completed successfully."
