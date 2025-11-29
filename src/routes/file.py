from fastapi import APIRouter, UploadFile
from fastapi.responses import FileResponse

from src.dependencies import UserDep
from src.schemas import FileMetadataResponse
from src.services import FileServiceDep

file_router = APIRouter(tags=["file"])


@file_router.post("/file/docs/upload", status_code=201)
async def upload_file(
    current_user: UserDep,
    file: UploadFile,
    file_service: FileServiceDep,
) -> FileMetadataResponse:
    file_meta = await file_service.upload_file(current_user, file)
    return FileMetadataResponse.model_validate(file_meta)


@file_router.get("/file/docs/download/{id}")
async def get_docs_by_id(id: str, file_service: FileServiceDep) -> FileResponse:
    return file_service.get_docs_by_id(id=id)


@file_router.post("/file/image/upload", status_code=201)
async def upload_image(
    current_user: UserDep,
    file: UploadFile,
    file_service: FileServiceDep,
) -> FileMetadataResponse:
    image_meta = await file_service.upload_image(current_user, file)
    return FileMetadataResponse.model_validate(image_meta)


@file_router.get("/file/image/download/{id}")
async def get_image_by_id(id: str, file_service: FileServiceDep) -> FileResponse:
    return file_service.get_image_by_id(id=id)
