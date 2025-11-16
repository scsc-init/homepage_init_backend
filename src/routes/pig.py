from fastapi import APIRouter

from src.controller import (
    BodyCreatePIG,
    BodyExecutiveJoinPIG,
    BodyExecutiveLeavePIG,
    BodyHandoverPIG,
    BodyUpdatePIG,
    PigServiceDep,
)
from src.util import SCSCGlobalStatusDep, UserDep

pig_router = APIRouter(tags=["pig"])


@pig_router.post("/pig/create", status_code=201)
async def create_pig(
    scsc_global_status: SCSCGlobalStatusDep,
    current_user: UserDep,
    body: BodyCreatePIG,
    pig_service: PigServiceDep,
):
    return await pig_service.create_pig(scsc_global_status, body, current_user)


@pig_router.get("/pig/{id}")
async def get_pig_by_id(id: int, pig_service: PigServiceDep):
    return pig_service.get_by_id(id)


@pig_router.get("/pigs")
async def get_all_pigs(pig_service: PigServiceDep):
    return pig_service.get_all()


@pig_router.post("/pig/{id}/update", status_code=204)
async def update_my_pig(
    id: int, current_user: UserDep, body: BodyUpdatePIG, pig_service: PigServiceDep
):
    await pig_service.update_pig(id, body, current_user, False)


@pig_router.post("/pig/{id}/delete", status_code=204)
async def delete_my_pig(id: int, current_user: UserDep, pig_service: PigServiceDep):
    await pig_service.delete_pig(id, current_user, False)


@pig_router.post("/executive/pig/{id}/update", status_code=204)
async def exec_update_pig(
    id: int, current_user: UserDep, body: BodyUpdatePIG, pig_service: PigServiceDep
):
    await pig_service.update_pig(id, body, current_user, True)


@pig_router.post("/executive/pig/{id}/delete", status_code=204)
async def exec_delete_pig(id: int, current_user: UserDep, pig_service: PigServiceDep):
    await pig_service.delete_pig(id, current_user, True)


@pig_router.post("/pig/{id}/handover", status_code=204)
async def handover_pig(
    id: int, current_user: UserDep, body: BodyHandoverPIG, pig_service: PigServiceDep
) -> None:
    pig_service.handover_pig(id, body, current_user, False)


@pig_router.post("/executive/pig/{id}/handover", status_code=204)
async def executive_handover_pig(
    id: int, current_user: UserDep, body: BodyHandoverPIG, pig_service: PigServiceDep
) -> None:
    pig_service.handover_pig(id, body, current_user, True)


@pig_router.get("/pig/{id}/members")
async def get_pig_members(id: int, pig_service: PigServiceDep) -> list:
    return pig_service.get_members(id)


@pig_router.post("/pig/{id}/member/join", status_code=204)
async def join_pig(id: int, current_user: UserDep, pig_service: PigServiceDep):
    await pig_service.join_pig(id, current_user)


@pig_router.post("/pig/{id}/member/leave", status_code=204)
async def leave_pig(id: int, current_user: UserDep, pig_service: PigServiceDep):
    await pig_service.leave_pig(id, current_user)


@pig_router.post("/executive/pig/{id}/member/join", status_code=204)
async def executive_join_pig(
    id: int,
    current_user: UserDep,
    body: BodyExecutiveJoinPIG,
    pig_service: PigServiceDep,
):
    await pig_service.executive_join_pig(id, current_user, body)


@pig_router.post("/executive/pig/{id}/member/leave", status_code=204)
async def executive_leave_pig(
    id: int,
    current_user: UserDep,
    body: BodyExecutiveLeavePIG,
    pig_service: PigServiceDep,
):
    await pig_service.executive_leave_pig(id, current_user, body)
