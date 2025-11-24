from datetime import datetime, timezone
from typing import Annotated, Optional, Sequence

from fastapi import Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError

from src.core import logger
from src.model import Comment, User
from src.repositories import (
    ArticleRepositoryDep,
    BoardRepositoryDep,
    CommentRepositoryDep,
)
from src.schemas import CommentResponse
from src.util import DELETED


class BodyCreateComment(BaseModel):
    content: str
    article_id: int
    parent_id: Optional[int]


class BodyUpdateComment(BaseModel):
    content: str


class CommentService:
    def __init__(
        self,
        article_repository: ArticleRepositoryDep,
        board_repository: BoardRepositoryDep,
        comment_repository: CommentRepositoryDep,
    ) -> None:
        self.article_repository = article_repository
        self.board_repository = board_repository
        self.comment_repository = comment_repository

    def create_comment(self, current_user: User, body: BodyCreateComment) -> Comment:
        article = self.article_repository.get_by_id(body.article_id)
        if not article:
            raise HTTPException(
                status_code=404, detail=f"Article {body.article_id} does not exist"
            )
        if article.is_deleted:
            raise HTTPException(status_code=410, detail="Article has been deleted")
        board = self.board_repository.get_by_id(article.board_id)
        if not board:
            raise HTTPException(503, detail="board does not exist")

        if current_user.role < board.writing_permission_level:
            raise HTTPException(
                status_code=403,
                detail="You are not allowed to write this comment",
            )
        comment = Comment(
            content=body.content,
            author_id=current_user.id,
            article_id=article.id,
            parent_id=body.parent_id,
        )
        try:
            comment = self.comment_repository.create(comment)
        except IntegrityError as exc:
            raise HTTPException(
                status_code=409, detail="unique field already exists"
            ) from exc

        logger.info(
            f"info_type=comment_created ; content={body.content[:100]} ; author_id={current_user.id} ; article_id={article.id} ; parent_id={body.parent_id}"
        )
        return comment

    def get_comments_by_article(
        self, article_id: int, current_user: User
    ) -> Sequence[CommentResponse]:
        article = self.article_repository.get_by_id(article_id)
        if not article:
            raise HTTPException(
                status_code=404, detail=f"Article {article_id} does not exist"
            )
        board = self.board_repository.get_by_id(article.board_id)
        if not board:
            raise HTTPException(503, detail="board does not exist")

        if current_user.role < board.reading_permission_level:
            raise HTTPException(
                status_code=403,
                detail="You are not allowed to read these comments",
            )

        comments = self.comment_repository.get_comments_by_article_id(article_id)
        result = []
        for comment in comments:
            comment = CommentResponse.model_validate(comment)
            if comment.is_deleted:
                comment.content = DELETED
            result.append(comment)
        return result

    def get_comment_by_id(self, id: int, current_user: User) -> CommentResponse:
        comment = self.comment_repository.get_by_id(id)
        if not comment:
            raise HTTPException(status_code=404, detail=f"Comment {id} does not exist")
        article = self.article_repository.get_by_id(comment.article_id)
        if not article:
            raise HTTPException(503, detail="article does not exist")
        board = self.board_repository.get_by_id(article.board_id)
        if not board:
            raise HTTPException(503, detail="board does not exist")

        if current_user.role < board.reading_permission_level:
            raise HTTPException(
                status_code=403,
                detail="You are not allowed to read this comment",
            )

        comment = CommentResponse.model_validate(comment)
        if comment.is_deleted:
            comment.content = DELETED
        return comment

    def update_comment_by_author(
        self, id: int, current_user: User, body: BodyUpdateComment
    ) -> Comment:
        comment = self.comment_repository.get_by_id(id)
        if not comment:
            raise HTTPException(
                status_code=404,
                detail="Comment not found",
            )
        if comment.is_deleted:
            raise HTTPException(status_code=410, detail="Comment has been deleted")

        if current_user.id != comment.author_id:
            raise HTTPException(
                status_code=403,
                detail="You are not the author of this comment",
            )

        comment.content = body.content
        comment.updated_at = datetime.now(timezone.utc)
        try:
            comment = self.comment_repository.update(comment)
        except IntegrityError as exc:
            raise HTTPException(
                status_code=409, detail="unique field already exists"
            ) from exc
        logger.info(
            f"info_type=comment_updated ; comment_id={comment.id} ; article_id={comment.article_id} ; parent_id={comment.parent_id} ; content={body.content[:100]} ; revisioner_id={current_user.id}"
        )

        return comment

    def delete_comment_by_author(self, id: int, current_user: User) -> None:
        comment = self.comment_repository.get_by_id(id)
        if not comment:
            raise HTTPException(
                status_code=404,
                detail="Comment not found",
            )
        if comment.is_deleted:
            raise HTTPException(status_code=410, detail="Already deleted")

        if current_user.id != comment.author_id:
            raise HTTPException(
                status_code=403,
                detail="You are not the author of this comment",
            )

        comment.is_deleted = True
        comment.deleted_at = datetime.now(timezone.utc)

        try:
            comment = self.comment_repository.update(comment)
        except IntegrityError as exc:
            raise HTTPException(
                status_code=409, detail="unique field already exists"
            ) from exc
        logger.info(
            f"info_type=comment_deleted ; comment_id={comment.id} ; article_id={comment.article_id} ; parent_id={comment.parent_id} ; remover_id={current_user.id}"
        )

    def delete_comment_by_executive(self, id: int, current_user: User) -> None:
        comment = self.comment_repository.get_by_id(id)
        if not comment:
            raise HTTPException(
                status_code=404,
                detail="Comment not found",
            )
        if comment.is_deleted:
            raise HTTPException(status_code=410, detail="Already deleted")

        comment.is_deleted = True
        comment.deleted_at = datetime.now(timezone.utc)

        try:
            comment = self.comment_repository.update(comment)
        except IntegrityError as exc:
            raise HTTPException(
                status_code=409, detail="unique field already exists"
            ) from exc
        logger.info(
            f"info_type=comment_deleted ; comment_id={comment.id} ; article_id={comment.article_id} ; parent_id={comment.parent_id} ; remover_id={current_user.id}"
        )


CommentServiceDep = Annotated[CommentService, Depends()]
