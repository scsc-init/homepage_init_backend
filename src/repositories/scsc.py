from typing import Annotated

from fastapi import Depends

from src.model import SCSCGlobalStatus

from .crud_repository import CRUDRepository


class SCSCGlobalStatusRepository(CRUDRepository[SCSCGlobalStatus, int]):
    @property
    def model(self) -> type[SCSCGlobalStatus]:
        return SCSCGlobalStatus

    def get_current_scsc_global_status(self):
        return self.get_by_id(1)


SCSCGlobalStatusRepositoryDep = Annotated[SCSCGlobalStatusRepository, Depends()]
