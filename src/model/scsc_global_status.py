from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, ConfigDict
from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.db import Base


class SCSCStatus(str, Enum):
    recruiting = "recruiting"
    active = "active"
    inactive = "inactive"


class SCSCGlobalStatus(Base):
    __tablename__ = "scsc_global_status"  # type: ignore
    __table_args__ = (
        CheckConstraint("id = 1", name="ck_id_valid"),
        CheckConstraint("year >= 2025", name="ck_year_min"),
        CheckConstraint("semester IN (1, 2, 3, 4)", name="ck_semester_valid"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    status: Mapped[SCSCStatus] = mapped_column(String, nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    semester: Mapped[int] = mapped_column(Integer, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default_factory=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
