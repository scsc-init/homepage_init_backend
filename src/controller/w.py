import os
import re
from os import path
from typing import Annotated, Sequence

from fastapi import Depends, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from src.core import get_settings, logger
from src.db import SessionDep
from src.model import User, WHTMLMetadata
from src.util import validate_and_read_file


class WService:
    def __init__(
        self,
        session: SessionDep,
    ) -> None:
        self.session = session

    async def upload_file(self, file: UploadFile, current_user: User) -> WHTMLMetadata:
        content, basename, _, _ = await validate_and_read_file(
            file, valid_mime_type="text/html", valid_ext=frozenset({"html"})
        )
        if not re.fullmatch(r"^[a-zA-Z0-9_-]+$", basename):
            raise HTTPException(
                400,
                detail="filename should consist of alphabets, numbers, underscores, and hyphens",
            )

        with open(path.join(get_settings().w_html_dir, f"{basename}.html"), "wb") as fp:
            fp.write(content)

        w_meta = WHTMLMetadata(
            name=basename, size=len(content), creator=current_user.id
        )
        self.session.add(w_meta)
        try:
            self.session.commit()
        except IntegrityError as err:
            self.session.rollback()
            try:
                os.remove(path.join(get_settings().w_html_dir, f"{basename}.html"))
            except OSError:
                logger.warning(
                    "warn_type=w_html_create_cleanup_failed ; %s",
                    f"{basename}.html",
                    exc_info=True,
                )
            raise HTTPException(409, detail="unique field exists") from err
        self.session.refresh(w_meta)
        logger.info(
            f"info_type=w_html_created ; {basename=} ; file_size={len(content)} ; executer_id={current_user.id}"
        )
        return w_meta

    def get_w_by_name(self, name: str) -> FileResponse:
        w_meta = self.session.get(WHTMLMetadata, name)
        if not w_meta:
            raise HTTPException(404, detail="file not found")
        return FileResponse(
            path.join(get_settings().w_html_dir, f"{name}.html"), media_type="text/html"
        )

    def get_all_metadata(self) -> Sequence[tuple[WHTMLMetadata, str]]:
        return self.session.exec(
            select(WHTMLMetadata, User.name).where(WHTMLMetadata.creator == User.id)
        ).all()

    async def update_w_by_name(
        self, name: str, file: UploadFile, current_user: User
    ) -> WHTMLMetadata:
        w_meta = self.session.get(WHTMLMetadata, name)
        if not w_meta:
            raise HTTPException(404, detail="file not found")
        content, _, _, _ = await validate_and_read_file(
            file, valid_mime_type="text/html", valid_ext=frozenset({"html"})
        )

        w_meta.size = len(content)
        w_meta.creator = current_user.id
        self.session.commit()
        self.session.refresh(w_meta)

        with open(path.join(get_settings().w_html_dir, f"{name}.html"), "wb") as fp:
            fp.write(content)

        logger.info(
            f"info_type=w_html_updated ; {name=} ; file_size={len(content)} ; executer_id={current_user.id}"
        )
        return w_meta

    def delete_w_by_name(self, name: str, current_user: User) -> None:
        w_meta = self.session.get(WHTMLMetadata, name)
        if not w_meta:
            raise HTTPException(404, detail="file not found")
        self.session.delete(w_meta)
        try:
            self.session.commit()
        except Exception:
            self.session.rollback()
            logger.error(
                f"err_type=delete_w_by_name ; {name=} ; msg=failed to remove file"
            )
            raise
        try:
            os.remove(path.join(get_settings().w_html_dir, f"{name}.html"))
        except OSError:
            logger.error(
                f"err_type=delete_w_by_name ; {name=} ; executer_id={current_user.id} ; msg=failed to remove file from disk"
            )
        logger.info(
            f"info_type=w_html_deleted ; {name=} ; executer_id={current_user.id}"
        )
        return


WServiceDep = Annotated[WService, Depends()]
