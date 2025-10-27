PRAGMA foreign_keys = ON;

BEGIN TRANSACTION;

ALTER TABLE key_value RENAME TO key_value_old;

CREATE TABLE key_value (
    key TEXT PRIMARY KEY,
    value TEXT,
    writing_permission_level INTEGER NOT NULL DEFAULT 500
        REFERENCES user_role(level) ON DELETE RESTRICT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO key_value (
    key,
    value,
    writing_permission_level,
    created_at,
    updated_at
)
SELECT
    key,
    value,
    writing_permission_level,
    created_at,
    updated_at
FROM key_value_old;

DROP TABLE key_value_old;

INSERT OR IGNORE INTO key_value (key, value, writing_permission_level)
VALUES 
    ('president', NULL, 500),
    ('vice-president', NULL, 500);

DROP TRIGGER IF EXISTS key_value_updated_at;
CREATE TRIGGER key_value_updated_at
AFTER UPDATE OF value ON key_value
FOR EACH ROW
WHEN NEW.updated_at = OLD.updated_at
BEGIN
    UPDATE key_value
    SET updated_at = CURRENT_TIMESTAMP
    WHERE key = NEW.key;
END;

COMMIT;
