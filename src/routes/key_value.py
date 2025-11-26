from typing import Optional

from fastapi import APIRouter, Request

from src.controller import KvServiceDep, KvUpdateBody
from src.dependencies import UserDep
from src.schemas import KvResponse

kv_router = APIRouter(prefix="/kv", tags=["kv"])


@kv_router.get("/{key}")
async def get_kv_value(
    key: str,
    kv_service: KvServiceDep,
) -> KvResponse:
    kv = kv_service.get_kv_value(key)
    return KvResponse.model_validate(kv)


# This works as "api/kv" + "s" (="api/kvs")
@kv_router.get("s")
async def get_all_kv_values(
    request: Request,
    kv_service: KvServiceDep,
) -> dict[str, Optional[str]]:
    current_user = request.state.user
    role = current_user.role if current_user else 0
    return kv_service.get_all_kv_values(role)


@kv_router.post("/{key}/update")
async def update_kv_value(
    key: str,
    current_user: UserDep,
    body: KvUpdateBody,
    kv_service: KvServiceDep,
) -> KvResponse:
    kv = kv_service.update_kv_value(key, current_user, body)
    return KvResponse.model_validate(kv)
