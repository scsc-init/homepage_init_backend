BEGIN;

ALTER TABLE sig DROP COLUMN is_rolling_admission;

ALTER TABLE sig ADD COLUMN is_rolling_admission TEXT 
    DEFAULT 'during_recruiting' 
    NOT NULL 
    CHECK (is_rolling_admission IN ('always', 'never', 'during_recruiting'));

COMMIT;