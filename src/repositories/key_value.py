from typing import Annotated, Optional

from fastapi import Depends
from sqlalchemy import select

from src.model import KeyValue

from .crud_repository import CRUDRepository


class KeyValueRepository(CRUDRepository[KeyValue, str]):
    @property
    def model(self) -> type[KeyValue]:
        return KeyValue

    def get_kv_values_by_role(self, keys: Optional[list[str]], user_role: int):
        stmt = select(KeyValue).where(KeyValue.writing_permission_level <= user_role)
        if keys:
            stmt = stmt.where(KeyValue.key.in_(keys))
        return self.session.scalars(stmt).all()


KeyValueRepositoryDep = Annotated[KeyValueRepository, Depends()]
