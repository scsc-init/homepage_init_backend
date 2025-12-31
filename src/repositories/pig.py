from typing import Annotated, Any, Optional, Sequence

from fastapi import Depends
from sqlalchemy import select

from src.model import PIG, PIGMember, SCSCStatus

from .crud_repository import CRUDRepository


class PigRepository(CRUDRepository[PIG, int]):
    @property
    def model(self) -> type[PIG]:
        return PIG

    def get_by_year_semester_not_inactive(
        self, year: int, semester: int
    ) -> Sequence[PIG]:
        stmt = select(PIG).where(
            PIG.year == year,
            PIG.semester == semester,
            PIG.status != SCSCStatus.inactive,
        )
        return self.session.scalars(stmt).all()

    def get_by_status(self, status: SCSCStatus) -> Sequence[PIG]:
        return self.session.scalars(select(PIG).where(PIG.status == status)).all()

    def get_by_filters(self, filters: dict[str, Any]) -> Sequence[PIG]:
        query = select(PIG)
        for attr, value in filters.items():
            if value is not None:
                query = query.where(getattr(PIG, attr) == value)
        return self.session.scalars(query).all()


class PigMemberRepository(CRUDRepository[PIGMember, int]):
    @property
    def model(self) -> type[PIGMember]:
        return PIGMember

    def get_by_pig_and_user_id(self, pig_id: int, user_id: str) -> Optional[PIGMember]:
        stmt = select(PIGMember).where(
            PIGMember.ig_id == pig_id, PIGMember.user_id == user_id
        )
        return self.session.scalars(stmt).first()

    def get_members_by_pig_id(self, pig_id: int) -> Sequence[PIGMember]:
        stmt = select(PIGMember).where(PIGMember.ig_id == pig_id)
        return self.session.scalars(stmt).all()


PigRepositoryDep = Annotated[PigRepository, Depends()]
PigMemberRepositoryDep = Annotated[PigMemberRepository, Depends()]
