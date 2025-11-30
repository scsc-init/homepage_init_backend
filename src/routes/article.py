from fastapi import APIRouter

from src.dependencies import UserDep
from src.schemas import ArticleResponse, ArticleWithAttachmentResponse
from src.services import ArticleServiceDep, BodyCreateArticle, BodyUpdateArticle

article_router = APIRouter(tags=["article"])
article_general_router = APIRouter(prefix="/article")
article_executive_router = APIRouter(prefix="/executive/article", tags=["executive"])


@article_general_router.post("/create", status_code=201)
async def create_article(
    article_service: ArticleServiceDep,
    current_user: UserDep,
    body: BodyCreateArticle,
) -> ArticleWithAttachmentResponse:
    return await article_service.create_article(
        body, current_user.id, current_user.role
    )


# This works as "api/article" + "s/{board_id}" (="api/articles/{board_id}")
@article_general_router.get("s/{board_id}")
async def get_article_list_by_board(
    board_id: int,
    article_service: ArticleServiceDep,
    current_user: UserDep,
) -> list[ArticleResponse]:
    return article_service.get_article_list_by_board(board_id, current_user)


@article_general_router.get("/{id}")
async def get_article_by_id(
    id: int,
    article_service: ArticleServiceDep,
    current_user: UserDep,
) -> ArticleWithAttachmentResponse:
    return article_service.get_article_by_id(id, current_user)


@article_general_router.post("/update/{id}", status_code=204)
async def update_article_by_author(
    id: int,
    article_service: ArticleServiceDep,
    current_user: UserDep,
    body: BodyUpdateArticle,
) -> None:
    await article_service.update_article_by_author(id, current_user, body)


@article_executive_router.post("/update/{id}", status_code=204)
async def update_article_by_executive(
    id: int,
    article_service: ArticleServiceDep,
    current_user: UserDep,
    body: BodyUpdateArticle,
) -> None:
    await article_service.update_article_by_executive(id, current_user, body)


@article_general_router.post("/delete/{id}", status_code=204)
async def delete_article_by_author(
    id: int,
    article_service: ArticleServiceDep,
    current_user: UserDep,
) -> None:
    article_service.delete_article_by_author(id, current_user)


@article_executive_router.post("/delete/{id}", status_code=204)
async def delete_article_by_executive(
    id: int,
    article_service: ArticleServiceDep,
    current_user: UserDep,
) -> None:
    article_service.delete_article_by_executive(id, current_user)


article_router.include_router(article_general_router)
article_router.include_router(article_executive_router)
