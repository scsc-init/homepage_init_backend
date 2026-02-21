BEGIN TRANSACTION;

CREATE TABLE enrollment (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    year INTEGER NOT NULL CHECK (year >= 2025),
    semester INTEGER NOT NULL CHECK (semester IN (1, 2, 3, 4)),
    user_id TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
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
DROP TRIGGER update_user_updated_at;
ALTER TABLE user DROP COLUMN status;
CREATE TRIGGER update_user_updated_at
AFTER UPDATE ON user
FOR EACH ROW
WHEN 
    OLD.email != NEW.email OR
    OLD.name != NEW.name OR
    OLD.phone != NEW.phone OR
    OLD.student_id != NEW.student_id OR
    OLD.role != NEW.role OR
    OLD.is_active != NEW.is_active OR
    OLD.is_banned != NEW.is_banned OR
    OLD.discord_id IS NOT NEW.discord_id OR
    OLD.discord_name IS NOT NEW.discord_name OR
    OLD.major_id != NEW.major_id
BEGIN
    UPDATE user
    SET updated_at = CURRENT_TIMESTAMP
    WHERE id = OLD.id;
END;

CREATE TABLE check_user_status_rule_new (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    method TEXT NOT NULL CHECK (method IN ('GET', 'POST')),
    path TEXT NOT NULL,
    UNIQUE (method, path)
);
INSERT INTO check_user_status_rule_new (method, path)
SELECT method, path 
FROM check_user_status_rule 
WHERE user_status = 'banned';
DROP TABLE check_user_status_rule;
ALTER TABLE check_user_status_rule_new RENAME TO check_user_status_rule;

INSERT INTO key_value (key, value) VALUES 
    ('grant_semester_count_1', '2'),
    ('grant_semester_count_2', '3'),
    ('grant_semester_count_3', '2'),
    ('grant_semester_count_4', '3');

COMMIT;
