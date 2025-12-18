from typing import Sequence

from fastapi import APIRouter

from src.dependencies import NullableUserDep, UserDep
from src.schemas import KvResponse
from src.services import KvServiceDep, KvUpdateBody

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
    current_user: NullableUserDep,
    kv_service: KvServiceDep,
) -> Sequence[KvResponse]:
    role = current_user.role if current_user else 0
    kvs = kv_service.get_all_kv_values(role)
    return KvResponse.model_validate_list(kvs)


@kv_router.post("/{key}/update")
async def update_kv_value(
    key: str,
    current_user: UserDep,
    body: KvUpdateBody,
    kv_service: KvServiceDep,
) -> KvResponse:
    kv = kv_service.update_kv_value(key, current_user, body)
    return KvResponse.model_validate(kv)
