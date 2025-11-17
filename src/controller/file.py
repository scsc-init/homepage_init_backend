import os
from os import path
from typing import Annotated

from fastapi import Depends, File, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse

from src.core import get_settings, logger
from src.db import SessionDep
from src.model import FileMetadata, User
from src.util import create_uuid, split_filename, validate_and_read_file


class FileService:
    def __init__(
        self,
        session: SessionDep,
    ) -> None:
        self.session = session

    async def upload_file(
        self, current_user: User, file: UploadFile = File(...), request: Request
    ) -> FileMetadata:
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
        self.session.add(file_meta)
        try:
            self.session.commit()
        except Exception:
            self.session.rollback()
            try:
                os.remove(path.join(get_settings().file_dir, f"{uuid}.{ext}"))
            except OSError:
                logger.warning(
                    "warn_type=file_upload_cleanup_failed ; %s",
                    f"{uuid}.{ext}",
                    exc_info=True,
                )
            raise
        self.session.refresh(file_meta)
        return file_meta

    def get_docs_by_id(self, id: str) -> FileResponse:
        file_meta = self.session.get(FileMetadata, id)
        if not file_meta:
            raise HTTPException(404, detail="file not found")
        _, ext = split_filename(file_meta.original_filename)
        return FileResponse(path.join(get_settings().file_dir, f"{file_meta.id}.{ext}"))

    async def upload_image(
        self, current_user: User, file: UploadFile = File(...), request: Request
    ) -> FileMetadata:
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
        self.session.add(image)
        try:
            self.session.commit()
        except Exception:
            self.session.rollback()
            try:
                os.remove(path.join(get_settings().image_dir, f"{uuid}.{ext}"))
            except OSError:
                logger.warning(
                    "warn_type=image_upload_cleanup_failed ; %s",
                    f"{uuid}.{ext}",
                    exc_info=True,
                )
            raise
        self.session.refresh(image)
        return image

    def get_image_by_id(self, id: str) -> FileResponse:
        image = self.session.get(FileMetadata, id)
        if not image:
            raise HTTPException(404, detail="image not found")
        _, ext = split_filename(image.original_filename)
        return FileResponse(path.join(get_settings().image_dir, f"{image.id}.{ext}"))


FileServiceDep = Annotated[FileService, Depends()]
