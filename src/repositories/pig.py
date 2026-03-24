from __future__ import annotations

from typing import Annotated, Any, Optional, Sequence

from fastapi import Depends
from sqlalchemy import delete, select

from src.model import PIG, PIGMember, PIGWebsite, SCSCStatus

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


class PigWebsiteRepository(CRUDRepository[PIGWebsite, int]):
    @property
    def model(self) -> type[PIGWebsite]:
        return PIGWebsite

    def get_by_pig_id(self, pig_id: int) -> Sequence[PIGWebsite]:
        stmt = (
            select(PIGWebsite)
            .where(PIGWebsite.pig_id == pig_id)
            .order_by(PIGWebsite.sort_order, PIGWebsite.id)
        )
        return self.session.scalars(stmt).all()

    def replace_for_pig(self, pig_id: int, websites: Sequence[PIGWebsite]) -> None:
        with self.transaction:
            self.session.execute(delete(PIGWebsite).where(PIGWebsite.pig_id == pig_id))
            for website in websites:
                self.session.add(website)

    def delete_by_pig_id(self, pig_id: int) -> None:
        with self.transaction:
            self.session.execute(delete(PIGWebsite).where(PIGWebsite.pig_id == pig_id))


PigRepositoryDep = Annotated[PigRepository, Depends()]
PigMemberRepositoryDep = Annotated[PigMemberRepository, Depends()]
PigWebsiteRepositoryDep = Annotated[PigWebsiteRepository, Depends()]
