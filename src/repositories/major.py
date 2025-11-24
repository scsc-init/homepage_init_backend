from typing import Annotated

from fastapi import Depends

from src.model import Major

from .dao import DAO


class MajorRepository(DAO[Major, int]):
    @property
    def model(self) -> type[Major]:
        return Major


MajorRepositoryDep = Annotated[MajorRepository, Depends()]
