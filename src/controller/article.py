from fastapi import HTTPException
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from os import path

from src.db import SessionDep
from src.model import Article, Board, ArticleResponse
from src.core import get_settings


class BodyCreateArticle(BaseModel):
    title: str
    content: str
    board_id: int


async def create_article_ctrl(session: SessionDep, body: BodyCreateArticle, user_id: str, user_role: int) -> Article:
    board = session.get(Board, body.board_id)
    if not board:
        raise HTTPException(status_code=404, detail=f"Board {body.board_id} does not exist")
    if user_role < board.writing_permission_level:
        raise HTTPException(status_code=403, detail="You are not allowed to write this article",)
    article = Article(
        title=body.title,
        author_id=user_id,
        board_id=body.board_id,
    )
    session.add(article)
    try: session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=409, detail="unique field already exists")
    session.refresh(article)
    with open(path.join(get_settings().article_dir, f"{article.id}.md"), "w", encoding="utf-8") as fp:
        fp.write(body.content)
    article_response = ArticleResponse(
        **article.dict(),
        content=body.content
    )
    return article_response
