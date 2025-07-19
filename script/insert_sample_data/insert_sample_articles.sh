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

# Insert Sample Article into Notice Board with President ID(president@example.com)
sqlite3 "$DB_FILE" <<EOF
INSERT INTO article (id, title, author_id, board_id) VALUES (0, 'Sample Notice', 'fc2eef7ad1e1f2f91786b4fd4f65508651373b0ad6fc4f13103c452369bc9703', 5);
EOF

CONTENT="# Sample Notice

This is an auto-generated markdown file.

"

mkdir -p ./static/article

echo "$CONTENT" > "./static/article/0.md"

echo "Sample articles inserted successfully into '$DB_FILE'."
