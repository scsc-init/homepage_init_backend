DO $$ 
BEGIN 
    ALTER TABLE public.board 
    ADD COLUMN board_type varchar(5) NOT NULL DEFAULT 'TEXT';

    ALTER TABLE public.board 
    ADD CONSTRAINT match_constraint CHECK (board_type IN ('IMAGE', 'TEXT', 'NONE', 'FILE'));

    UPDATE public.board 
    SET board_type = CASE 
        WHEN name = 'Album' THEN 'IMAGE' 
        WHEN name IN ('Sig', 'Pig') THEN 'NONE' 
        ELSE 'TEXT' 
    END;
END $$;
