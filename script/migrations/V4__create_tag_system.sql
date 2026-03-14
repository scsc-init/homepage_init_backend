DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.tables
        WHERE table_schema = 'public'
          AND table_name = 'tag'
    ) THEN
        CREATE TABLE public.tag (
            id BIGSERIAL PRIMARY KEY,
            text TEXT NOT NULL UNIQUE,
            is_major BOOLEAN NOT NULL DEFAULT false,
            created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
    END IF;
END $$;

DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM information_schema.tables
        WHERE table_schema = 'public'
          AND table_name = 'sig_tag'
    ) AND NOT EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_schema = 'public'
          AND table_name = 'sig_tag'
          AND column_name = 'tag_id'
    ) THEN
        ALTER TABLE public.sig_tag
        ADD COLUMN tag_id BIGINT;
    END IF;
END $$;

INSERT INTO public.tag (text)
SELECT DISTINCT st.label
FROM public.sig_tag st
LEFT JOIN public.tag t ON t.text = st.label
WHERE st.label IS NOT NULL
  AND t.id IS NULL;

UPDATE public.sig_tag st
SET tag_id = t.id
FROM public.tag t
WHERE st.label = t.text
  AND st.tag_id IS NULL;

DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_schema = 'public'
          AND table_name = 'sig_tag'
          AND column_name = 'tag_id'
    ) THEN
        ALTER TABLE public.sig_tag
        ALTER COLUMN tag_id SET NOT NULL;
    END IF;
END $$;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.table_constraints
        WHERE table_schema = 'public'
          AND table_name = 'sig_tag'
          AND constraint_name = 'sig_tag_tag_id_fkey'
    ) THEN
        ALTER TABLE public.sig_tag
        ADD CONSTRAINT sig_tag_tag_id_fkey
        FOREIGN KEY (tag_id) REFERENCES public.tag(id) ON DELETE CASCADE;
    END IF;
END $$;

DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM information_schema.table_constraints
        WHERE table_schema = 'public'
          AND table_name = 'sig_tag'
          AND constraint_name = 'sig_tag_sig_id_label_key'
    ) THEN
        ALTER TABLE public.sig_tag
        DROP CONSTRAINT sig_tag_sig_id_label_key;
    END IF;
END $$;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.table_constraints
        WHERE table_schema = 'public'
          AND table_name = 'sig_tag'
          AND constraint_name = 'sig_tag_sig_id_tag_id_key'
    ) THEN
        ALTER TABLE public.sig_tag
        ADD CONSTRAINT sig_tag_sig_id_tag_id_key UNIQUE (sig_id, tag_id);
    END IF;
END $$;

DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_schema = 'public'
          AND table_name = 'sig_tag'
          AND column_name = 'label'
    ) THEN
        ALTER TABLE public.sig_tag
        DROP COLUMN label;
    END IF;
END $$;