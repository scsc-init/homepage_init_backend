from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.db import Base


class FileMetadata(Base):
    __tablename__ = "file_metadata"

    id: Mapped[str] = mapped_column(String, primary_key=True)

    original_filename: Mapped[str] = mapped_column(String, nullable=False)
    size: Mapped[int] = mapped_column(Integer, nullable=False)
    mime_type: Mapped[str] = mapped_column(String, nullable=False)
    owner: Mapped[Optional[str]] = mapped_column(
        String, ForeignKey("user.id"), nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default_factory=lambda: datetime.now(timezone.utc)
    )
