from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


class Board(SQLModel, table=True):
    __tablename__ = 'board'  # type: ignore
    id: int = Field(default=None, primary_key=True)  # default=None because of autoincrement
    name: str = Field()
    description: str = Field()
    writing_permission_level: int = Field(foreign_key="user_role.level", default=0)
    reading_permission_level: int = Field(foreign_key="user_role.level", default=0)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Article(SQLModel, table=True):
    __tablename__ = "article"  # type: ignore
    id: int = Field(default=None, primary_key=True)  # default=None because of autoincrement
    title: str = Field()
    content: str = Field()
    author_id: str = Field(foreign_key="user.id")
    board_id: int = Field(foreign_key="board.id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))