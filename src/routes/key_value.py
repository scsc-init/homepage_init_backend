import logging

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from src.controller.key_value import get_kv_entry, update_kv_entry
from src.db import SessionDep
from src.util import get_user

logger = logging.getLogger("app")

kv_router = APIRouter(prefix="/kv", tags=["kv"])


class KvUpdateBody(BaseModel):
    value: str


def ensure_allowed_key(session: SessionDep, key: str):
    try:
        return get_kv_entry(session, key)
    except HTTPException as exc:
        if exc.status_code == 503:
            raise HTTPException(
                status_code=404, detail="unknown kv key") from exc
        raise


@kv_router.get("/{key}")
async def get_kv_value(
    key: str,
    session: SessionDep,
    request: Request,
) -> dict[str, str]:
    entry = ensure_allowed_key(session, key)
    return {"key": entry.key, "value": entry.value}


@kv_router.post("/{key}/update")
async def update_kv_value(
    key: str,
    body: KvUpdateBody,
    session: SessionDep,
    request: Request,
) -> dict[str, str]:
    ensure_allowed_key(session, key)

    current_user = get_user(request)

    updated_entry = update_kv_entry(
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
