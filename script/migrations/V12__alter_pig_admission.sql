BEGIN TRANSACTION;

ALTER TABLE pig ADD is_rolling_admission_new TEXT DEFAULT 'always' NOT NULL CHECK (is_rolling_admission IN ('always', 'never', 'during_recruiting_period'));

UPDATE pig
SET is_rolling_admission_new = 'never', updated_at = CURRENT_TIMESTAMP
WHERE is_rolling_admission = FALSE;

UPDATE pig
SET is_rolling_admission_new = 'always', updated_at = CURRENT_TIMESTAMP
WHERE is_rolling_admission = TRUE;

ALTER TABLE pig DROP COLUMN is_rolling_admission;
ALTER TABLE pig RENAME COLUMN is_rolling_admission_new to is_rolling_admission;

END;
COMMIT;
