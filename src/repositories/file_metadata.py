from typing import Annotated

from fastapi import Depends

from src.model import FileMetadata

from .dao import CRUDRepository


class FileMetadataRepository(CRUDRepository[FileMetadata, str]):
    @property
    def model(self) -> type[FileMetadata]:
        return FileMetadata


FileMetadataRepositoryDep = Annotated[FileMetadataRepository, Depends()]
