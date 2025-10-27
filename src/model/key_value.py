from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Field, SQLModel


class KeyValue(SQLModel, table=True):
    __tablename__ = "key_value"  # type: ignore

    key: str = Field(primary_key=True)
    value: Optional[str] = Field(default=None, nullable=True)
    writing_permission_level: int = Field(foreign_key="user_role.level", default=500)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), nullable=False
    )
