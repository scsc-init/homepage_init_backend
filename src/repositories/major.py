from typing import Annotated

from fastapi import Depends

from src.model import Major

from .crud_repository import CRUDRepository


class MajorRepository(CRUDRepository[Major, int]):
    @property
    def model(self) -> type[Major]:
        return Major


MajorRepositoryDep = Annotated[MajorRepository, Depends()]
