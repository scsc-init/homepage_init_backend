from abc import ABC, abstractmethod
from typing import Any, Generic, Optional, Sequence, Type, TypeVar

from sqlalchemy import select

from src.db import SessionDep, TransactionDep

ModelT = TypeVar("ModelT")
IdT = TypeVar("IdT")


class DAO(Generic[ModelT, IdT], ABC):
    def __init__(self, session: SessionDep, transaction: TransactionDep):
        self.session = session
        self.transaction = transaction

    @property
    @abstractmethod
    def model(self) -> type[ModelT]:
        """Return the SQLAlchemy ORM model class managed by this DAO."""
        raise NotImplementedError

    def get_by_id(self, id: IdT) -> Optional[ModelT]:
        return self.session.get(self.model, id)

    def list_all(self) -> Sequence[ModelT]:
        stmt = select(self.model)
        return self.session.scalars(stmt).all()

    def create(self, obj: ModelT) -> ModelT:
        with self.transaction:
            self.session.add(obj)
        return obj

    def delete_by_id(self, id: IdT) -> None:
        obj = self.get_by_id(id)
        with self.transaction:
            self.session.delete(obj)

    def update(self, obj: ModelT) -> ModelT:
        with self.transaction:
            self.session.merge(obj)
        return obj
