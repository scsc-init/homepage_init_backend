from typing import Annotated, Sequence

from fastapi import APIRouter, Form, UploadFile
from fastapi.responses import FileResponse

from src.dependencies import UserDep
from src.model import WHTMLMetadata
from src.schemas import WHTMLMetadataResponse
from src.services import WServiceDep

w_router = APIRouter(tags=["w"])


@w_router.post("/executive/w/create", status_code=201)
async def upload_file(
    current_user: UserDep,
    file: UploadFile,
    w_service: WServiceDep,
    name: Annotated[str | None, Form()] = None,
) -> WHTMLMetadataResponse:
    w_meta = await w_service.upload_file(current_user, file, name)
    return WHTMLMetadataResponse.model_validate(w_meta)


@w_router.get("/w/{name:path}")
async def get_w_by_name(name: str, w_service: WServiceDep) -> FileResponse:
    return w_service.get_w_by_name(name)


@w_router.get("/executive/ws")
async def get_all_metadata(
    w_service: WServiceDep,
) -> Sequence[tuple[WHTMLMetadata, str]]:
    return w_service.get_all_metadata()


@w_router.post("/executive/w/{name:path}/update", status_code=200)
async def update_w_by_name(
    name: str,
    current_user: UserDep,
    file: UploadFile,
    w_service: WServiceDep,
) -> WHTMLMetadataResponse:
    w_meta = await w_service.update_w_by_name(name, current_user, file)
    return WHTMLMetadataResponse.model_validate(w_meta)


@w_router.post("/executive/w/{name:path}/delete", status_code=204)
async def delete_w_by_name(
    name: str,
    current_user: UserDep,
    w_service: WServiceDep,
) -> None:
    await w_service.delete_w_by_name(name, current_user)


@w_router.get("/executive/w/{name:path}/download")
async def download_w_by_name(
    name: str,
    current_user: UserDep,
    w_service: WServiceDep,
):
    return w_service.download_w_by_name(name, current_user)
