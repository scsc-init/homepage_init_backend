from os import path

from fastapi import APIRouter, HTTPException, Request, UploadFile, File
from fastapi.responses import FileResponse

from src.core import get_settings
from src.db import SessionDep
from src.model import FileMetadata
from src.util import create_uuid, get_file_extension, get_user

file_router = APIRouter(tags=['file'])


@file_router.post('/file/upload', status_code=201)
async def upload_file(session: SessionDep, request: Request, file: UploadFile = File(...)) -> FileMetadata:
    current_user = get_user(request)
    if file.content_type is None: raise HTTPException(400, detail="cannot upload file without content_type")
    ext_whitelist = ('pdf', 'docx', 'pptx')
    if file.filename is None or (ext := get_file_extension(file.filename)) not in ext_whitelist: raise HTTPException(400, detail=f"cannot upload if the extension is not {ext_whitelist}")
    content = await file.read()
    if len(content) > get_settings().file_max_size: raise HTTPException(413, detail=f"cannot upload file larger than {get_settings().file_max_size} bytes")

    uuid = create_uuid()
    with open(path.join(get_settings().file_dir, f"{uuid}.{ext}"), "wb") as fp:
        fp.write(content)

    file_meta = FileMetadata(
        id=uuid,
        original_filename=file.filename,
        size=len(content),
        mime_type=file.content_type,
        owner=current_user.id
    )
    session.add(file_meta)
    session.commit()
    session.refresh(file_meta)
    return file_meta


@file_router.get('/file/download/{id}')
async def get_sig_by_id(id: str, session: SessionDep) -> FileResponse:
    file_meta = session.get(FileMetadata, id)
    if not file_meta: raise HTTPException(404, detail="file not found")
    return FileResponse(path.join(get_settings().file_dir, f"{file_meta.id}.{get_file_extension(file_meta.original_filename)}"))
