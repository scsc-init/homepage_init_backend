from __future__ import annotations

import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path

from src.core import get_settings, logger
from src.model import SCSCGlobalStatus

from .helper import map_semester_name

_PROJECT_ROOT = Path(__file__).resolve().parents[2]


def backup_db_before_status_change(scsc_global_status: SCSCGlobalStatus) -> Path:
    """Create a timestamped SQLite backup before status roll-over."""
    year = scsc_global_status.year
    semester = scsc_global_status.semester
    status = scsc_global_status.status

    settings = get_settings()
    sqlite_path = Path(settings.sqlite_filename)
    if not sqlite_path.is_absolute():
        sqlite_path = _PROJECT_ROOT / sqlite_path

    if not sqlite_path.exists():
        raise FileNotFoundError(f"database file '{sqlite_path}' does not exist")

    backup_dir = _PROJECT_ROOT / "logs" / "db_backups"
    backup_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    semester_label = map_semester_name.get(semester, str(semester))
    suffix = sqlite_path.suffix or ".db"
    backup_name = (
        f"{sqlite_path.stem}_{year}_{semester_label}_{status}_{timestamp}_before_status_change"
        f"{suffix}"
    )
    backup_path = backup_dir / backup_name

    with (
        closing(sqlite3.connect(str(sqlite_path))) as src_conn,
        closing(sqlite3.connect(str(backup_path))) as dst_conn,
    ):
        with dst_conn:
            src_conn.backup(dst_conn)

    logger.info(
        "info_type=db_backup ; action=before_status_change ; source=%s ; backup=%s",
        sqlite_path,
        backup_path,
    )

    return backup_path
