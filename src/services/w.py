import re
from os import name, path
from typing import Annotated, Sequence

import aiofiles
from aiofiles import os as aiofiles_os
from fastapi import Depends, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.exc import IntegrityError

from src.core import get_settings, logger
from src.model import User, WHTMLMetadata
from src.repositories import WRepositoryDep
from src.util import validate_and_read_file


class WService:
    def __init__(self, w_repository: WRepositoryDep) -> None:
        self.w_repository = w_repository

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
            w_meta = self.w_repository.create(w_meta)
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

    def _is_bot(self, user_agent: str) -> bool:
        bot_patterns = [
            r"googlebot",
            r"bingbot",
            r"slurp",
            r"duckduckbot",
            r"baiduspider",
            r"yandexbot",
            r"sogou",
            r"exabot",
            r"facebookexternalhit",
            r"twitterbot",
            r"linkedinbot",
            r"whatsapp",
            r"telegrambot",
            r"discordbot",
            r"slackbot",
            r"crawler",
            r"spider",
            r"bot",
        ]
        user_agent_lower = user_agent.lower()
        return any(re.search(pattern, user_agent_lower) for pattern in bot_patterns)

    def get_w_by_name(self, name: str) -> FileResponse:
        w_meta = self.w_repository.get_by_id(name)
        if not w_meta:
            raise HTTPException(404, detail="file not found")
        return FileResponse(
            path.join(get_settings().w_html_dir, f"{name}.html"),
            media_type="text/html",
            headers={"X-View-Count": str(w_meta.view_cnt)},
        )

    async def record_view(self, name: str, request: Request) -> None:
        w_meta = self.w_repository.get_by_id(name)
        if not w_meta:
            raise HTTPException(404, detail="file not found")

        user_agent = request.headers.get("X-Forwarded-User-Agent", "")
        if self._is_bot(user_agent):
            return
        try:
            self.w_repository.increase_view_count(name)
        except Exception:
            logger.error("err_type=w_view_increment_failed", exc_info=True)

    def get_all_metadata(self) -> Sequence[tuple[WHTMLMetadata, str]]:
        results = self.w_repository.get_all_with_creator_name()
        response_list: list[tuple[WHTMLMetadata, str]] = []
        for row in results:
            response_list.append(row._tuple())
        return response_list

    async def update_w_by_name(
        self, name: str, current_user: User, file: UploadFile
    ) -> WHTMLMetadata:
        w_meta = self.w_repository.get_by_id(name)
        if not w_meta:
            raise HTTPException(404, detail="file not found")

        content, _, _, _ = await validate_and_read_file(
            file, valid_mime_type="text/html", valid_ext=frozenset({"html"})
        )

        w_meta.size = len(content)
        w_meta.creator = current_user.id

        w_meta = self.w_repository.update(w_meta)

        async with aiofiles.open(
            path.join(get_settings().w_html_dir, f"{name}.html"), "wb"
        ) as fp:
            await fp.write(content)

        logger.info(
            f"info_type=w_html_updated ; {name=} ; file_size={len(content)} ; executer_id={current_user.id}"
        )
        return w_meta

    def download_w_by_name(self, name: str, current_user: User) -> FileResponse:
        w_meta = self.w_repository.get_by_id(name)
        if not w_meta:
            raise HTTPException(404, detail="file not found")
        file_path = path.join(get_settings().w_html_dir, f"{name}.html")
        if not path.isfile(file_path):
            raise HTTPException(404, detail="file not found")
        return FileResponse(
            file_path,
            media_type="text/html",
            filename=f"{name}.html",
        )

    async def delete_w_by_name(self, name: str, current_user: User) -> None:
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
