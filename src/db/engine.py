from typing import Annotated, Iterator

import sqlalchemy
from fastapi import Depends
from sqlalchemy import orm
from sqlalchemy.orm.session import Session

from src.core import get_settings
from src.util import SingletonMeta


class DBSessionFactory(metaclass=SingletonMeta):
    def __init__(self):
        settings = get_settings()
        # 1. PostgreSQL 연결 URL 구성 (psycopg2 드라이버 권장)
        self._psql_url = (
            f"postgresql://{settings.db_user}:{settings.db_password}@"
            f"db/{settings.db_name}"
        )

        self._engine: sqlalchemy.Engine = sqlalchemy.create_engine(
            self._psql_url,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,
        )

        self._session_maker = orm.sessionmaker(
            bind=self._engine, expire_on_commit=False
        )

    def get_engine(self) -> sqlalchemy.Engine:
        return self._engine

    def make_session(self) -> Session:
        return self._session_maker()

    def teardown(self):
        self._engine.dispose()


engine = DBSessionFactory().get_engine()


def get_session() -> Iterator[Session]:
    session = DBSessionFactory().make_session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
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
