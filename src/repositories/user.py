from typing import Annotated, Any, Optional, Sequence

from fastapi import Depends
from sqlalchemy import func, select

from src.model import OldboyApplicant, StandbyReqTbl, User, UserRole, UserStatus
from src.util import get_user_role_level

from .dao import CRUDRepository


class UserRepository(CRUDRepository[User, str]):
    @property
    def model(self) -> type[User]:
        return User

    def get_by_status_and_role(self, status: UserStatus, role: int) -> Sequence[User]:
        return self.session.scalars(
            select(User).where(User.status == status, User.role == role)
        ).all()

    def get_by_filters(self, filters: dict[str, Any]) -> Sequence[User]:
        query = select(User)
        for attr, value in filters.items():
            if value is not None:
                if attr == "discord_id" and value == "IS_NULL":
                    query = query.where(User.discord_id == None)
                elif attr == "discord_name" and value == "IS_NULL":
                    query = query.where(User.discord_name == None)
                else:
                    query = query.where(getattr(User, attr) == value)
        return self.session.scalars(query).all()

    def get_by_name_and_phone_tail(self, name: str, phone_tail: str) -> Sequence[User]:
        return self.session.scalars(
            select(User).where(
                User.name == name,
                func.substring(User.phone, func.length(User.phone) - 1, 2)
                == phone_tail,
            )
        ).all()

    def get_by_name(self, name: str) -> Sequence[User]:
        return self.session.scalars(select(User).where(User.name == name)).all()

    def get_executives(self) -> Sequence[User]:
        return self.session.scalars(
            select(User).where(User.role >= get_user_role_level("executive"))
        ).all()


class UserRoleRepository(CRUDRepository[UserRole, int]):
    @property
    def model(self) -> type[UserRole]:
        return UserRole


class StandbyReqTblRepository(CRUDRepository[StandbyReqTbl, str]):
    @property
    def model(self) -> type[StandbyReqTbl]:
        return StandbyReqTbl

    def get_unchecked_by_deposit_name(
        self, deposit_name: str
    ) -> Sequence[StandbyReqTbl]:
        return self.session.scalars(
            select(StandbyReqTbl).where(
                StandbyReqTbl.is_checked == False,
                StandbyReqTbl.deposit_name == deposit_name,
            )
        ).all()

    def get_unchecked_by_user_name(self, user_name: str) -> Sequence[StandbyReqTbl]:
        return self.session.scalars(
            select(StandbyReqTbl).where(
                StandbyReqTbl.is_checked == False,
                StandbyReqTbl.user_name == user_name,
            )
        ).all()

    def get_by_user_id(self, user_id: str) -> Optional[StandbyReqTbl]:
        return self.session.scalars(
            select(StandbyReqTbl)
            .where(StandbyReqTbl.standby_user_id == user_id)
            .where(StandbyReqTbl.is_checked == False)
        ).first()


class OldboyApplicantRepository(CRUDRepository[OldboyApplicant, str]):
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
