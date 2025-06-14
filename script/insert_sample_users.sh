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
EMAIL1="user1@example.com"
EMAIL2="exec@example.com"
EMAIL3="president@example.com"

ID1=$(generate_hash "$EMAIL1")
ID2=$(generate_hash "$EMAIL2")
ID3=$(generate_hash "$EMAIL3")

sqlite3 "$DB_FILE" <<EOF
INSERT INTO user (id, email, name, phone, student_id, role, status, last_login, created_at, updated_at, major_id)
VALUES
  ('$ID1', '$EMAIL1', 'Alice Kim', '01012345678', '202512345', 200, 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 1),
  ('$ID2', '$EMAIL2', 'Bob Lee', '01023456789', '202512346', 500, 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 1),
  ('$ID3', '$EMAIL3', 'Carol Choi', '01034567890', '202512347', 600, 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 1);
EOF

echo "✅ Sample users inserted successfully into '$DB_FILE'."
