from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy import literal, select

from src.model import CheckUserStatusRule

from .dao import DAO


class CheckUserStatusRuleRepository(DAO[CheckUserStatusRule, int]):
    @property
    def model(self) -> type[CheckUserStatusRule]:
        return CheckUserStatusRule

    def get_blacklist_rules_by_request(self, request: Request):
        stmt = select(CheckUserStatusRule).where(
            CheckUserStatusRule.method == request.method,
            literal(request.url.path).like(CheckUserStatusRule.path),
        )
        return self.session.scalars(stmt).all()


CheckUserStatusRuleRepositoryDep = Annotated[CheckUserStatusRuleRepository, Depends()]
