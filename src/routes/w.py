from os import path

from fastapi import APIRouter, HTTPException, Request, UploadFile, File
from fastapi.responses import FileResponse

from src.core import get_settings
from src.db import SessionDep
from src.model import WHTMLMetadata
from src.util import get_user

w_router = APIRouter(tags=['w'])


@w_router.post('/executive/w/create', status_code=201)
async def upload_file(session: SessionDep, request: Request, file: UploadFile = File(...)) -> WHTMLMetadata:
    if file.content_type is None or file.content_type != "text/html": raise HTTPException(400, detail="you can only upload file with mime type text/html")
    if file.filename is None or file.filename[-5:] != ".html": raise HTTPException(400, detail="cannot upload if the extension is not html")
    content = await file.read()
    if len(content) > get_settings().file_max_size: raise HTTPException(413, detail=f"cannot upload file larger than {get_settings().file_max_size} bytes")

    name = file.filename[:-5]
    with open(path.join(get_settings().w_html_dir, f"{file.filename}"), "wb") as fp:
        fp.write(content)

    current_user = get_user(request)
    w_meta = WHTMLMetadata(
        name=name,
        size=len(content),
        owner=current_user.id
    )
    session.add(w_meta)
    session.commit()
    session.refresh(w_meta)
    return w_meta


@w_router.get('/w/{name}')
async def get_w_by_name(name: str, session: SessionDep) -> FileResponse:
    w_meta = session.get(WHTMLMetadata, name)
    if not w_meta: raise HTTPException(404, detail="file not found")
    return FileResponse(path.join(get_settings().w_html_dir, f"{name}.html"))


@w_router.post('/executive/w/{name}/update', status_code=200)
async def update_w_by_name(name: str, session: SessionDep, request: Request, file: UploadFile = File(...)) -> WHTMLMetadata:
    w_meta = session.get(WHTMLMetadata, name)
    if not w_meta: raise HTTPException(404, detail="file not found")

    if file.content_type is None or file.content_type != "text/html": raise HTTPException(400, detail="you can only upload file with mime type text/html")
    if file.filename is None or file.filename[-5:] != ".html": raise HTTPException(400, detail="cannot upload if the extension is not html")
    content = await file.read()
    if len(content) > get_settings().file_max_size: raise HTTPException(413, detail=f"cannot upload file larger than {get_settings().file_max_size} bytes")

    with open(path.join(get_settings().w_html_dir, f"{name}.html"), "wb") as fp:
        fp.write(content)

    current_user = get_user(request)
    w_meta.size = len(content)
    w_meta.owner = current_user.id
    session.add(w_meta)
    session.commit()
    session.refresh(w_meta)
    return w_meta


@w_router.post('/executive/w/{name}/delete', status_code=204)
async def delete_w_by_name(name: str, session: SessionDep) -> FileResponse:
    w_meta = session.get(WHTMLMetadata, name)
    if not w_meta: raise HTTPException(404, detail="file not found")
    return FileResponse(path.join(get_settings().w_html_dir, f"{w_meta.name}.html"))
