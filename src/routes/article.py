from datetime import datetime, timezone
from os import path, remove

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from sqlmodel import select
import logging

from src.controller import BodyCreateArticle, create_article_ctrl
from src.core import get_settings
from src.db import SessionDep
from src.model import Article, ArticleResponse, Board
from src.util import get_user, send_discord_bot_request_no_reply

logger = logging.getLogger("app")

article_router = APIRouter(tags=['article'])
article_general_router = APIRouter(prefix="/article")
article_executive_router = APIRouter(prefix="/executive/article", tags=['executive'])


@article_general_router.post('/create', status_code=201)
async def create_article(session: SessionDep, request: Request, body: BodyCreateArticle) -> ArticleResponse:
    current_user = get_user(request)
    ret = await create_article_ctrl(session, body, current_user.id, current_user.role)
    if body.board_id == 5: # notice
        await send_discord_bot_request_no_reply(action_code=1002, body={'channel_id': get_settings().notice_channel_id, 'content': body.content})
    elif body.board_id == 6: # grant
        await send_discord_bot_request_no_reply(action_code=1002, body={'channel_id': get_settings().grant_channel_id, 'content': body.content})
    return ret


# This works as "api/article" + "s/{board_id}" (="api/articles/{board_id}")
@article_general_router.get('s/{board_id}')
async def get_article_list_by_board(board_id: int, session: SessionDep, request: Request) -> list[ArticleResponse]:
    user = get_user(request)
    board = session.get(Board, board_id)
    if not board: raise HTTPException(404, detail="Board not found")
    if user.role < board.reading_permission_level: raise HTTPException(403, detail="You are not allowed to read this board")
    articles = session.exec(select(Article).where(Article.board_id == board_id)).all()
    result: list[ArticleResponse] = []
    for article in articles:
        with open(path.join(get_settings().article_dir, f"{article.id}.md"), "r", encoding="utf-8") as fp:
            content = fp.read()
            result.append(ArticleResponse(**article.model_dump(), content=content))
    return result


@article_general_router.get('/{id}')
async def get_article_by_id(id: int, session: SessionDep, request: Request) -> ArticleResponse:
    user = get_user(request)
    article = session.get(Article, id)
    if not article: raise HTTPException(404, detail="Article not found")
    board = session.get(Board, article.board_id)
    if user.role < board.reading_permission_level: raise HTTPException(403, detail="You are not allowed to read this article")
    with open(path.join(get_settings().article_dir, f"{article.id}.md"), "r", encoding="utf-8") as fp:
        content = fp.read()
        return ArticleResponse(**article.model_dump(), content=content)


class BodyUpdateArticle(BaseModel):
    title: str
    content: str
    board_id: int


@article_general_router.post('/update/{id}', status_code=204)
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
    logger.info(f'\ninfo_type=article_updated \narticle_id={article.id} \ntitle={body.title} \nrevisioner_id={current_user.id} \nboard_id={body.board_id}')
    with open(path.join(get_settings().article_dir, f"{article.id}.md"), "w", encoding="utf-8") as fp: fp.write(body.content)


@article_executive_router.post('/update/{id}', status_code=204)
async def update_article_by_executive(id: int, session: SessionDep, request: Request, body: BodyUpdateArticle) -> None:
    current_user = get_user(request)
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
    logger.info(f'\ninfo_type=article_updated \narticle_id={article.id} \ntitle={body.title} \nrevisioner_id={current_user.id} \nboard_id={body.board_id}')
    with open(path.join(get_settings().article_dir, f"{article.id}.md"), "w", encoding="utf-8") as fp: fp.write(body.content)


@article_general_router.post('/delete/{id}', status_code=204)
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
    logger.info(f'\ninfo_type=article_deleted \narticle_id={article.id} \ntitle={article.title} \nremover_id={current_user.id} \nboard_id={article.board_id}')
    session.commit()


@article_executive_router.post('/delete/{id}', status_code=204)
async def delete_article_by_executive(id: int, session: SessionDep, request: Request) -> None:
    current_user = get_user(request)
    article = session.get(Article, id)
    if not article: raise HTTPException(status_code=404, detail="Article not found",)
    session.delete(article)
    try:
        remove(path.join(get_settings().article_dir, f"{article.id}.md"))
    except:
        pass
    logger.info(f'\ninfo_type=article_deleted \narticle_id={article.id} \ntitle={article.title} \nremover_id={current_user.id} \nboard_id={article.board_id}')
    session.commit()

article_router.include_router(article_general_router)
article_router.include_router(article_executive_router)
