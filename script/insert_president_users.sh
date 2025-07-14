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

# Helper function to generate SHA-256 hash of an email
generate_hash() {
  echo -n "$1" | sha256sum | awk '{print $1}'
}

# Sample user data
EMAIL2="zizonms@snu.ac.kr"
EMAIL3="tteokgook1@snu.ac.kr"
ID2=$(generate_hash "$EMAIL2")
ID3=$(generate_hash "$EMAIL3")

sqlite3 "$DB_FILE" <<EOF
INSERT INTO user (id, email, name, phone, student_id, role, status, last_login, created_at, updated_at, major_id)
VALUES
  ('$ID2', '$EMAIL2', '강명석', '09900000002', '200000002', 1000, 'pending', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 1),
  ('$ID3', '$EMAIL3', '이한경', '09900000003', '200000003', 1000, 'pending', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 1);
EOF

echo "President users inserted successfully into '$DB_FILE'."
