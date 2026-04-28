BEGIN;

DELETE FROM public.article
WHERE is_deleted = true
  AND id NOT IN (
    SELECT content_id FROM public.sig
    UNION
    SELECT content_id FROM public.pig
  );

DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public'
          AND table_name = 'article'
          AND column_name = 'is_deleted'
    ) THEN
        ALTER TABLE public.article DROP COLUMN is_deleted;
    END IF;
END $$;

DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public'
          AND table_name = 'article'
          AND column_name = 'deleted_at'
    ) THEN
        ALTER TABLE public.article DROP COLUMN deleted_at;
    END IF;
END $$;

COMMIT;