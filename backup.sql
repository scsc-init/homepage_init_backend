--
-- PostgreSQL database dump
--

\restrict qT0xgS3lMfdIZz0aYUWbaoD0JnFNjfXfwEdvzNf3Ie37ji4wbjMT13SeMoIj6RV

-- Dumped from database version 17.9
-- Dumped by pg_dump version 17.10 (Debian 17.10-1.pgdg12+1)

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

ALTER TABLE ONLY public.w_html_metadata DROP CONSTRAINT w_html_metadata_creator_fkey;
ALTER TABLE ONLY public."user" DROP CONSTRAINT user_role_fkey;
ALTER TABLE ONLY public."user" DROP CONSTRAINT user_major_id_fkey;
ALTER TABLE ONLY public.standby_req_tbl DROP CONSTRAINT standby_req_tbl_standby_user_id_fkey;
ALTER TABLE ONLY public.sig_website DROP CONSTRAINT sig_website_sig_id_fkey;
ALTER TABLE ONLY public.sig_tag DROP CONSTRAINT sig_tag_tag_id_fkey;
ALTER TABLE ONLY public.sig_tag DROP CONSTRAINT sig_tag_sig_id_fkey;
ALTER TABLE ONLY public.sig DROP CONSTRAINT sig_owner_fkey;
ALTER TABLE ONLY public.sig_member DROP CONSTRAINT sig_member_user_id_fkey;
ALTER TABLE ONLY public.sig_member DROP CONSTRAINT sig_member_ig_id_fkey;
ALTER TABLE ONLY public.sig DROP CONSTRAINT sig_content_id_fkey;
ALTER TABLE ONLY public.pig_website DROP CONSTRAINT pig_website_pig_id_fkey;
ALTER TABLE ONLY public.pig DROP CONSTRAINT pig_owner_fkey;
ALTER TABLE ONLY public.pig_member DROP CONSTRAINT pig_member_user_id_fkey;
ALTER TABLE ONLY public.pig_member DROP CONSTRAINT pig_member_ig_id_fkey;
ALTER TABLE ONLY public.pig DROP CONSTRAINT pig_content_id_fkey;
ALTER TABLE ONLY public.oldboy_applicant DROP CONSTRAINT oldboy_applicant_id_fkey;
ALTER TABLE ONLY public.key_value DROP CONSTRAINT key_value_writing_permission_level_fkey;
ALTER TABLE ONLY public.file_metadata DROP CONSTRAINT file_metadata_owner_fkey;
ALTER TABLE ONLY public.enrollment DROP CONSTRAINT enrollment_user_id_fkey;
ALTER TABLE ONLY public.comment DROP CONSTRAINT comment_parent_id_fkey;
ALTER TABLE ONLY public.comment DROP CONSTRAINT comment_author_id_fkey;
ALTER TABLE ONLY public.comment DROP CONSTRAINT comment_article_id_fkey;
ALTER TABLE ONLY public.board DROP CONSTRAINT board_writing_permission_level_fkey;
ALTER TABLE ONLY public.board DROP CONSTRAINT board_reading_permission_level_fkey;
ALTER TABLE ONLY public.attachment DROP CONSTRAINT attachment_file_id_fkey;
ALTER TABLE ONLY public.attachment DROP CONSTRAINT attachment_article_id_fkey;
ALTER TABLE ONLY public.article DROP CONSTRAINT article_board_id_fkey;
ALTER TABLE ONLY public.article DROP CONSTRAINT article_author_id_fkey;
DROP INDEX public.idx_16548_sqlite_autoindex_check_user_status_rule_1;
DROP INDEX public.idx_16540_sqlite_autoindex_enrollment_1;
DROP INDEX public.idx_16529_sqlite_autoindex_pig_3;
DROP INDEX public.idx_16529_sqlite_autoindex_pig_2;
DROP INDEX public.idx_16529_sqlite_autoindex_pig_1;
DROP INDEX public.idx_16518_sqlite_autoindex_sig_3;
DROP INDEX public.idx_16518_sqlite_autoindex_sig_2;
DROP INDEX public.idx_16518_sqlite_autoindex_sig_1;
DROP INDEX public.idx_16510_sqlite_autoindex_pig_member_1;
DROP INDEX public.idx_16493_sqlite_autoindex_attachment_1;
DROP INDEX public.idx_16481_sqlite_autoindex_user_6;
DROP INDEX public.idx_16481_sqlite_autoindex_user_5;
DROP INDEX public.idx_16481_sqlite_autoindex_user_4;
DROP INDEX public.idx_16481_sqlite_autoindex_user_3;
DROP INDEX public.idx_16481_sqlite_autoindex_user_2;
DROP INDEX public.idx_16481_idx_user_role;
DROP INDEX public.idx_16481_idx_user_major;
DROP INDEX public.idx_16474_sqlite_autoindex_sig_member_1;
DROP INDEX public.idx_16444_idx_parent_id;
DROP INDEX public.idx_16444_idx_article_id;
DROP INDEX public.idx_16435_idx_board_id;
DROP INDEX public.idx_16417_idx_file_metadata_owner;
DROP INDEX public.idx_16403_idx_oldboy_applicant_processed;
DROP INDEX public.idx_16397_sqlite_autoindex_major_1;
DROP INDEX public.idx_16391_sqlite_autoindex_user_role_2;
DROP INDEX public.idx_16391_sqlite_autoindex_user_role_1;
DROP INDEX public.flyway_schema_history_s_idx;
ALTER TABLE ONLY public.tag DROP CONSTRAINT tag_text_key;
ALTER TABLE ONLY public.tag DROP CONSTRAINT tag_pkey;
ALTER TABLE ONLY public.sig_website DROP CONSTRAINT sig_website_pkey;
ALTER TABLE ONLY public.sig_tag DROP CONSTRAINT sig_tag_sig_id_tag_id_key;
ALTER TABLE ONLY public.sig_tag DROP CONSTRAINT sig_tag_pkey;
ALTER TABLE ONLY public.check_user_status_rule DROP CONSTRAINT idx_16548_check_user_status_rule_pkey;
ALTER TABLE ONLY public.enrollment DROP CONSTRAINT idx_16540_enrollment_pkey;
ALTER TABLE ONLY public.pig DROP CONSTRAINT idx_16529_pig_pkey;
ALTER TABLE ONLY public.sig DROP CONSTRAINT idx_16518_sig_pkey;
ALTER TABLE ONLY public.pig_member DROP CONSTRAINT idx_16510_pig_member_pkey;
ALTER TABLE ONLY public.pig_website DROP CONSTRAINT idx_16500_pig_website_pkey;
ALTER TABLE ONLY public.attachment DROP CONSTRAINT idx_16493_attachment_pkey;
ALTER TABLE ONLY public."user" DROP CONSTRAINT idx_16481_sqlite_autoindex_user_1;
ALTER TABLE ONLY public.sig_member DROP CONSTRAINT idx_16474_sig_member_pkey;
ALTER TABLE ONLY public.key_value DROP CONSTRAINT idx_16465_sqlite_autoindex_key_value_1;
ALTER TABLE ONLY public.w_html_metadata DROP CONSTRAINT idx_16458_sqlite_autoindex_w_html_metadata_1;
ALTER TABLE ONLY public.standby_req_tbl DROP CONSTRAINT idx_16452_sqlite_autoindex_standby_req_tbl_1;
ALTER TABLE ONLY public.comment DROP CONSTRAINT idx_16444_comment_pkey;
ALTER TABLE ONLY public.article DROP CONSTRAINT idx_16435_article_pkey;
ALTER TABLE ONLY public.board DROP CONSTRAINT idx_16424_board_pkey;
ALTER TABLE ONLY public.file_metadata DROP CONSTRAINT idx_16417_sqlite_autoindex_file_metadata_1;
ALTER TABLE ONLY public.scsc_global_status DROP CONSTRAINT idx_16411_scsc_global_status_pkey;
ALTER TABLE ONLY public.oldboy_applicant DROP CONSTRAINT idx_16403_sqlite_autoindex_oldboy_applicant_1;
ALTER TABLE ONLY public.major DROP CONSTRAINT idx_16397_major_pkey;
ALTER TABLE ONLY public.user_role DROP CONSTRAINT idx_16391_user_role_pkey;
ALTER TABLE ONLY public.flyway_schema_history DROP CONSTRAINT flyway_schema_history_pk;
ALTER TABLE public.tag ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.sig_website ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.sig_tag ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.sig_member ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.sig ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.pig_website ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.pig_member ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.pig ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.major ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.enrollment ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.comment ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.check_user_status_rule ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.board ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.attachment ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public.article ALTER COLUMN id DROP DEFAULT;
DROP TABLE public.w_html_metadata;
DROP TABLE public.user_role;
DROP TABLE public."user";
DROP SEQUENCE public.tag_id_seq;
DROP TABLE public.tag;
DROP TABLE public.standby_req_tbl;
DROP SEQUENCE public.sig_website_id_seq;
DROP TABLE public.sig_website;
DROP SEQUENCE public.sig_tag_id_seq;
DROP TABLE public.sig_tag;
DROP SEQUENCE public.sig_member_id_seq;
DROP TABLE public.sig_member;
DROP SEQUENCE public.sig_id_seq;
DROP TABLE public.sig;
DROP TABLE public.scsc_global_status;
DROP SEQUENCE public.pig_website_id_seq;
DROP TABLE public.pig_website;
DROP SEQUENCE public.pig_member_id_seq;
DROP TABLE public.pig_member;
DROP SEQUENCE public.pig_id_seq;
DROP TABLE public.pig;
DROP TABLE public.oldboy_applicant;
DROP SEQUENCE public.major_id_seq;
DROP TABLE public.major;
DROP TABLE public.key_value;
DROP TABLE public.flyway_schema_history;
DROP TABLE public.file_metadata;
DROP SEQUENCE public.enrollment_id_seq;
DROP TABLE public.enrollment;
DROP SEQUENCE public.comment_id_seq;
DROP TABLE public.comment;
DROP SEQUENCE public.check_user_status_rule_id_seq;
DROP TABLE public.check_user_status_rule;
DROP SEQUENCE public.board_id_seq;
DROP TABLE public.board;
DROP SEQUENCE public.attachment_id_seq;
DROP TABLE public.attachment;
DROP SEQUENCE public.article_id_seq;
DROP TABLE public.article;
SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: article; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.article (
    id bigint NOT NULL,
    title text NOT NULL,
    author_id text NOT NULL,
    board_id bigint NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    content text
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
    writing_permission_level bigint DEFAULT '0'::bigint NOT NULL,
    reading_permission_level bigint DEFAULT '0'::bigint NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    board_type character varying(5) DEFAULT 'TEXT'::character varying NOT NULL,
    CONSTRAINT match_constraint CHECK (((board_type)::text = ANY ((ARRAY['IMAGE'::character varying, 'TEXT'::character varying, 'NONE'::character varying, 'FILE'::character varying])::text[])))
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
    parent_id bigint,
    is_deleted boolean DEFAULT false NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    deleted_at timestamp without time zone
);


--
-- Name: comment_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.comment_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: comment_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.comment_id_seq OWNED BY public.comment.id;


--
-- Name: enrollment; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.enrollment (
    id bigint NOT NULL,
    year bigint NOT NULL,
    semester bigint NOT NULL,
    user_id text NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
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
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    owner text
);


--
-- Name: flyway_schema_history; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.flyway_schema_history (
    installed_rank integer NOT NULL,
    version character varying(50),
    description character varying(200) NOT NULL,
    type character varying(20) NOT NULL,
    script character varying(1000) NOT NULL,
    checksum integer,
    installed_by character varying(100) NOT NULL,
    installed_on timestamp without time zone DEFAULT now() NOT NULL,
    execution_time integer NOT NULL,
    success boolean NOT NULL
);


--
-- Name: key_value; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.key_value (
    key text NOT NULL,
    value text NOT NULL,
    writing_permission_level bigint DEFAULT '500'::bigint NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
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
    processed boolean DEFAULT false NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
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
    should_extend boolean DEFAULT false NOT NULL,
    is_rolling_admission text DEFAULT 'during_recruiting'::text NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
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
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
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
    sort_order bigint DEFAULT '0'::bigint NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
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
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
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
    should_extend boolean DEFAULT false NOT NULL,
    is_rolling_admission text DEFAULT 'during_recruiting'::text NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    owner text,
    CONSTRAINT check_is_rolling_admission CHECK ((is_rolling_admission = ANY (ARRAY['always'::text, 'never'::text, 'during_recruiting'::text])))
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
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
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
-- Name: sig_tag; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.sig_tag (
    id bigint NOT NULL,
    sig_id bigint NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    tag_id bigint NOT NULL
);


--
-- Name: sig_tag_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.sig_tag_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: sig_tag_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.sig_tag_id_seq OWNED BY public.sig_tag.id;


--
-- Name: sig_website; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.sig_website (
    id bigint NOT NULL,
    sig_id bigint NOT NULL,
    label text NOT NULL,
    url text NOT NULL,
    sort_order bigint DEFAULT '0'::bigint NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


--
-- Name: sig_website_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.sig_website_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: sig_website_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.sig_website_id_seq OWNED BY public.sig_website.id;


--
-- Name: standby_req_tbl; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.standby_req_tbl (
    standby_user_id text NOT NULL,
    user_name text NOT NULL,
    deposit_name text NOT NULL,
    deposit_time timestamp without time zone,
    is_checked boolean DEFAULT false NOT NULL
);


--
-- Name: tag; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.tag (
    id bigint NOT NULL,
    text text NOT NULL,
    is_major boolean DEFAULT false NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


--
-- Name: tag_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.tag_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: tag_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.tag_id_seq OWNED BY public.tag.id;


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
    profile_picture_is_url boolean DEFAULT false NOT NULL,
    last_login timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    major_id bigint NOT NULL,
    is_active boolean DEFAULT false NOT NULL,
    is_banned boolean DEFAULT false NOT NULL
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
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
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
-- Name: comment id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.comment ALTER COLUMN id SET DEFAULT nextval('public.comment_id_seq'::regclass);


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
-- Name: sig_tag id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sig_tag ALTER COLUMN id SET DEFAULT nextval('public.sig_tag_id_seq'::regclass);


--
-- Name: sig_website id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sig_website ALTER COLUMN id SET DEFAULT nextval('public.sig_website_id_seq'::regclass);


--
-- Name: tag id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tag ALTER COLUMN id SET DEFAULT nextval('public.tag_id_seq'::regclass);


--
-- Data for Name: article; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.article (id, title, author_id, board_id, created_at, updated_at, content) FROM stdin;
1	1	85470db4f36b6d4141cc7528b8170e0f3f61c1199f4b08d5533e33ec28e23af2	1	2026-04-09 07:16:26.006766	2026-04-09 07:16:26.00678	1
2	1	85470db4f36b6d4141cc7528b8170e0f3f61c1199f4b08d5533e33ec28e23af2	1	2026-04-26 07:12:33.823565	2026-04-26 07:12:33.823585	1
3	1	85470db4f36b6d4141cc7528b8170e0f3f61c1199f4b08d5533e33ec28e23af2	4	2026-05-04 04:26:17.742475	2026-05-04 04:26:17.742499	![album_image](/api/image/download/bbe04e8c-3133-44c1-91be-78b666027127)\n\n1
\.


--
-- Data for Name: attachment; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.attachment (id, article_id, file_id) FROM stdin;
1	3	bbe04e8c-3133-44c1-91be-78b666027127
\.


--
-- Data for Name: board; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.board (id, name, description, writing_permission_level, reading_permission_level, created_at, updated_at, board_type) FROM stdin;
1	Sig	sig advertising board	1000	0	2026-04-08 08:04:24.720287	2026-04-08 08:04:24.720287	NONE
2	Pig	pig advertising board	1000	0	2026-04-08 08:04:24.720287	2026-04-08 08:04:24.720287	NONE
3	Project Archive	archive of various projects held in the club	300	0	2026-04-08 08:04:24.720287	2026-04-08 08:04:24.720287	TEXT
4	Album	photos of club members and activities	500	0	2026-04-08 08:04:24.720287	2026-04-08 08:04:24.720287	IMAGE
5	Notice	notices from club executive	500	100	2026-04-08 08:04:24.720287	2026-04-08 08:04:24.720287	TEXT
6	Grant	applications for sig/pig grant	200	500	2026-04-08 08:04:24.720287	2026-04-08 08:04:24.720287	TEXT
\.


--
-- Data for Name: check_user_status_rule; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.check_user_status_rule (id, method, path) FROM stdin;
1	POST	/api/executive/pig/%/delete
2	POST	/api/executive/pig/%/member/join
3	POST	/api/executive/pig/%/member/leave
4	POST	/api/executive/pig/%/update
5	POST	/api/executive/sig/%/delete
6	POST	/api/executive/sig/%/member/join
7	POST	/api/executive/sig/%/member/leave
8	POST	/api/executive/sig/%/update
9	POST	/api/pig/%/delete
10	POST	/api/pig/%/handover
11	POST	/api/pig/%/member/join
12	POST	/api/pig/%/member/leave
13	POST	/api/pig/%/update
14	POST	/api/pig/create
15	POST	/api/sig/%/delete
16	POST	/api/sig/%/handover
17	POST	/api/sig/%/member/join
18	POST	/api/sig/%/member/leave
19	POST	/api/sig/%/update
20	POST	/api/sig/create
\.


--
-- Data for Name: comment; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.comment (id, content, author_id, article_id, parent_id, is_deleted, created_at, updated_at, deleted_at) FROM stdin;
\.


--
-- Data for Name: enrollment; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.enrollment (id, year, semester, user_id, created_at) FROM stdin;
\.


--
-- Data for Name: file_metadata; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.file_metadata (id, original_filename, size, mime_type, created_at, owner) FROM stdin;
bbe04e8c-3133-44c1-91be-78b666027127	스크린샷 2026-05-04 132536.png	59202	image/png	2026-05-04 04:26:11.105557	85470db4f36b6d4141cc7528b8170e0f3f61c1199f4b08d5533e33ec28e23af2
18bbc7b5-19ca-4da3-b70f-fb3b2fa4e054	스크린샷 2025-07-17 144110.png	40933	image/png	2026-05-04 09:32:14.926734	85470db4f36b6d4141cc7528b8170e0f3f61c1199f4b08d5533e33ec28e23af2
08c61eec-b398-4790-b8ca-16dfb0431953	스크린샷 2025-07-23 211500.png	22384	image/png	2026-05-04 09:35:04.999707	85470db4f36b6d4141cc7528b8170e0f3f61c1199f4b08d5533e33ec28e23af2
c0b7e54e-ecdf-4465-ae45-32fef7a93f77	스크린샷 2025-07-17 144110.png	40933	image/png	2026-05-04 09:35:12.825772	85470db4f36b6d4141cc7528b8170e0f3f61c1199f4b08d5533e33ec28e23af2
4b34c3ce-518d-43a4-8a5e-fbcaf1d7fae3	스크린샷 2025-07-23 211500.png	22384	image/png	2026-05-04 09:35:13.014766	85470db4f36b6d4141cc7528b8170e0f3f61c1199f4b08d5533e33ec28e23af2
2b211a70-3f36-4190-b7b3-0a3a120468da	스크린샷 2025-07-25 175803.png	21727	image/png	2026-05-04 09:35:13.242903	85470db4f36b6d4141cc7528b8170e0f3f61c1199f4b08d5533e33ec28e23af2
85b43d18-d621-4354-b725-7172e7538fe7	스크린샷 2025-07-26 150907.png	15103	image/png	2026-05-04 09:35:13.425269	85470db4f36b6d4141cc7528b8170e0f3f61c1199f4b08d5533e33ec28e23af2
96bb3423-8370-4002-807e-753b5f6074b4	스크린샷 2025-07-26 152118.png	18884	image/png	2026-05-04 09:35:13.584961	85470db4f36b6d4141cc7528b8170e0f3f61c1199f4b08d5533e33ec28e23af2
a828d46d-2268-44e8-a997-3bb34af667c0	스크린샷 2025-07-26 164505.png	5210	image/png	2026-05-04 09:35:13.757047	85470db4f36b6d4141cc7528b8170e0f3f61c1199f4b08d5533e33ec28e23af2
fb601124-9d10-4d9d-be5b-47b6c2ea33fd	스크린샷 2025-07-26 180721.png	2445	image/png	2026-05-04 09:35:13.932564	85470db4f36b6d4141cc7528b8170e0f3f61c1199f4b08d5533e33ec28e23af2
abc436e2-9726-41eb-b43e-3ebc6ef63f68	스크린샷 2025-07-26 181712.png	19383	image/png	2026-05-04 09:35:14.104253	85470db4f36b6d4141cc7528b8170e0f3f61c1199f4b08d5533e33ec28e23af2
\.


--
-- Data for Name: flyway_schema_history; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.flyway_schema_history (installed_rank, version, description, type, script, checksum, installed_by, installed_on, execution_time, success) FROM stdin;
1	1	init	SQL	V1__init.sql	-755420259	postgres	2026-04-08 08:04:24.51241	546	t
2	2	make deposit time nullable	SQL	V2__make_deposit_time_nullable.sql	823010732	postgres	2026-04-08 08:04:25.281177	45	t
3	3	create sig tag	SQL	V3__create_sig_tag.sql	1041146251	postgres	2026-04-08 08:04:25.350632	17	t
4	4	create tag system	SQL	V4__create_tag_system.sql	-926774988	postgres	2026-04-08 08:04:25.392165	93	t
5	5	add leadership kv	SQL	V5__add_leadership_kv.sql	-946048167	postgres	2026-04-08 08:04:25.508019	9	t
6	6	create sig website	SQL	V6__create_sig_website.sql	85078318	postgres	2026-04-08 08:04:25.532995	14	t
7	7	align sig with pig	SQL	V7__align_sig_with_pig.sql	1868158606	postgres	2026-04-08 08:04:25.565172	28	t
8	8	add article content	SQL	V8__add_article_content.sql	-1752135588	postgres	2026-04-08 08:04:25.604796	4	t
9	9	alter board add board type	SQL	V9__alter_board_add_board_type.sql	359054153	postgres	2026-04-08 08:04:25.623961	12	t
10	10	remove article soft delete	SQL	V10__remove_article_soft_delete.sql	1782590859	postgres	2026-05-04 04:20:15.969849	230	t
\.


--
-- Data for Name: key_value; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.key_value (key, value, writing_permission_level, created_at, updated_at) FROM stdin;
footer-message	서울대학교 컴퓨터 연구회\\n회장 XXX 010-xxxx-xxxx\\nscsc.snu@gmail.com	500	2026-04-08 08:04:24.720287	2026-04-08 08:04:24.720287
main-president		500	2026-04-08 08:04:24.720287	2026-04-08 08:04:24.720287
vice-president		500	2026-04-08 08:04:24.720287	2026-04-08 08:04:24.720287
enrollment_grant_until	2026-2	500	2026-04-08 08:04:24.720287	2026-04-08 08:04:24.720287
president-name	XXX	500	2026-04-08 08:04:25.513598	2026-04-08 08:04:25.513598
vice-president-name	XXX;XXX	500	2026-04-08 08:04:25.513598	2026-04-08 08:04:25.513598
president-phone	010-XXXX-XXXX	500	2026-04-08 08:04:25.513598	2026-04-08 08:04:25.513598
vice-president-phone	010-XXXX-XXXX;010-XXXX-XXXX	500	2026-04-08 08:04:25.513598	2026-04-08 08:04:25.513598
\.


--
-- Data for Name: major; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.major (id, college, major_name) FROM stdin;
1	인문대학	인문계열
2	인문대학	국어국문학과
3	인문대학	중어중문학과
4	인문대학	영어영문학과
5	인문대학	불어불문학과
6	인문대학	독어독문학과
7	인문대학	노어노문학과
8	인문대학	서어서문학과
9	인문대학	언어학과
10	인문대학	아시아언어문명학부
11	인문대학	역사학부
12	인문대학	고고미술사학과
13	인문대학	철학과
14	인문대학	종교학과
15	인문대학	미학과
16	사회과학대학	정치외교학부
17	사회과학대학	경제학부
18	사회과학대학	사회학과
19	사회과학대학	인류학과
20	사회과학대학	심리학과
21	사회과학대학	지리학과
22	사회과학대학	사회복지학과
23	사회과학대학	언론정보학과
24	자연과학대학	수리과학부
25	자연과학대학	통계학과
26	자연과학대학	물리·천문학부
27	자연과학대학	화학부
28	자연과학대학	생명과학부
29	자연과학대학	지구환경과학부
30	간호대학	간호대학
31	경영대학	경영대학
32	공과대학	광역
33	공과대학	건설환경공학부
34	공과대학	기계공학부
35	공과대학	재료공학부
36	공과대학	전기·정보공학부
37	공과대학	컴퓨터공학부
38	공과대학	화학생물공학부
39	공과대학	건축학과
40	공과대학	산업공학과
41	공과대학	에너지자원공학과
42	공과대학	원자핵공학과
43	공과대학	조선해양공학과
44	공과대학	항공우주공학과
45	농업생명과학대학	농경제사회학부
46	농업생명과학대학	식물생산과학부
47	농업생명과학대학	산림과학부
48	농업생명과학대학	식품·동물생명공학부
49	농업생명과학대학	응용생물화학부
50	농업생명과학대학	조경·지역시스템공학부
51	농업생명과학대학	바이오시스템·소재학부
52	농업생명과학대학	스마트시스템과학과
53	미술대학	동양화과
54	미술대학	서양화과
55	미술대학	조소과
56	미술대학	공예과
57	미술대학	디자인과
58	사범대학	교육학과
59	사범대학	국어교육과
60	사범대학	영어교육과
61	사범대학	독어교육과
62	사범대학	불어교육과
63	사범대학	사회교육과
64	사범대학	역사교육과
65	사범대학	지리교육과
66	사범대학	윤리교육과
67	사범대학	수학교육과
68	사범대학	물리교육과
69	사범대학	화학교육과
70	사범대학	생물교육과
71	사범대학	지구과학교육과
72	사범대학	체육교육과
73	생활과학대학	소비자아동학부
74	생활과학대학	식품영양학과
75	생활과학대학	의류학과
76	수의과대학	수의예과
77	약학대학	약학계열
78	음악대학	성악과
79	음악대학	작곡과
80	음악대학	음악학과
81	음악대학	피아노과
82	음악대학	관현악과
83	음악대학	국악과
84	의과대학	의예과
85	첨단융합학부	첨단융합학부
86	학부대학	광역
87	학부대학	자유전공학부
88	치의학대학원	치의학과
\.


--
-- Data for Name: oldboy_applicant; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.oldboy_applicant (id, processed, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: pig; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.pig (id, title, description, content_id, status, created_year, created_semester, year, semester, should_extend, is_rolling_admission, created_at, updated_at, owner) FROM stdin;
1	1	1	2	recruiting	2026	1	2026	1	f	during_recruiting	2026-04-26 07:12:33.863042	2026-04-26 07:12:33.863055	85470db4f36b6d4141cc7528b8170e0f3f61c1199f4b08d5533e33ec28e23af2
\.


--
-- Data for Name: pig_member; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.pig_member (id, ig_id, user_id, created_at) FROM stdin;
1	1	85470db4f36b6d4141cc7528b8170e0f3f61c1199f4b08d5533e33ec28e23af2	2026-04-26 07:12:33.877843
\.


--
-- Data for Name: pig_website; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.pig_website (id, pig_id, label, url, sort_order, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: scsc_global_status; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.scsc_global_status (id, status, year, semester, updated_at) FROM stdin;
1	recruiting	2026	1	2026-04-08 08:04:24.720287
\.


--
-- Data for Name: sig; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.sig (id, title, description, content_id, status, created_year, created_semester, year, semester, should_extend, is_rolling_admission, created_at, updated_at, owner) FROM stdin;
1	1	1	1	recruiting	2026	1	2026	1	f	always	2026-04-09 07:16:26.033517	2026-04-09 07:16:26.033538	85470db4f36b6d4141cc7528b8170e0f3f61c1199f4b08d5533e33ec28e23af2
\.


--
-- Data for Name: sig_member; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.sig_member (id, ig_id, user_id, created_at) FROM stdin;
1	1	85470db4f36b6d4141cc7528b8170e0f3f61c1199f4b08d5533e33ec28e23af2	2026-04-09 07:16:26.042785
\.


--
-- Data for Name: sig_tag; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.sig_tag (id, sig_id, created_at, tag_id) FROM stdin;
\.


--
-- Data for Name: sig_website; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.sig_website (id, sig_id, label, url, sort_order, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: standby_req_tbl; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.standby_req_tbl (standby_user_id, user_name, deposit_name, deposit_time, is_checked) FROM stdin;
\.


--
-- Data for Name: tag; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.tag (id, text, is_major, created_at) FROM stdin;
\.


--
-- Data for Name: user; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public."user" (id, email, name, phone, student_id, role, discord_id, discord_name, profile_picture, profile_picture_is_url, last_login, created_at, updated_at, major_id, is_active, is_banned) FROM stdin;
0bf31e3f7519f1a089553e619c01b015fbe206b37634ad27b056d0059d41786d	deposit.app@scsc.dev	Deposit App	09900000002	200000002	1000	\N	\N	\N	f	2026-04-08 08:04:24.720287	2026-04-08 08:04:24.720287	2026-04-08 08:04:24.720287	1	t	f
a44946fbf09c326520c2ca0a324b19100381911c9afe5af06a90b636d8f35dd5	bot@discord.com	Discord Bot	09900000001	200000001	1000	\N	\N	\N	f	2026-04-08 08:04:24.720287	2026-04-08 08:04:24.720287	2026-04-08 08:04:24.720287	1	t	f
85470db4f36b6d4141cc7528b8170e0f3f61c1199f4b08d5533e33ec28e23af2	ty0908@snu.ac.kr	이태윤	01025193272	202516742	500	\N	\N	https://lh3.googleusercontent.com/a/ACg8ocJ6WBMmE94Bso0l3uBCj_JlL1A_Xs8HugUqBgR9foTyNALIkA=s96-c	t	2026-05-04 09:31:44.217227	2026-04-08 08:11:42.449419	2026-05-04 09:31:44.225904	78	t	f
fc2eef7ad1e1f2f91786b4fd4f65508651373b0ad6fc4f13103c452369bc9703	president@example.com	President	01012345678	202412345	1000	\N	\N	\N	f	2026-05-17 11:33:03.19648	2026-05-17 11:31:30.396624	2026-05-17 11:33:03.198823	1	t	f
\.


--
-- Data for Name: user_role; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.user_role (level, name, kor_name) FROM stdin;
0	lowest	최저권한
100	dormant	휴회원
200	newcomer	준회원
300	member	정회원
400	oldboy	졸업생
500	executive	운영진
1000	president	회장
\.


--
-- Data for Name: w_html_metadata; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.w_html_metadata (name, size, created_at, updated_at, creator) FROM stdin;
\.


--
-- Name: article_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.article_id_seq', 3, true);


--
-- Name: attachment_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.attachment_id_seq', 1, true);


--
-- Name: board_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.board_id_seq', 6, true);


--
-- Name: check_user_status_rule_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.check_user_status_rule_id_seq', 20, true);


--
-- Name: comment_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.comment_id_seq', 1, false);


--
-- Name: enrollment_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.enrollment_id_seq', 1, false);


--
-- Name: major_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.major_id_seq', 88, true);


--
-- Name: pig_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.pig_id_seq', 1, true);


--
-- Name: pig_member_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.pig_member_id_seq', 1, true);


--
-- Name: pig_website_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.pig_website_id_seq', 1, false);


--
-- Name: sig_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.sig_id_seq', 1, true);


--
-- Name: sig_member_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.sig_member_id_seq', 1, true);


--
-- Name: sig_tag_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.sig_tag_id_seq', 1, false);


--
-- Name: sig_website_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.sig_website_id_seq', 1, false);


--
-- Name: tag_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.tag_id_seq', 1, false);


--
-- Name: flyway_schema_history flyway_schema_history_pk; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.flyway_schema_history
    ADD CONSTRAINT flyway_schema_history_pk PRIMARY KEY (installed_rank);


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
-- Name: sig_tag sig_tag_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sig_tag
    ADD CONSTRAINT sig_tag_pkey PRIMARY KEY (id);


--
-- Name: sig_tag sig_tag_sig_id_tag_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sig_tag
    ADD CONSTRAINT sig_tag_sig_id_tag_id_key UNIQUE (sig_id, tag_id);


--
-- Name: sig_website sig_website_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sig_website
    ADD CONSTRAINT sig_website_pkey PRIMARY KEY (id);


--
-- Name: tag tag_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tag
    ADD CONSTRAINT tag_pkey PRIMARY KEY (id);


--
-- Name: tag tag_text_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tag
    ADD CONSTRAINT tag_text_key UNIQUE (text);


--
-- Name: flyway_schema_history_s_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX flyway_schema_history_s_idx ON public.flyway_schema_history USING btree (success);


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
-- Name: sig_tag sig_tag_sig_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sig_tag
    ADD CONSTRAINT sig_tag_sig_id_fkey FOREIGN KEY (sig_id) REFERENCES public.sig(id) ON DELETE CASCADE;


--
-- Name: sig_tag sig_tag_tag_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sig_tag
    ADD CONSTRAINT sig_tag_tag_id_fkey FOREIGN KEY (tag_id) REFERENCES public.tag(id) ON DELETE CASCADE;


--
-- Name: sig_website sig_website_sig_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.sig_website
    ADD CONSTRAINT sig_website_sig_id_fkey FOREIGN KEY (sig_id) REFERENCES public.sig(id) ON DELETE CASCADE;


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
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: -
--

GRANT USAGE ON SCHEMA public TO app_user;
GRANT USAGE ON SCHEMA public TO readonly_user;


--
-- Name: TABLE article; Type: ACL; Schema: public; Owner: -
--

GRANT ALL ON TABLE public.article TO app_user;
GRANT SELECT ON TABLE public.article TO readonly_user;


--
-- Name: SEQUENCE article_id_seq; Type: ACL; Schema: public; Owner: -
--

GRANT ALL ON SEQUENCE public.article_id_seq TO app_user;
GRANT SELECT,USAGE ON SEQUENCE public.article_id_seq TO readonly_user;


--
-- Name: TABLE attachment; Type: ACL; Schema: public; Owner: -
--

GRANT ALL ON TABLE public.attachment TO app_user;
GRANT SELECT ON TABLE public.attachment TO readonly_user;


--
-- Name: SEQUENCE attachment_id_seq; Type: ACL; Schema: public; Owner: -
--

GRANT ALL ON SEQUENCE public.attachment_id_seq TO app_user;
GRANT SELECT,USAGE ON SEQUENCE public.attachment_id_seq TO readonly_user;


--
-- Name: TABLE board; Type: ACL; Schema: public; Owner: -
--

GRANT ALL ON TABLE public.board TO app_user;
GRANT SELECT ON TABLE public.board TO readonly_user;


--
-- Name: SEQUENCE board_id_seq; Type: ACL; Schema: public; Owner: -
--

GRANT ALL ON SEQUENCE public.board_id_seq TO app_user;
GRANT SELECT,USAGE ON SEQUENCE public.board_id_seq TO readonly_user;


--
-- Name: TABLE check_user_status_rule; Type: ACL; Schema: public; Owner: -
--

GRANT ALL ON TABLE public.check_user_status_rule TO app_user;
GRANT SELECT ON TABLE public.check_user_status_rule TO readonly_user;


--
-- Name: SEQUENCE check_user_status_rule_id_seq; Type: ACL; Schema: public; Owner: -
--

GRANT ALL ON SEQUENCE public.check_user_status_rule_id_seq TO app_user;
GRANT SELECT,USAGE ON SEQUENCE public.check_user_status_rule_id_seq TO readonly_user;


--
-- Name: TABLE comment; Type: ACL; Schema: public; Owner: -
--

GRANT ALL ON TABLE public.comment TO app_user;
GRANT SELECT ON TABLE public.comment TO readonly_user;


--
-- Name: SEQUENCE comment_id_seq; Type: ACL; Schema: public; Owner: -
--

GRANT ALL ON SEQUENCE public.comment_id_seq TO app_user;
GRANT SELECT,USAGE ON SEQUENCE public.comment_id_seq TO readonly_user;


--
-- Name: TABLE enrollment; Type: ACL; Schema: public; Owner: -
--

GRANT ALL ON TABLE public.enrollment TO app_user;
GRANT SELECT ON TABLE public.enrollment TO readonly_user;


--
-- Name: SEQUENCE enrollment_id_seq; Type: ACL; Schema: public; Owner: -
--

GRANT ALL ON SEQUENCE public.enrollment_id_seq TO app_user;
GRANT SELECT,USAGE ON SEQUENCE public.enrollment_id_seq TO readonly_user;


--
-- Name: TABLE file_metadata; Type: ACL; Schema: public; Owner: -
--

GRANT ALL ON TABLE public.file_metadata TO app_user;
GRANT SELECT ON TABLE public.file_metadata TO readonly_user;


--
-- Name: TABLE flyway_schema_history; Type: ACL; Schema: public; Owner: -
--

GRANT ALL ON TABLE public.flyway_schema_history TO app_user;
GRANT SELECT ON TABLE public.flyway_schema_history TO readonly_user;


--
-- Name: TABLE key_value; Type: ACL; Schema: public; Owner: -
--

GRANT ALL ON TABLE public.key_value TO app_user;
GRANT SELECT ON TABLE public.key_value TO readonly_user;


--
-- Name: TABLE major; Type: ACL; Schema: public; Owner: -
--

GRANT ALL ON TABLE public.major TO app_user;
GRANT SELECT ON TABLE public.major TO readonly_user;


--
-- Name: SEQUENCE major_id_seq; Type: ACL; Schema: public; Owner: -
--

GRANT ALL ON SEQUENCE public.major_id_seq TO app_user;
GRANT SELECT,USAGE ON SEQUENCE public.major_id_seq TO readonly_user;


--
-- Name: TABLE oldboy_applicant; Type: ACL; Schema: public; Owner: -
--

GRANT ALL ON TABLE public.oldboy_applicant TO app_user;
GRANT SELECT ON TABLE public.oldboy_applicant TO readonly_user;


--
-- Name: TABLE pig; Type: ACL; Schema: public; Owner: -
--

GRANT ALL ON TABLE public.pig TO app_user;
GRANT SELECT ON TABLE public.pig TO readonly_user;


--
-- Name: SEQUENCE pig_id_seq; Type: ACL; Schema: public; Owner: -
--

GRANT ALL ON SEQUENCE public.pig_id_seq TO app_user;
GRANT SELECT,USAGE ON SEQUENCE public.pig_id_seq TO readonly_user;


--
-- Name: TABLE pig_member; Type: ACL; Schema: public; Owner: -
--

GRANT ALL ON TABLE public.pig_member TO app_user;
GRANT SELECT ON TABLE public.pig_member TO readonly_user;


--
-- Name: SEQUENCE pig_member_id_seq; Type: ACL; Schema: public; Owner: -
--

GRANT ALL ON SEQUENCE public.pig_member_id_seq TO app_user;
GRANT SELECT,USAGE ON SEQUENCE public.pig_member_id_seq TO readonly_user;


--
-- Name: TABLE pig_website; Type: ACL; Schema: public; Owner: -
--

GRANT ALL ON TABLE public.pig_website TO app_user;
GRANT SELECT ON TABLE public.pig_website TO readonly_user;


--
-- Name: SEQUENCE pig_website_id_seq; Type: ACL; Schema: public; Owner: -
--

GRANT ALL ON SEQUENCE public.pig_website_id_seq TO app_user;
GRANT SELECT,USAGE ON SEQUENCE public.pig_website_id_seq TO readonly_user;


--
-- Name: TABLE scsc_global_status; Type: ACL; Schema: public; Owner: -
--

GRANT ALL ON TABLE public.scsc_global_status TO app_user;
GRANT SELECT ON TABLE public.scsc_global_status TO readonly_user;


--
-- Name: TABLE sig; Type: ACL; Schema: public; Owner: -
--

GRANT ALL ON TABLE public.sig TO app_user;
GRANT SELECT ON TABLE public.sig TO readonly_user;


--
-- Name: SEQUENCE sig_id_seq; Type: ACL; Schema: public; Owner: -
--

GRANT ALL ON SEQUENCE public.sig_id_seq TO app_user;
GRANT SELECT,USAGE ON SEQUENCE public.sig_id_seq TO readonly_user;


--
-- Name: TABLE sig_member; Type: ACL; Schema: public; Owner: -
--

GRANT ALL ON TABLE public.sig_member TO app_user;
GRANT SELECT ON TABLE public.sig_member TO readonly_user;


--
-- Name: SEQUENCE sig_member_id_seq; Type: ACL; Schema: public; Owner: -
--

GRANT ALL ON SEQUENCE public.sig_member_id_seq TO app_user;
GRANT SELECT,USAGE ON SEQUENCE public.sig_member_id_seq TO readonly_user;


--
-- Name: TABLE sig_tag; Type: ACL; Schema: public; Owner: -
--

GRANT ALL ON TABLE public.sig_tag TO app_user;
GRANT SELECT ON TABLE public.sig_tag TO readonly_user;


--
-- Name: SEQUENCE sig_tag_id_seq; Type: ACL; Schema: public; Owner: -
--

GRANT ALL ON SEQUENCE public.sig_tag_id_seq TO app_user;
GRANT SELECT,USAGE ON SEQUENCE public.sig_tag_id_seq TO readonly_user;


--
-- Name: TABLE sig_website; Type: ACL; Schema: public; Owner: -
--

GRANT ALL ON TABLE public.sig_website TO app_user;
GRANT SELECT ON TABLE public.sig_website TO readonly_user;


--
-- Name: SEQUENCE sig_website_id_seq; Type: ACL; Schema: public; Owner: -
--

GRANT ALL ON SEQUENCE public.sig_website_id_seq TO app_user;
GRANT SELECT,USAGE ON SEQUENCE public.sig_website_id_seq TO readonly_user;


--
-- Name: TABLE standby_req_tbl; Type: ACL; Schema: public; Owner: -
--

GRANT ALL ON TABLE public.standby_req_tbl TO app_user;
GRANT SELECT ON TABLE public.standby_req_tbl TO readonly_user;


--
-- Name: TABLE tag; Type: ACL; Schema: public; Owner: -
--

GRANT ALL ON TABLE public.tag TO app_user;
GRANT SELECT ON TABLE public.tag TO readonly_user;


--
-- Name: SEQUENCE tag_id_seq; Type: ACL; Schema: public; Owner: -
--

GRANT ALL ON SEQUENCE public.tag_id_seq TO app_user;
GRANT SELECT,USAGE ON SEQUENCE public.tag_id_seq TO readonly_user;


--
-- Name: TABLE "user"; Type: ACL; Schema: public; Owner: -
--

GRANT ALL ON TABLE public."user" TO app_user;
GRANT SELECT ON TABLE public."user" TO readonly_user;


--
-- Name: TABLE user_role; Type: ACL; Schema: public; Owner: -
--

GRANT ALL ON TABLE public.user_role TO app_user;
GRANT SELECT ON TABLE public.user_role TO readonly_user;


--
-- Name: TABLE w_html_metadata; Type: ACL; Schema: public; Owner: -
--

GRANT ALL ON TABLE public.w_html_metadata TO app_user;
GRANT SELECT ON TABLE public.w_html_metadata TO readonly_user;


--
-- Name: DEFAULT PRIVILEGES FOR SEQUENCES; Type: DEFAULT ACL; Schema: public; Owner: -
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT ALL ON SEQUENCES TO app_user;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT SELECT,USAGE ON SEQUENCES TO readonly_user;


--
-- Name: DEFAULT PRIVILEGES FOR TABLES; Type: DEFAULT ACL; Schema: public; Owner: -
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT ALL ON TABLES TO app_user;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT SELECT ON TABLES TO readonly_user;


--
-- PostgreSQL database dump complete
--

\unrestrict qT0xgS3lMfdIZz0aYUWbaoD0JnFNjfXfwEdvzNf3Ie37ji4wbjMT13SeMoIj6RV

