from typing import Annotated

from fastapi import Depends
from sqlalchemy import select

from src.model import UserRole

from .dao import DAO


class UserRoleRepository(DAO[UserRole, int]):
    @property
    def model(self) -> type[UserRole]:
        return UserRole


UserRoleRepositoryDep = Annotated[UserRoleRepository, Depends()]
