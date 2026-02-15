PRAGMA foreign_keys=OFF;

BEGIN TRANSACTION;

-- ========== SIG ==========

CREATE TABLE sig_new (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    content_id INTEGER NOT NULL UNIQUE,
    status TEXT NOT NULL CHECK (status IN ('surveying', 'recruiting', 'active', 'inactive')),
    created_year INTEGER NOT NULL CHECK (created_year >= 2025),
    created_semester INTEGER NOT NULL CHECK (created_semester IN (1, 2, 3, 4)),
    year INTEGER NOT NULL CHECK (year >= 2025),
    semester INTEGER NOT NULL CHECK (semester IN (1, 2, 3, 4)),

    should_extend BOOLEAN NOT NULL DEFAULT FALSE,
    is_rolling_admission TEXT NOT NULL DEFAULT 'during_recruiting'
        CHECK (is_rolling_admission IN ('always', 'never', 'during_recruiting')),


    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    owner TEXT NOT NULL,
    UNIQUE(created_year, created_semester, title),
    UNIQUE(year, semester, title),
    FOREIGN KEY (owner) REFERENCES user(id) ON DELETE RESTRICT,
    FOREIGN KEY (content_id) REFERENCES article(id) ON DELETE RESTRICT
);

INSERT INTO sig_new (
    id,
    title,
    description,
    content_id,
    status,
    created_year,
    created_semester,
    year,
    semester,
    should_extend,
    is_rolling_admission,
    created_at,
    updated_at,
    owner
)
SELECT
    id,
    title,
    description,
    content_id,
    status,
    year,
    semester,
    year,
    semester,
    should_extend,
    is_rolling_admission,
    created_at,
    updated_at,
    owner
FROM sig;

DROP TABLE sig;
ALTER TABLE sig_new RENAME TO sig;

DROP TRIGGER IF EXISTS update_sig_updated_at;
CREATE TRIGGER update_sig_updated_at
AFTER UPDATE OF title, description, content_id, status, year, semester, owner, should_extend, is_rolling_admission ON sig
FOR EACH ROW
BEGIN
    UPDATE sig SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
END;

-- ========== PIG ==========

CREATE TABLE pig_new (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    content_id INTEGER NOT NULL UNIQUE,
    status TEXT NOT NULL CHECK (status IN ('surveying', 'recruiting', 'active', 'inactive')),
    created_year INTEGER NOT NULL CHECK (created_year >= 2025),
    created_semester INTEGER NOT NULL CHECK (created_semester IN (1, 2, 3, 4)),
    year INTEGER NOT NULL CHECK (year >= 2025),
    semester INTEGER NOT NULL CHECK (semester IN (1, 2, 3, 4)),

    should_extend BOOLEAN NOT NULL DEFAULT FALSE,
    is_rolling_admission BOOLEAN NOT NULL DEFAULT FALSE,

    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    owner TEXT NOT NULL,
    UNIQUE(created_year, created_semester, title),
    UNIQUE(year, semester, title),
    FOREIGN KEY (owner) REFERENCES user(id) ON DELETE RESTRICT,
    FOREIGN KEY (content_id) REFERENCES article(id) ON DELETE RESTRICT
);

INSERT INTO pig_new (
    id,
    title,
    description,
    content_id,
    status,
    created_year,
    created_semester,
    year,
    semester,
    should_extend,
    is_rolling_admission,
    created_at,
    updated_at,
    owner
)
SELECT
    id,
    title,
    description,
    content_id,
    status,
    year,
    semester,
    year,
    semester,
    should_extend,
    is_rolling_admission,
    created_at,
    updated_at,
    owner
FROM pig;

DROP TABLE pig;
ALTER TABLE pig_new RENAME TO pig;

DROP TRIGGER IF EXISTS update_pig_updated_at;
CREATE TRIGGER update_pig_updated_at
AFTER UPDATE OF title, description, content_id, status, year, semester, owner, should_extend, is_rolling_admission ON pig
FOR EACH ROW
BEGIN
    UPDATE pig SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
END;


COMMIT;

PRAGMA foreign_keys=ON;
