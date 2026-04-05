ALTER TABLE public.board
ADD COLUMN board_type varchar(5),
ADD CONSTRAINT match_constraint CHECK (board_type IN ('IMAGE', 'TEXT', 'NONE', 'FILE'));

UPDATE public.board
SET
    board_type = CASE id
        WHEN 1 THEN 'NONE'
        WHEN 2 THEN 'NONE'
        WHEN 3 THEN 'TEXT'
        WHEN 4 THEN 'IMAGE'
        WHEN 5 THEN 'TEXT'
        WHEN 6 THEN 'TEXT'
    END