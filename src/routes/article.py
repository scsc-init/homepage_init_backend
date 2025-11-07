from fastapi import APIRouter, Request

from src.controller import ArticleServiceDep, BodyCreateArticle, BodyUpdateArticle
from src.model import ArticleResponse

article_router = APIRouter(tags=["article"])
article_general_router = APIRouter(prefix="/article")
article_executive_router = APIRouter(prefix="/executive/article", tags=["executive"])


@article_general_router.post("/create", status_code=201)
async def create_article(
    request: Request,
    body: BodyCreateArticle,
    article_service: ArticleServiceDep,
) -> ArticleResponse:
    return await article_service.create_article(request=request, body=body)


# This works as "api/article" + "s/{board_id}" (="api/articles/{board_id}")
@article_general_router.get("s/{board_id}")
async def get_article_list_by_board(
    board_id: int,
    request: Request,
    article_service: ArticleServiceDep,
) -> list[ArticleResponse]:
    return article_service.get_article_list_by_board(board_id=board_id, request=request)


@article_general_router.get("/{id}")
async def get_article_by_id(
    id: int,
    request: Request,
    article_service: ArticleServiceDep,
) -> ArticleResponse:
    return article_service.get_article_by_id(id=id, request=request)


@article_general_router.post("/update/{id}", status_code=204)
async def update_article_by_author(
    id: int,
    request: Request,
    body: BodyUpdateArticle,
    article_service: ArticleServiceDep,
) -> None:
    article_service.update_article_by_author(id=id, request=request, body=body)


@article_executive_router.post("/update/{id}", status_code=204)
async def update_article_by_executive(
    id: int,
    request: Request,
    body: BodyUpdateArticle,
    article_service: ArticleServiceDep,
) -> None:
    article_service.update_article_by_executive(id=id, request=request, body=body)


@article_general_router.post("/delete/{id}", status_code=204)
async def delete_article_by_author(
    id: int,
    request: Request,
    article_service: ArticleServiceDep,
) -> None:
    article_service.delete_article_by_author(id=id, request=request)


@article_executive_router.post("/delete/{id}", status_code=204)
async def delete_article_by_executive(
    id: int,
    request: Request,
    article_service: ArticleServiceDep,
) -> None:
    article_service.delete_article_by_executive(id=id, request=request)


article_router.include_router(article_general_router)
article_router.include_router(article_executive_router)
