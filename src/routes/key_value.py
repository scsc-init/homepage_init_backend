from typing import Optional

from fastapi import APIRouter

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


@kv_router.post("/{key}/update")
async def update_kv_value(
    key: str,
    current_user: UserDep,
    body: KvUpdateBody,
    kv_service: KvServiceDep,
) -> KvResponse:
    kv = kv_service.update_kv_value(key, current_user, body)
    return KvResponse.model_validate(kv)
