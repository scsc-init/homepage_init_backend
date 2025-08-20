from datetime import datetime, timezone
from typing import Optional, Sequence

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from src.db import SessionDep
from src.model import Article, Board, Comment
from src.util import get_user

comment_router = APIRouter(tags=['comment'])
comment_general_router = APIRouter(prefix="/comment", )
comment_executive_router = APIRouter(prefix="/executive/comment", tags=['executive'])


class BodyCreateComment(BaseModel):
    content: str
    article_id: int
    parent_id: Optional[int]


@comment_general_router.post('/create', status_code=201)
async def create_comment(session: SessionDep, request: Request, body: BodyCreateComment) -> Comment:
    user = get_user(request)
    article = session.get(Article, body.article_id)
    if not article: raise HTTPException(status_code=404, detail=f"Article {body.article_id} does not exist")
    board = session.get(Board, article.board_id)
    if user.role < board.writing_permission_level: raise HTTPException(status_code=403,
                                                                       detail="You are not allowed to write this comment", )
    comment = Comment(content=body.content, author_id=user.id, article_id=article.id, parent_id=body.parent_id)
    session.add(comment)
    try: session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=409, detail="unique field already exists")
    session.refresh(comment)
    return comment


# This works as "api/comment" + "s/{article_id}" (="api/comments/{article_id}")
@comment_general_router.get('s/{article_id}')
async def get_comments_by_article(article_id: int, session: SessionDep, request: Request) -> Sequence[Comment]:
    user = get_user(request)
    article = session.get(Article, article_id)
    if not article: raise HTTPException(status_code=404, detail=f"Article {article_id} does not exist")
    board = session.get(Board, article.board_id)
    if user.role < board.reading_permission_level: raise HTTPException(status_code=403, detail="You are not allowed to read these comments", )
    comments = session.exec(select(Comment).where(Comment.article_id == article_id)).all()
    for comment in comments:
        if comment.is_deleted:
            comment.content = None
    return comments


@comment_general_router.get('/{id}')
async def get_comment_by_id(id: int, session: SessionDep, request: Request) -> Comment:
    user = get_user(request)
    comment = session.get(Comment, id)
    if not comment: raise HTTPException(status_code=404, detail=f"Comment {id} does not exist")
    article = session.get(Article, comment.article_id)
    board = session.get(Board, article.board_id)
    if user.role < board.reading_permission_level: raise HTTPException(status_code=403, detail="You are not allowed to read this comment", )
    if comment.is_deleted:
        comment.content = None
    return comment


class BodyUpdateComment(BaseModel):
    content: str


@comment_general_router.post('/update/{id}', status_code=204)
async def update_comment_by_author(id: int, session: SessionDep, request: Request, body: BodyUpdateComment) -> None:
    current_user = get_user(request)
    comment = session.get(Comment, id)
    if not comment: raise HTTPException(status_code=404, detail="Comment not found",)
    if current_user.id != comment.author_id:
        raise HTTPException(status_code=403, detail="You are not the author of this comment",)
    comment.content = body.content
    comment.updated_at = datetime.now(timezone.utc)
    try: session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=409, detail="unique field already exists")
    session.refresh(comment)


# @comment_executive_router.post('/update/{id}', status_code=204)
# async def update_article_by_executive(id: int, session: SessionDep, body: BodyUpdateComment) -> None:
#     comment = session.get(Comment, id)
#     if not comment: raise HTTPException(status_code=404, detail="Comment not found",)
#     comment.content = body.content
#     comment.updated_at = datetime.now(timezone.utc)
#     try: session.commit()
#     except IntegrityError:
#         session.rollback()
#         raise HTTPException(status_code=409, detail="unique field already exists")
#     session.refresh(comment)


@comment_general_router.post('/delete/{id}', status_code=204)
async def delete_comment_by_author(id: int, session: SessionDep, request: Request) -> None:
    current_user = get_user(request)
    comment = session.get(Comment, id)
    if not comment: raise HTTPException(status_code=404, detail="Comment not found", )
    if current_user.id != comment.author_id: raise HTTPException(status_code=403, detail="You are not the author of this comment",)
    session.delete(comment)
    session.commit()


@comment_executive_router.post('/delete/{id}', status_code=204)
async def delete_comment_by_executive(id: int, session: SessionDep) -> None:
    comment = session.get(Comment, id)
    if not comment: raise HTTPException(status_code=404, detail="Comment not found", )
    session.delete(comment)
    session.commit()


comment_router.include_router(comment_general_router, )
comment_router.include_router(comment_executive_router)
