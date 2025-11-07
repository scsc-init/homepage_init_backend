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
from src.model import User, WHTMLMetadata
from src.util import get_user, validate_and_read_file

logger = logging.getLogger("app")

w_router = APIRouter(tags=["w"])


@w_router.post("/executive/w/create", status_code=201)
async def upload_file(
    session: SessionDep, request: Request, file: UploadFile = File(...)
) -> WHTMLMetadata:
    content, basename, _, _ = await validate_and_read_file(
        file, valid_mime_type="text/html", valid_ext=frozenset({"html"})
    )
    if not re.fullmatch(r"^[a-zA-Z0-9_-]+$", basename):
        raise HTTPException(
            400,
            detail="filename should consist of alphabets, numbers, underscores, and hyphens",
        )

    with open(path.join(get_settings().w_html_dir, f"{file.filename}"), "wb") as fp:
        fp.write(content)

    current_user = get_user(request)
    w_meta = WHTMLMetadata(name=basename, size=len(content), creator=current_user.id)
    session.add(w_meta)
    try:
        session.commit()
    except IntegrityError as err:
        session.rollback()
        try:
            os.remove(path.join(get_settings().w_html_dir, f"{basename}.html"))
        except OSError:
            logger.warning(
                "warn_type=w_html_create_cleanup_failed ; %s",
                f"{basename}.html",
                exc_info=True,
            )
        raise HTTPException(409, detail="unique field exists") from err
    session.refresh(w_meta)
    logger.info(
        f"info_type=w_html_created ; {basename=} ; file_size={len(content)} ; executer_id={current_user.id}"
    )
    return w_meta


@w_router.get("/w/{name}")
async def get_w_by_name(name: str, session: SessionDep) -> FileResponse:
    w_meta = session.get(WHTMLMetadata, name)
    if not w_meta:
        raise HTTPException(404, detail="file not found")
    return FileResponse(
        path.join(get_settings().w_html_dir, f"{name}.html"), media_type="text/html"
    )


@w_router.get("/executive/ws")
async def get_all_metadata(session: SessionDep) -> Sequence[tuple[WHTMLMetadata, str]]:
    return session.exec(
        select(WHTMLMetadata, User.name).where(WHTMLMetadata.creator == User.id)
    ).all()


@w_router.post("/executive/w/{name}/update", status_code=200)
async def update_w_by_name(
    name: str, session: SessionDep, request: Request, file: UploadFile = File(...)
) -> WHTMLMetadata:
    w_meta = session.get(WHTMLMetadata, name)
    if not w_meta:
        raise HTTPException(404, detail="file not found")
    content, _, _, _ = await validate_and_read_file(
        file, valid_mime_type="text/html", valid_ext=frozenset({"html"})
    )

    with open(path.join(get_settings().w_html_dir, f"{name}.html"), "wb") as fp:
        fp.write(content)

    current_user = get_user(request)
    w_meta.size = len(content)
    w_meta.creator = current_user.id
    session.commit()
    session.refresh(w_meta)
    logger.info(
        f"info_type=w_html_updated ; {name=} ; file_size={len(content)} ; executer_id={current_user.id}"
    )
    return w_meta


@w_router.post("/executive/w/{name}/delete", status_code=204)
async def delete_w_by_name(name: str, session: SessionDep, request: Request) -> None:
    w_meta = session.get(WHTMLMetadata, name)
    if not w_meta:
        raise HTTPException(404, detail="file not found")
    session.delete(w_meta)
    session.commit()
    current_user = get_user(request)
    try:
        os.remove(path.join(get_settings().w_html_dir, f"{name}.html"))
    except OSError:
        logger.error(
            f"err_type=delete_w_by_name ; {name=} ; executer_id={current_user.id} ; msg=failed to remove file from disk"
        )
    logger.info(f"info_type=w_html_deleted ; {name=} ; executer_id={current_user.id}")
    return
