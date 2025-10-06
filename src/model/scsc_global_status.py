from datetime import datetime, timezone
from enum import Enum

from sqlmodel import CheckConstraint, Field, SQLModel


class SCSCStatus(str, Enum):
    surveying = "surveying"
    recruiting = "recruiting"
    active = "active"
    inactive = "inactive"


class SCSCGlobalStatus(SQLModel, table=True):
    __tablename__ = "scsc_global_status"  # type: ignore
    __table_args__ = (
        CheckConstraint("id = 1", name="ck_id_valid"),
        CheckConstraint("year >= 2025", name="ck_year_min"),
        CheckConstraint("semester IN (1, 2, 3, 4)", name="ck_semester_valid"),
    )

    id: int = Field(primary_key=True)
    status: SCSCStatus = Field(nullable=False)
    year: int = Field(nullable=False)
    semester: int = Field(nullable=False)
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), nullable=False)
