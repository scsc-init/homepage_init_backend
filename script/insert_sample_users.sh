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
EMAIL4="member@example.com"
EMAIL5="oldboy@example.com"
EMAIL6="dormant@example.com"

ID1=$(generate_hash "$EMAIL1")
ID2=$(generate_hash "$EMAIL2")
ID3=$(generate_hash "$EMAIL3")
ID4=$(generate_hash "$EMAIL4")
ID5=$(generate_hash "$EMAIL5")
ID6=$(generate_hash "$EMAIL6")

sqlite3 "$DB_FILE" <<EOF
INSERT INTO user (id, email, name, phone, student_id, role, status, last_login, created_at, updated_at, major_id)
VALUES
  ('$ID1', '$EMAIL1', 'Alice Kim', '01012345678', '202512345', 200, 'pending', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 1),
  ('$ID2', '$EMAIL2', 'Bob Lee', '01023456789', '202512346', 500, 'pending', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 1),
  ('$ID3', '$EMAIL3', 'Carol Choi', '01034567890', '202512347', 1000, 'pending', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 1),
  ('$ID4', '$EMAIL4', 'David Park', '01045678901', '202512348', 300, 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 2),
  ('$ID5', '$EMAIL5', 'Eunseo Han', '01056789012', '202512349', 400, 'banned', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 2),
  ('$ID6', '$EMAIL6', 'Gyuri Seo', '01067890123', '202512350', 100, 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 3);
EOF

echo "Sample users and discord bot user inserted successfully into '$DB_FILE'."
