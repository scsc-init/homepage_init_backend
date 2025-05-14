#!/bin/bash

# Check for both database file and CSV file arguments
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <database_file_path> <csv_file_path>"
    exit 1
fi

DB_FILE="$1"
CSV_FILE="$2"

# Check if the database file exists
if [ ! -f "$DB_FILE" ]; then
    echo "Error: Database file '$DB_FILE' does not exist."
    exit 1
fi

# Check if the CSV file exists
if [ ! -f "$CSV_FILE" ]; then
    echo "Error: CSV file '$CSV_FILE' not found."
    exit 1
fi

# Read CSV line by line, skipping the header
tail -n +2 "$CSV_FILE" | while IFS=',' read -r college major_name; do
    # Trim whitespace
    college=$(echo "$college" | xargs)
    major_name=$(echo "$major_name" | xargs)

    # Insert into the major table
    sqlite3 "$DB_FILE" <<EOF
INSERT OR IGNORE INTO major (college, major_name)
VALUES ('$college', '$major_name');
EOF

done

echo "Import completed successfully into '$DB_FILE' using '$CSV_FILE'."
