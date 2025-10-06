from os import path

from fastapi import APIRouter, File, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse

from src.core import get_settings
from src.db import SessionDep
from src.model import FileMetadata
from src.util import create_uuid, get_user, split_filename, validate_and_read_file

file_router = APIRouter(tags=["file"])


@file_router.post("/file/docs/upload", status_code=201)
async def upload_file(
    session: SessionDep, request: Request, file: UploadFile = File(...)
) -> FileMetadata:
    current_user = get_user(request)
    content, basename, ext, mime_type = await validate_and_read_file(
        file, valid_ext=frozenset({"pdf", "docx", "pptx"})
    )
    uuid = create_uuid()
    with open(path.join(get_settings().file_dir, f"{uuid}.{ext}"), "wb") as fp:
        fp.write(content)

    file_meta = FileMetadata(
        id=uuid,
        original_filename=f"{basename}.{ext}",
        size=len(content),
        mime_type=mime_type,
        owner=current_user.id,
    )
    session.add(file_meta)
    session.commit()
    session.refresh(file_meta)
    return file_meta


@file_router.get("/file/docs/download/{id}")
async def get_docs_by_id(id: str, session: SessionDep) -> FileResponse:
    file_meta = session.get(FileMetadata, id)
    if not file_meta:
        raise HTTPException(404, detail="file not found")
    _, ext = split_filename(file_meta.original_filename)
    return FileResponse(path.join(get_settings().file_dir, f"{file_meta.id}.{ext}"))


@file_router.post("/file/image/upload", status_code=201)
async def upload_image(
    session: SessionDep, request: Request, file: UploadFile = File(...)
) -> FileMetadata:
    current_user = get_user(request)
    content, basename, ext, mime_type = await validate_and_read_file(
        file, valid_mime_type="image/", valid_ext=frozenset({"jpg", "jpeg", "png"})
    )

    uuid = create_uuid()
    with open(path.join(get_settings().image_dir, f"{uuid}.{ext}"), "wb") as fp:
        fp.write(content)

    image = FileMetadata(
        id=uuid,
        original_filename=f"{basename}.{ext}",
        size=len(content),
        mime_type=mime_type,
        owner=current_user.id,
    )
    session.add(image)
    session.commit()
    session.refresh(image)
    return image


@file_router.get("/file/image/download/{id}")
async def get_image_by_id(id: str, session: SessionDep) -> FileResponse:
    image = session.get(FileMetadata, id)
    if not image:
        raise HTTPException(404, detail="image not found")
    _, ext = split_filename(image.original_filename)
    return FileResponse(path.join(get_settings().image_dir, f"{image.id}.{ext}"))
