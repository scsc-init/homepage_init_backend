from fastapi import APIRouter, Request

from src.controller import (
    BodyCreateSIG,
    BodyUpdateSIG,
    SigServiceDep,
)
from src.util import get_user

sig_router = APIRouter(tags=["sig"])


@sig_router.post("/create", status_code=201)
async def create_sig(
    request: Request,
    body: BodyCreateSIG,
    sig_service: SigServiceDep,
):
    current_user = get_user(request)
    return await sig_service.create_sig(body, current_user)


@sig_router.get("/{id}")
async def get_sig_by_id(id: int, sig_service: SigServiceDep):
    return sig_service.get_by_id(id)


@sig_router.get("s")
async def get_all_sigs(sig_service: SigServiceDep):
    return sig_service.get_all()


@sig_router.post("/{id}/update", status_code=204)
async def update_my_sig(
    id: int, request: Request, body: BodyUpdateSIG, sig_service: SigServiceDep
):
    current_user = get_user(request)
    await sig_service.update_sig(id, body, current_user, False)


@sig_router.post("/{id}/delete", status_code=204)
async def delete_my_sig(id: int, request: Request, sig_service: SigServiceDep):
    current_user = get_user(request)
    await sig_service.delete_sig(id, current_user, False)


@sig_router.post("/executive/{id}/update", status_code=204)
async def exec_update_sig(
    id: int, request: Request, body: BodyUpdateSIG, sig_service: SigServiceDep
):
    current_user = get_user(request)
    await sig_service.update_sig(id, body, current_user, True)


@sig_router.post("/executive/{id}/delete", status_code=204)
async def exec_delete_sig(id: int, request: Request, sig_service: SigServiceDep):
    current_user = get_user(request)
    await sig_service.delete_sig(id, current_user, True)
