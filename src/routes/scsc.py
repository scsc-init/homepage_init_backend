from fastapi import APIRouter, Depends
from pydantic import BaseModel

from src.db import SessionDep
from src.model import SCSCGlobalStatus, SCSCStatus
from src.util import get_scsc_global_status
from src.controller import update_scsc_global_status_controller


scsc_router = APIRouter(tags=['scsc'])


@scsc_router.get('/scsc/global/status')
async def _get_scsc_global_status(scsc_global_status: SCSCGlobalStatus = Depends(get_scsc_global_status)):
    return {'status': scsc_global_status.status}


class BodyUpdateSCSCGlobalStatus(BaseModel):
    status: SCSCStatus


@scsc_router.post('/executive/scsc/global/status', status_code=204)
async def update_scsc_global_status(body: BodyUpdateSCSCGlobalStatus, session: SessionDep, scsc_global_status: SCSCGlobalStatus = Depends(get_scsc_global_status)):
    return await update_scsc_global_status_controller(session, body.status, scsc_global_status)
