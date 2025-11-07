from fastapi import APIRouter, Request

from src.controller import (
    BodyCreatePIG,
    BodyUpdatePIG,
    PigServiceDep,
)
from src.util import get_user

pig_router = APIRouter(tags=["pig"])


@pig_router.post("/create", status_code=201)
async def create_pig(
    request: Request,
    body: BodyCreatePIG,
    pig_service: PigServiceDep,
):
    current_user = get_user(request)
    return await pig_service.create_pig(body, current_user)


@pig_router.get("/{id}")
async def get_pig_by_id(id: int, pig_service: PigServiceDep):
    return pig_service.get_by_id(id)


@pig_router.get("s")
async def get_all_pigs(pig_service: PigServiceDep):
    return pig_service.get_all()


@pig_router.post("/{id}/update", status_code=204)
async def update_my_pig(
    id: int, request: Request, body: BodyUpdatePIG, pig_service: PigServiceDep
):
    current_user = get_user(request)
    await pig_service.update_pig(id, body, current_user, False)


@pig_router.post("/{id}/delete", status_code=204)
async def delete_my_pig(id: int, request: Request, pig_service: PigServiceDep):
    current_user = get_user(request)
    await pig_service.delete_pig(id, current_user, False)


@pig_router.post("/executive/{id}/update", status_code=204)
async def exec_update_pig(
    id: int, request: Request, body: BodyUpdatePIG, pig_service: PigServiceDep
):
    current_user = get_user(request)
    await pig_service.update_pig(id, body, current_user, True)


@pig_router.post("/executive/{id}/delete", status_code=204)
async def exec_delete_pig(id: int, request: Request, pig_service: PigServiceDep):
    current_user = get_user(request)
    await pig_service.delete_pig(id, current_user, True)
