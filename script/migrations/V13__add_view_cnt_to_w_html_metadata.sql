BEGIN;

ALTER TABLE public.w_html_metadata ADD COLUMN view_cnt INTEGER NOT NULL DEFAULT 0;

ALTER TABLE public.w_html_metadata ADD CONSTRAINT check_view_cnt_non_negative CHECK (view_cnt >= 0);

COMMIT;
