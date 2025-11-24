from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.db import Base


class Comment(Base):
    __tablename__ = "comment"
    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, init=False
    )
    content: Mapped[str] = mapped_column(String)
    author_id: Mapped[str] = mapped_column(String, ForeignKey("user.id"))
    article_id: Mapped[int] = mapped_column(Integer, ForeignKey("article.id"))
    parent_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("comment.id"), default=None, nullable=True
    )
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default_factory=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        default=None,
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=True,
    )
