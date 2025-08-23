from enum import Enum
from typing import Optional

from sqlmodel import Field, SQLModel, UniqueConstraint

from .user import UserStatus


class HTTPMethod(str, Enum):
    GET = "GET"
    POST = "POST"


class CheckUserStatusRule(SQLModel, table=True):
    __tablename__ = "check_user_status_rule"  # type: ignore

    id: Optional[int] = Field(default=None, primary_key=True)
    user_status: UserStatus = Field(nullable=False)
    method: HTTPMethod = Field(nullable=False)
    path: str = Field(nullable=False)

    __table_args__ = (
        UniqueConstraint("user_status", "method", "path", name="uq_user_status_method_path"),
    )
