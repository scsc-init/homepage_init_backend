import os
import re
from typing import Annotated, Sequence

import aiofiles
from aiofiles import os as aiofiles_os
from fastapi import Depends, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.exc import IntegrityError

from src.core import get_settings, logger
from src.model import User, WHTMLMetadata
from src.repositories import WRepositoryDep
from src.util import validate_and_read_file


class WService:
    def __init__(self, w_repository: WRepositoryDep) -> None:
        self.w_repository = w_repository

    async def upload_file(
        self, current_user: User, file: UploadFile, name: str | None = None
    ) -> WHTMLMetadata:
        content, basename, _, _ = await validate_and_read_file(
            file, valid_mime_type="text/html", valid_ext=frozenset({"html"})
        )
        basename = self._normalize_name(name or basename)
        file_path = self._build_file_path(basename)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        async with aiofiles.open(file_path, "wb") as fp:
            await fp.write(content)

        w_meta = WHTMLMetadata(
            name=basename, size=len(content), creator=current_user.id
        )

        try:
            w_meta = self.w_repository.create(w_meta)
        except IntegrityError as err:
            try:
                await aiofiles_os.remove(file_path)
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
        name = self._normalize_name(name)
        w_meta = self.w_repository.get_by_id(name)
        if not w_meta:
            raise HTTPException(404, detail="file not found")
        file_path = self._build_file_path(name)
        if not os.path.isfile(file_path):
            raise HTTPException(404, detail="file not found")
        return FileResponse(
            file_path,
            media_type="text/html",
        )

    def get_all_metadata(self) -> Sequence[tuple[WHTMLMetadata, str]]:
        results = self.w_repository.get_all_with_creator_name()
        response_list: list[tuple[WHTMLMetadata, str]] = []
        for row in results:
            response_list.append(row._tuple())
        return response_list

    async def update_w_by_name(
        self, name: str, current_user: User, file: UploadFile
    ) -> WHTMLMetadata:
        name = self._normalize_name(name)
        w_meta = self.w_repository.get_by_id(name)
        if not w_meta:
            raise HTTPException(404, detail="file not found")

        content, _, _, _ = await validate_and_read_file(
            file, valid_mime_type="text/html", valid_ext=frozenset({"html"})
        )

        w_meta.size = len(content)
        w_meta.creator = current_user.id

        w_meta = self.w_repository.update(w_meta)

        file_path = self._build_file_path(name)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        async with aiofiles.open(file_path, "wb") as fp:
            await fp.write(content)

        logger.info(
            f"info_type=w_html_updated ; {name=} ; file_size={len(content)} ; executer_id={current_user.id}"
        )
        return w_meta

    def download_w_by_name(self, name: str, current_user: User) -> FileResponse:
        name = self._normalize_name(name)
        w_meta = self.w_repository.get_by_id(name)
        if not w_meta:
            raise HTTPException(404, detail="file not found")
        file_path = self._build_file_path(name)
        if not os.path.isfile(file_path):
            raise HTTPException(404, detail="file not found")
        return FileResponse(
            file_path,
            media_type="text/html",
            filename=f"{name.replace('/', '__')}.html",
        )

    async def delete_w_by_name(self, name: str, current_user: User) -> None:
        name = self._normalize_name(name)
        w_meta = self.w_repository.get_by_id(name)
        if not w_meta:
            raise HTTPException(404, detail="file not found")

        try:
            self.w_repository.delete(w_meta)
        except Exception:
            logger.error(
                f"err_type=delete_w_by_name ; {name=} ; msg=failed to remove file record from DB"
            )
            raise

        try:
            await aiofiles_os.remove(self._build_file_path(name))
        except OSError:
            logger.error(
                f"err_type=delete_w_by_name ; {name=} ; executer_id={current_user.id} ; msg=failed to remove file from disk"
            )

        logger.info(
            f"info_type=w_html_deleted ; {name=} ; executer_id={current_user.id}"
        )

    def _normalize_name(self, raw_name: str) -> str:
        normalized = raw_name.strip().replace("\\", "/")
        if normalized.endswith(".html"):
            normalized = normalized[:-5]
        if not normalized:
            raise HTTPException(400, detail="name cannot be empty")
        if normalized.startswith("/") or normalized.endswith("/"):
            raise HTTPException(400, detail="name cannot start or end with slash")

        segments = normalized.split("/")
        if any(segment in {"", ".", ".."} for segment in segments):
            raise HTTPException(400, detail="invalid path segment")
        if any(not re.fullmatch(r"[a-zA-Z0-9_-]+", segment) for segment in segments):
            raise HTTPException(
                400,
                detail="name segments should consist of alphabets, numbers, underscores, and hyphens",
            )
        return "/".join(segments)

    def _build_file_path(self, name: str) -> str:
        root = os.path.abspath(get_settings().w_html_dir)
        target = os.path.abspath(os.path.join(root, *name.split("/")) + ".html")
        if os.path.commonpath([root, target]) != root:
            raise HTTPException(400, detail="invalid file path")
        return target


WServiceDep = Annotated[WService, Depends()]
