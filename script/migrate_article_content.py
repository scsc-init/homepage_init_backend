from __future__ import annotations

import argparse
import logging
import os
import sys
from pathlib import Path
from typing import Iterable, NamedTuple

from dotenv import load_dotenv

try:
    import psycopg
except ImportError as exc:
    raise SystemExit(
        'psycopg package is required. Install it via `uv add "psycopg[binary]"` '
        "or `pip install psycopg[binary]`."
    ) from exc


LOG = logging.getLogger("migrate_article_content")


load_dotenv()


class ProcessResult(NamedTuple):
    article_id: int
    status: str
    detail: str | None = None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Populate the article.content column with data from static markdown "
            "files."
        )
    )
    parser.add_argument(
        "--dsn",
        help=(
            "Full psycopg connection string. If omitted, individual host/user"
            "/password options are used."
        ),
    )
    parser.add_argument(
        "--host",
        default=os.getenv("DB_HOST", "localhost"),
        help="Database host (default: %(default)s)",
    )
    parser.add_argument(
        "--port",
        default=int(os.getenv("DB_PORT", 5432)),
        type=int,
        help="Database port (default: %(default)s)",
    )
    parser.add_argument(
        "--dbname",
        default=os.getenv("DB_NAME", "main_db"),
        help="Database name (default: %(default)s)",
    )
    parser.add_argument(
        "--user",
        default=os.getenv("DB_USER", "app_user"),
        help="Database user (default: DB_USER env or %(default)s)",
    )
    parser.add_argument(
        "--password",
        default=os.getenv("DB_PASSWORD"),
        help="Database password (default: DB_PASSWORD env)",
    )
    parser.add_argument(
        "--article-dir",
        default=os.getenv("ARTICLE_DIR", "static/article"),
        help="Directory containing article markdown files (default: %(default)s)",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=100,
        help="How many updates to apply before committing (default: %(default)s)",
    )
    parser.add_argument(
        "--resume-after",
        type=int,
        help="Skip files with article_id <= this value (useful for restarts)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Scan files and log actions without touching the database",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing article.content values instead of skipping",
    )
    parser.add_argument(
        "--encoding",
        default="utf-8",
        help="Encoding used to read .md files (default: %(default)s)",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
    )
    return parser.parse_args()


def iter_article_files(article_dir: Path) -> Iterable[tuple[int, Path]]:
    for file_path in sorted(article_dir.glob("*.md")):
        try:
            article_id = int(file_path.stem)
        except ValueError:
            LOG.warning("Skipping %s: filename is not an integer id", file_path)
            continue
        yield article_id, file_path


def update_article_content(
    conn: psycopg.Connection,
    article_id: int,
    content: str,
    force: bool,
) -> ProcessResult:
    sql = "UPDATE article SET content = %s WHERE id = %s"
    params: tuple[object, ...] = (content, article_id)
    if not force:
        sql += " AND content IS NULL"

    with conn.cursor() as cur:
        cur.execute(sql, params)
        if cur.rowcount:
            return ProcessResult(article_id, "updated")

        cur.execute("SELECT 1 FROM article WHERE id = %s", (article_id,))
        exists = cur.fetchone() is not None

    if exists:
        return ProcessResult(article_id, "skipped", "content already present")
    return ProcessResult(article_id, "missing", "article row not found")


def main() -> int:
    args = parse_args()
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )

    article_dir = Path(args.article_dir).expanduser().resolve()
    if not article_dir.exists():
        LOG.error("Article directory %s does not exist", article_dir)
        return 1

    connect_args: dict[str, object]
    if args.dsn:
        connect_args = {"conninfo": args.dsn}
    else:
        connect_args = {
            "host": args.host,
            "port": args.port,
            "dbname": args.dbname,
            "user": args.user,
            "password": args.password,
        }
        connect_args = {k: v for k, v in connect_args.items() if v is not None}

    stats = {"updated": 0, "skipped": 0, "missing": 0}
    processed = 0
    commit_counter = 0

    if args.dry_run:
        for article_id, path in iter_article_files(article_dir):
            if args.resume_after and article_id <= args.resume_after:
                continue
            _ = path.read_text(encoding=args.encoding)
            LOG.info("[dry-run] would update article_id=%s", article_id)
        LOG.info("Dry run complete")
        return 0

    with psycopg.connect(**connect_args) as conn:
        conn.autocommit = False
        for article_id, path in iter_article_files(article_dir):
            if args.resume_after and article_id <= args.resume_after:
                continue

            try:
                content = path.read_text(encoding=args.encoding)
            except UnicodeDecodeError as exc:
                LOG.error("Failed to read %s: %s", path, exc)
                continue

            result = update_article_content(conn, article_id, content, args.force)
            stats[result.status] += 1
            processed += 1
            commit_counter += 1

            if result.status == "missing":
                LOG.warning("article_id=%s missing in DB", article_id)
            elif result.status == "skipped":
                LOG.info(
                    "article_id=%s skipped (%s)",
                    article_id,
                    result.detail or "already migrated",
                )

            if commit_counter >= args.batch_size:
                conn.commit()
                commit_counter = 0
                LOG.info("Committed batch after %s processed rows", processed)

        if commit_counter:
            conn.commit()

    LOG.info(
        "Done. updated=%s skipped=%s missing=%s",
        stats["updated"],
        stats["skipped"],
        stats["missing"],
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
