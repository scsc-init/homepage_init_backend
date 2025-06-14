from fastapi import HTTPException

from src.db import SessionDep
from src.model import SCSCGlobalStatus


def get_scsc_global_status(session: SessionDep) -> SCSCGlobalStatus:
    status = session.get(SCSCGlobalStatus, 1)
    if status is None: raise HTTPException(503, detail="scsc global status does not exist")
    return status
