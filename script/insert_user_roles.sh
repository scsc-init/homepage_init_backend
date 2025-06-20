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
INSERT INTO user_role (level, name, kor_name)
VALUES
  (0, 'lowest', '최저권한'),
  (100, 'dormant', '휴회원'),
  (200, 'newcomer', '준회원'),
  (300, 'member', '정회원'),
  (400, 'oldboy', '졸업생'),
  (500, 'executive', '운영진'),
  (1000, 'president', '회장');
EOF

echo "User roles inserted successfully into '$DB_FILE'."
