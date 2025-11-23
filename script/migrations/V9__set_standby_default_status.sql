BEGIN TRANSACTION;

DELETE FROM check_user_status_rule
WHERE user_status = 'standby';

CREATE TABLE user_new (
    id TEXT PRIMARY KEY,
    email TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    phone TEXT NOT NULL UNIQUE,
    student_id TEXT NOT NULL UNIQUE,
    role INTEGER NOT NULL,
    status TEXT DEFAULT 'standby' NOT NULL CHECK (status IN ('active', 'pending', 'standby', 'banned')),
    discord_id INTEGER UNIQUE DEFAULT NULL,
    discord_name TEXT UNIQUE DEFAULT NULL,
    profile_picture TEXT,
    profile_picture_is_url BOOLEAN NOT NULL DEFAULT FALSE,
    last_login DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    major_id INTEGER NOT NULL,
    FOREIGN KEY (major_id) REFERENCES major(id) ON DELETE RESTRICT,
    FOREIGN KEY (role) REFERENCES user_role(level) ON DELETE RESTRICT
);

INSERT INTO user_new (
    id,
    email,
    name,
    phone,
    student_id,
    role,
    status,
    discord_id,
    discord_name,
    profile_picture,
    profile_picture_is_url,
    last_login,
    created_at,
    updated_at,
    major_id
)
SELECT
    id,
    email,
    name,
    phone,
    student_id,
    role,
    status,
    discord_id,
    discord_name,
    profile_picture,
    profile_picture_is_url,
    last_login,
    created_at,
    updated_at,
    major_id
FROM user;

DROP TABLE user;

ALTER TABLE user_new RENAME TO user;

CREATE INDEX idx_user_major ON user(major_id);
CREATE INDEX idx_user_role ON user(role);

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
    OLD.discord_id != NEW.discord_id OR
    OLD.discord_name != NEW.discord_name OR
    OLD.major_id != NEW.major_id
BEGIN
    UPDATE user
    SET updated_at = CURRENT_TIMESTAMP
    WHERE id = OLD.id;
END;

COMMIT;
