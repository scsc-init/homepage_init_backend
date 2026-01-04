from fastapi import APIRouter, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from src.dependencies import UserDep
from src.schemas import FileMetadataResponse
from src.services import FileServiceDep

file_router = APIRouter(tags=["file"])


class BodyGetFileMetadata(BaseModel):
    ids: list[str] = Field(default_factory=list, description="File IDs to fetch")


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


@file_router.post("/file/metadata")
async def get_file_metadata(
    body: BodyGetFileMetadata, file_service: FileServiceDep
) -> list[FileMetadataResponse]:
    files = file_service.get_metadata_by_ids(body.ids)
    return FileMetadataResponse.model_validate_list(files)
