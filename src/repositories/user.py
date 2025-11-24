from typing import Annotated, Sequence

from fastapi import Depends
from sqlalchemy import select

from src.model import OldboyApplicant, StandbyReqTbl, User, UserRole, UserStatus

from .dao import DAO


class UserRepository(DAO[User, str]):
    @property
    def model(self) -> type[User]:
        return User

    def get_by_status_and_role(self, status: UserStatus, role: int) -> Sequence[User]:
        return self.session.scalars(
            select(User).where(User.status == status, User.role == role)
        ).all()


class UserRoleRepository(DAO[UserRole, int]):
    @property
    def model(self) -> type[UserRole]:
        return UserRole


class StandbyReqTblRepository(DAO[StandbyReqTbl, str]):
    @property
    def model(self) -> type[StandbyReqTbl]:
        return StandbyReqTbl


class OldboyApplicantRepository(DAO[OldboyApplicant, str]):
    @property
    def model(self) -> type[OldboyApplicant]:
        return OldboyApplicant

    def get_unprocessed(self) -> Sequence[OldboyApplicant]:
        stmt = select(OldboyApplicant).where(OldboyApplicant.processed == False)
        return self.session.scalars(stmt).all()


UserRepositoryDep = Annotated[UserRepository, Depends()]
UserRoleRepositoryDep = Annotated[UserRoleRepository, Depends()]
StandbyReqTblRepositoryDep = Annotated[StandbyReqTblRepository, Depends()]
OldboyApplicantRepositoryDep = Annotated[OldboyApplicantRepository, Depends()]
