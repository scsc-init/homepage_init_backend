from fastapi import APIRouter
from fastapi.responses import FileResponse

from src.dependencies import UserDep
from src.schemas import SCSCGlobalStatusResponse
from src.services import BodyUpdateSCSCGlobalStatus, SCSCServiceDep

scsc_router = APIRouter(tags=["scsc"])


@scsc_router.get("/scsc/global/status")
async def get_scsc_global_status(
    scsc_service: SCSCServiceDep,
) -> SCSCGlobalStatusResponse:
    scsc_global_status = scsc_service.get_global_status()
    return SCSCGlobalStatusResponse.model_validate(scsc_global_status)


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


@scsc_router.get("/executive/scsc/global/status/backup")
async def download_scsc_global_status_backup(
    current_user: UserDep,
    scsc_service: SCSCServiceDep,
) -> FileResponse:
    backup_path = scsc_service.backup_current_db(current_user)
    return FileResponse(
        path=backup_path,
        filename=backup_path.name,
        media_type="application/sql",
    )
