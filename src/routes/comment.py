from typing import Sequence

from fastapi import APIRouter, Request

from src.controller import BodyCreateComment, BodyUpdateComment, CommentServiceDep
from src.model import Comment, CommentResponse
from src.util import UserDep

comment_router = APIRouter(tags=["comment"])
comment_general_router = APIRouter(
    prefix="/comment",
)
comment_executive_router = APIRouter(prefix="/executive/comment", tags=["executive"])


@comment_general_router.post("/create", status_code=201)
async def create_comment(
    request: Request,
    body: BodyCreateComment,
    comment_service: CommentServiceDep,
    current_user: UserDep,
) -> Comment:
    return comment_service.create_comment(
        body=body, current_user=current_user, request=request
    )


# This works as "api/comment" + "s/{article_id}" (="api/comments/{article_id}")
@comment_general_router.get("s/{article_id}", response_model=Sequence[CommentResponse])
async def get_comments_by_article(
    article_id: int,
    request: Request,
    comment_service: CommentServiceDep,
    current_user: UserDep,
) -> Sequence[CommentResponse]:
    return comment_service.get_comments_by_article(
        article_id=article_id, current_user=current_user, request=request
    )


@comment_general_router.get("/{id}", response_model=CommentResponse)
async def get_comment_by_id(
    id: int,
    request: Request,
    comment_service: CommentServiceDep,
    current_user: UserDep,
) -> CommentResponse:
    return comment_service.get_comment_by_id(
        id=id, current_user=current_user, request=request
    )


@comment_general_router.post("/update/{id}", status_code=204)
async def update_comment_by_author(
    id: int,
    request: Request,
    body: BodyUpdateComment,
    comment_service: CommentServiceDep,
    current_user: UserDep,
) -> None:
    comment_service.update_comment_by_author(
        id=id, body=body, current_user=current_user, request=request
    )


@comment_general_router.post("/delete/{id}", status_code=204)
async def delete_comment_by_author(
    id: int,
    request: Request,
    comment_service: CommentServiceDep,
    current_user: UserDep,
) -> None:
    comment_service.delete_comment_by_author(
        id=id, current_user=current_user, request=request
    )


@comment_executive_router.post("/delete/{id}", status_code=204)
async def delete_comment_by_executive(
    id: int,
    request: Request,
    comment_service: CommentServiceDep,
    current_user: UserDep,
) -> None:
    comment_service.delete_comment_by_executive(
        id=id, current_user=current_user, request=request
    )


comment_router.include_router(
    comment_general_router,
)
comment_router.include_router(comment_executive_router)
