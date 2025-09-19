ALTER TABLE sig ADD COLUMN is_rolling_admission BOOLEAN NOT NULL DEFAULT FALSE;
ALTER TABLE pig ADD COLUMN is_rolling_admission BOOLEAN NOT NULL DEFAULT FALSE;

CREATE INDEX IF NOT EXISTS idx_pig_owner ON pig(owner);
CREATE INDEX IF NOT EXISTS idx_pig_term ON pig(year, semester);

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