from datetime import datetime, timezone

from sqlmodel import CheckConstraint, Field, SQLModel, UniqueConstraint

from .scsc_global_status import SCSCStatus


class SIG(SQLModel, table=True):
    __tablename__ = "sig"  # type: ignore
    __table_args__ = (
        UniqueConstraint("title", "year", "semester", name="uq_title_year_semester"),
        CheckConstraint("year >= 2025", name="ck_year_min"),
        CheckConstraint("semester IN (1, 2, 3, 4)", name="ck_semester_valid"),
    )

    id: int = Field(
        default=None, primary_key=True
    )  # default=None because of autoincrement

    title: str = Field(nullable=False)
    description: str = Field(nullable=False)
    content_id: int = Field(foreign_key="article.id", nullable=False, unique=True)

    status: SCSCStatus = Field(nullable=False)

    year: int = Field(nullable=False)
    semester: int = Field(nullable=False)

    should_extend: bool = Field(default=False, nullable=False)
    is_rolling_admission: bool = Field(default=False, nullable=False)

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), nullable=False
    )

    owner: str = Field(foreign_key="user.id", nullable=False)


class SIGMember(SQLModel, table=True):
    __tablename__ = "sig_member"  # type: ignore
    __table_args__ = (
        UniqueConstraint("ig_id", "user_id", "status", name="uq_ig_user_status"),
    )

    id: int = Field(
        default=None, primary_key=True
    )  # default=None because of autoincrement

    ig_id: int = Field(foreign_key="sig.id", nullable=False)
    user_id: str = Field(foreign_key="user.id", nullable=False)
    status: SCSCStatus = Field(nullable=False)

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), nullable=False
    )
