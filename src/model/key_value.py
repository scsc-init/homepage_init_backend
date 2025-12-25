from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.db import Base
from src.util import utcnow


class KeyValue(Base):
    __tablename__ = "key_value"

    key: Mapped[str] = mapped_column(String, primary_key=True)
    value: Mapped[Optional[str]] = mapped_column(String, default=None, nullable=True)
    writing_permission_level: Mapped[int] = mapped_column(
        Integer, ForeignKey("user_role.level"), default=500
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        default_factory=utcnow,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        default_factory=utcnow,
        onupdate=utcnow,
    )
