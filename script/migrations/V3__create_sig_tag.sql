CREATE TABLE public.sig_tag (
    id BIGSERIAL PRIMARY KEY,
    sig_id bigint NOT NULL REFERENCES sig(id) ON DELETE CASCADE,
    label text NOT NULL,
    created_at timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(sig_id, label)
);
