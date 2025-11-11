from typing import Optional

from fastapi import APIRouter, Request

from src.controller import KvServiceDep, KvUpdateBody

kv_router = APIRouter(prefix="/kv", tags=["kv"])


@kv_router.get("/{key}")
async def get_kv_value(
    key: str,
    kv_service: KvServiceDep,
) -> dict[str, Optional[str]]:
    return kv_service.get_kv_value(key)


@kv_router.post("/{key}/update")
async def update_kv_value(
    key: str,
    body: KvUpdateBody,
    request: Request,
    kv_service: KvServiceDep,
) -> dict[str, Optional[str]]:
    return kv_service.update_kv_value(key, body, request)
