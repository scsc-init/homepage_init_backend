import os
from os import path
from typing import Annotated, Sequence

from fastapi import Depends, File, HTTPException, UploadFile
from fastapi.responses import FileResponse

from src.core import get_settings, logger
from src.model import FileMetadata, User
from src.repositories import FileMetadataRepositoryDep
from src.util import create_uuid, split_filename, validate_and_read_file


class FileService:
    def __init__(
        self,
        file_metadata_repository: FileMetadataRepositoryDep,
    ) -> None:
        self.file_metadata_repository = file_metadata_repository

    def _attach_public_url(
        self, metadata: FileMetadata, *, is_image: bool | None = None
    ) -> None:
        base_url = get_settings().public_base_url.rstrip("/")
        if not base_url:
            return

        if is_image is None:
            mime_type = (metadata.mime_type or "").lower()
            is_image = mime_type.startswith("image/")

        endpoint = (
            f"/file/image/download/{metadata.id}"
            if is_image
            else f"/file/docs/download/{metadata.id}"
        )
        setattr(metadata, "url", f"{base_url}{endpoint}")

    async def upload_file(
        self, current_user: User, file: UploadFile = File(...)
    ) -> FileMetadata:
        settings = get_settings()
        content, basename, ext, mime_type = await validate_and_read_file(
            file, valid_ext=frozenset({"pdf", "docx", "pptx"})
        )
        uuid = create_uuid()
        with open(path.join(settings.file_dir, f"{uuid}.{ext}"), "wb") as fp:
            fp.write(content)

        file_meta = FileMetadata(
            id=uuid,
            original_filename=f"{basename}.{ext}",
            size=len(content),
            mime_type=mime_type,
            owner=current_user.id,
        )

        try:
            file_meta = self.file_metadata_repository.create(file_meta)
        except Exception:
            try:
                os.remove(path.join(settings.file_dir, f"{uuid}.{ext}"))
            except OSError:
                logger.warning(
                    "warn_type=file_upload_cleanup_failed ; %s",
                    f"{uuid}.{ext}",
                    exc_info=True,
                )
            raise

        self._attach_public_url(file_meta, is_image=False)
        return file_meta

    def get_docs_by_id(self, id: str) -> FileResponse:
        file_meta = self.file_metadata_repository.get_by_id(id)
        if not file_meta:
            raise HTTPException(404, detail="file not found")
        _, ext = split_filename(file_meta.original_filename)
        return FileResponse(path.join(get_settings().file_dir, f"{file_meta.id}.{ext}"))

    async def upload_image(
        self, current_user: User, file: UploadFile = File(...)
    ) -> FileMetadata:
        settings = get_settings()
        content, basename, ext, mime_type = await validate_and_read_file(
            file,
            valid_mime_type="image/",
            valid_ext=frozenset({"jpg", "jpeg", "png", "svg", "gif", "webp"}),
        )

        uuid = create_uuid()
        with open(path.join(settings.image_dir, f"{uuid}.{ext}"), "wb") as fp:
            fp.write(content)

        image = FileMetadata(
            id=uuid,
            original_filename=f"{basename}.{ext}",
            size=len(content),
            mime_type=mime_type,
            owner=current_user.id,
        )
        try:
            image = self.file_metadata_repository.create(image)
        except Exception:
            try:
                os.remove(path.join(settings.image_dir, f"{uuid}.{ext}"))
            except OSError:
                logger.warning(
                    "warn_type=image_upload_cleanup_failed ; %s",
                    f"{uuid}.{ext}",
                    exc_info=True,
                )
            raise

        self._attach_public_url(image, is_image=True)
        return image

    def get_image_by_id(self, id: str) -> FileResponse:
        image = self.file_metadata_repository.get_by_id(id)
        if not image:
            raise HTTPException(404, detail="image not found")
        _, ext = split_filename(image.original_filename)
        return FileResponse(path.join(get_settings().image_dir, f"{image.id}.{ext}"))

    def get_metadata_by_ids(self, ids: Sequence[str]) -> list[FileMetadata]:
        if not ids:
            return []
        normalized = [i for i in ids if isinstance(i, str) and i]
        if not normalized:
            return []
        records = self.file_metadata_repository.get_by_ids(normalized)
        for record in records:
            self._attach_public_url(record)
        record_map = {record.id: record for record in records}
        return [record_map[i] for i in normalized if i in record_map]


FileServiceDep = Annotated[FileService, Depends()]
