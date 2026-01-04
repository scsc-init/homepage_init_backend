from typing import Annotated, Sequence

from fastapi import Depends
from sqlalchemy import select

from src.model import FileMetadata

from .crud_repository import CRUDRepository


class FileMetadataRepository(CRUDRepository[FileMetadata, str]):
    @property
    def model(self) -> type[FileMetadata]:
        return FileMetadata

    def get_by_ids(self, ids: Sequence[str]) -> list[FileMetadata]:
        if not ids:
            return []
        stmt = select(FileMetadata).where(FileMetadata.id.in_(ids))
        return self.session.scalars(stmt).all()


FileMetadataRepositoryDep = Annotated[FileMetadataRepository, Depends()]
