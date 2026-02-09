PRAGMA foreign_keys = OFF;
BEGIN TRANSACTION;

ALTER TABLE pig RENAME TO pig_old;

CREATE TABLE pig (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    content_id INTEGER NOT NULL UNIQUE,
    status TEXT NOT NULL CHECK (status IN ('surveying', 'recruiting', 'active', 'inactive')),
    year INTEGER NOT NULL CHECK (year >= 2025),
    semester INTEGER NOT NULL CHECK (semester IN (1, 2, 3, 4)),

    should_extend BOOLEAN NOT NULL DEFAULT FALSE,
    is_rolling_admission TEXT DEFAULT 'always' NOT NULL CHECK (is_rolling_admission IN ('always', 'never', 'during_recruiting_period')),

    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    owner TEXT NOT NULL,
    UNIQUE (title, year, semester),
    FOREIGN KEY (owner) REFERENCES user(id) ON DELETE RESTRICT,
    FOREIGN KEY (content_id) REFERENCES article(id) ON DELETE RESTRICT
);

INSERT INTO pig (id, title, description, content_id, status, year, semester, should_extend, is_rolling_admission, created_at, updated_at, owner)
SELECT id, title, description, content_id, status, year, semester, should_extend, CASE WHEN is_rolling_admission = true THEN 'always' ELSE 'never' END, created_at, CURRENT_TIMESTAMP, owner
FROM pig_old;

ALTER TABLE pig_website RENAME TO pig_website_old;

CREATE TABLE pig_website (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pig_id INTEGER NOT NULL,
    label TEXT NOT NULL,
    url TEXT NOT NULL,
    sort_order INTEGER DEFAULT 0 NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    FOREIGN KEY (pig_id) REFERENCES pig(id) ON DELETE CASCADE
);

INSERT INTO pig_website (id, pig_id, label, url, sort_order, created_at, updated_at)
SELECT id, pig_id, label, url, sort_order, created_at, CURRENT_TIMESTAMP
FROM pig_website_old;

DROP TABLE pig_website_old;

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

DROP TABLE pig_old;
PRAGMA foreign_keys = ON;

END;
