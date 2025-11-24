from typing import Annotated

from fastapi import Depends

from src.model import KeyValue

from .dao import DAO


class KeyValueRepository(DAO[KeyValue, str]):
    @property
    def model(self) -> type[KeyValue]:
        return KeyValue


KeyValueRepositoryDep = Annotated[KeyValueRepository, Depends()]
