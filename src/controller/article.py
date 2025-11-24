from datetime import datetime, timezone
from os import path
from typing import Annotated

import aiofiles
from fastapi import Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from src.core import get_settings, logger
from src.db import SessionDep
from src.model import Article, ArticleResponse, Board, User
from src.util import DELETED, send_discord_bot_request_no_reply


class BodyCreateArticle(BaseModel):
    title: str
    content: str
    board_id: int


async def create_article_ctrl(
    session: SessionDep, body: BodyCreateArticle, user_id: str, user_role: int
) -> ArticleResponse:
    board = session.get(Board, body.board_id)
    if not board:
        raise HTTPException(
            status_code=404, detail=f"Board {body.board_id} does not exist"
        )
    if user_role < board.writing_permission_level:
        raise HTTPException(
            status_code=403,
            detail="You are not allowed to write this article",
        )

    article = Article(title=body.title, author_id=user_id, board_id=body.board_id)
    session.add(article)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=409, detail="unique field already exists")
    session.refresh(article)
    try:
        file_path = path.join(get_settings().article_dir, f"{article.id}.md")
        async with aiofiles.open(file_path, "w", encoding="utf-8") as fp:
            await fp.write(body.content)
    except Exception:
        logger.error(
            f"err_type=create_article_ctrl ; failed to write file ; {article.id=}",
            exc_info=True,
        )
    logger.info(
        f"info_type=article_created ; article_id={article.id} ; title={body.title} ; author_id={user_id} ; board_id={body.board_id}"
    )
    article_response = ArticleResponse(**article.model_dump(), content=body.content)
    return article_response


class BodyUpdateArticle(BaseModel):
    title: str
    content: str
    board_id: int


class ArticleService:
    def __init__(
        self,
        session: SessionDep,
    ) -> None:
        self.session = session

    async def create_article(
        self, current_user: User, body: BodyCreateArticle
    ) -> ArticleResponse:
        ret = await create_article_ctrl(
            self.session, body, current_user.id, current_user.role
        )
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

    def get_article_list_by_board(
        self, board_id: int, current_user: User
    ) -> list[ArticleResponse]:
        board = self.session.get(Board, board_id)
        if not board:
            raise HTTPException(404, detail="Board not found")

        if board.reading_permission_level > 0:
            if current_user.role < board.reading_permission_level:
                raise HTTPException(
                    403, detail="You are not allowed to read this board"
                )

        articles = self.session.exec(
            select(Article).where(Article.board_id == board_id)
        ).all()
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

    def get_article_by_id(self, id: int, current_user: User) -> ArticleResponse:
        article = self.session.get(Article, id)
        if not article:
            raise HTTPException(404, detail="Article not found")
        board = self.session.get(Board, article.board_id)
        if not board:
            raise HTTPException(503, detail="board does not exist")

        if board.reading_permission_level > 0:
            if current_user.role < board.reading_permission_level:
                raise HTTPException(
                    403, detail="You are not allowed to read this article"
                )

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

    async def _update_article(
        self, article: Article, body: BodyUpdateArticle, current_user: User
    ) -> None:
        board = self.session.get(Board, body.board_id)
        if not board:
            raise HTTPException(503, detail="board does not exist")
        if current_user.role < board.writing_permission_level:
            raise HTTPException(
                403, detail="You are not allowed to write to this board"
            )

        article.title = body.title
        article.board_id = body.board_id
        article.updated_at = datetime.now(timezone.utc)
        try:
            self.session.commit()
        except IntegrityError:
            self.session.rollback()
            raise HTTPException(status_code=409, detail="unique field already exists")
        self.session.refresh(article)
        logger.info(
            f"info_type=article_updated ; article_id={article.id} ; title={body.title} ; revisioner_id={current_user.id} ; board_id={body.board_id}"
        )
        try:
            file_path = path.join(get_settings().article_dir, f"{article.id}.md")
            async with aiofiles.open(file_path, "w", encoding="utf-8") as fp:
                await fp.write(body.content)
        except Exception:
            logger.error(
                f"err_type=update_article_by_author ; failed to write file ; {article.id=}",
                exc_info=True,
            )

    async def update_article_by_author(
        self, id: int, current_user: User, body: BodyUpdateArticle
    ) -> None:
        article = self.session.get(Article, id)
        if not article:
            raise HTTPException(
                status_code=404,
                detail="Article not found",
            )
        if current_user.id != article.author_id:
            raise HTTPException(
                status_code=403,
                detail="You are not the author of this article",
            )
        if article.is_deleted:
            raise HTTPException(status_code=410, detail="Article has been deleted")
        await self._update_article(article, body, current_user)

    async def update_article_by_executive(
        self, id: int, current_user: User, body: BodyUpdateArticle
    ) -> None:
        article = self.session.get(Article, id)
        if not article:
            raise HTTPException(
                status_code=404,
                detail="Article not found",
            )
        if article.is_deleted:
            raise HTTPException(status_code=410, detail="Article has been deleted")
        await self._update_article(article, body, current_user)

    def delete_article_by_author(self, id: int, current_user: User) -> None:
        article = self.session.get(Article, id)
        if not article:
            raise HTTPException(
                status_code=404,
                detail="Article not found",
            )
        if current_user.id != article.author_id:
            raise HTTPException(
                status_code=403,
                detail="You are not the author of this article",
            )
        if article.is_deleted:
            raise HTTPException(status_code=410, detail="Article has been deleted")
        if article.board_id in (1, 2):
            raise HTTPException(
                status_code=400, detail="cannot delete article of sig/pig"
            )

        article.is_deleted = True
        article.deleted_at = datetime.now(timezone.utc)

        logger.info(
            f"info_type=article_deleted ; article_id={article.id} ; title={article.title} ; remover_id={current_user.id} ; board_id={article.board_id}"
        )
        self.session.commit()

    def delete_article_by_executive(self, id: int, current_user: User) -> None:
        article = self.session.get(Article, id)
        if not article:
            raise HTTPException(
                status_code=404,
                detail="Article not found",
            )
        if article.is_deleted:
            raise HTTPException(status_code=410, detail="Article has been deleted")

        article.is_deleted = True
        article.deleted_at = datetime.now(timezone.utc)

        logger.info(
            f"info_type=article_deleted ; article_id={article.id} ; title={article.title} ; remover_id={current_user.id} ; board_id={article.board_id}"
        )
        self.session.commit()


ArticleServiceDep = Annotated[ArticleService, Depends()]
