from datetime import datetime, timezone

from fastapi import HTTPException

from src.db import SessionDep
from src.model import KeyValue


def get_kv_entry(session: SessionDep, key: str) -> KeyValue:
    kv_entry = session.get(KeyValue, key)
    if kv_entry is None:
        raise HTTPException(503, detail=f"config entry '{key}' not configured")
    return kv_entry


def update_kv_entry(
    session: SessionDep,
    *,
    key: str,
    value: str,
    actor_role: int,
) -> KeyValue:
    kv_entry = get_kv_entry(session, key)

    required_role = kv_entry.writing_permission_level
    if actor_role < required_role:
        raise HTTPException(403, detail="insufficient permission")

    kv_entry.value = value
    kv_entry.updated_at = datetime.now(timezone.utc)

    session.add(kv_entry)
    session.commit()
    session.refresh(kv_entry)
    return kv_entry
