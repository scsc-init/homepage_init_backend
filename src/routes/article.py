from datetime import datetime, timezone
from os import path

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from src.controller import BodyCreateArticle, create_article_ctrl
from src.core import get_settings, logger
from src.db import SessionDep
from src.model import Article, ArticleResponse, Board
from src.util import DELETED, get_user, send_discord_bot_request_no_reply

article_router = APIRouter(tags=["article"])
article_general_router = APIRouter(prefix="/article")
article_executive_router = APIRouter(prefix="/executive/article", tags=["executive"])


@article_general_router.post("/create", status_code=201)
async def create_article(
    session: SessionDep, request: Request, body: BodyCreateArticle
) -> ArticleResponse:
    current_user = get_user(request)
    ret = await create_article_ctrl(session, body, current_user.id, current_user.role)
    try:
        if body.board_id == 5:  # notice
            await send_discord_bot_request_no_reply(
                action_code=1002,
                body={
                    "channel_id": get_settings().notice_channel_id,
                    "content": f"{body.title}\n\n{body.content}",
                },
            )
        elif body.board_id == 6:  # grant
            await send_discord_bot_request_no_reply(
                action_code=1002,
                body={
                    "channel_id": get_settings().grant_channel_id,
                    "content": body.content,
                },
            )
    except Exception:
        logger.error(
            f"err_type=create_article ; error occurred during connecting to discord ; {body=}",
            exc_info=True,
        )
    return ret


# This works as "api/article" + "s/{board_id}" (="api/articles/{board_id}")
@article_general_router.get("s/{board_id}")
async def get_article_list_by_board(
    board_id: int, session: SessionDep, request: Request
) -> list[ArticleResponse]:
    board = session.get(Board, board_id)
    if not board:
        raise HTTPException(404, detail="Board not found")

    if board.reading_permission_level > 0:
        current_user = get_user(request)
        if current_user.role < board.reading_permission_level:
            raise HTTPException(403, detail="You are not allowed to read this board")

    articles = session.exec(select(Article).where(Article.board_id == board_id)).all()
    result: list[ArticleResponse] = []
    for article in articles:
        if article.is_deleted:
            result.append(ArticleResponse(**article.model_dump(), content=DELETED))
        else:
            try:
                with open(
                    path.join(get_settings().article_dir, f"{article.id}.md"),
                    "r",
                    encoding="utf-8",
                ) as fp:
                    content = fp.read()
            except Exception:
                logger.error(
                    f"err_type=get_article_list_by_board ; error occurred during reading a file ; {board_id=} ; {article.id=}",
                    exc_info=True,
                )
                content = ""
            result.append(ArticleResponse(**article.model_dump(), content=content))

    return result


@article_general_router.get("/{id}")
async def get_article_by_id(
    id: int, session: SessionDep, request: Request
) -> ArticleResponse:
    article = session.get(Article, id)
    if not article:
        raise HTTPException(404, detail="Article not found")
    board = session.get(Board, article.board_id)
    if not board:
        raise HTTPException(503, detail="board does not exist")

    if board.reading_permission_level > 0:
        current_user = get_user(request)
        if current_user.role < board.reading_permission_level:
            raise HTTPException(403, detail="You are not allowed to read this article")

    if article.is_deleted:
        return ArticleResponse(**article.model_dump(), content=DELETED)

    try:
        with open(
            path.join(get_settings().article_dir, f"{article.id}.md"),
            "r",
            encoding="utf-8",
        ) as fp:
            content = fp.read()
    except Exception:
        logger.error(
            f"err_type=get_article_by_id ; error occurred during reading a file ; {article.id=}",
            exc_info=True,
        )
        content = ""
    return ArticleResponse(**article.model_dump(), content=content)


class BodyUpdateArticle(BaseModel):
    title: str
    content: str
    board_id: int


@article_general_router.post("/update/{id}", status_code=204)
async def update_article_by_author(
    id: int, session: SessionDep, request: Request, body: BodyUpdateArticle
) -> None:
    article = session.get(Article, id)
    if not article:
        raise HTTPException(
            status_code=404,
            detail="Article not found",
        )
    current_user = get_user(request)
    if current_user.id != article.author_id:
        raise HTTPException(
            status_code=403,
            detail="You are not the author of this article",
        )
    if article.is_deleted:
        raise HTTPException(status_code=410, detail="Article has been deleted")
    board = session.get(Board, body.board_id)
    if not board:
        raise HTTPException(503, detail="board does not exist")
    if current_user.role < board.writing_permission_level:
        raise HTTPException(403, detail="You are not allowed to write to this board")

    article.title = body.title
    article.board_id = body.board_id
    article.updated_at = datetime.now(timezone.utc)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=409, detail="unique field already exists")
    session.refresh(article)
    logger.info(
        f"info_type=article_updated ; article_id={article.id} ; title={body.title} ; revisioner_id={current_user.id} ; board_id={body.board_id}"
    )
    try:
        file_path = path.join(get_settings().article_dir, f"{article.id}.md")
        with open(file_path, "w", encoding="utf-8") as fp:
            fp.write(body.content)
    except Exception:
        logger.error(
            f"err_type=update_article_by_author ; failed to write file ; {article.id=}",
            exc_info=True,
        )


@article_executive_router.post("/update/{id}", status_code=204)
async def update_article_by_executive(
    id: int, session: SessionDep, request: Request, body: BodyUpdateArticle
) -> None:
    article = session.get(Article, id)
    if not article:
        raise HTTPException(
            status_code=404,
            detail="Article not found",
        )
    if article.is_deleted:
        raise HTTPException(status_code=410, detail="Article has been deleted")
    board = session.get(Board, body.board_id)
    if not board:
        raise HTTPException(503, detail="board does not exist")
    current_user = get_user(request)
    if current_user.role < board.writing_permission_level:
        raise HTTPException(403, detail="You are not allowed to write to this board")

    article.title = body.title
    article.board_id = body.board_id
    article.updated_at = datetime.now(timezone.utc)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=409, detail="unique field already exists")
    session.refresh(article)
    logger.info(
        f"info_type=article_updated ; article_id={article.id} ; title={body.title} ; revisioner_id={current_user.id} ; board_id={body.board_id}"
    )
    try:
        file_path = path.join(get_settings().article_dir, f"{article.id}.md")
        with open(file_path, "w", encoding="utf-8") as fp:
            fp.write(body.content)
    except Exception:
        logger.error(
            f"err_type=update_article_by_executive ; failed to write file ; {article.id=}",
            exc_info=True,
        )


@article_general_router.post("/delete/{id}", status_code=204)
async def delete_article_by_author(
    id: int, session: SessionDep, request: Request
) -> None:
    article = session.get(Article, id)
    if not article:
        raise HTTPException(
            status_code=404,
            detail="Article not found",
        )
    current_user = get_user(request)
    if current_user.id != article.author_id:
        raise HTTPException(
            status_code=403,
            detail="You are not the author of this article",
        )
    if article.is_deleted:
        raise HTTPException(status_code=410, detail="Article has been deleted")
    if article.board_id in (1, 2):
        raise HTTPException(status_code=400, detail="cannot delete article of sig/pig")

    article.is_deleted = True
    article.deleted_at = datetime.now(timezone.utc)

    logger.info(
        f"info_type=article_deleted ; article_id={article.id} ; title={article.title} ; remover_id={current_user.id} ; board_id={article.board_id}"
    )
    session.commit()


@article_executive_router.post("/delete/{id}", status_code=204)
async def delete_article_by_executive(
    id: int, session: SessionDep, request: Request
) -> None:
    article = session.get(Article, id)
    if not article:
        raise HTTPException(
            status_code=404,
            detail="Article not found",
        )
    if article.is_deleted:
        raise HTTPException(status_code=410, detail="Article has been deleted")

    article.is_deleted = True
    article.deleted_at = datetime.now(timezone.utc)

    current_user = get_user(request)
    logger.info(
        f"info_type=article_deleted ; article_id={article.id} ; title={article.title} ; remover_id={current_user.id} ; board_id={article.board_id}"
    )
    session.commit()


article_router.include_router(article_general_router)
article_router.include_router(article_executive_router)
