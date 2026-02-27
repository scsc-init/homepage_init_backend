--
-- PostgreSQL database dump
--

-- \restrict X3wE36NbJb0SfRbzWuhlDQeNv8PWMier5MZSYf7gX7ad1rVGz9VmT2apMIOVeKC

-- Dumped from database version 17.8
-- Dumped by pg_dump version 17.9 (Debian 17.9-1.pgdg12+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

BEGIN;

--
-- Name: article; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.article (
    id bigint NOT NULL,
    title text NOT NULL,
    author_id text NOT NULL,
    board_id bigint NOT NULL,
    created_at timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_deleted boolean NOT NULL DEFAULT false,
    deleted_at timestamp without time zone
);


--
-- Name: article_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.article_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: article_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.article_id_seq OWNED BY public.article.id;


--
-- Name: attachment; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.attachment (
    id bigint NOT NULL,
    article_id bigint NOT NULL,
    file_id text NOT NULL
);


--
-- Name: attachment_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.attachment_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: attachment_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.attachment_id_seq OWNED BY public.attachment.id;


--
-- Name: board; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.board (
    id bigint NOT NULL,
    name text NOT NULL,
    description text NOT NULL,
    writing_permission_level bigint NOT NULL DEFAULT '0'::bigint,
    reading_permission_level bigint NOT NULL DEFAULT '0'::bigint,
    created_at timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: board_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.board_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: board_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.board_id_seq OWNED BY public.board.id;


--
-- Name: check_user_status_rule; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.check_user_status_rule (
    id bigint NOT NULL,
    method text NOT NULL,
    path text NOT NULL
);


--
-- Name: check_user_status_rule_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.check_user_status_rule_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: check_user_status_rule_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.check_user_status_rule_id_seq OWNED BY public.check_user_status_rule.id;


--
-- Name: comment; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.comment (
    id bigint NOT NULL,
    content text NOT NULL,
    author_id text NOT NULL,
    article_id bigint NOT NULL,
    parent_id bigint NOT NULL,
    is_deleted boolean NOT NULL DEFAULT false,
    created_at timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at timestamp without time zone
);


--
-- Name: enrollment; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.enrollment (
    id bigint NOT NULL,
    year bigint NOT NULL,
    semester bigint NOT NULL,
    user_id text NOT NULL,
    created_at timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: enrollment_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.enrollment_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: enrollment_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.enrollment_id_seq OWNED BY public.enrollment.id;


--
-- Name: file_metadata; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.file_metadata (
    id text NOT NULL,
    original_filename text NOT NULL,
    size integer NOT NULL,
    mime_type text NOT NULL,
    created_at timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    owner text
);


--
-- Name: key_value; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.key_value (
    key text NOT NULL,
    value text NOT NULL,
    writing_permission_level bigint NOT NULL DEFAULT '500'::bigint,
    created_at timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: major; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.major (
    id bigint NOT NULL,
    college text NOT NULL,
    major_name text NOT NULL
);


--
-- Name: major_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.major_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: major_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.major_id_seq OWNED BY public.major.id;


--
-- Name: oldboy_applicant; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.oldboy_applicant (
    id text NOT NULL,
    processed boolean NOT NULL DEFAULT false,
    created_at timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: pig; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.pig (
    id bigint NOT NULL,
    title text NOT NULL,
    description text NOT NULL,
    content_id bigint NOT NULL,
    status text NOT NULL,
    created_year bigint NOT NULL,
    created_semester bigint NOT NULL,
    year bigint NOT NULL,
    semester bigint NOT NULL,
    should_extend boolean NOT NULL DEFAULT false,
    is_rolling_admission text NOT NULL DEFAULT 'during_recruiting'::text,
    created_at timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    owner text
);


--
-- Name: pig_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.pig_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: pig_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.pig_id_seq OWNED BY public.pig.id;


--
-- Name: pig_member; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.pig_member (
    id bigint NOT NULL,
    ig_id bigint NOT NULL,
    user_id text NOT NULL,
    created_at timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: pig_member_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.pig_member_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: pig_member_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.pig_member_id_seq OWNED BY public.pig_member.id;


--
-- Name: pig_website; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.pig_website (
    id bigint NOT NULL,
    pig_id bigint NOT NULL,
    label text NOT NULL,
    url text NOT NULL,
    sort_order bigint NOT NULL DEFAULT '0'::bigint,
    created_at timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: pig_website_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.pig_website_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: pig_website_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.pig_website_id_seq OWNED BY public.pig_website.id;


--
-- Name: scsc_global_status; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.scsc_global_status (
    id bigint NOT NULL,
    status text NOT NULL,
    year bigint NOT NULL,
    semester bigint NOT NULL,
    updated_at timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: sig; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.sig (
    id bigint NOT NULL,
    title text NOT NULL,
    description text NOT NULL,
    content_id bigint NOT NULL,
    status text NOT NULL,
    created_year bigint NOT NULL,
    created_semester bigint NOT NULL,
    year bigint NOT NULL,
    semester bigint NOT NULL,
    should_extend boolean NOT NULL DEFAULT false,
    is_rolling_admission boolean NOT NULL DEFAULT false,
    created_at timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    owner text
);


--
-- Name: sig_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.sig_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: sig_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.sig_id_seq OWNED BY public.sig.id;


--
-- Name: sig_member; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.sig_member (
    id bigint NOT NULL,
    ig_id bigint NOT NULL,
    user_id text NOT NULL,
    created_at timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: sig_member_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.sig_member_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: sig_member_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.sig_member_id_seq OWNED BY public.sig_member.id;


--
-- Name: standby_req_tbl; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.standby_req_tbl (
    standby_user_id text NOT NULL,
    user_name text NOT NULL,
    deposit_name text NOT NULL,
    deposit_time timestamp without time zone NOT NULL,
    is_checked boolean NOT NULL DEFAULT false
);


--
-- Name: user; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public."user" (
    id text NOT NULL,
    email text NOT NULL,
    name text NOT NULL,
    phone text NOT NULL,
    student_id text NOT NULL,
    role bigint NOT NULL,
    discord_id bigint,
    discord_name text,
    profile_picture text,
    profile_picture_is_url boolean NOT NULL DEFAULT false,
    last_login timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    major_id bigint NOT NULL,
    is_active boolean NOT NULL DEFAULT false,
    is_banned boolean NOT NULL DEFAULT false
);


--
-- Name: user_role; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.user_role (
    level bigint NOT NULL,
    name text NOT NULL,
    kor_name text NOT NULL
);


--
-- Name: w_html_metadata; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.w_html_metadata (
    name text NOT NULL,
    size bigint NOT NULL,
    created_at timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    creator text
);


--
-- Name: article id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.article ALTER COLUMN id SET DEFAULT nextval('public.article_id_seq'::regclass);


--
-- Name: attachment id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.attachment ALTER COLUMN id SET DEFAULT nextval('public.attachment_id_seq'::regclass);


--
-- Name: board id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.board ALTER COLUMN id SET DEFAULT nextval('public.board_id_seq'::regclass);


--
-- Name: check_user_status_rule id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.check_user_status_rule ALTER COLUMN id SET DEFAULT nextval('public.check_user_status_rule_id_seq'::regclass);


--
-- Name: enrollment id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.enrollment ALTER COLUMN id SET DEFAULT nextval('public.enrollment_id_seq'::regclass);


--
-- Name: major id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.major ALTER COLUMN id SET DEFAULT nextval('public.major_id_seq'::regclass);


--
-- Name: pig id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.pig ALTER COLUMN id SET DEFAULT nextval('public.pig_id_seq'::regclass);


--
-- Name: pig_member id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.pig_member ALTER COLUMN id SET DEFAULT nextval('public.pig_member_id_seq'::regclass);


--
-- Name: pig_website id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.pig_website ALTER COLUMN id SET DEFAULT nextval('public.pig_website_id_seq'::regclass);


--
-- Name: sig id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sig ALTER COLUMN id SET DEFAULT nextval('public.sig_id_seq'::regclass);


--
-- Name: sig_member id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sig_member ALTER COLUMN id SET DEFAULT nextval('public.sig_member_id_seq'::regclass);


--
-- Name: user_role idx_16391_user_role_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.user_role
    ADD CONSTRAINT idx_16391_user_role_pkey PRIMARY KEY (level);


--
-- Name: major idx_16397_major_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.major
    ADD CONSTRAINT idx_16397_major_pkey PRIMARY KEY (id);


--
-- Name: oldboy_applicant idx_16403_sqlite_autoindex_oldboy_applicant_1; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.oldboy_applicant
    ADD CONSTRAINT idx_16403_sqlite_autoindex_oldboy_applicant_1 PRIMARY KEY (id);


--
-- Name: scsc_global_status idx_16411_scsc_global_status_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.scsc_global_status
    ADD CONSTRAINT idx_16411_scsc_global_status_pkey PRIMARY KEY (id);


--
-- Name: file_metadata idx_16417_sqlite_autoindex_file_metadata_1; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.file_metadata
    ADD CONSTRAINT idx_16417_sqlite_autoindex_file_metadata_1 PRIMARY KEY (id);


--
-- Name: board idx_16424_board_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.board
    ADD CONSTRAINT idx_16424_board_pkey PRIMARY KEY (id);


--
-- Name: article idx_16435_article_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.article
    ADD CONSTRAINT idx_16435_article_pkey PRIMARY KEY (id);


--
-- Name: comment idx_16444_comment_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.comment
    ADD CONSTRAINT idx_16444_comment_pkey PRIMARY KEY (id);


--
-- Name: standby_req_tbl idx_16452_sqlite_autoindex_standby_req_tbl_1; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.standby_req_tbl
    ADD CONSTRAINT idx_16452_sqlite_autoindex_standby_req_tbl_1 PRIMARY KEY (standby_user_id);


--
-- Name: w_html_metadata idx_16458_sqlite_autoindex_w_html_metadata_1; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.w_html_metadata
    ADD CONSTRAINT idx_16458_sqlite_autoindex_w_html_metadata_1 PRIMARY KEY (name);


--
-- Name: key_value idx_16465_sqlite_autoindex_key_value_1; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.key_value
    ADD CONSTRAINT idx_16465_sqlite_autoindex_key_value_1 PRIMARY KEY (key);


--
-- Name: sig_member idx_16474_sig_member_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sig_member
    ADD CONSTRAINT idx_16474_sig_member_pkey PRIMARY KEY (id);


--
-- Name: user idx_16481_sqlite_autoindex_user_1; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."user"
    ADD CONSTRAINT idx_16481_sqlite_autoindex_user_1 PRIMARY KEY (id);


--
-- Name: attachment idx_16493_attachment_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.attachment
    ADD CONSTRAINT idx_16493_attachment_pkey PRIMARY KEY (id);


--
-- Name: pig_website idx_16500_pig_website_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.pig_website
    ADD CONSTRAINT idx_16500_pig_website_pkey PRIMARY KEY (id);


--
-- Name: pig_member idx_16510_pig_member_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.pig_member
    ADD CONSTRAINT idx_16510_pig_member_pkey PRIMARY KEY (id);


--
-- Name: sig idx_16518_sig_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sig
    ADD CONSTRAINT idx_16518_sig_pkey PRIMARY KEY (id);


--
-- Name: pig idx_16529_pig_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.pig
    ADD CONSTRAINT idx_16529_pig_pkey PRIMARY KEY (id);


--
-- Name: enrollment idx_16540_enrollment_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.enrollment
    ADD CONSTRAINT idx_16540_enrollment_pkey PRIMARY KEY (id);


--
-- Name: check_user_status_rule idx_16548_check_user_status_rule_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.check_user_status_rule
    ADD CONSTRAINT idx_16548_check_user_status_rule_pkey PRIMARY KEY (id);


--
-- Name: idx_16391_sqlite_autoindex_user_role_1; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX idx_16391_sqlite_autoindex_user_role_1 ON public.user_role USING btree (name);


--
-- Name: idx_16391_sqlite_autoindex_user_role_2; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX idx_16391_sqlite_autoindex_user_role_2 ON public.user_role USING btree (kor_name);


--
-- Name: idx_16397_sqlite_autoindex_major_1; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX idx_16397_sqlite_autoindex_major_1 ON public.major USING btree (college, major_name);


--
-- Name: idx_16403_idx_oldboy_applicant_processed; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_16403_idx_oldboy_applicant_processed ON public.oldboy_applicant USING btree (processed);


--
-- Name: idx_16417_idx_file_metadata_owner; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_16417_idx_file_metadata_owner ON public.file_metadata USING btree (owner);


--
-- Name: idx_16435_idx_board_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_16435_idx_board_id ON public.article USING btree (board_id);


--
-- Name: idx_16444_idx_article_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_16444_idx_article_id ON public.comment USING btree (article_id);


--
-- Name: idx_16444_idx_parent_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_16444_idx_parent_id ON public.comment USING btree (parent_id);


--
-- Name: idx_16474_sqlite_autoindex_sig_member_1; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX idx_16474_sqlite_autoindex_sig_member_1 ON public.sig_member USING btree (ig_id, user_id);


--
-- Name: idx_16481_idx_user_major; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_16481_idx_user_major ON public."user" USING btree (major_id);


--
-- Name: idx_16481_idx_user_role; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_16481_idx_user_role ON public."user" USING btree (role);


--
-- Name: idx_16481_sqlite_autoindex_user_2; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX idx_16481_sqlite_autoindex_user_2 ON public."user" USING btree (email);


--
-- Name: idx_16481_sqlite_autoindex_user_3; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX idx_16481_sqlite_autoindex_user_3 ON public."user" USING btree (phone);


--
-- Name: idx_16481_sqlite_autoindex_user_4; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX idx_16481_sqlite_autoindex_user_4 ON public."user" USING btree (student_id);


--
-- Name: idx_16481_sqlite_autoindex_user_5; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX idx_16481_sqlite_autoindex_user_5 ON public."user" USING btree (discord_id);


--
-- Name: idx_16481_sqlite_autoindex_user_6; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX idx_16481_sqlite_autoindex_user_6 ON public."user" USING btree (discord_name);


--
-- Name: idx_16493_sqlite_autoindex_attachment_1; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX idx_16493_sqlite_autoindex_attachment_1 ON public.attachment USING btree (article_id, file_id);


--
-- Name: idx_16510_sqlite_autoindex_pig_member_1; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX idx_16510_sqlite_autoindex_pig_member_1 ON public.pig_member USING btree (ig_id, user_id);


--
-- Name: idx_16518_sqlite_autoindex_sig_1; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX idx_16518_sqlite_autoindex_sig_1 ON public.sig USING btree (content_id);


--
-- Name: idx_16518_sqlite_autoindex_sig_2; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX idx_16518_sqlite_autoindex_sig_2 ON public.sig USING btree (created_year, created_semester, title);


--
-- Name: idx_16518_sqlite_autoindex_sig_3; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX idx_16518_sqlite_autoindex_sig_3 ON public.sig USING btree (year, semester, title);


--
-- Name: idx_16529_sqlite_autoindex_pig_1; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX idx_16529_sqlite_autoindex_pig_1 ON public.pig USING btree (content_id);


--
-- Name: idx_16529_sqlite_autoindex_pig_2; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX idx_16529_sqlite_autoindex_pig_2 ON public.pig USING btree (created_year, created_semester, title);


--
-- Name: idx_16529_sqlite_autoindex_pig_3; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX idx_16529_sqlite_autoindex_pig_3 ON public.pig USING btree (year, semester, title);


--
-- Name: idx_16540_sqlite_autoindex_enrollment_1; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX idx_16540_sqlite_autoindex_enrollment_1 ON public.enrollment USING btree (year, semester, user_id);


--
-- Name: idx_16548_sqlite_autoindex_check_user_status_rule_1; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX idx_16548_sqlite_autoindex_check_user_status_rule_1 ON public.check_user_status_rule USING btree (method, path);


--
-- Name: article article_author_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.article
    ADD CONSTRAINT article_author_id_fkey FOREIGN KEY (author_id) REFERENCES public."user"(id) ON DELETE RESTRICT;


--
-- Name: article article_board_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.article
    ADD CONSTRAINT article_board_id_fkey FOREIGN KEY (board_id) REFERENCES public.board(id) ON DELETE CASCADE;


--
-- Name: attachment attachment_article_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.attachment
    ADD CONSTRAINT attachment_article_id_fkey FOREIGN KEY (article_id) REFERENCES public.article(id) ON DELETE CASCADE;


--
-- Name: attachment attachment_file_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.attachment
    ADD CONSTRAINT attachment_file_id_fkey FOREIGN KEY (file_id) REFERENCES public.file_metadata(id) ON DELETE CASCADE;


--
-- Name: board board_reading_permission_level_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.board
    ADD CONSTRAINT board_reading_permission_level_fkey FOREIGN KEY (reading_permission_level) REFERENCES public.user_role(level) ON DELETE RESTRICT;


--
-- Name: board board_writing_permission_level_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.board
    ADD CONSTRAINT board_writing_permission_level_fkey FOREIGN KEY (writing_permission_level) REFERENCES public.user_role(level) ON DELETE RESTRICT;


--
-- Name: comment comment_article_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.comment
    ADD CONSTRAINT comment_article_id_fkey FOREIGN KEY (article_id) REFERENCES public.article(id) ON DELETE CASCADE;


--
-- Name: comment comment_author_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.comment
    ADD CONSTRAINT comment_author_id_fkey FOREIGN KEY (author_id) REFERENCES public."user"(id) ON DELETE RESTRICT;


--
-- Name: comment comment_parent_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.comment
    ADD CONSTRAINT comment_parent_id_fkey FOREIGN KEY (parent_id) REFERENCES public.comment(id) ON DELETE SET NULL;


--
-- Name: enrollment enrollment_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.enrollment
    ADD CONSTRAINT enrollment_user_id_fkey FOREIGN KEY (user_id) REFERENCES public."user"(id);


--
-- Name: file_metadata file_metadata_owner_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.file_metadata
    ADD CONSTRAINT file_metadata_owner_fkey FOREIGN KEY (owner) REFERENCES public."user"(id) ON DELETE SET NULL;


--
-- Name: key_value key_value_writing_permission_level_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.key_value
    ADD CONSTRAINT key_value_writing_permission_level_fkey FOREIGN KEY (writing_permission_level) REFERENCES public.user_role(level) ON DELETE RESTRICT;


--
-- Name: oldboy_applicant oldboy_applicant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.oldboy_applicant
    ADD CONSTRAINT oldboy_applicant_id_fkey FOREIGN KEY (id) REFERENCES public."user"(id) ON DELETE CASCADE;


--
-- Name: pig pig_content_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.pig
    ADD CONSTRAINT pig_content_id_fkey FOREIGN KEY (content_id) REFERENCES public.article(id) ON DELETE RESTRICT;


--
-- Name: pig_member pig_member_ig_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.pig_member
    ADD CONSTRAINT pig_member_ig_id_fkey FOREIGN KEY (ig_id) REFERENCES public.pig(id) ON DELETE CASCADE;


--
-- Name: pig_member pig_member_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.pig_member
    ADD CONSTRAINT pig_member_user_id_fkey FOREIGN KEY (user_id) REFERENCES public."user"(id) ON DELETE CASCADE;


--
-- Name: pig pig_owner_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.pig
    ADD CONSTRAINT pig_owner_fkey FOREIGN KEY (owner) REFERENCES public."user"(id) ON DELETE RESTRICT;


--
-- Name: pig_website pig_website_pig_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.pig_website
    ADD CONSTRAINT pig_website_pig_id_fkey FOREIGN KEY (pig_id) REFERENCES public.pig(id) ON DELETE CASCADE;


--
-- Name: sig sig_content_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sig
    ADD CONSTRAINT sig_content_id_fkey FOREIGN KEY (content_id) REFERENCES public.article(id) ON DELETE RESTRICT;


--
-- Name: sig_member sig_member_ig_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sig_member
    ADD CONSTRAINT sig_member_ig_id_fkey FOREIGN KEY (ig_id) REFERENCES public.sig(id) ON DELETE CASCADE;


--
-- Name: sig_member sig_member_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sig_member
    ADD CONSTRAINT sig_member_user_id_fkey FOREIGN KEY (user_id) REFERENCES public."user"(id) ON DELETE CASCADE;


--
-- Name: sig sig_owner_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sig
    ADD CONSTRAINT sig_owner_fkey FOREIGN KEY (owner) REFERENCES public."user"(id) ON DELETE RESTRICT;


--
-- Name: standby_req_tbl standby_req_tbl_standby_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.standby_req_tbl
    ADD CONSTRAINT standby_req_tbl_standby_user_id_fkey FOREIGN KEY (standby_user_id) REFERENCES public."user"(id) ON DELETE RESTRICT;


--
-- Name: user user_major_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."user"
    ADD CONSTRAINT user_major_id_fkey FOREIGN KEY (major_id) REFERENCES public.major(id) ON DELETE RESTRICT;


--
-- Name: user user_role_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."user"
    ADD CONSTRAINT user_role_fkey FOREIGN KEY (role) REFERENCES public.user_role(level) ON DELETE RESTRICT;


--
-- Name: w_html_metadata w_html_metadata_creator_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.w_html_metadata
    ADD CONSTRAINT w_html_metadata_creator_fkey FOREIGN KEY (creator) REFERENCES public."user"(id) ON DELETE SET NULL;


--
-- Data for Name: user_role; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.user_role (level, name, kor_name) VALUES
(0,'lowest','최저권한'),
(100,'dormant','휴회원'),
(200,'newcomer','준회원'),
(300,'member','정회원'),
(400,'oldboy','졸업생'),
(500,'executive','운영진'),
(1000,'president','회장')
;


--
-- Data for Name: board; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.board (id, name, description, writing_permission_level, reading_permission_level) VALUES
(1,'Sig','sig advertising board',1000,0),
(2,'Pig','pig advertising board',1000,0),
(3,'Project Archive','archive of various projects held in the club',300,0),
(4,'Album','photos of club members and activities',500,0),
(5,'Notice','notices from club executive',500,100),
(6,'Grant','applications for sig/pig grant',200,500)
;


--
-- Data for Name: check_user_status_rule; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.check_user_status_rule (id, method, path) VALUES
(1,'POST','/api/executive/pig/%/delete'),
(2,'POST','/api/executive/pig/%/member/join'),
(3,'POST','/api/executive/pig/%/member/leave'),
(4,'POST','/api/executive/pig/%/update'),
(5,'POST','/api/executive/sig/%/delete'),
(6,'POST','/api/executive/sig/%/member/join'),
(7,'POST','/api/executive/sig/%/member/leave'),
(8,'POST','/api/executive/sig/%/update'),
(9,'POST','/api/pig/%/delete'),
(10,'POST','/api/pig/%/handover'),
(11,'POST','/api/pig/%/member/join'),
(12,'POST','/api/pig/%/member/leave'),
(13,'POST','/api/pig/%/update'),
(14,'POST','/api/pig/create'),
(15,'POST','/api/sig/%/delete'),
(16,'POST','/api/sig/%/handover'),
(17,'POST','/api/sig/%/member/join'),
(18,'POST','/api/sig/%/member/leave'),
(19,'POST','/api/sig/%/update'),
(20,'POST','/api/sig/create')
;


--
-- Data for Name: key_value; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.key_value (key, value, writing_permission_level) VALUES
('footer-message','서울대학교 컴퓨터 연구회\n회장 XXX 010-xxxx-xxxx\nscsc.snu@gmail.com',500),
('main-president','',500),
('vice-president','',500),
('enrollment_grant_until','2026-2',500)
;


--
-- Data for Name: major; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.major (id, college, major_name) VALUES
(1,'인문대학','인문계열'),
(2,'인문대학','국어국문학과'),
(3,'인문대학','중어중문학과'),
(4,'인문대학','영어영문학과'),
(5,'인문대학','불어불문학과'),
(6,'인문대학','독어독문학과'),
(7,'인문대학','노어노문학과'),
(8,'인문대학','서어서문학과'),
(9,'인문대학','언어학과'),
(10,'인문대학','아시아언어문명학부'),
(11,'인문대학','역사학부'),
(12,'인문대학','고고미술사학과'),
(13,'인문대학','철학과'),
(14,'인문대학','종교학과'),
(15,'인문대학','미학과'),
(16,'사회과학대학','정치외교학부'),
(17,'사회과학대학','경제학부'),
(18,'사회과학대학','사회학과'),
(19,'사회과학대학','인류학과'),
(20,'사회과학대학','심리학과'),
(21,'사회과학대학','지리학과'),
(22,'사회과학대학','사회복지학과'),
(23,'사회과학대학','언론정보학과'),
(24,'자연과학대학','수리과학부'),
(25,'자연과학대학','통계학과'),
(26,'자연과학대학','물리·천문학부'),
(27,'자연과학대학','화학부'),
(28,'자연과학대학','생명과학부'),
(29,'자연과학대학','지구환경과학부'),
(30,'간호대학','간호대학'),
(31,'경영대학','경영대학'),
(32,'공과대학','광역'),
(33,'공과대학','건설환경공학부'),
(34,'공과대학','기계공학부'),
(35,'공과대학','재료공학부'),
(36,'공과대학','전기·정보공학부'),
(37,'공과대학','컴퓨터공학부'),
(38,'공과대학','화학생물공학부'),
(39,'공과대학','건축학과'),
(40,'공과대학','산업공학과'),
(41,'공과대학','에너지자원공학과'),
(42,'공과대학','원자핵공학과'),
(43,'공과대학','조선해양공학과'),
(44,'공과대학','항공우주공학과'),
(45,'농업생명과학대학','농경제사회학부'),
(46,'농업생명과학대학','식물생산과학부'),
(47,'농업생명과학대학','산림과학부'),
(48,'농업생명과학대학','식품·동물생명공학부'),
(49,'농업생명과학대학','응용생물화학부'),
(50,'농업생명과학대학','조경·지역시스템공학부'),
(51,'농업생명과학대학','바이오시스템·소재학부'),
(52,'농업생명과학대학','스마트시스템과학과'),
(53,'미술대학','동양화과'),
(54,'미술대학','서양화과'),
(55,'미술대학','조소과'),
(56,'미술대학','공예과'),
(57,'미술대학','디자인과'),
(58,'사범대학','교육학과'),
(59,'사범대학','국어교육과'),
(60,'사범대학','영어교육과'),
(61,'사범대학','독어교육과'),
(62,'사범대학','불어교육과'),
(63,'사범대학','사회교육과'),
(64,'사범대학','역사교육과'),
(65,'사범대학','지리교육과'),
(66,'사범대학','윤리교육과'),
(67,'사범대학','수학교육과'),
(68,'사범대학','물리교육과'),
(69,'사범대학','화학교육과'),
(70,'사범대학','생물교육과'),
(71,'사범대학','지구과학교육과'),
(72,'사범대학','체육교육과'),
(73,'생활과학대학','소비자아동학부'),
(74,'생활과학대학','식품영양학과'),
(75,'생활과학대학','의류학과'),
(76,'수의과대학','수의예과'),
(77,'약학대학','약학계열'),
(78,'음악대학','성악과'),
(79,'음악대학','작곡과'),
(80,'음악대학','음악학과'),
(81,'음악대학','피아노과'),
(82,'음악대학','관현악과'),
(83,'음악대학','국악과'),
(84,'의과대학','의예과'),
(85,'첨단융합학부','첨단융합학부'),
(86,'학부대학','광역'),
(87,'학부대학','자유전공학부'),
(88,'치의학대학원','치의학과')
;


--
-- Data for Name: scsc_global_status; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.scsc_global_status (id, status, year, semester) VALUES
(1,'recruiting',2026,1)
;


--
-- Data for Name: user; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public."user" (id, email, name, phone, student_id, role, major_id, is_active, is_banned) VALUES
('0bf31e3f7519f1a089553e619c01b015fbe206b37634ad27b056d0059d41786d','deposit.app@scsc.dev','Deposit App','09900000002','200000002',1000,1,true,false),
('a44946fbf09c326520c2ca0a324b19100381911c9afe5af06a90b636d8f35dd5','bot@discord.com','Discord Bot','09900000001','200000001',1000,1,true,false)
;


--
-- Name: board_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.board_id_seq', 6, true);


--
-- Name: check_user_status_rule_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.check_user_status_rule_id_seq', 20, true);


--
-- Name: major_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.major_id_seq', 88, true);


COMMIT;

--
-- PostgreSQL database dump complete
--

-- \unrestrict X3wE36NbJb0SfRbzWuhlDQeNv8PWMier5MZSYf7gX7ad1rVGz9VmT2apMIOVeKC

