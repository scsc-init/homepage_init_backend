from typing import Annotated
from fastapi import Depends
from sqlmodel import Session, create_engine


sqlite_file_name = "scsc_init.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)

def SessionLocal():
    return Session(autocommit=False, autoflush=False, bind=engine)

def get_session():
    with SessionLocal() as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]