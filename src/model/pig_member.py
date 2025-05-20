from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Field, SQLModel, UniqueConstraint

from .pig import PIGStatus


class PIGMember(SQLModel, table=True):
    __tablename__ = "pig_member"  # type: ignore
    __table_args__ = (
        UniqueConstraint("ig_id", "user_id", "status", name="uq_ig_user_status"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)

    ig_id: int = Field(foreign_key="pig.id", nullable=False)
    user_id: str = Field(foreign_key="user.id", nullable=False)
    status: PIGStatus = Field(nullable=False)

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False)
