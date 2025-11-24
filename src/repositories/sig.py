from typing import Annotated, Optional, Sequence

from fastapi import Depends
from sqlalchemy import select

from src.model import SIG, SCSCStatus, SIGMember

from .dao import DAO


class SigRepository(DAO[SIG, int]):
    @property
    def model(self) -> type[SIG]:
        return SIG

    def get_by_year_semester_not_inactive(
        self, year: int, semester: int
    ) -> Sequence[SIG]:
        stmt = select(SIG).where(
            SIG.year == year,
            SIG.semester == semester,
            SIG.status != SCSCStatus.inactive,
        )
        return self.session.scalars(stmt).all()

    def get_by_status(self, status: SCSCStatus) -> Sequence[SIG]:
        return self.session.scalars(select(SIG).where(SIG.status == status)).all()


class SigMemberRepository(DAO[SIGMember, int]):
    @property
    def model(self) -> type[SIGMember]:
        return SIGMember

    def get_by_sig_and_user_id(self, SIG_id: int, user_id: str) -> Optional[SIGMember]:
        stmt = select(SIGMember).where(
            SIGMember.ig_id == SIG_id, SIGMember.user_id == user_id
        )
        return self.session.scalars(stmt).first()

    def get_members_by_sig_id(self, SIG_id: int) -> Sequence[SIGMember]:
        stmt = select(SIGMember).where(SIGMember.ig_id == SIG_id)
        return self.session.scalars(stmt).all()


SigRepositoryDep = Annotated[SigRepository, Depends()]
SigMemberRepositoryDep = Annotated[SigMemberRepository, Depends()]
