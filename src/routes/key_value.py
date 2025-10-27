import logging
from typing import Any

from fastapi import APIRouter, Request
from pydantic import BaseModel

from src.controller.key_value import get_kv_value as get_kv_value_ctrl
from src.controller.key_value import update_kv_value as update_kv_value_ctrl
from src.db import SessionDep
from src.util import get_user

logger = logging.getLogger("app")

kv_router = APIRouter(prefix="/kv", tags=["kv"])


class KvUpdateBody(BaseModel):
    value: Any | None


@kv_router.get("/{key}")
async def get_kv_value(
    key: str,
    session: SessionDep,
    request: Request,
) -> dict[str, Any | None]:
    entry = get_kv_value_ctrl(session, key)
    return {"key": entry.key, "value": entry.value}


@kv_router.post("/{key}/update")
async def update_kv_value(
    key: str,
    body: KvUpdateBody,
    session: SessionDep,
    request: Request,
) -> dict[str, Any | None]:
    current_user = get_user(request)

    updated_entry = update_kv_value_ctrl(
        session,
        key=key,
        value=body.value,
        actor_role=current_user.role,
    )

    logger.info(
        "info_type=kv_updated ; key=%s ; value=%s ; updater_id=%s",
        key,
        updated_entry.value,
        current_user.id,
    )

    return {"key": updated_entry.key, "value": updated_entry.value}
