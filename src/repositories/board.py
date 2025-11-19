from typing import Annotated

from fastapi import Depends

from src.model import Board

from .dao import DAO


class BoardRepository(DAO[Board, int]):
    @property
    def model(self) -> type[Board]:
        return Board


BoardRepositoryDep = Annotated[BoardRepository, Depends()]
