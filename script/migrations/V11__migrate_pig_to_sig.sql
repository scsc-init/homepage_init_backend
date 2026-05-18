BEGIN;

INSERT INTO public.tag (text, is_major)
VALUES
    ('SIG', true),
    ('PIG', true)
ON CONFLICT (text) DO UPDATE
SET is_major = true;

CREATE TEMP TABLE pig_to_sig_migration (
    pig_id bigint PRIMARY KEY,
    sig_id bigint NOT NULL UNIQUE
) ON COMMIT DROP;

INSERT INTO pig_to_sig_migration (pig_id, sig_id)
SELECT p.id, s.id
FROM public.pig p
JOIN public.sig s ON s.content_id = p.content_id;

DO $$
DECLARE
    conflict_count integer;
    missing_owner_count integer;
BEGIN
    SELECT count(*)
    INTO missing_owner_count
    FROM public.pig
    WHERE owner IS NULL;

    IF missing_owner_count > 0 THEN
        RAISE EXCEPTION
            'Cannot migrate pig rows to sig because % row(s) have no owner',
            missing_owner_count;
    END IF;

    SELECT count(*)
    INTO conflict_count
    FROM public.pig p
    JOIN public.sig s
      ON s.content_id <> p.content_id
     AND (
        (
            s.created_year = p.created_year
            AND s.created_semester = p.created_semester
            AND s.title = p.title
        )
        OR (
            s.year = p.year
            AND s.semester = p.semester
            AND s.title = p.title
        )
     );

    IF conflict_count > 0 THEN
        RAISE EXCEPTION
            'Cannot migrate pig rows to sig because % row(s) conflict with existing sig unique keys',
            conflict_count;
    END IF;
END $$;

INSERT INTO public.sig_tag (sig_id, tag_id)
SELECT s.id, t.id
FROM public.sig s
JOIN public.tag t ON t.text = 'SIG'
WHERE NOT EXISTS (
    SELECT 1
    FROM public.pig p
    WHERE p.content_id = s.content_id
)
ON CONFLICT (sig_id, tag_id) DO NOTHING;

WITH inserted_sig AS (
    INSERT INTO public.sig (
        title,
        description,
        content_id,
        status,
        created_year,
        created_semester,
        year,
        semester,
        should_extend,
        is_rolling_admission,
        created_at,
        updated_at,
        owner
    )
    SELECT
        p.title,
        p.description,
        p.content_id,
        p.status,
        p.created_year,
        p.created_semester,
        p.year,
        p.semester,
        p.should_extend,
        p.is_rolling_admission,
        p.created_at,
        p.updated_at,
        p.owner
    FROM public.pig p
    WHERE NOT EXISTS (
        SELECT 1
        FROM public.sig s
        WHERE s.content_id = p.content_id
    )
    RETURNING id, content_id
)
INSERT INTO pig_to_sig_migration (pig_id, sig_id)
SELECT p.id, s.id
FROM inserted_sig s
JOIN public.pig p ON p.content_id = s.content_id;

INSERT INTO public.sig_member (ig_id, user_id, created_at)
SELECT
    m.sig_id,
    pm.user_id,
    pm.created_at
FROM public.pig_member pm
JOIN pig_to_sig_migration m ON m.pig_id = pm.ig_id
ON CONFLICT (ig_id, user_id) DO NOTHING;

INSERT INTO public.sig_website (
    sig_id,
    label,
    url,
    sort_order,
    created_at,
    updated_at
)
SELECT
    m.sig_id,
    pw.label,
    pw.url,
    pw.sort_order,
    pw.created_at,
    pw.updated_at
FROM public.pig_website pw
JOIN pig_to_sig_migration m ON m.pig_id = pw.pig_id
WHERE NOT EXISTS (
    SELECT 1
    FROM public.sig_website sw
    WHERE sw.sig_id = m.sig_id
      AND sw.label = pw.label
      AND sw.url = pw.url
      AND sw.sort_order = pw.sort_order
);

UPDATE public.article a
SET board_id = 1
FROM public.pig p
JOIN pig_to_sig_migration m ON m.pig_id = p.id
WHERE a.id = p.content_id
  AND a.board_id = 2;

INSERT INTO public.sig_tag (sig_id, tag_id)
SELECT
    m.sig_id,
    t.id
FROM pig_to_sig_migration m
JOIN public.tag t ON t.text = 'PIG'
ON CONFLICT (sig_id, tag_id) DO NOTHING;

COMMIT;
