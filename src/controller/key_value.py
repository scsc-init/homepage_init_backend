from typing import Annotated, Optional

from fastapi import Depends, HTTPException, Request
from pydantic import BaseModel

from src.core import logger
from src.db import SessionDep
from src.model import KeyValue, User


def _ensure_allowed_key(session: SessionDep, key: str) -> KeyValue:
    kv_entry = session.get(KeyValue, key)
    if kv_entry is None:
        raise HTTPException(status_code=404, detail="unknown kv key")
    return kv_entry


def get_kv_value(session: SessionDep, key: str) -> KeyValue:
    return _ensure_allowed_key(session, key)


def update_kv_value(
    session: SessionDep,
    *,
    key: str,
    value: Optional[str],
    actor_role: int,
) -> KeyValue:
    kv_entry = _ensure_allowed_key(session, key)

    required_role = kv_entry.writing_permission_level
    if actor_role < required_role:
        raise HTTPException(status_code=403, detail="insufficient permission")

    kv_entry.value = value

    session.add(kv_entry)
    session.commit()
    session.refresh(kv_entry)
    return kv_entry


class KvUpdateBody(BaseModel):
    value: Optional[str]


class KvService:
    def __init__(self, session: SessionDep):
        self.session = session

    def get_kv_value(self, key: str) -> dict[str, Optional[str]]:
        entry = get_kv_value(self.session, key)
        if not entry:
            raise HTTPException(status_code=404, detail=f"Key '{key}' not found")
        return {"key": entry.key, "value": entry.value}

    def update_kv_value(
        self, key: str, body: KvUpdateBody, current_user: User, request: Request
    ) -> dict[str, Optional[str]]:

        updated_entry = update_kv_value(
            self.session,
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


KvServiceDep = Annotated[KvService, Depends()]
