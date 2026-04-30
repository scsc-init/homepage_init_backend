from typing import Annotated, Optional

from fastapi import Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError

from src.amqp import mq_client
from src.core import get_settings, logger
from src.model import Article, User
from src.repositories import (
    ArticleRepositoryDep,
    AttachmentRepositoryDep,
    BoardRepositoryDep,
)
from src.schemas import ArticleResponse
from src.util import utcnow


class BodyCreateArticle(BaseModel):
    title: str
    content: str
    board_id: int
    attachments: list[str] = []


class BodyUpdateArticle(BaseModel):
    title: str
    content: str
    board_id: int
    attachments: list[str] = []


class ArticleService:
    def __init__(
        self,
        article_repository: ArticleRepositoryDep,
        attachment_repository: AttachmentRepositoryDep,
        board_repository: BoardRepositoryDep,
    ) -> None:
        self.article_repository = article_repository
        self.attachment_repository = attachment_repository
        self.board_repository = board_repository

    async def create_article(
        self, body: BodyCreateArticle, user_id: str, user_role: int
    ) -> ArticleResponse:
        board = self.board_repository.get_by_id(body.board_id)
        if not board:
            raise HTTPException(
                status_code=404, detail=f"Board {body.board_id} does not exist"
            )
        if user_role < board.writing_permission_level:
            raise HTTPException(
                status_code=403,
                detail="You are not allowed to write this article",
            )

        article = Article(
            title=body.title,
            author_id=user_id,
            board_id=body.board_id,
            content=body.content,
        )
        try:
            article = self.article_repository.create(article)
        except IntegrityError as exc:
            raise HTTPException(
                status_code=409, detail="unique field already exists"
            ) from exc
        attach_inserted = self.attachment_repository.insert_or_ignore_list(
            article.id, body.attachments
        )
        logger.info(
            f"info_type=article_created ; article_id={article.id} ; title={body.title} ; author_id={user_id} ; board_id={body.board_id}"
        )

        article = self.article_repository.get_by_id(article.id)
        article_response = ArticleResponse.model_validate(article)

        try:
            if mq_client:
                if body.board_id == 5:  # notice
                    await mq_client.send_discord_bot_request_no_reply(
                        action_code=1002,
                        body={
                            "channel_id": get_settings().notice_channel_id,
                            "content": f"{body.title}\n\n{body.content}",
                        },
                    )
                elif body.board_id == 6:  # grant
                    await mq_client.send_discord_bot_request_no_reply(
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

        return article_response

    def get_article_list_by_board(
        self, board_id: int, current_user: Optional[User]
    ) -> list[ArticleResponse]:
        board = self.board_repository.get_by_id(board_id)
        if board is None:
            raise HTTPException(404, detail="Board not found")

        if board.reading_permission_level > 0:
            if current_user is None:
                raise HTTPException(status_code=401, detail="Not authenticated")
            if current_user.role < board.reading_permission_level:
                raise HTTPException(
                    403, detail="You are not allowed to read this board"
                )

        articles = self.article_repository.get_articles_by_board_id(board_id)
        return ArticleResponse.model_validate_list(articles)

    def get_article_by_id(
        self, id: int, current_user: Optional[User]
    ) -> ArticleResponse:
        article = self.article_repository.get_by_id(id)
        if not article:
            raise HTTPException(404, detail="Article not found")
        board = self.board_repository.get_by_id(article.board_id)
        if not board:
            raise HTTPException(503, detail="board does not exist")

        if board.reading_permission_level > 0:
            if current_user is None:
                raise HTTPException(status_code=401, detail="Not authenticated")
            if current_user.role < board.reading_permission_level:
                raise HTTPException(
                    403, detail="You are not allowed to read this article"
                )

        return ArticleResponse.model_validate(article)

    async def _update_article(
        self, article: Article, body: BodyUpdateArticle, current_user: User
    ) -> None:
        board = self.board_repository.get_by_id(article.board_id)
        if not board:
            raise HTTPException(503, detail="board does not exist")
        if current_user.role < board.writing_permission_level:
            raise HTTPException(
                403, detail="You are not allowed to write to this board"
            )

        article.title = body.title
        article.board_id = body.board_id
        article.content = body.content
        article.updated_at = utcnow()
        try:
            article = self.article_repository.update(article)
        except IntegrityError as exc:
            raise HTTPException(
                status_code=409, detail="unique field already exists"
            ) from exc
        logger.info(
            f"info_type=article_updated ; article_id={article.id} ; title={body.title} ; revisioner_id={current_user.id} ; board_id={body.board_id}"
        )
        self.attachment_repository.delete_by_article_id(article.id)
        self.attachment_repository.insert_or_ignore_list(article.id, body.attachments)

    async def update_article_by_author(
        self, id: int, current_user: User, body: BodyUpdateArticle
    ) -> None:
        article = self.article_repository.get_by_id(id)
        if article is None:
            raise HTTPException(status_code=404, detail="Article not found")
        if current_user.id != article.author_id:
            raise HTTPException(
                status_code=403,
                detail="You are not the author of this article",
            )
        await self._update_article(article, body, current_user)

    async def update_article_by_executive(
        self, id: int, current_user: User, body: BodyUpdateArticle
    ) -> None:
        article = self.article_repository.get_by_id(id)
        if not article:
            raise HTTPException(status_code=404, detail="Article not found")
        await self._update_article(article, body, current_user)

    def delete_article_by_author(self, id: int, current_user: User) -> None:
        article = self.article_repository.get_by_id(id)
        if not article:
            raise HTTPException(status_code=404, detail="Article not found")
        if current_user.id != article.author_id:
            raise HTTPException(
                status_code=403,
                detail="You are not the author of this article",
            )
        if article.board_id in (1, 2):
            raise HTTPException(
                status_code=400, detail="cannot delete article of sig/pig"
            )

        self.article_repository.delete(article)

        logger.info(
            f"info_type=article_deleted ; article_id={article.id} ; title={article.title} ; remover_id={current_user.id} ; board_id={article.board_id}"
        )

    def delete_article_by_executive(self, id: int, current_user: User) -> None:
        article = self.article_repository.get_by_id(id)
        if not article:
            raise HTTPException(status_code=404, detail="Article not found")
        if article.board_id in (1, 2):
            raise HTTPException(
                status_code=400, detail="cannot delete article of sig/pig"
            )

        self.article_repository.delete(article)

        logger.info(
            f"info_type=article_deleted ; article_id={article.id} ; title={article.title} ; remover_id={current_user.id} ; board_id={article.board_id}"
        )


ArticleServiceDep = Annotated[ArticleService, Depends()]
