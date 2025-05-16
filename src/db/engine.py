from typing import Annotated

from fastapi import Depends
from sqlalchemy import event
from sqlmodel import Session, create_engine

from src.core import get_settings

sqlite_url = f"sqlite:///{get_settings().sqlite_filename}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)


@event.listens_for(engine, "connect")
def enable_sqlite_foreign_keys(dbapi_connection, connection_record):
    "Enable foreign keys in SQLite"
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


def SessionLocal():
    return Session(autocommit=False, autoflush=False, bind=engine)


def get_session():
    with SessionLocal() as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
