from typing import Annotated

from fastapi import Depends
from sqlalchemy import select

from src.model import Article

from .dao import DAO


class ArticleRepository(DAO[Article, int]):
    @property
    def model(self) -> type[Article]:
        return Article

    def get_articles_by_board_id(self, board_id: int):
        stmt = select(Article).where(Article.board_id == board_id)
        return self.session.scalars(stmt).all()


ArticleRepositoryDep = Annotated[ArticleRepository, Depends()]
