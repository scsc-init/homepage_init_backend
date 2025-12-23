from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from src.db import Base

from .scsc_global_status import SCSCStatus


class PIG(Base):
    __tablename__ = "pig"
    __table_args__ = (
        UniqueConstraint("title", "year", "semester", name="uq_title_year_semester"),
        CheckConstraint("year >= 2025", name="ck_year_min"),
        CheckConstraint("semester IN (1, 2, 3, 4)", name="ck_semester_valid"),
    )

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, init=False
    )
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    content_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("article.id"), nullable=False, unique=True
    )
    status: Mapped[SCSCStatus] = mapped_column(Enum(SCSCStatus), nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    semester: Mapped[int] = mapped_column(Integer, nullable=False)
    owner: Mapped[str] = mapped_column(String, ForeignKey("user.id"), nullable=False)
    should_extend: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_rolling_admission: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        default_factory=datetime.now,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        default_factory=datetime.now,
        onupdate=datetime.now,
    )


class PIGMember(Base):
    __tablename__ = "pig_member"
    __table_args__ = (UniqueConstraint("ig_id", "user_id", name="uq_ig_user"),)

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, init=False
    )
    ig_id: Mapped[int] = mapped_column(Integer, ForeignKey("pig.id"), nullable=False)
    user_id: Mapped[str] = mapped_column(String, ForeignKey("user.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        default_factory=datetime.now,
    )
