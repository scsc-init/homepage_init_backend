from fastapi import HTTPException

from src.db import SessionDep
from src.model import KeyValue


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
    value: str,
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
