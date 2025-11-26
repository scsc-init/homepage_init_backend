from typing import Annotated, Optional

from fastapi import Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import select

from src.core import logger
from src.model import KeyValue, User
from src.repositories import KeyValueRepositoryDep


class KvUpdateBody(BaseModel):
    value: Optional[str]


class KvService:
    def __init__(self, kv_repo: KeyValueRepositoryDep):
        self.kv_repo = kv_repo

    def get_kv_value(self, key: str) -> KeyValue:
        entry = self.kv_repo.get_by_id(key)
        if entry is None:
            raise HTTPException(status_code=404, detail="unknown kv key")
        return entry

    def get_all_kv_values(self, user_role: int) -> dict[str, Optional[str]]:
        entries = self.session.exec(
            select(KeyValue).where(KeyValue.writing_permission_level <= user_role)
        ).all()
        return {entry.key: entry.value for entry in entries}

    def update_kv_value(
        self, key: str, current_user: User, body: KvUpdateBody
    ) -> KeyValue:
        kv_entry = self.kv_repo.get_by_id(key)
        if kv_entry is None:
            raise HTTPException(status_code=404, detail="unknown kv key")

        required_role = kv_entry.writing_permission_level
        if current_user.role < required_role:
            raise HTTPException(status_code=403, detail="insufficient permission")

        kv_entry.value = body.value
        updated_entry = self.kv_repo.update(kv_entry)

        logger.info(
            "info_type=kv_updated ; key=%s ; value=%s ; updater_id=%s",
            key,
            updated_entry.value,
            current_user.id,
        )

        return updated_entry


KvServiceDep = Annotated[KvService, Depends()]
