from datetime import datetime
from enum import Enum as enum
from typing import Optional

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.db import Base
from src.util import utcnow


class UserStatus(str, enum):
    active = "active"
    pending = "pending"
    standby = "standby"
    banned = "banned"


class UserRole(Base):
    __tablename__ = "user_role"

    level: Mapped[int] = mapped_column(Integer, primary_key=True)

    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    kor_name: Mapped[str] = mapped_column(String, nullable=False, unique=True)


class User(Base):
    __tablename__ = "user"

    id: Mapped[str] = mapped_column(String, primary_key=True)

    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    phone: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    student_id: Mapped[str] = mapped_column(String, nullable=False, unique=True)

    role: Mapped[int] = mapped_column(
        Integer, ForeignKey("user_role.level"), nullable=False
    )
    major_id: Mapped[int] = mapped_column(ForeignKey("major.id"), nullable=False)
    status: Mapped[UserStatus] = mapped_column(
        Enum(UserStatus), default=UserStatus.standby, nullable=False
    )

    discord_id: Mapped[Optional[int]] = mapped_column(
        default=None, nullable=True, unique=True
    )
    discord_name: Mapped[Optional[str]] = mapped_column(
        default=None, nullable=True, unique=True
    )

    profile_picture: Mapped[Optional[str]] = mapped_column(default=None, nullable=True)
    profile_picture_is_url: Mapped[bool] = mapped_column(default=False, nullable=False)

    last_login: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        default_factory=utcnow,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), default_factory=utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        default_factory=utcnow,
        onupdate=utcnow,
    )


class StandbyReqTbl(Base):
    __tablename__ = "standby_req_tbl"

    standby_user_id: Mapped[str] = mapped_column(
        ForeignKey("user.id"), primary_key=True
    )
    user_name: Mapped[str] = mapped_column(nullable=False)
    deposit_name: Mapped[str] = mapped_column(nullable=False)
    deposit_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=False),
        default=None,
        nullable=True,
    )
    is_checked: Mapped[bool] = mapped_column(default=False, nullable=False)


class OldboyApplicant(Base):
    __tablename__ = "oldboy_applicant"

    id: Mapped[str] = mapped_column(ForeignKey("user.id"), primary_key=True)
    processed: Mapped[bool] = mapped_column(default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), default_factory=utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        default_factory=utcnow,
        onupdate=utcnow,
    )
