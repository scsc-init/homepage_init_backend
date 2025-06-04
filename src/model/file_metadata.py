from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Field, SQLModel


class FileMetadata(SQLModel, table=True):
    __tablename__ = "file_metadata"  # type: ignore

    id: str = Field(primary_key=True)

    original_filename: str = Field(nullable=False)
    size: int = Field(nullable=False)
    mime_type: str = Field(nullable=False)

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False)

    owner: Optional[str] = Field(nullable=True, foreign_key="user.id")
