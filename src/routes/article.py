from datetime import datetime, timezone
from typing import Optional, Sequence

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from src.auth import get_current_user
from src.db import SessionDep
from src.model import Article, User, UserRole, Board

article_router = APIRouter(prefix="/article", tags=['article'])

class BodyCreateArticle(BaseModel):
    title: str
    content: str
    board_id: int

@article_router.post('/create', status_code=201)
async def create_article(body: BodyCreateArticle, session: SessionDep, current_user: User = Depends(get_current_user)) -> Article:
    article = Article(
        title=body.title,
        content=body.content,
        author_id=current_user.id,
        board_id=body.board_id,
    )
    board = session.get(Board, article.board_id)
    if not board:
        raise HTTPException(status_code=404, detail=f"Board {article.board_id} does not exist",)
    if int(current_user.role) < board.writing_permission_level:
        raise HTTPException(status_code=403, detail="You are not allowed to write this article",)
    session.add(article)
    try: session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=409, detail="unique field already exists")
    session.refresh(article)
    return article

class BodyUpdateArticle(BaseModel):
    title: str
    content: str
    board_id: int

@article_router.post('/update/{id}', status_code=204)
async def update_article(id: int, body: BodyUpdateArticle, session: SessionDep, current_user: User = Depends(get_current_user)) -> None:
    article = session.get(Article, id)
    if not article: raise HTTPException(status_code=404, detail="Article not found",)
    # if currentUser.id != article.author_id:
    #     raise HTTPException(
    #         status_code=403,
    #         detail="You are not the author of this article",
    #     )
    # TODO: Who can, What can?
    article.title = body.title
    article.content = body.content
    article.board_id = body.board_id
    article.updated_at = datetime.now(timezone.utc)
    session.flush()


@article_router.post('/delete/{id}', status_code=204)
async def delete_article(id: int, session: SessionDep, current_user: User = Depends(get_current_user)) -> None:
    article = session.get(Article, id)
    if not article: raise HTTPException(status_code=404, detail="Article not found",)
    # if current_user.id != article.author_id:
    #     raise HTTPException(
    #         status_code=403,
    #         detail="You are not the author of this article",
    #     )
    # TODO: Who can, What can?
    session.delete(article)
    session.flush()


@article_router.get('/{id}')
async def get_article_by_id(id: int, session: SessionDep) -> Article:
    article = session.get(Article, id)
    if not article: raise HTTPException(404, detail="Article not found")
    return article


@article_router.get('/list/{board_id}')
async def get_article_list_by_board(board_id: int, session: SessionDep) -> Article:
    articles = session.exec(select(Article).where(Article.board_id == board_id)) if board_id else session.exec(select(Article))
    return articles.all()


