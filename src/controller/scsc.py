from fastapi import HTTPException
from sqlmodel import select

from src.db import SessionDep
from src.model import SIG, SCSCGlobalStatus, SCSCStatus


_valid_scsc_global_status_update = (
    (SCSCStatus.inactive, SCSCStatus.surveying),
    (SCSCStatus.surveying, SCSCStatus.recruiting),
    (SCSCStatus.recruiting, SCSCStatus.active),
    (SCSCStatus.surveying, SCSCStatus.inactive),
    (SCSCStatus.recruiting, SCSCStatus.inactive),
    (SCSCStatus.active, SCSCStatus.inactive),
)


def _check_valid_scsc_global_status_update(old_status: SCSCStatus, new_status: SCSCStatus) -> bool:
    for valid_update in _valid_scsc_global_status_update:
        if (old_status, new_status) == valid_update: return True
    return False


async def update_scsc_global_status_controller(session: SessionDep, status: SCSCStatus, scsc_global_status: SCSCGlobalStatus) -> None:
    if not _check_valid_scsc_global_status_update(scsc_global_status.status, status): raise HTTPException(400, "invalid sig global status update")
    if status == SCSCStatus.inactive:
        sigs = session.exec(select(SIG).where(SIG.status != SCSCStatus.inactive)).all()
        for sig in sigs:
            sig.status = SCSCStatus.inactive
            session.add(sig)
    elif status in (SCSCStatus.recruiting, SCSCStatus.active):
        sigs = session.exec(select(SIG).where(SIG.status == scsc_global_status.status)).all()
        for sig in sigs:
            sig.status = status
            session.add(sig)
    scsc_global_status.status = status
    session.add(scsc_global_status)
    session.commit()
    return
