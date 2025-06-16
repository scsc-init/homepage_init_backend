from datetime import datetime, timezone
from typing import Sequence

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from src.controller import BodyCreateArticle, create_article_controller
from src.db import SessionDep
from src.model import Article, Board
from src.util import get_user

article_router = APIRouter(tags=['article'])


@article_router.post('/article/create', status_code=201)
async def create_article(session: SessionDep, request: Request, body: BodyCreateArticle) -> Article:
    current_user = get_user(request)
    return await create_article_controller(session, body, current_user.id, current_user.role)


@article_router.get('/articles/{board_id}')
async def get_article_list_by_board(board_id: int, session: SessionDep) -> Sequence[Article]:
    board = session.get(Board, board_id)
    if not board: raise HTTPException(404, detail="Board not found")
    articles = session.exec(select(Article).where(Article.board_id == board_id))
    return articles.all()


@article_router.get('/article/{id}')
async def get_article_by_id(id: int, session: SessionDep) -> Article:
    article = session.get(Article, id)
    if not article: raise HTTPException(404, detail="Article not found")
    return article


class BodyUpdateArticle(BaseModel):
    title: str
    content: str
    board_id: int


@article_router.post('/article/update/{id}', status_code=204)
async def update_article_by_author(id: int, session: SessionDep, request: Request, body: BodyUpdateArticle) -> None:
    current_user = get_user(request)
    article = session.get(Article, id)
    if not article: raise HTTPException(status_code=404, detail="Article not found",)
    if current_user.id != article.author_id:
        raise HTTPException(status_code=403, detail="You are not the author of this article",)
    board = session.get(Board, body.board_id)
    if not board: raise HTTPException(404, detail="Board not found")
    article.title = body.title
    article.content = body.content
    article.board_id = body.board_id
    article.updated_at = datetime.now(timezone.utc)
    try: session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=409, detail="unique field already exists")


@article_router.post('/executive/article/update/{id}', status_code=204)
async def update_article_by_executive(id: int, session: SessionDep, body: BodyUpdateArticle) -> None:
    article = session.get(Article, id)
    if not article: raise HTTPException(status_code=404, detail="Article not found",)
    board = session.get(Board, body.board_id)
    if not board: raise HTTPException(404, detail="Board not found")
    article.title = body.title
    article.content = body.content
    article.board_id = body.board_id
    article.updated_at = datetime.now(timezone.utc)
    try: session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=409, detail="unique field already exists")


@article_router.post('/article/delete/{id}', status_code=204)
async def delete_article_by_author(id: int, session: SessionDep, request: Request) -> None:
    current_user = get_user(request)
    article = session.get(Article, id)
    if not article: raise HTTPException(status_code=404, detail="Article not found",)
    if current_user.id != article.author_id:
        raise HTTPException(status_code=403, detail="You are not the author of this article",)
    session.delete(article)
    session.commit()


@article_router.post('/executive/article/delete/{id}', status_code=204)
async def delete_article_by_executive(id: int, session: SessionDep) -> None:
    article = session.get(Article, id)
    if not article: raise HTTPException(status_code=404, detail="Article not found",)
    # TODO: Which permission is needed
    session.delete(article)
    session.commit()
