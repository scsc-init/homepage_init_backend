from typing import Annotated, Iterator

import sqlalchemy
from fastapi import Depends
from sqlalchemy import event, orm
from sqlalchemy.orm.session import Session

from src.core import get_settings
from src.util import SingletonMeta


class DBSessionFactory(metaclass=SingletonMeta):
    def __init__(self):
        self._sqlite_url = f"sqlite:///{get_settings().sqlite_filename}"
        self._engine: sqlalchemy.Engine = sqlalchemy.create_engine(
            self._sqlite_url, connect_args={"check_same_thread": False}
        )

        self._session_maker = orm.sessionmaker(
            bind=self._engine, expire_on_commit=False
        )

    def get_engine(self) -> sqlalchemy.Engine:
        return self._engine

    def make_session(self) -> Session:
        session = self._session_maker()
        return session

    def teardown(self):
        orm.close_all_sessions()
        self._engine.dispose()


engine = DBSessionFactory().get_engine()


@event.listens_for(engine, "connect")
def enable_sqlite_foreign_keys(dbapi_connection, connection_record):
    "Enable foreign keys in SQLite"
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


def get_session() -> Iterator[Session]:
    session = DBSessionFactory().make_session()
    try:
        yield session
    finally:
        session.commit()
        session.close()


SessionDep = Annotated[Session, Depends(get_session)]


class Transaction:
    """
    A context manager class for flushing changes to the database without committing
    the transaction. This class can be used to check for integrity errors before
    committing the transaction. The transaction is committed when the scope of each
    request is finished. See `get_session` for more details.
    """

    def __init__(self, session: SessionDep):
        self._session = session

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        if exc_type is not None:
            # rollback and let the exception propagate
            self._session.rollback()
            return False

        self._session.flush()
        return True


TransactionDep = Annotated[Transaction, Depends()]
