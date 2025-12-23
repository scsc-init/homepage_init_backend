from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.db import Base


class Board(Base):
    __tablename__ = "board"
    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, init=False
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    writing_permission_level: Mapped[int] = mapped_column(
        Integer, ForeignKey("user_role.level"), default=0, nullable=False
    )
    reading_permission_level: Mapped[int] = mapped_column(
        Integer, ForeignKey("user_role.level"), default=0, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), default_factory=datetime.now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        default_factory=datetime.now,
        onupdate=datetime.now,
        nullable=False,
    )


class Article(Base):
    __tablename__ = "article"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, init=False
    )

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
        DateTime(timezone=False),
        default_factory=datetime.now,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        default_factory=datetime.now,
        onupdate=datetime.now,
        nullable=False,
    )

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=False),
        nullable=True,
        default=None,
    )
