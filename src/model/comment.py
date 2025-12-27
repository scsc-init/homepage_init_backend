from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.util import utcnow

from .base import Base


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
        DateTime(timezone=False), default_factory=utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        default_factory=utcnow,
        onupdate=utcnow,
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=False),
        default=None,
        nullable=True,
    )
