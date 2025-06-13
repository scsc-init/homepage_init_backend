from datetime import datetime, timezone
from enum import Enum

from sqlmodel import CheckConstraint, Field, SQLModel, UniqueConstraint


class PIGStatus(str, Enum):
    surveying = "surveying"
    recruiting = "recruiting"
    active = "active"
    inactive = "inactive"


class PIG(SQLModel, table=True):
    __tablename__ = "pig"  # type: ignore
    __table_args__ = (
        UniqueConstraint("title", "year", "semester", name="uq_title_year_semester"),
        CheckConstraint("year >= 2025", name="ck_year_min"),
        CheckConstraint("semester IN (1, 2)", name="ck_semester_valid"),
    )

    id: int = Field(default=None, primary_key=True)

    title: str = Field(nullable=False)
    description: str = Field(nullable=False)
    content_id: int = Field(foreign_key="article.id", unique=True)

    status: PIGStatus = Field(nullable=False)

    year: int = Field(nullable=False)
    semester: int = Field(nullable=False)

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False)

    owner: str = Field(foreign_key="user.id", nullable=False)


class PIGMember(SQLModel, table=True):
    __tablename__ = "pig_member"  # type: ignore
    __table_args__ = (
        UniqueConstraint("ig_id", "user_id", "status", name="uq_ig_user_status"),
    )

    id: int = Field(default=None, primary_key=True)

    ig_id: int = Field(foreign_key="pig.id", nullable=False)
    user_id: str = Field(foreign_key="user.id", nullable=False)
    status: PIGStatus = Field(nullable=False)

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False)
