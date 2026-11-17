import os
import subprocess
import tarfile
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from src.core import get_settings, logger
from src.model import SCSCGlobalStatus
from src.util import map_semester_name

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_STATIC_DIR = _PROJECT_ROOT / "static"

_ARCHIVE_SQL_NAME = "db.sql"
_ARCHIVE_STATIC_NAME = "static"


def backup_db_before_status_change(scsc_global_status: SCSCGlobalStatus) -> Path:
    """Create a timestamped .tar.gz backup using (pg_dump SQL+static folder) before status roll-over."""
    settings = get_settings()

    year = scsc_global_status.year
    semester = scsc_global_status.semester
    status = scsc_global_status.status
    semester_label = map_semester_name.get(semester, str(semester))

    backup_dir = _PROJECT_ROOT / "logs" / "db_backups"
    backup_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    backup_name = (
        f"{settings.db_name}_{year}_{semester_label}_{status.value}_"
        f"{timestamp}_before_status_change.tar.gz"
    )
    backup_path = backup_dir / backup_name

    with tempfile.TemporaryDirectory() as tmp_dir:
        sql_path = Path(tmp_dir) / _ARCHIVE_SQL_NAME
        _dump_db(sql_path)

        try:
            with tarfile.open(backup_path, "w:gz") as tar:
                tar.add(sql_path, arcname=_ARCHIVE_SQL_NAME)
                if _STATIC_DIR.is_dir():
                    tar.add(_STATIC_DIR, arcname=_ARCHIVE_STATIC_NAME)
        except Exception:
            backup_path.unlink(missing_ok=True)
            raise

    logger.info(
        "info_type=db_backup ; action=before_status_change ; database=%s ; backup=%s",
        settings.db_name,
        backup_path,
    )
    return backup_path


def _dump_db(sql_path: Path) -> None:
    settings = get_settings()
    env = os.environ.copy()
    env["PGPASSWORD"] = settings.db_password

    command = [
        "pg_dump",
        "-h",
        "db",
        "-U",
        settings.db_user,
        "-d",
        settings.db_name,
        "-f",
        str(sql_path),
        "--no-owner",
        "--clean",
        "--if-exists",
    ]

    try:
        subprocess.run(command, env=env, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        logger.error("Database backup failed: %s", e.stderr)
        raise RuntimeError(f"PostgreSQL backup failed: {e.stderr}") from e
