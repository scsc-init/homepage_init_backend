from datetime import datetime
from enum import Enum as enum

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.util import utcnow

from .base import Base


class BoardType(str, enum):
    TEXT = "TEXT"
    NONE = "NONE"
    FILE = "FILE"
    IMAGE = "IMAGE"


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
        DateTime(timezone=False),
        default_factory=utcnow,
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        default_factory=utcnow,
        onupdate=utcnow,
        nullable=False,
    )
    board_type: Mapped[BoardType] = mapped_column(
        Enum(
            BoardType,
            name="board_type_enum",
            native_enum=False,
            values_callable=lambda obj: [e.value for e in obj],
        ),
        nullable=False,
        default="TEXT",
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

    content: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        default_factory=utcnow,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        default_factory=utcnow,
        onupdate=utcnow,
        nullable=False,
    )

    attachments: Mapped[list["Attachment"]] = relationship(
        "Attachment",
        lazy="selectin",
        init=False,
        viewonly=True,
    )
