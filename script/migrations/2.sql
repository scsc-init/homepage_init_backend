ALTER TABLE sig ADD COLUMN should_extend BOOLEAN NOT NULL DEFAULT 0;
ALTER TABLE pig ADD COLUMN should_extend BOOLEAN NOT NULL DEFAULT 0;
ALTER TABLE sig ALTER COLUMN content_id SET NOT NULL;
ALTER TABLE pig ALTER COLUMN content_id SET NOT NULL;

DROP TRIGGER IF EXISTS update_sig_updated_at ON sig;
CREATE TRIGGER update_sig_updated_at
AFTER UPDATE ON sig
FOR EACH ROW
WHEN 
    OLD.title != NEW.title OR
    OLD.description != NEW.description OR
    OLD.content_id != NEW.content_id OR
    OLD.status != NEW.status OR
    OLD.year != NEW.year OR
    OLD.semester != NEW.semester OR
    OLD.owner != NEW.owner OR
    OLD.should_extend != NEW.should_extend
BEGIN
    UPDATE sig
    SET updated_at = CURRENT_TIMESTAMP
    WHERE id = OLD.id;
END;

DROP TRIGGER IF EXISTS update_pig_updated_at ON pig;
CREATE TRIGGER update_pig_updated_at
AFTER UPDATE ON pig
FOR EACH ROW
WHEN 
    OLD.title != NEW.title OR
    OLD.description != NEW.description OR
    OLD.content_id != NEW.content_id OR
    OLD.status != NEW.status OR
    OLD.year != NEW.year OR
    OLD.semester != NEW.semester OR
    OLD.owner != NEW.owner OR
    OLD.should_extend != NEW.should_extend
BEGIN
    UPDATE pig
    SET updated_at = CURRENT_TIMESTAMP
    WHERE id = OLD.id;
END;
