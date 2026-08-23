UPDATE public.board
SET reading_permission_level = 0
WHERE name = 'Notice'
  AND reading_permission_level <> 0;