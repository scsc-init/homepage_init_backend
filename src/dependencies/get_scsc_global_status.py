from typing import Annotated

from fastapi import Depends, HTTPException

from src.model import SCSCGlobalStatus
from src.repositories import SCSCGlobalStatusRepositoryDep


def _get_scsc_global_status(
    scsc_global_status_repository: SCSCGlobalStatusRepositoryDep,
) -> SCSCGlobalStatus:
    status = scsc_global_status_repository.get_current_scsc_global_status()
    if status is None:
        raise HTTPException(503, detail="scsc global status does not exist")
    return status


SCSCGlobalStatusDep = Annotated[SCSCGlobalStatus, Depends(_get_scsc_global_status)]
