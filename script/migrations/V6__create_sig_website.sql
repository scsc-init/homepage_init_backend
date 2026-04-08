CREATE TABLE public.sig_website (
    id BIGSERIAL PRIMARY KEY,
    sig_id bigint NOT NULL REFERENCES public.sig(id) ON DELETE CASCADE,
    label text NOT NULL,
    url text NOT NULL,
    sort_order bigint NOT NULL DEFAULT '0'::bigint,
    created_at timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP
);
