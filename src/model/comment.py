from datetime import datetime, timezone
from pydantic import BaseModel
from sqlmodel import Field, SQLModel


class Comment(SQLModel, table=True):
    __tablename__ = "comment"  # type: ignore
    id: int = Field(default=None, primary_key=True)  # default=None because of autoincrement
    content: str = Field()
    author_id: str = Field(foreign_key="user.id")
    article_id: int = Field(foreign_key="article.id")
    parent_id: int = Field(foreign_key="comment.id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

