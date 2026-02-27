import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from src.core import get_settings, logger
from src.model import SCSCGlobalStatus
from src.util import map_semester_name

_PROJECT_ROOT = Path(__file__).resolve().parents[2]


def backup_db_before_status_change(scsc_global_status: SCSCGlobalStatus) -> Path:
    """Create a timestamped PostgreSQL backup using pg_dump before status roll-over."""
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
        f"{timestamp}_before_status_change.sql"
    )
    backup_path = backup_dir / backup_name

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
        str(backup_path),
        "--no-owner",
        "--clean",
    ]

    try:
        subprocess.run(command, env=env, check=True, capture_output=True, text=True)
        logger.info(
            "info_type=db_backup ; action=before_status_change ; database=%s ; backup=%s",
            settings.db_name,
            backup_path,
        )
    except subprocess.CalledProcessError as e:
        logger.error("Database backup failed: %s", e.stderr)
        raise RuntimeError(f"PostgreSQL backup failed: {e.stderr}") from e

    return backup_path
