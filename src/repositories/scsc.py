from typing import Annotated

from fastapi import Depends
from sqlalchemy import select

from src.model import SCSCGlobalStatus

from .dao import DAO


class SCSCGlobalStatusRepository(DAO[SCSCGlobalStatus, int]):
    @property
    def model(self) -> type[SCSCGlobalStatus]:
        return SCSCGlobalStatus

    def get_current_scsc_global_status(self):
        return self.get_by_id(1)


SCSCGlobalStatusRepositoryDep = Annotated[SCSCGlobalStatusRepository, Depends()]
