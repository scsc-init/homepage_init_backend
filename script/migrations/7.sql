BEGIN TRANSACTION;

UPDATE sig 
SET status = 'recruiting', updated_at = CURRENT_TIMESTAMP 
WHERE status = 'surveying';

UPDATE pig 
SET status = 'recruiting', updated_at = CURRENT_TIMESTAMP 
WHERE status = 'surveying';

UPDATE scsc_global_status 
SET status = 'recruiting', updated_at = CURRENT_TIMESTAMP 
WHERE status = 'surveying';


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

COMMIT;
