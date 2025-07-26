#!/bin/bash

set -e

# Check arguments
if [ $# -ne 2 ]; then
  echo "Usage: $0 <database_file> <csv_file>"
  echo "CSV should have a header: email,name"
  exit 1
fi

DB_FILE="$1"
CSV_FILE="$2"

if [ ! -f "$DB_FILE" ]; then
  echo "Error: Database file '$DB_FILE' does not exist."
  exit 1
fi

if [ ! -f "$CSV_FILE" ]; then
  echo "Error: CSV file '$CSV_FILE' does not exist."
  exit 1
fi

generate_hash() {
  echo -n "$1" | sha256sum | awk '{print $1}'
}

# Initialize counters
phone_number_base=9900000001
student_id_base=200000001

SQL_VALUES=""

# Skip header using tail
while IFS=',' read -r email name; do
  id=$(generate_hash "$email")
  phone="0${phone_number_base}"
  student_id="${student_id_base}"

  SQL_VALUES+="  ('$id', '$email', '$name', '$phone', '$student_id', 1000, 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 1),\n"

  ((phone_number_base++))
  ((student_id_base++))
done < <(tail -n +2 "$CSV_FILE")

# Remove trailing comma
SQL_VALUES=$(echo -e "$SQL_VALUES")
SQL_VALUES="${SQL_VALUES%,*}"

sqlite3 "$DB_FILE" <<EOF
INSERT INTO user (id, email, name, phone, student_id, role, status, last_login, created_at, updated_at, major_id)
VALUES
$SQL_VALUES;
EOF

echo "President users from '$CSV_FILE' inserted into '$DB_FILE'."
