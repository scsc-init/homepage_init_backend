ALTER TABLE sig 
    ALTER COLUMN is_rolling_admission TYPE TEXT 
    USING (CASE 
        WHEN is_rolling_admission = TRUE THEN 'always'::TEXT 
        ELSE 'never'::TEXT 
    END);

ALTER TABLE sig ALTER COLUMN is_rolling_admission SET DEFAULT 'during_recruiting';
ALTER TABLE sig ALTER COLUMN is_rolling_admission SET NOT NULL;
ALTER TABLE sig ADD CONSTRAINT check_is_rolling_admission 
    CHECK (is_rolling_admission IN ('always', 'never', 'during_recruiting'));