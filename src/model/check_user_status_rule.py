from enum import Enum as enum

from sqlalchemy import Enum, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class HTTPMethod(str, enum):
    GET = "GET"
    POST = "POST"


class CheckUserStatusRule(Base):
    __tablename__ = "check_user_status_rule"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, init=False
    )
    method: Mapped[HTTPMethod] = mapped_column(Enum(HTTPMethod), nullable=False)
    path: Mapped[str] = mapped_column(String, nullable=False)

    __table_args__ = (UniqueConstraint("method", "path", name="uq_method_path"),)
