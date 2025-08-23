#!/bin/bash

set -e

# Check arguments
if [ $# -ne 2 ]; then
  echo "Usage: $0 <database_file> <csv_file>"
  echo "CSV should have a header: user_status,method,path"
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

# Initialize the SQL values string
SQL_VALUES=""

# Skip header using tail and read each row
while IFS=',' read -r user_status method path; do
  # Escape single quotes in path to prevent SQL injection issues, if any exist.
  # For this specific schema, it's unlikely ' or " would be in user_status or method
  # but it's good practice for string inputs.
  escaped_path=$(echo "$path" | sed "s/'/''/g")

  # Build the VALUES part of the SQL INSERT statement
  SQL_VALUES+="  ('$user_status', '$method', '$escaped_path'),\n"
done < <(tail -n +2 "$CSV_FILE")

# Remove the trailing comma from the last set of values
SQL_VALUES=$(echo -e "$SQL_VALUES")
SQL_VALUES="${SQL_VALUES%,*}"

# Execute the INSERT statement using sqlite3
if [ -z "$SQL_VALUES" ]; then
  echo "No data to insert from CSV file '$CSV_FILE'."
else
  sqlite3 "$DB_FILE" <<EOF
  INSERT INTO check_user_status_rule (user_status, method, path)
  VALUES
  $SQL_VALUES;
EOF

  echo "Rules from '$CSV_FILE' inserted into 'check_user_status_rule' table in '$DB_FILE'."
fi
