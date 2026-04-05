ALTER TABLE public.board
ADD COLUMN board_type varchar(5) NOT NULL DEFAULT 'TEXT',
ADD CONSTRAINT match_constraint CHECK (board_type IN ('IMAGE', 'TEXT', 'NONE', 'FILE'));

UPDATE public.board
SET
    board_type = CASE id
        WHEN name = 'Album' THEN 'IMAGE'
        WHEN name IN ('Sig', 'Pig') THEN 'NONE'
        ELSE 'TEXT'
    END;