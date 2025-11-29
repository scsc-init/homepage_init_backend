from typing import Annotated

from fastapi import Depends
from sqlalchemy import select

from src.model import KeyValue

from .dao import CRUDRepository


class KeyValueRepository(CRUDRepository[KeyValue, str]):
    @property
    def model(self) -> type[KeyValue]:
        return KeyValue

    def get_kv_values_by_role(self, user_role: int):
        stmt = select(KeyValue).where(KeyValue.writing_permission_level <= user_role)
        return self.session.scalars(stmt).all()


KeyValueRepositoryDep = Annotated[KeyValueRepository, Depends()]
