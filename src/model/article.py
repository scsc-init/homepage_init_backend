from datetime import datetime, timezone

from pydantic import BaseModel
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.db import Base, intpk


class Board(Base):
    __tablename__ = "board"
    id: Mapped[intpk]
    name: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(String)
    writing_permission_level: Mapped[int] = mapped_column(
        Integer, ForeignKey("user_role.level"), default=0
    )
    reading_permission_level: Mapped[int] = mapped_column(
        Integer, ForeignKey("user_role.level"), default=0
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default_factory=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class Article(Base):
    __tablename__ = "article"

    id: Mapped[intpk]

    title: Mapped[str] = mapped_column(String, nullable=False)

    author_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("user.id"),
        nullable=False,
    )

    board_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("board.id"),
        nullable=False,
    )

    is_deleted: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default_factory=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
    )


class ArticleResponse(BaseModel):
    id: int
    title: str
    author_id: str
    board_id: int
    is_deleted: bool
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None
    content: str
