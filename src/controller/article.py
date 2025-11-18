from datetime import datetime, timezone
from os import path
from typing import Annotated

from fastapi import Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError

from src.core import get_settings, logger
from src.model import Article, ArticleResponse, User
from src.repositories import ArticleRepositoryDep, BoardRepositoryDep
from src.util import DELETED, send_discord_bot_request_no_reply


class BodyCreateArticle(BaseModel):
    title: str
    content: str
    board_id: int


class BodyUpdateArticle(BaseModel):
    title: str
    content: str
    board_id: int


class ArticleService:
    def __init__(
        self,
        article_repository: ArticleRepositoryDep,
        board_repository: BoardRepositoryDep,
    ) -> None:
        self.article_repository = article_repository
        self.board_repository = board_repository

    async def create_article(
        self, current_user: User, body: BodyCreateArticle
    ) -> ArticleResponse:
        board = self.board_repository.get_by_id(body.board_id)
        if not board:
            raise HTTPException(
                status_code=404, detail=f"Board {body.board_id} does not exist"
            )
        if current_user.role < board.writing_permission_level:
            raise HTTPException(
                status_code=403,
                detail="You are not allowed to write this article",
            )

        article = Article(
            title=body.title, author_id=current_user.id, board_id=body.board_id
        )
        try:
            article = self.article_repository.create(article)
        except IntegrityError as exc:
            raise HTTPException(
                status_code=409, detail="unique field already exists"
            ) from exc

        try:
            file_path = path.join(get_settings().article_dir, f"{article.id}.md")
            with open(file_path, "w", encoding="utf-8") as fp:
                fp.write(body.content)
        except Exception:
            logger.error(
                f"err_type=create_article_ctrl ; failed to write file ; {article.id=}",
                exc_info=True,
            )
        logger.info(
            f"info_type=article_created ; article_id={article.id} ; title={body.title} ; author_id={current_user.id} ; board_id={body.board_id}"
        )

        article_response = ArticleResponse.model_validate(article).model_copy(
            update={"content": body.content}
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

        return article_response

    def get_article_list_by_board(
        self, board_id: int, current_user: User
    ) -> list[ArticleResponse]:
        board = self.board_repository.get_by_id(board_id)
        if board is None:
            raise HTTPException(404, detail="Board not found")

        if board.reading_permission_level > 0:
            if current_user.role < board.reading_permission_level:
                raise HTTPException(
                    403, detail="You are not allowed to read this board"
                )

        articles = self.article_repository.get_articles_by_board_id(board_id)
        result: list[ArticleResponse] = []
        for article in articles:
            if article.is_deleted:
                result.append(
                    ArticleResponse.model_validate(article).model_copy(
                        update={"content": DELETED}
                    )
                )
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
                result.append(
                    ArticleResponse.model_validate(article).model_copy(
                        update={"content": content}
                    )
                )

        return result

    def get_article_by_id(self, id: int, current_user: User) -> ArticleResponse:
        article = self.article_repository.get_by_id(id)
        if not article:
            raise HTTPException(404, detail="Article not found")
        board = self.board_repository.get_by_id(article.board_id)
        if not board:
            raise HTTPException(503, detail="board does not exist")

        if board.reading_permission_level > 0:
            if current_user.role < board.reading_permission_level:
                raise HTTPException(
                    403, detail="You are not allowed to read this article"
                )

        if article.is_deleted:
            return ArticleResponse.model_validate(article).model_copy(
                update={"content": DELETED}
            )

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
        return ArticleResponse.model_validate(article).model_copy(
            update={"content": content}
        )

    def _update_article(
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
        article.updated_at = datetime.now(timezone.utc)
        try:
            article = self.article_repository.update(article)
        except IntegrityError as exc:
            raise HTTPException(
                status_code=409, detail="unique field already exists"
            ) from exc
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

    def update_article_by_author(
        self, id: int, current_user: User, body: BodyUpdateArticle
    ) -> None:
        article = self.article_repository.get_by_id(id)
        if article is None:
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
        self._update_article(article, body, current_user)

    def update_article_by_executive(
        self, id: int, current_user: User, body: BodyUpdateArticle
    ) -> None:
        article = self.article_repository.get_by_id(id)
        if not article:
            raise HTTPException(
                status_code=404,
                detail="Article not found",
            )
        if article.is_deleted:
            raise HTTPException(status_code=410, detail="Article has been deleted")
        self._update_article(article, body, current_user)

    def delete_article_by_author(self, id: int, current_user: User) -> None:
        article = self.article_repository.get_by_id(id)
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

        article = self.article_repository.update(article)

        logger.info(
            f"info_type=article_deleted ; article_id={article.id} ; title={article.title} ; remover_id={current_user.id} ; board_id={article.board_id}"
        )

    def delete_article_by_executive(self, id: int, current_user: User) -> None:
        article = self.article_repository.get_by_id(id)
        if not article:
            raise HTTPException(
                status_code=404,
                detail="Article not found",
            )
        if article.is_deleted:
            raise HTTPException(status_code=410, detail="Article has been deleted")

        article.is_deleted = True
        article.deleted_at = datetime.now(timezone.utc)

        article = self.article_repository.update(article)

        logger.info(
            f"info_type=article_deleted ; article_id={article.id} ; title={article.title} ; remover_id={current_user.id} ; board_id={article.board_id}"
        )


ArticleServiceDep = Annotated[ArticleService, Depends()]
