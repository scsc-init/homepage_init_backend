from typing import Annotated, Optional, Sequence

from fastapi import Depends
from sqlalchemy import select

from src.model import PIG, PIGMember

from .dao import DAO


class PigRepository(DAO[PIG, int]):
    @property
    def model(self) -> type[PIG]:
        return PIG


class PigMemberRepository(DAO[PIGMember, int]):
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
