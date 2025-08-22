from typing import Optional

from sqlmodel import CheckConstraint, Field, SQLModel, UniqueConstraint


class CheckUserStatusRule(SQLModel, table=True):
    __tablename__ = "check_user_status_rule"  # type: ignore

    id: Optional[int] = Field(default=None, primary_key=True)
    user_status: str = Field(nullable=False)
    method: str = Field(nullable=False)
    path: str = Field(nullable=False)

    __table_args__ = (
        CheckConstraint("user_status IN ('active', 'pending', 'standby', 'banned')", name="ck_user_status_valid"),
        CheckConstraint("method IN ('GET', 'POST')", name="ck_method_valid"),
        UniqueConstraint("user_status", "method", "path", name="uq_user_status_method_path")
    )
