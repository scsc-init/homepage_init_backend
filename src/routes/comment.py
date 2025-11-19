from typing import Sequence

from fastapi import APIRouter

from src.controller import BodyCreateComment, BodyUpdateComment, CommentServiceDep
from src.dependencies import UserDep
from src.model import Comment, CommentResponse

comment_router = APIRouter(tags=["comment"])
comment_general_router = APIRouter(
    prefix="/comment",
)
comment_executive_router = APIRouter(prefix="/executive/comment", tags=["executive"])


@comment_general_router.post("/create", status_code=201)
async def create_comment(
    current_user: UserDep,
    body: BodyCreateComment,
    comment_service: CommentServiceDep,
) -> Comment:
    return comment_service.create_comment(current_user, body)


# This works as "api/comment" + "s/{article_id}" (="api/comments/{article_id}")
@comment_general_router.get("s/{article_id}", response_model=Sequence[CommentResponse])
async def get_comments_by_article(
    article_id: int,
    current_user: UserDep,
    comment_service: CommentServiceDep,
) -> Sequence[CommentResponse]:
    return comment_service.get_comments_by_article(article_id, current_user)


@comment_general_router.get("/{id}", response_model=CommentResponse)
async def get_comment_by_id(
    id: int,
    current_user: UserDep,
    comment_service: CommentServiceDep,
) -> CommentResponse:
    return comment_service.get_comment_by_id(id, current_user)


@comment_general_router.post("/update/{id}", status_code=204)
async def update_comment_by_author(
    id: int,
    current_user: UserDep,
    body: BodyUpdateComment,
    comment_service: CommentServiceDep,
) -> None:
    comment_service.update_comment_by_author(id, current_user, body)


@comment_general_router.post("/delete/{id}", status_code=204)
async def delete_comment_by_author(
    id: int,
    current_user: UserDep,
    comment_service: CommentServiceDep,
) -> None:
    comment_service.delete_comment_by_author(id, current_user)


@comment_executive_router.post("/delete/{id}", status_code=204)
async def delete_comment_by_executive(
    id: int,
    current_user: UserDep,
    comment_service: CommentServiceDep,
) -> None:
    comment_service.delete_comment_by_executive(id, current_user)


comment_router.include_router(
    comment_general_router,
)
comment_router.include_router(comment_executive_router)
