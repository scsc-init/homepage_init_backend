INSERT INTO public.board (
    name,
    description,
    writing_permission_level,
    reading_permission_level,
    created_at,
    updated_at,
    board_type
)
SELECT
    'Files',
    'file upload board',
    500,
    0,
    NOW(),
    NOW(),
    'FILE'
WHERE NOT EXISTS (
    SELECT 1
    FROM public.board
    WHERE name = 'Files'
);
