from typing import Optional

from fastapi import HTTPException
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError

from src.db import SessionDep
from src.model import Article, Board, User


class BodyCreateArticle(BaseModel):
    title: str
    content: str
    board_id: int


async def create_article_controller(body: BodyCreateArticle, session: SessionDep, current_user: Optional[User]) -> Article:
    """
    If current_user is None: author_id will be NULL and role level will be treated as the highest role.

    The controller can raise HTTPException.
    """

    board = session.get(Board, body.board_id)
    if not board:
        raise HTTPException(status_code=404, detail=f"Board {body.board_id} does not exist")
    if current_user and int(current_user.role) < board.writing_permission_level:
        raise HTTPException(status_code=403, detail="You are not allowed to write this article",)
    article = Article(
        title=body.title,
        content=body.content,
        author_id=current_user.id if current_user else None,
        board_id=body.board_id,
    )
    session.add(article)
    try: session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=409, detail="unique field already exists")
    session.refresh(article)
    return article
