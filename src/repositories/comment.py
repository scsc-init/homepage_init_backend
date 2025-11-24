from typing import Annotated

from fastapi import Depends
from sqlalchemy import select

from src.model import Comment

from .dao import DAO


class CommentRepository(DAO[Comment, int]):
    @property
    def model(self) -> type[Comment]:
        return Comment

    def get_comments_by_article_id(self, article_id: int):
        stmt = select(Comment).where(Comment.article_id == article_id)
        return self.session.scalars(stmt).all()


CommentRepositoryDep = Annotated[CommentRepository, Depends()]
