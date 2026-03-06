from abc import ABC, abstractmethod
from typing import Generic, Optional, Sequence, TypeVar

from sqlalchemy import delete, select

from src.db import SessionDep, TransactionDep

ModelT = TypeVar("ModelT")
IdT = TypeVar("IdT")


class CRUDRepository(Generic[ModelT, IdT], ABC):
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

    def delete(self, obj: ModelT) -> None:
        with self.transaction:
            self.session.delete(obj)

    def update(self, obj: ModelT) -> ModelT:
        with self.transaction:
            self.session.merge(obj)
        return obj

    def delete_all(self) -> None:
        with self.transaction:
            self.session.execute(delete(self.model))
