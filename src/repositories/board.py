from typing import Annotated

from fastapi import Depends

from src.model import Board

from .dao import DAO


class BoardRepository(DAO[Board, int]): ...


BoardRepositoryDep = Annotated[BoardRepository, Depends()]
