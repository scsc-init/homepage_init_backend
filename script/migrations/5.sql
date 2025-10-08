PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS key_value (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    writing_permission_level INTEGER NOT NULL DEFAULT 500
        REFERENCES user_role(level) ON DELETE RESTRICT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

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

INSERT OR IGNORE INTO key_value (key, value, writing_permission_level)
VALUES ('footer-message', '서울대학교 컴퓨터 연구회\n회장 한성재 010-5583-1811\nscsc.snu@gmail.com', 500);
