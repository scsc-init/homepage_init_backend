from datetime import datetime, timezone
from os import path, remove

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from src.controller import BodyCreateArticle, create_article_ctrl
from src.core import get_settings
from src.db import SessionDep
from src.model import Article, ArticleResponse, Board
from src.util import get_user

article_router = APIRouter(tags=['article'])


@article_router.post('/article/create', status_code=201)
async def create_article(session: SessionDep, request: Request, body: BodyCreateArticle) -> ArticleResponse:
    current_user = get_user(request)
    return await create_article_ctrl(session, body, current_user.id, current_user.role)


@article_router.get('/articles/{board_id}')
async def get_article_list_by_board(board_id: int, session: SessionDep) -> list[ArticleResponse]:
    board = session.get(Board, board_id)
    if not board: raise HTTPException(404, detail="Board not found")
    articles = session.exec(select(Article).where(Article.board_id == board_id)).all()
    result: list[ArticleResponse] = []
    for article in articles:
        with open(path.join(get_settings().article_dir, f"{article.id}.md"), "r", encoding="utf-8") as fp:
            content = fp.read()
            result.append(ArticleResponse(**article.model_dump(), content=content))
    return result


@article_router.get('/article/{id}')
async def get_article_by_id(id: int, session: SessionDep) -> ArticleResponse:
    article = session.get(Article, id)
    if not article: raise HTTPException(404, detail="Article not found")
    with open(path.join(get_settings().article_dir, f"{article.id}.md"), "r", encoding="utf-8") as fp:
        content = fp.read()
        return ArticleResponse(**article.model_dump(), content=content)


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
    article.board_id = body.board_id
    article.updated_at = datetime.now(timezone.utc)
    try: session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=409, detail="unique field already exists")
    session.refresh(article)
    with open(path.join(get_settings().article_dir, f"{article.id}.md"), "w", encoding="utf-8") as fp: fp.write(body.content)


@article_router.post('/executive/article/update/{id}', status_code=204)
async def update_article_by_executive(id: int, session: SessionDep, body: BodyUpdateArticle) -> None:
    article = session.get(Article, id)
    if not article: raise HTTPException(status_code=404, detail="Article not found",)
    board = session.get(Board, body.board_id)
    if not board: raise HTTPException(404, detail="Board not found")
    article.title = body.title
    article.board_id = body.board_id
    article.updated_at = datetime.now(timezone.utc)
    try: session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=409, detail="unique field already exists")
    session.refresh(article)
    with open(path.join(get_settings().article_dir, f"{article.id}.md"), "w", encoding="utf-8") as fp: fp.write(body.content)


@article_router.post('/article/delete/{id}', status_code=204)
async def delete_article_by_author(id: int, session: SessionDep, request: Request) -> None:
    current_user = get_user(request)
    article = session.get(Article, id)
    if not article: raise HTTPException(status_code=404, detail="Article not found",)
    if current_user.id != article.author_id:
        raise HTTPException(status_code=403, detail="You are not the author of this article",)
    session.delete(article)
    try:
        remove(path.join(get_settings().article_dir, f"{article.id}.md"))
    except:
        pass
    session.commit()


@article_router.post('/executive/article/delete/{id}', status_code=204)
async def delete_article_by_executive(id: int, session: SessionDep) -> None:
    article = session.get(Article, id)
    if not article: raise HTTPException(status_code=404, detail="Article not found",)
    # TODO: Which permission is needed
    session.delete(article)
    try:
        remove(path.join(get_settings().article_dir, f"{article.id}.md"))
    except:
        pass
    session.commit()
