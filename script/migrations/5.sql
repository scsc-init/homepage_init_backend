PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS key_value (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    writing_permission_level INTEGER NOT NULL
        REFERENCES user_role(level) ON DELETE RESTRICT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

INSERT OR IGNORE INTO key_value (key, value, writing_permission_level)
VALUES ('footer-message', '서울대학교 컴퓨터 연구회\n회장 한성재 010-5583-1811\nscsc.snu@gmail.com', 500);

DROP TRIGGER IF EXISTS trg_key_value_updated_at;
CREATE TRIGGER trg_key_value_updated_at
AFTER UPDATE OF key_value
FOR EACH ROW
BEGIN
    UPDATE key_value
    SET updated_at = CURRENT_TIMESTAMP
    WHERE key = OLD.key;
END;
