from fastapi import APIRouter
from pydantic import BaseModel

from src.db import SessionDep
from src.model import SCSCStatus, SCSCGlobalStatus
from src.util import SCSCGlobalStatusDep
from src.controller import update_scsc_global_status_ctrl


scsc_router = APIRouter(tags=['scsc'])


@scsc_router.get('/scsc/global/status')
async def _get_scsc_global_status(scsc_global_status: SCSCGlobalStatusDep) -> SCSCGlobalStatus:
    return scsc_global_status


@scsc_router.get('/scsc/global/statuses')
async def _get_scsc_global_statuses() -> dict[str, list[str]]:
    return {"statuses": ["surveying", "recruiting", "active", "inactive"]}


class BodyUpdateSCSCGlobalStatus(BaseModel):
    status: SCSCStatus


@scsc_router.post('/executive/scsc/global/status', status_code=204)
async def update_scsc_global_status(session: SessionDep, scsc_global_status: SCSCGlobalStatusDep, body: BodyUpdateSCSCGlobalStatus):
    return await update_scsc_global_status_ctrl(session, body.status, scsc_global_status)
