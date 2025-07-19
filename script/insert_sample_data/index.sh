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

# Check if the database file exists
if [ ! -f "$DB_FILE" ]; then
    echo "Error: Database file '$DB_FILE' does not exist."
    exit 1
fi

echo "Inserting sample data at $DB_FILE..."

"$SCRIPT_DIR/insert_sample_users.sh" "$DB_FILE"
"$SCRIPT_DIR/insert_sample_articles.sh" "$DB_FILE"
"$SCRIPT_DIR/insert_sample_comments.sh" "$DB_FILE"

echo "Inserts completed successfully."
