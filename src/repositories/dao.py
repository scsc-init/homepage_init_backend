from abc import ABC
from typing import Any, Generic, Optional, Sequence, Type, TypeVar

from sqlalchemy import select

from src.db import SessionDep, TransactionDep

ModelT = TypeVar("ModelT")
IdT = TypeVar("IdT")


class DAO(Generic[ModelT, IdT], ABC):
    def __init__(
        self, session: SessionDep, transaction: TransactionDep, model: Type[ModelT]
    ):
        self.session = session
        self.transaction = transaction
        self.model = model

    def get_by_id(self, id: IdT) -> Optional[ModelT]:
        return self.session.get(self.model, id)

    def list_all(self) -> Sequence[ModelT]:
        stmt = select(self.model)
        return self.session.scalars(stmt).all()

    def list_by(self, **filters: Any) -> Sequence[ModelT]:
        stmt = select(self.model).where(**filters)
        return self.session.scalars(stmt).all()

    def create(self, obj: ModelT) -> ModelT:
        with self.transaction:
            self.session.add(obj)
        return obj

    def delete(self, obj: ModelT) -> None:
        with self.transaction:
            self.session.delete(obj)

    def update(self, obj: ModelT, **kwargs) -> ModelT:
        with self.transaction:
            for key, value in kwargs.items():
                setattr(obj, key, value)
        return obj
