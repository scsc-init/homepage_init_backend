#!/bin/bash

set -e

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
INSERT INTO board (id, name, description, writing_permission_level, reading_permission_level) VALUES (1, 'Sig', 'sig advertising board', 1000, 0);
INSERT INTO board (id, name, description, writing_permission_level, reading_permission_level) VALUES (2, 'Pig', 'pig advertising board', 1000, 0);
INSERT INTO board (id, name, description, writing_permission_level, reading_permission_level) VALUES (3, 'Project Archive', 'archive of various projects held in the club', 300, 0);
INSERT INTO board (id, name, description, writing_permission_level, reading_permission_level) VALUES (4, 'Album', 'photos of club members and activities', 500, 0);
INSERT INTO board (id, name, description, writing_permission_level, reading_permission_level) VALUES (5, 'Notice', 'notices from club executive', 500, 100);
INSERT INTO board (id, name, description, writing_permission_level, reading_permission_level) VALUES (6, 'Grant', 'applications for sig/pig grant', 200, 500);
EOF

echo "All boards inserted successfully into '$DB_FILE'."
