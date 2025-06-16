from os import path

from fastapi import APIRouter, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse

from src.core import get_settings
from src.db import SessionDep
from src.model import FileMetadata
from src.util import create_uuid, get_file_extension, get_user

image_router = APIRouter(tags=['image'])


@image_router.post('/image/upload', status_code=201)
async def upload_image(session: SessionDep, request: Request, file: UploadFile) -> FileMetadata:
    current_user = get_user(request)
    if file.content_type is None or not file.content_type.startswith("image"): raise HTTPException(400, detail="cannot upload non-image file")
    ext_whitelist = ('jpg', 'jpeg', 'png')
    if file.filename is None or (ext := get_file_extension(file.filename)) not in ext_whitelist: raise HTTPException(400, detail=f"cannot upload if the extension is not {ext_whitelist}")
    content = await file.read()
    if len(content) > get_settings().image_max_size: raise HTTPException(413, detail=f"cannot upload image larger than {get_settings().image_max_size} bytes")

    uuid = create_uuid()
    with open(path.join(get_settings().image_dir, f"{uuid}.{ext}"), "wb") as fp:
        fp.write(content)

    image = FileMetadata(
        id=uuid,
        original_filename=file.filename,
        size=len(content),
        mime_type=file.content_type,
        owner=current_user.id
    )
    session.add(image)
    session.commit()
    session.refresh(image)
    return image


@image_router.get('/image/download/{id}')
async def get_sig_by_id(id: str, session: SessionDep) -> FileResponse:
    image = session.get(FileMetadata, id)
    if not image: raise HTTPException(404, detail="image not found")
    return FileResponse(path.join(get_settings().image_dir, f"{image.id}.{get_file_extension(image.original_filename)}"))
