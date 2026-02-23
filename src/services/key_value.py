from typing import Annotated, Optional, Sequence

from fastapi import Depends, HTTPException
from pydantic import BaseModel

from src.core import logger
from src.model import KeyValue, User
from src.repositories import KeyValueRepositoryDep


class KvUpdateBody(BaseModel):
    value: Optional[str]


class KvService:
    def __init__(self, kv_repository: KeyValueRepositoryDep):
        self.kv_repository = kv_repository

    def get_kv_value(self, key: str) -> KeyValue:
        entry = self.kv_repository.get_by_id(key)
        if entry is None:
            raise HTTPException(status_code=404, detail="unknown kv key")
        return entry

    def get_all_kv_values(self, user_role: int) -> Sequence[KeyValue]:
        return self.kv_repository.get_kv_values_by_role(user_role)

    def update_kv_value(
        self, key: str, current_user: User, body: KvUpdateBody
    ) -> KeyValue:
        kv_entry = self.kv_repository.get_by_id(key)
        if kv_entry is None:
            raise HTTPException(status_code=404, detail="unknown kv key")

        required_role = kv_entry.writing_permission_level
        if current_user.role < required_role:
            raise HTTPException(status_code=403, detail="insufficient permission")

        kv_entry.value = body.value
        updated_entry = self.kv_repository.update(kv_entry)

        logger.info(
            "info_type=kv_updated ; key=%s ; value=%s ; updater_id=%s",
            key,
            updated_entry.value,
            current_user.id,
        )

        return updated_entry

    def get_enrollment_grant_until(self) -> tuple[int, int]:
        grant_until_str = self.get_kv_value("enrollment_grant_until").value
        if grant_until_str is None:
            raise HTTPException(500, detail="enrollment_grant_until is null")
        until_year, until_semester = map(int, grant_until_str.split("-"))
        return until_year, until_semester


KvServiceDep = Annotated[KvService, Depends()]
