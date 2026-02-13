PRAGMA foreign_keys = OFF;

BEGIN TRANSACTION;

ALTER TABLE sig RENAME TO sig_old;

CREATE TABLE sig (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    content_id INTEGER NOT NULL UNIQUE,
    status TEXT NOT NULL CHECK (status IN ('recruiting', 'active', 'inactive')),

    year INTEGER NOT NULL CHECK (year >= 2025),
    semester INTEGER NOT NULL CHECK (semester IN (1, 2, 3, 4)),

    created_year INTEGER NOT NULL CHECK (created_year >= 2025),
    created_semester INTEGER NOT NULL CHECK (created_semester IN (1, 2, 3, 4)),

    should_extend BOOLEAN NOT NULL DEFAULT 0,
    is_rolling_admission BOOLEAN NOT NULL DEFAULT FALSE,

    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    owner TEXT NOT NULL,

    UNIQUE (title, created_year, created_semester),
    FOREIGN KEY (owner) REFERENCES user(id) ON DELETE RESTRICT,
    FOREIGN KEY (content_id) REFERENCES article(id) ON DELETE RESTRICT
);

INSERT INTO sig (
    id, title, description, content_id, status,
    year, semester,
    created_year, created_semester,
    should_extend, is_rolling_admission,
    created_at, updated_at,
    owner
)
SELECT
    id, title, description, content_id, status,
    year, semester,
    year, semester,
    should_extend, is_rolling_admission,
    created_at, updated_at,
    owner
FROM sig_old;

DROP TABLE sig_old;

CREATE INDEX IF NOT EXISTS idx_sig_term ON sig(year, semester);


ALTER TABLE pig RENAME TO pig_old;

CREATE TABLE pig (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    content_id INTEGER NOT NULL UNIQUE,
    status TEXT NOT NULL CHECK (status IN ('recruiting', 'active', 'inactive')),

    year INTEGER NOT NULL CHECK (year >= 2025),
    semester INTEGER NOT NULL CHECK (semester IN (1, 2, 3, 4)),

    created_year INTEGER NOT NULL CHECK (created_year >= 2025),
    created_semester INTEGER NOT NULL CHECK (created_semester IN (1, 2, 3, 4)),

    should_extend BOOLEAN NOT NULL DEFAULT 0,
    is_rolling_admission BOOLEAN NOT NULL DEFAULT FALSE,

    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    owner TEXT NOT NULL,

    UNIQUE (title, created_year, created_semester),
    FOREIGN KEY (owner) REFERENCES user(id) ON DELETE RESTRICT,
    FOREIGN KEY (content_id) REFERENCES article(id) ON DELETE RESTRICT
);

INSERT INTO pig (
    id, title, description, content_id, status,
    year, semester,
    created_year, created_semester,
    should_extend, is_rolling_admission,
    created_at, updated_at,
    owner
)
SELECT
    id, title, description, content_id, status,
    year, semester,
    year, semester,
    should_extend, is_rolling_admission,
    created_at, updated_at,
    owner
FROM pig_old;

DROP TABLE pig_old;

CREATE INDEX IF NOT EXISTS idx_pig_owner ON pig(owner);
CREATE INDEX IF NOT EXISTS idx_pig_term ON pig(year, semester);


ALTER TABLE sig_member RENAME TO sig_member_old;

CREATE TABLE sig_member (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ig_id INTEGER NOT NULL,
    user_id TEXT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    UNIQUE (ig_id, user_id),
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
    FOREIGN KEY (ig_id) REFERENCES sig(id) ON DELETE CASCADE
);

INSERT INTO sig_member (id, ig_id, user_id, created_at)
SELECT id, ig_id, user_id, created_at
FROM sig_member_old;

DROP TABLE sig_member_old;


ALTER TABLE pig_member RENAME TO pig_member_old;

CREATE TABLE pig_member (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ig_id INTEGER NOT NULL,
    user_id TEXT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    UNIQUE (ig_id, user_id),
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
    FOREIGN KEY (ig_id) REFERENCES pig(id) ON DELETE CASCADE
);

INSERT INTO pig_member (id, ig_id, user_id, created_at)
SELECT id, ig_id, user_id, created_at
FROM pig_member_old;

DROP TABLE pig_member_old;


ALTER TABLE pig_website RENAME TO pig_website_old;

CREATE TABLE pig_website (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pig_id INTEGER NOT NULL,
    label TEXT NOT NULL,
    url TEXT NOT NULL,
    sort_order INTEGER NOT NULL DEFAULT 0,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (pig_id) REFERENCES pig(id) ON DELETE CASCADE
);

INSERT INTO pig_website (id, pig_id, label, url, sort_order, created_at, updated_at)
SELECT id, pig_id, label, url, sort_order, created_at, updated_at
FROM pig_website_old;

DROP TABLE pig_website_old;


DROP TRIGGER IF EXISTS update_sig_updated_at;
CREATE TRIGGER update_sig_updated_at
AFTER UPDATE OF title, description, content_id, status, year, semester, owner, should_extend, is_rolling_admission ON sig
FOR EACH ROW
BEGIN
    UPDATE sig SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
END;

DROP TRIGGER IF EXISTS update_pig_updated_at;
CREATE TRIGGER update_pig_updated_at
AFTER UPDATE OF title, description, content_id, status, year, semester, owner, should_extend, is_rolling_admission ON pig
FOR EACH ROW
BEGIN
    UPDATE pig SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
END;


DROP TRIGGER IF EXISTS prevent_sig_created_term_update;
CREATE TRIGGER prevent_sig_created_term_update
BEFORE UPDATE OF created_year, created_semester ON sig
FOR EACH ROW
WHEN OLD.created_year != NEW.created_year OR OLD.created_semester != NEW.created_semester
BEGIN
    SELECT RAISE(ABORT, 'sig.created_term is immutable');
END;

DROP TRIGGER IF EXISTS prevent_pig_created_term_update;
CREATE TRIGGER prevent_pig_created_term_update
BEFORE UPDATE OF created_year, created_semester ON pig
FOR EACH ROW
WHEN OLD.created_year != NEW.created_year OR OLD.created_semester != NEW.created_semester
BEGIN
    SELECT RAISE(ABORT, 'pig.created_term is immutable');
END;

COMMIT;

PRAGMA foreign_keys = ON;
