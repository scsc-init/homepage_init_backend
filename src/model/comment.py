from datetime import datetime, timezone
from sqlmodel import Field, SQLModel


class Comment(SQLModel, table=True):
    __tablename__ = "comment"  # type: ignore
    # default=None because of autoincrement
    id: int = Field(default=None, primary_key=True)
    content: str = Field()
    author_id: str = Field(foreign_key="user.id")
    article_id: int = Field(foreign_key="article.id")
    parent_id: int | None = Field(
        default=None, foreign_key="comment.id", nullable=True)
    is_deleted: bool = Field(default=False, nullable=False)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc))
    deleted_at: datetime | None = Field(default=None, nullable=True)


class CommentResponse(SQLModel, table=False):
    id: int
    content: str
    author_id: str
    article_id: int
    parent_id: int | None
    is_deleted: bool
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None
