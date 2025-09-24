import logging
import os
import re
from os import path
from typing import Sequence

from fastapi import APIRouter, File, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from src.core import get_settings
from src.db import SessionDep
from src.model import WHTMLMetadata, User
from src.util import get_user

logger = logging.getLogger("app")

w_router = APIRouter(tags=['w'])


@w_router.post('/executive/w/create', status_code=201)
async def upload_file(session: SessionDep, request: Request, file: UploadFile = File(...)) -> WHTMLMetadata:
    if file.content_type is None or not file.content_type.startswith("text/html"): raise HTTPException(400, detail="you can only upload file with mime type text/html")
    if file.filename is None or file.filename[-5:] != ".html": raise HTTPException(400, detail="cannot upload if the extension is not html")
    if not re.fullmatch(r'^[a-zA-Z0-9_-]+$', file.filename[:-5]): raise HTTPException(400, detail="filename should consist of alphabets, numbers, underscores, and hyphens")
    content = await file.read()
    if (file_size := len(content)) > get_settings().file_max_size: raise HTTPException(413, detail=f"cannot upload file larger than {get_settings().file_max_size} bytes")

    name = file.filename[:-5]
    with open(path.join(get_settings().w_html_dir, f"{file.filename}"), "wb") as fp:
        fp.write(content)

    current_user = get_user(request)
    w_meta = WHTMLMetadata(
        name=name,
        size=file_size,
        creator=current_user.id
    )
    session.add(w_meta)
    try: session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(409, detail="unique field exists")
    session.refresh(w_meta)
    logger.info(f'info_type=w_html_created ; {name=} ; {file_size=} ; executer_id={current_user.id}')
    return w_meta


@w_router.get('/w/{name}')
async def get_w_by_name(name: str, session: SessionDep) -> FileResponse:
    w_meta = session.get(WHTMLMetadata, name)
    if not w_meta: raise HTTPException(404, detail="file not found")
    return FileResponse(path.join(get_settings().w_html_dir, f"{name}.html"), media_type="text/html")


@w_router.get('/executive/ws')
async def get_all_metadata(session: SessionDep) -> Sequence[tuple[WHTMLMetadata, str]]:
    return session.exec(select(WHTMLMetadata, User.name).where(WHTMLMetadata.creator == User.id)).all()


@w_router.post('/executive/w/{name}/update', status_code=200)
async def update_w_by_name(name: str, session: SessionDep, request: Request, file: UploadFile = File(...)) -> WHTMLMetadata:
    w_meta = session.get(WHTMLMetadata, name)
    if not w_meta: raise HTTPException(404, detail="file not found")

    if file.content_type is None or file.content_type != "text/html": raise HTTPException(400, detail="you can only upload file with mime type text/html")
    if file.filename is None or file.filename[-5:] != ".html": raise HTTPException(400, detail="cannot upload if the extension is not html")
    content = await file.read()
    if (file_size := len(content)) > get_settings().file_max_size: raise HTTPException(413, detail=f"cannot upload file larger than {get_settings().file_max_size} bytes")

    with open(path.join(get_settings().w_html_dir, f"{name}.html"), "wb") as fp:
        fp.write(content)

    current_user = get_user(request)
    w_meta.size = file_size
    w_meta.creator = current_user.id
    session.commit()
    session.refresh(w_meta)
    logger.info(f'info_type=w_html_updated ; {name=} ; {file_size=} ; executer_id={current_user.id}')
    return w_meta


@w_router.post('/executive/w/{name}/delete', status_code=204)
async def delete_w_by_name(name: str, session: SessionDep, request: Request) -> None:
    w_meta = session.get(WHTMLMetadata, name)
    if not w_meta: raise HTTPException(404, detail="file not found")
    try: os.remove(path.join(get_settings().w_html_dir, f"{name}.html"))
    except OSError: pass
    session.delete(w_meta)
    session.commit()
    current_user = get_user(request)
    logger.info(f'info_type=w_html_deleted ; {name=} ; executer_id={current_user.id}')
    return
