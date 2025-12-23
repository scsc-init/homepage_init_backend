from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.db import Base


class WHTMLMetadata(Base):
    __tablename__ = "w_html_metadata"

    name: Mapped[str] = mapped_column(String, primary_key=True)
    size: Mapped[int] = mapped_column(
        Integer, CheckConstraint("size >= 0"), nullable=False
    )
    creator: Mapped[Optional[str]] = mapped_column(
        String, ForeignKey("user.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        default_factory=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
