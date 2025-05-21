from fastapi import HTTPException

from src.db import SessionDep
from src.model import PIGGlobalStatus, SIGGlobalStatus


def get_sig_global_status(session: SessionDep) -> SIGGlobalStatus:
    status = session.get(SIGGlobalStatus, 1)
    if status is None: raise HTTPException(503, detail="sig global status does not exist")
    return status


def get_pig_global_status(session: SessionDep) -> PIGGlobalStatus:
    status = session.get(PIGGlobalStatus, 1)
    if status is None: raise HTTPException(503, detail="pig global status does not exist")
    return status
