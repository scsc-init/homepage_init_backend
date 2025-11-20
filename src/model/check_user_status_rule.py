from enum import Enum

from sqlalchemy import Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.db import Base

from .user import UserStatus


class HTTPMethod(str, Enum):
    GET = "GET"
    POST = "POST"


class CheckUserStatusRule(Base):
    __tablename__ = "check_user_status_rule"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, init=False
    )
    user_status: Mapped[UserStatus] = mapped_column(String, nullable=False)
    method: Mapped[HTTPMethod] = mapped_column(String, nullable=False)
    path: Mapped[str] = mapped_column(String, nullable=False)

    __table_args__ = (
        UniqueConstraint(
            "user_status", "method", "path", name="uq_user_status_method_path"
        ),
    )
