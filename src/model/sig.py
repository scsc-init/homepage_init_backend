from __future__ import annotations

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
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.util import utcnow

from .base import Base
from .scsc_global_status import SCSCStatus
from .user import UserSummary


class SIG(Base):
    __tablename__ = "sig"
    __table_args__ = (
        UniqueConstraint(
            "created_year",
            "created_semester",
            "title",
            name="uq_sig_created_year_created_semester_title",
        ),
        UniqueConstraint(
            "year",
            "semester",
            "title",
            name="uq_sig_year_semester_title",
        ),
        CheckConstraint("year >= 2025", name="ck_sig_year_min"),
        CheckConstraint("semester IN (1, 2, 3, 4)", name="ck_sig_semester_valid"),
        CheckConstraint("created_year >= 2025", name="ck_sig_created_year_min"),
        CheckConstraint(
            "created_semester IN (1, 2, 3, 4)",
            name="ck_sig_created_semester_valid",
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
    status: Mapped[SCSCStatus] = mapped_column(Enum(SCSCStatus), nullable=False)
    created_year: Mapped[int] = mapped_column(Integer, nullable=False)
    created_semester: Mapped[int] = mapped_column(Integer, nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    semester: Mapped[int] = mapped_column(Integer, nullable=False)
    owner: Mapped[str] = mapped_column(String, ForeignKey("user.id"), nullable=False)
    should_extend: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_rolling_admission: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
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
    members: Mapped[list[SIGMember]] = relationship(
        "SIGMember", lazy="selectin", init=False, viewonly=True
    )
    tags: Mapped[list[Tag]] = relationship(
        "Tag", secondary="sig_tag", lazy="selectin", init=False, viewonly=True
    )


class SIGMember(Base):
    __tablename__ = "sig_member"
    __table_args__ = (
        UniqueConstraint("ig_id", "user_id", name="uq_sig_member_ig_user"),
    )

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, init=False
    )
    ig_id: Mapped[int] = mapped_column(Integer, ForeignKey("sig.id"), nullable=False)
    user_id: Mapped[str] = mapped_column(String, ForeignKey("user.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        default_factory=utcnow,
    )

    user: Mapped[UserSummary] = relationship(
        "UserSummary", lazy="selectin", init=False, viewonly=True
    )


class Tag(Base):
    __tablename__ = "tag"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, init=False
    )
    text: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    is_major: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        default_factory=utcnow,
    )


class SIGTag(Base):
    __tablename__ = "sig_tag"
    __table_args__ = (
        UniqueConstraint(
            "sig_id",
            "tag_id",
            name="uq_sig_tag_sig_id_tag_id",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, init=False
    )
    sig_id: Mapped[int] = mapped_column(Integer, ForeignKey("sig.id"), nullable=False)
    tag_id: Mapped[int] = mapped_column(Integer, ForeignKey("tag.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        default_factory=utcnow,
    )
