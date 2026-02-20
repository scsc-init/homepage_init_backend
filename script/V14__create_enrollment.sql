BEGIN TRANSACTION;

CREATE TABLE enrollment (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    year INTEGER NOT NULL CHECK (year >= 2025),
    semester INTEGER NOT NULL CHECK (semester IN (1, 2, 3, 4)),
    user_id TEXT NOT NULL,
    UNIQUE(year, semester, user_id),
    FOREIGN KEY (user_id) REFERENCES user(id)
);

INSERT INTO enrollment (year, semester, user_id)
SELECT 2026, 1, id FROM user WHERE status = 'active' AND role < 500
UNION ALL
SELECT 2026, 2, id FROM user WHERE status = 'active' AND role < 500;

ALTER TABLE user ADD COLUMN is_active BOOLEAN NOT NULL DEFAULT 0;
ALTER TABLE user ADD COLUMN is_banned BOOLEAN NOT NULL DEFAULT 0;
UPDATE user 
SET 
    is_active = (status = 'active'),
    is_banned = (status = 'banned');
ALTER TABLE user DROP COLUMN status;
DELETE FROM check_user_status_rule WHERE user_status!='banned';
ALTER TABLE check_user_status_rule DROP COLUMN user_status;

INSERT INTO key_value (key, value) VALUES 
    ('grant_semester_count_1', '2'),
    ('grant_semester_count_2', '3'),
    ('grant_semester_count_3', '2'),
    ('grant_semester_count_4', '3');

COMMIT;
