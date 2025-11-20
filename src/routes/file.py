from fastapi import APIRouter, UploadFile
from fastapi.responses import FileResponse

from src.controller import FileServiceDep
from src.dependencies import UserDep
from src.model import FileMetadata

file_router = APIRouter(tags=["file"])


@file_router.post("/file/docs/upload", status_code=201)
async def upload_file(
    current_user: UserDep,
    file: UploadFile,
    file_service: FileServiceDep,
) -> FileMetadata:
    return await file_service.upload_file(current_user, file)


@file_router.get("/file/docs/download/{id}")
async def get_docs_by_id(id: str, file_service: FileServiceDep) -> FileResponse:
    return file_service.get_docs_by_id(id=id)


@file_router.post("/file/image/upload", status_code=201)
async def upload_image(
    current_user: UserDep,
    file: UploadFile,
    file_service: FileServiceDep,
) -> FileMetadata:
    return await file_service.upload_image(current_user, file)


@file_router.get("/file/image/download/{id}")
async def get_image_by_id(id: str, file_service: FileServiceDep) -> FileResponse:
    return file_service.get_image_by_id(id=id)
