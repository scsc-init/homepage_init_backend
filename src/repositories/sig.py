from typing import Annotated, Any, Optional, Sequence

from fastapi import Depends
from sqlalchemy import select

from src.model import SIG, SCSCStatus, SIGMember, SIGTag, Tag

from .crud_repository import CRUDRepository


class SigRepository(CRUDRepository[SIG, int]):
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

    def get_by_filters(self, filters: dict[str, Any]) -> Sequence[SIG]:
        query = select(SIG)
        for attr, value in filters.items():
            if value is not None:
                query = query.where(getattr(SIG, attr) == value)
        return self.session.scalars(query).all()


class SigMemberRepository(CRUDRepository[SIGMember, int]):
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


class SigTagRepository(CRUDRepository[SIGTag, int]):
    @property
    def model(self) -> type[SIGTag]:
        return SIGTag

    def get_by_sig_id(self, sig_id: int) -> Sequence[SIGTag]:
        stmt = select(SIGTag).where(SIGTag.sig_id == sig_id)
        return self.session.scalars(stmt).all()

    def get_by_sig_id_and_tag_id(self, sig_id: int, tag_id: int) -> Optional[SIGTag]:
        stmt = select(SIGTag).where(SIGTag.sig_id == sig_id, SIGTag.tag_id == tag_id)
        return self.session.scalar(stmt)


class TagRepository(CRUDRepository[Tag, int]):
    @property
    def model(self) -> type[Tag]:
        return Tag

    def get_by_text(self, text: str) -> Optional[Tag]:
        stmt = select(Tag).where(Tag.text == text)
        return self.session.scalar(stmt)

    def get_all(self) -> Sequence[Tag]:
        return self.session.scalars(select(Tag)).all()

    def get_non_major(self) -> Sequence[Tag]:
        stmt = select(Tag).where(Tag.is_major.is_(False))
        return self.session.scalars(stmt).all()


SigRepositoryDep = Annotated[SigRepository, Depends()]
SigMemberRepositoryDep = Annotated[SigMemberRepository, Depends()]
SigTagRepositoryDep = Annotated[SigTagRepository, Depends()]
TagRepositoryDep = Annotated[TagRepository, Depends()]
