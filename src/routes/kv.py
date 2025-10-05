import logging

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from src.db import SessionDep
from src.util import (
  FOOTER_MESSAGE_KEY,
  get_kv_entry,
  get_user,
  update_kv_entry,
)

logger = logging.getLogger("app")

kv_router = APIRouter(prefix="/kv", tags=["kv"])


ALLOWED_CONFIG_KEYS = {FOOTER_MESSAGE_KEY}


def ensure_allowed_key(key: str) -> str:
  if key not in ALLOWED_CONFIG_KEYS:
    raise HTTPException(status_code=404, detail="unknown kv key")
  return key


class KvUpdateBody(BaseModel):
  value: str


@kv_router.get("/{key}")
async def get_kv_value(
  key: str,
  session: SessionDep,
  request: Request,
) -> dict[str, str]:
  ensure_allowed_key(key)
  entry = get_kv_entry(session, key)
  return {"key": entry.key, "value": entry.value}


@kv_router.put("/{key}")
async def update_kv_value(
  key: str,
  body: KvUpdateBody,
  session: SessionDep,
  request: Request,
) -> dict[str, str]:
  ensure_allowed_key(key)

  current_user = get_user(request)

  updated_entry = update_kv_entry(
    session,
    key=key,
    value=body.value,
    actor_role=current_user.role,
  )

  logger.info(
    "info_type=kv_updated ; key=%s ; updater_id=%s",
    key,
    current_user.id,
  )

  return {"key": updated_entry.key, "value": updated_entry.value}

kv_router.include_router(kv_router)
