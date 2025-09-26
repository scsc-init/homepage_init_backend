from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Field, SQLModel


class WHTMLMetadata(SQLModel, table=True):
    __tablename__ = "w_html_metadata"  # type: ignore

    name: str = Field(primary_key=True)
    size: int = Field(nullable=False, ge=0)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False)
    creator: Optional[str] = Field(nullable=True, foreign_key="user.id")
