import re
from os import path
from typing import Annotated, Sequence

import aiofiles
from aiofiles import os as aiofiles_os
from fastapi import Depends, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.exc import IntegrityError

from src.core import get_settings, logger
from src.model import User, WHTMLMetadata
from src.repositories import WRepositoryDep
from src.schemas import WHTMLMetadataWithCreatorResponse
from src.util import validate_and_read_file


class WService:
    def __init__(self, w_repo: WRepositoryDep) -> None:
        self.w_repo = w_repo

    async def upload_file(self, current_user: User, file: UploadFile) -> WHTMLMetadata:
        content, basename, _, _ = await validate_and_read_file(
            file, valid_mime_type="text/html", valid_ext=frozenset({"html"})
        )
        if not re.fullmatch(r"^[a-zA-Z0-9_-]+$", basename):
            raise HTTPException(
                400,
                detail="filename should consist of alphabets, numbers, underscores, and hyphens",
            )

        async with aiofiles.open(
            path.join(get_settings().w_html_dir, f"{basename}.html"), "wb"
        ) as fp:
            await fp.write(content)

        w_meta = WHTMLMetadata(
            name=basename, size=len(content), creator=current_user.id
        )

        try:
            w_meta = self.w_repo.create(w_meta)
        except IntegrityError as err:
            try:
                await aiofiles_os.remove(
                    path.join(get_settings().w_html_dir, f"{basename}.html")
                )
            except OSError:
                logger.warning(
                    "warn_type=w_html_create_cleanup_failed ; %s",
                    f"{basename}.html",
                    exc_info=True,
                )
            raise HTTPException(409, detail="unique field exists") from err

        logger.info(
            f"info_type=w_html_created ; {basename=} ; file_size={len(content)} ; executer_id={current_user.id}"
        )
        return w_meta

    def get_w_by_name(self, name: str) -> FileResponse:
        w_meta = self.w_repo.get_by_id(name)
        if not w_meta:
            raise HTTPException(404, detail="file not found")
        return FileResponse(
            path.join(get_settings().w_html_dir, f"{name}.html"),
            media_type="text/html",
        )

    def get_all_metadata(self) -> Sequence[tuple[WHTMLMetadata, str]]:
        results = self.w_repo.get_all_with_creator_name()
        response_list: list[tuple[WHTMLMetadata, str]] = []
        for row in results:
            response_list.append(row._tuple())
        return response_list

    async def update_w_by_name(
        self, name: str, current_user: User, file: UploadFile
    ) -> WHTMLMetadata:
        w_meta = self.w_repo.get_by_id(name)
        if not w_meta:
            raise HTTPException(404, detail="file not found")

        content, _, _, _ = await validate_and_read_file(
            file, valid_mime_type="text/html", valid_ext=frozenset({"html"})
        )

        w_meta.size = len(content)
        w_meta.creator = current_user.id

        w_meta = self.w_repo.update(w_meta)

        async with aiofiles.open(
            path.join(get_settings().w_html_dir, f"{name}.html"), "wb"
        ) as fp:
            await fp.write(content)

        logger.info(
            f"info_type=w_html_updated ; {name=} ; file_size={len(content)} ; executer_id={current_user.id}"
        )
        return w_meta

    async def delete_w_by_name(self, name: str, current_user: User) -> None:
        w_meta = self.w_repo.get_by_id(name)
        if not w_meta:
            raise HTTPException(404, detail="file not found")

        try:
            self.w_repo.delete(w_meta)
        except Exception:
            logger.error(
                f"err_type=delete_w_by_name ; {name=} ; msg=failed to remove file record from DB"
            )
            raise

        try:
            await aiofiles_os.remove(
                path.join(get_settings().w_html_dir, f"{name}.html")
            )
        except OSError:
            logger.error(
                f"err_type=delete_w_by_name ; {name=} ; executer_id={current_user.id} ; msg=failed to remove file from disk"
            )

        logger.info(
            f"info_type=w_html_deleted ; {name=} ; executer_id={current_user.id}"
        )


WServiceDep = Annotated[WService, Depends()]
