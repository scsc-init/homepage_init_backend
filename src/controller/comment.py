from datetime import datetime, timezone
from typing import Annotated, Optional, Sequence

from fastapi import Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from src.core import logger
from src.db import SessionDep
from src.model import Article, Board, Comment, CommentResponse, User
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
        session: SessionDep,
    ) -> None:
        self.session = session

    def create_comment(
        self, body: BodyCreateComment, current_user: User, request: Request
    ) -> Comment:
        article = self.session.get(Article, body.article_id)
        if not article:
            raise HTTPException(
                status_code=404, detail=f"Article {body.article_id} does not exist"
            )
        if article.is_deleted:
            raise HTTPException(status_code=410, detail="Article has been deleted")
        board = self.session.get(Board, article.board_id)
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
        self.session.add(comment)
        try:
            self.session.commit()
        except IntegrityError:
            self.session.rollback()
            raise HTTPException(status_code=409, detail="unique field already exists")
        self.session.refresh(comment)

        logger.info(
            f"info_type=comment_created ; content={body.content[:100]} ; author_id={current_user.id} ; article_id={article.id} ; parent_id={body.parent_id}"
        )
        return comment

    def get_comments_by_article(
        self, article_id: int, current_user: User, request: Request
    ) -> Sequence[CommentResponse]:
        article = self.session.get(Article, article_id)
        if not article:
            raise HTTPException(
                status_code=404, detail=f"Article {article_id} does not exist"
            )
        board = self.session.get(Board, article.board_id)
        if not board:
            raise HTTPException(503, detail="board does not exist")

        if current_user.role < board.reading_permission_level:
            raise HTTPException(
                status_code=403,
                detail="You are not allowed to read these comments",
            )

        comments = self.session.exec(
            select(Comment).where(Comment.article_id == article_id)
        ).all()
        result = []
        for comment in comments:
            comment = CommentResponse.model_validate(comment)
            if comment.is_deleted:
                comment.content = DELETED
            result.append(comment)
        return result

    def get_comment_by_id(
        self, id: int, current_user: User, request: Request
    ) -> CommentResponse:
        comment = self.session.get(Comment, id)
        if not comment:
            raise HTTPException(status_code=404, detail=f"Comment {id} does not exist")
        article = self.session.get(Article, comment.article_id)
        if not article:
            raise HTTPException(503, detail="article does not exist")
        board = self.session.get(Board, article.board_id)
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
        self, id: int, body: BodyUpdateComment, current_user: User, request: Request
    ) -> None:
        comment = self.session.get(Comment, id)
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
        logger.info(
            f"info_type=comment_updated ; comment_id={comment.id} ; article_id={comment.article_id} ; parent_id={comment.parent_id} ; content={body.content[:100]} ; revisioner_id={current_user.id}"
        )
        try:
            self.session.commit()
        except IntegrityError:
            self.session.rollback()
            raise HTTPException(status_code=409, detail="unique field already exists")

    def delete_comment_by_author(
        self, id: int, current_user: User, request: Request
    ) -> None:
        comment = self.session.get(Comment, id)
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
        logger.info(
            f"info_type=comment_deleted ; comment_id={comment.id} ; article_id={comment.article_id} ; parent_id={comment.parent_id} ; remover_id={current_user.id}"
        )
        self.session.commit()

    def delete_comment_by_executive(
        self, id: int, current_user: User, request: Request
    ) -> None:
        comment = self.session.get(Comment, id)
        if not comment:
            raise HTTPException(
                status_code=404,
                detail="Comment not found",
            )
        if comment.is_deleted:
            raise HTTPException(status_code=410, detail="Already deleted")

        comment.is_deleted = True
        comment.deleted_at = datetime.now(timezone.utc)

        logger.info(
            f"info_type=comment_deleted ; comment_id={comment.id} ; article_id={comment.article_id} ; parent_id={comment.parent_id} ; remover_id={current_user.id}"
        )
        self.session.commit()


CommentServiceDep = Annotated[CommentService, Depends()]
