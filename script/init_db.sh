#!/bin/bash

# Check if a database file name is provided
if [ -z "$1" ]; then
    echo "Usage: $0 <database_file_name>"
    exit 1
fi

DB_FILE="$1"

# Check if the database file already exists
if [ -f "$DB_FILE" ]; then
    echo "Error: Database file '$DB_FILE' already exists. Aborting."
    exit 1
fi

# Execute SQL commands using a here-document
sqlite3 "$DB_FILE" <<EOF
-- Enable foreign key constraints
PRAGMA foreign_keys = ON;

-- Create 'major' table
CREATE TABLE major (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    college TEXT NOT NULL,
    major_name TEXT NOT NULL,
    UNIQUE (college, major_name)
);

-- Create 'user' table
CREATE TABLE user (
    id TEXT PRIMARY KEY,
    email TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    phone TEXT NOT NULL UNIQUE,
    student_id TEXT NOT NULL UNIQUE,
    role TEXT DEFAULT 'user' NOT NULL CHECK (role IN ('user', 'executive', 'president')),
    status TEXT DEFAULT 'pending' NOT NULL CHECK (status IN ('active', 'pending', 'banned')),
    last_login DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    major_id INTEGER NOT NULL,
    FOREIGN KEY (major_id) REFERENCES major(id) ON DELETE RESTRICT
);

-- Create trigger to update 'updated_at'
CREATE TRIGGER update_user_updated_at
AFTER UPDATE ON user
FOR EACH ROW
WHEN 
    OLD.email != NEW.email OR
    OLD.name != NEW.name OR
    OLD.phone != NEW.phone OR
    OLD.student_id != NEW.student_id OR
    OLD.role != NEW.role OR
    OLD.status != NEW.status OR
    OLD.major_id != NEW.major_id
BEGIN
    UPDATE user
    SET updated_at = CURRENT_TIMESTAMP
    WHERE id = OLD.id;
END;
EOF

echo "Database initialized and schema created in '$DB_FILE'."
