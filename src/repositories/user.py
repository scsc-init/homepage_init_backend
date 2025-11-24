from typing import Annotated

from fastapi import Depends

from src.model import User, UserRole

from .dao import DAO


class UserRepository(DAO[User, str]):
    @property
    def model(self) -> type[User]:
        return User


class UserRoleRepository(DAO[UserRole, int]):
    @property
    def model(self) -> type[UserRole]:
        return UserRole


UserRepositoryDep = Annotated[UserRepository, Depends()]
UserRoleRepositoryDep = Annotated[UserRoleRepository, Depends()]
