from fastapi import APIRouter

from src.controller import BodyUpdateSCSCGlobalStatus, SCSCServiceDep
from src.dependencies import UserDep
from src.model import SCSCGlobalStatus

scsc_router = APIRouter(tags=["scsc"])


@scsc_router.get("/scsc/global/status")
async def get_scsc_global_status(
    scsc_service: SCSCServiceDep,
) -> SCSCGlobalStatus:
    return scsc_service.get_global_status()


@scsc_router.get("/scsc/global/statuses")
async def get_scsc_global_statuses(
    scsc_service: SCSCServiceDep,
) -> dict[str, list[str]]:
    return scsc_service.get_all_statuses()


@scsc_router.post("/executive/scsc/global/status", status_code=204)
async def update_scsc_global_status(
    current_user: UserDep,
    body: BodyUpdateSCSCGlobalStatus,
    scsc_service: SCSCServiceDep,
):
    await scsc_service.update_global_status(current_user.id, body.status)
