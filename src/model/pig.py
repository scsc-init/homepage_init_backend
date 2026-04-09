from __future__ import annotations

from datetime import datetime
from enum import Enum as enum

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
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.util import utcnow

from .article import Article
from .base import Base
from .scsc_global_status import SCSCStatus
from .user import UserSummary


class RollingAdmission(str, enum):
    ALWAYS = "always"
    NEVER = "never"
    DURING_RECRUITING = "during_recruiting"


class PIG(Base):
    __tablename__ = "pig"
    __table_args__ = (
        UniqueConstraint(
            "created_year",
            "created_semester",
            "title",
            name="uq_pig_created_year_created_semester_title",
        ),
        UniqueConstraint(
            "year",
            "semester",
            "title",
            name="uq_pig_title_year_semester",
        ),
        CheckConstraint("year >= 2025", name="ck_pig_year_min"),
        CheckConstraint("semester IN (1, 2, 3, 4)", name="ck_pig_semester_valid"),
        CheckConstraint("created_year >= 2025", name="ck_pig_created_year_min"),
        CheckConstraint(
            "created_semester IN (1, 2, 3, 4)",
            name="ck_pig_created_semester_valid",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, init=False
    )
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    content_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("article.id"), nullable=False, unique=True
    )
    status: Mapped[SCSCStatus] = mapped_column(
        Enum(
            SCSCStatus,
            name="scsc_status_enum",
            native_enum=False,
            values_callable=lambda obj: [e.value for e in obj],
        ),
        nullable=False,
    )
    created_year: Mapped[int] = mapped_column(Integer, nullable=False)
    created_semester: Mapped[int] = mapped_column(Integer, nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    semester: Mapped[int] = mapped_column(Integer, nullable=False)
    owner: Mapped[str] = mapped_column(String, ForeignKey("user.id"), nullable=False)
    should_extend: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_rolling_admission: Mapped[RollingAdmission] = mapped_column(
        Enum(
            RollingAdmission,
            name="rolling_admission_enum",
            native_enum=False,
            values_callable=lambda obj: [e.value for e in obj],
        ),
        nullable=False,
        default=RollingAdmission.DURING_RECRUITING,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        default_factory=utcnow,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        default_factory=utcnow,
        onupdate=utcnow,
    )

    owner_user: Mapped[UserSummary] = relationship(
        "UserSummary", lazy="selectin", init=False, viewonly=True
    )
    members: Mapped[list[PIGMember]] = relationship(
        "PIGMember", lazy="selectin", init=False, viewonly=True
    )
    websites: Mapped[list[PIGWebsite]] = relationship(
        "PIGWebsite", lazy="selectin", init=False, viewonly=True
    )
    article: Mapped["Article"] = relationship(
        "Article", lazy="selectin", init=False, viewonly=True
    )


class PIGMember(Base):
    __tablename__ = "pig_member"
    __table_args__ = (
        UniqueConstraint("ig_id", "user_id", name="uq_pig_member_ig_user"),
    )

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, init=False
    )
    ig_id: Mapped[int] = mapped_column(Integer, ForeignKey("pig.id"), nullable=False)
    user_id: Mapped[str] = mapped_column(String, ForeignKey("user.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        default_factory=utcnow,
    )

    user: Mapped[UserSummary] = relationship(
        "UserSummary", lazy="selectin", init=False, viewonly=True
    )


class PIGWebsite(Base):
    __tablename__ = "pig_website"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, init=False
    )
    pig_id: Mapped[int] = mapped_column(Integer, ForeignKey("pig.id"), nullable=False)
    label: Mapped[str] = mapped_column(String, nullable=False)
    url: Mapped[str] = mapped_column(String, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        default_factory=utcnow,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        default_factory=utcnow,
        onupdate=utcnow,
    )
