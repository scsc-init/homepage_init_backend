from typing import Sequence

from fastapi import APIRouter, Request, UploadFile
from fastapi.responses import FileResponse

from src.controller import WServiceDep
from src.model import WHTMLMetadata
from src.util import UserDep

w_router = APIRouter(tags=["w"])


@w_router.post("/executive/w/create", status_code=201)
async def upload_file(
    current_user: UserDep,
    file: UploadFile,
    w_service: WServiceDep,
    request: Request,
) -> WHTMLMetadata:
    return await w_service.upload_file(current_user, file, request)


@w_router.get("/w/{name}")
async def get_w_by_name(name: str, w_service: WServiceDep) -> FileResponse:
    return w_service.get_w_by_name(name)


@w_router.get("/executive/ws")
async def get_all_metadata(
    w_service: WServiceDep,
) -> Sequence[tuple[WHTMLMetadata, str]]:
    return w_service.get_all_metadata()


@w_router.post("/executive/w/{name}/update", status_code=200)
async def update_w_by_name(
    name: str,
    current_user: UserDep,
    file: UploadFile,
    w_service: WServiceDep,
    request: Request,
) -> WHTMLMetadata:
    return await w_service.update_w_by_name(name, current_user, file, request)


@w_router.post("/executive/w/{name}/delete", status_code=204)
async def delete_w_by_name(
    name: str,
    current_user: UserDep,
    w_service: WServiceDep,
    request: Request,
) -> None:
    w_service.delete_w_by_name(name, current_user, request)
