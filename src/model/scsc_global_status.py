from datetime import datetime
from enum import Enum as enum

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Enum,
    Integer,
)
from sqlalchemy.orm import Mapped, mapped_column

from src.db import Base


class SCSCStatus(str, enum):
    recruiting = "recruiting"
    active = "active"
    inactive = "inactive"


class SCSCGlobalStatus(Base):
    __tablename__ = "scsc_global_status"
    __table_args__ = (
        CheckConstraint("id = 1", name="ck_id_valid"),
        CheckConstraint("year >= 2025", name="ck_year_min"),
        CheckConstraint("semester IN (1, 2, 3, 4)", name="ck_semester_valid"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    status: Mapped[SCSCStatus] = mapped_column(Enum(SCSCStatus), nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    semester: Mapped[int] = mapped_column(Integer, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        default_factory=datetime.now,
        onupdate=datetime.now,
    )
