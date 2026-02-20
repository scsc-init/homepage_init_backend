from typing import Annotated, Any, Optional, Sequence

from fastapi import Depends
from sqlalchemy import delete, exists, func, select

from src.db import get_user_role_level
from src.model import Enrollment, OldboyApplicant, StandbyReqTbl, User, UserRole

from .crud_repository import CRUDRepository


class UserRepository(CRUDRepository[User, str]):
    @property
    def model(self) -> type[User]:
        return User

    def get_by_status_and_role(
        self, role: int, is_active: bool, is_banned: bool
    ) -> Sequence[User]:
        return self.session.scalars(
            select(User).where(
                User.role == role,
                User.is_active == is_active,
                User.is_banned == is_banned,
            )
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

    def delete_all_except_student_ids(self, excluded_student_ids: list[str]) -> None:
        if not excluded_student_ids:
            raise ValueError("예외 없이 모든 유저 삭제 불가")

        stmt = delete(self.model).where(
            ~self.model.student_id.in_(excluded_student_ids)
        )

        with self.transaction:
            self.session.execute(stmt)


class UserRoleRepository(CRUDRepository[UserRole, int]):
    cached_user_role = None

    @property
    def model(self) -> type[UserRole]:
        return UserRole

    def list_all(self) -> Sequence[UserRole]:
        if UserRoleRepository.cached_user_role is None:
            UserRoleRepository.cached_user_role = super().list_all()
        return UserRoleRepository.cached_user_role


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


class EnrollmentRepository(CRUDRepository[Enrollment, str]):
    @property
    def model(self) -> type[Enrollment]:
        return Enrollment

    def exists_by_user_id(self, user_id: str) -> bool:
        return bool(
            self.session.scalar(
                select(exists(select(1).where(Enrollment.user_id == user_id)))
            )
        )


UserRepositoryDep = Annotated[UserRepository, Depends()]
UserRoleRepositoryDep = Annotated[UserRoleRepository, Depends()]
StandbyReqTblRepositoryDep = Annotated[StandbyReqTblRepository, Depends()]
OldboyApplicantRepositoryDep = Annotated[OldboyApplicantRepository, Depends()]
EnrollmentRepositoryDep = Annotated[EnrollmentRepository, Depends()]
