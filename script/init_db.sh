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

-- Create index on foreign key
CREATE INDEX idx_user_major ON user(major_id);

-- Prevent updates to major(id)
CREATE TRIGGER prevent_major_id_update
BEFORE UPDATE ON major
FOR EACH ROW
WHEN OLD.id != NEW.id
BEGIN
    SELECT RAISE(ABORT, 'Updating major.id is not allowed');
END;

-- Create SIG/PIG table
CREATE TABLE sig (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    content_src TEXT NOT NULL UNIQUE,
    status TEXT NOT NULL CHECK (status IN ('surveying', 'recruiting', 'active', 'inactive')),
    year INTEGER NOT NULL CHECK (year >= 2025),
    semester INTEGER NOT NULL CHECK (semester IN (1, 2)),

    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    owner TEXT NOT NULL,
    UNIQUE (title, year, semester),
    FOREIGN KEY (owner) REFERENCES user(id) ON DELETE RESTRICT
);
CREATE TABLE pig (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    content_src TEXT NOT NULL UNIQUE,
    status TEXT NOT NULL CHECK (status IN ('surveying', 'recruiting', 'active', 'inactive')),
    year INTEGER NOT NULL CHECK (year >= 2025),
    semester INTEGER NOT NULL CHECK (semester IN (1, 2)),

    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    owner TEXT NOT NULL,
    UNIQUE (title, year, semester),
    FOREIGN KEY (owner) REFERENCES user(id) ON DELETE RESTRICT
);

-- Create SIG/PIG member table
CREATE TABLE sig_member (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ig_id INTEGER NOT NULL,
    user_id TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('surveying', 'recruiting', 'active', 'inactive')),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    UNIQUE (ig_id, user_id, status),
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
    FOREIGN KEY (ig_id) REFERENCES sig(id) ON DELETE CASCADE
);
CREATE TABLE pig_member (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ig_id INTEGER NOT NULL,
    user_id TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('surveying', 'recruiting', 'active', 'inactive')),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    UNIQUE (ig_id, user_id, status),
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
    FOREIGN KEY (ig_id) REFERENCES pig(id) ON DELETE CASCADE
);

-- Create index for SIG/PIG
CREATE INDEX idx_sig_owner ON sig(owner);
CREATE INDEX idx_sig_term ON sig(year, semester);
CREATE INDEX idx_sig_member_user ON sig_member(user_id);
CREATE INDEX idx_sig_member_ig ON sig_member(ig_id);
CREATE INDEX idx_pig_member_user ON pig_member(user_id);
CREATE INDEX idx_pig_member_ig ON pig_member(ig_id);

-- Create trigger for SIG/PIG
CREATE TRIGGER update_sig_updated_at
AFTER UPDATE ON sig
FOR EACH ROW
WHEN 
    OLD.title != NEW.title OR
    OLD.description != NEW.description OR
    OLD.content_src != NEW.content_src OR
    OLD.status != NEW.status OR
    OLD.year != NEW.year OR
    OLD.semester != NEW.semester OR
    OLD.owner != NEW.owner
BEGIN
    UPDATE sig
    SET updated_at = CURRENT_TIMESTAMP
    WHERE id = OLD.id;
END;

CREATE TRIGGER update_pig_updated_at
AFTER UPDATE ON pig
FOR EACH ROW
WHEN 
    OLD.title != NEW.title OR
    OLD.description != NEW.description OR
    OLD.content_src != NEW.content_src OR
    OLD.status != NEW.status OR
    OLD.year != NEW.year OR
    OLD.semester != NEW.semester OR
    OLD.owner != NEW.owner
BEGIN
    UPDATE pig
    SET updated_at = CURRENT_TIMESTAMP
    WHERE id = OLD.id;
END;

-- SIG/PIG global status
CREATE TABLE sig_global_status (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    status TEXT NOT NULL CHECK (status IN ('surveying', 'recruiting', 'active', 'inactive')),
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE pig_global_status (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    status TEXT NOT NULL CHECK (status IN ('surveying', 'recruiting', 'active', 'inactive')),
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TRIGGER update_sig_global_status_updated_at
AFTER UPDATE ON sig_global_status
FOR EACH ROW
WHEN 
    OLD.status != NEW.status
BEGIN
    UPDATE sig_global_status
    SET updated_at = CURRENT_TIMESTAMP
    WHERE id = OLD.id;
END;

CREATE TRIGGER update_pig_global_status_updated_at
AFTER UPDATE ON pig_global_status
FOR EACH ROW
WHEN 
    OLD.status != NEW.status
BEGIN
    UPDATE pig_global_status
    SET updated_at = CURRENT_TIMESTAMP
    WHERE id = OLD.id;
END;

INSERT INTO sig_global_status (id, status) VALUES (1, 'inactive');
INSERT INTO pig_global_status (id, status) VALUES (1, 'inactive');

-- File metadata table
CREATE TABLE file_metadata (
    id TEXT PRIMARY KEY,
    original_filename TEXT NOT NULL,
    size INT NOT NULL,
    mime_type TEXT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    owner TEXT,
    FOREIGN KEY (owner) REFERENCES user(id) ON DELETE SET NULL
);
CREATE INDEX idx_file_metadata_owner ON file_metadata(owner);

-- Board, Article, Comment table
CREATE TABLE "board" (
	"id"	INTEGER,
	"name"	TEXT,
	"description"	TEXT,
	"writing_permission_level"	INTEGER DEFAULT 0,
	"reading_permission_level"	INTEGER DEFAULT 0,
	PRIMARY KEY("id" AUTOINCREMENT)
);

CREATE TABLE "article" (
	"id"	INTEGER,
	"title"	TEXT,
	"content"	TEXT,
	"author_id"	TEXT,
	"board_id"	INTEGER,
	"created_at"	DATETIME DEFAULT CURRENT_TIMESTAMP,
	"updated_at"	DATETIME DEFAULT CURRENT_TIMESTAMP,
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY("author_id") REFERENCES "user"("id") ON DELETE SET NULL,
	FOREIGN KEY("board_id") REFERENCES "board"("id") ON DELETE CASCADE
);

CREATE TABLE "comment" (
	"id"	INTEGER,
	"content"	TEXT,
	"author_id"	TEXT,
	"board_id"	INTEGER,
	"post_id"	INTEGER,
	"parent_id"	INTEGER,
	"created_at"	DATETIME DEFAULT CURRENT_TIMESTAMP,
	"updated_at"	DATETIME DEFAULT CURRENT_TIMESTAMP,
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY("author_id") REFERENCES "user"("id"),
	FOREIGN KEY("board_id") REFERENCES "board"("id"),
	FOREIGN KEY("post_id") REFERENCES "article"("id"),
	FOREIGN KEY("parent_id") REFERENCES "comment"("id")
);

EOF

echo "Database initialized and schema created in '$DB_FILE'."
