-- V2__make_deposit_time_nullable.sql
DO $$ 
BEGIN 
    IF EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_schema = 'public' 
          AND table_name = 'standby_req_tbl' 
          AND column_name = 'deposit_time' 
          AND is_nullable = 'NO'
    ) THEN 
        ALTER TABLE public.standby_req_tbl 
        ALTER COLUMN deposit_time DROP NOT NULL;
    END IF;
END $$;
