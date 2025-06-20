#!/bin/bash

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

sqlite3 "$DB_FILE" <<EOF
INSERT INTO scsc_global_status (id, status, year, semester) VALUES (1, 'inactive', 2025, 1);
EOF

echo "SCSC Global Status inserted successfully into '$DB_FILE'."
