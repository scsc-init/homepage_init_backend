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
INSERT INTO key_value (key, value, writing_permission_level) VALUES ('footer-message', '서울대학교 컴퓨터 연구회\n회장 한성재 010-5583-1811\nscsc.snu@gmail.com', 500);
INSERT INTO key_value (key, value, writing_permission_level) VALUES ('leaders', NULL, 500);
EOF

echo "All key values inserted successfully into '$DB_FILE'."
