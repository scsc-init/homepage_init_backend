from typing import Annotated

from fastapi import Depends

from src.model import Board

from .crud_repository import CRUDRepository


class BoardRepository(CRUDRepository[Board, int]):
    @property
    def model(self) -> type[Board]:
        return Board


BoardRepositoryDep = Annotated[BoardRepository, Depends()]
