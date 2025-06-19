from fastapi import HTTPException
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError

from src.db import SessionDep
from src.model import Article, Board


class BodyCreateArticle(BaseModel):
    title: str
    content: str
    board_id: int


async def create_article(session: SessionDep, body: BodyCreateArticle, user_id: str, user_role: int) -> Article:
    board = session.get(Board, body.board_id)
    if not board:
        raise HTTPException(status_code=404, detail=f"Board {body.board_id} does not exist")
    if user_role < board.writing_permission_level:
        raise HTTPException(status_code=403, detail="You are not allowed to write this article",)
    article = Article(
        title=body.title,
        content=body.content,
        author_id=user_id,
        board_id=body.board_id,
    )
    session.add(article)
    try: session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=409, detail="unique field already exists")
    session.refresh(article)
    return article
