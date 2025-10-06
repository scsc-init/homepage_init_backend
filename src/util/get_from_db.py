from functools import lru_cache
from typing import Annotated

from fastapi import Depends, HTTPException
from sqlmodel import select

from src.db import SessionDep, SessionLocal
from src.model import SCSCGlobalStatus, UserRole


@lru_cache
def get_user_role_level(role_name: str) -> int:
    """Return the numeric level for the given role name."""
    session = None
    try:
        session = SessionLocal()
        user_role = session.exec(
            select(UserRole).where(UserRole.name == role_name)
        ).first()
        if not user_role:
            raise HTTPException(
                400, f"Role '{role_name}' not found in the database.")
        return user_role.level
    finally:
        if session:
            session.close()


def _get_scsc_global_status(session: SessionDep) -> SCSCGlobalStatus:
    status = session.get(SCSCGlobalStatus, 1)
    if status is None:
        raise HTTPException(503, detail="scsc global status does not exist")
    return status


SCSCGlobalStatusDep = Annotated[SCSCGlobalStatus,
                                Depends(_get_scsc_global_status)]
