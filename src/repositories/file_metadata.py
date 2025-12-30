from typing import Annotated

from fastapi import Depends

from src.model import FileMetadata

from .crud_repository import CRUDRepository


class FileMetadataRepository(CRUDRepository[FileMetadata, str]):
    @property
    def model(self) -> type[FileMetadata]:
        return FileMetadata


FileMetadataRepositoryDep = Annotated[FileMetadataRepository, Depends()]
