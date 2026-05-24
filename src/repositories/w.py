from typing import Annotated, Sequence, Tuple

from fastapi import Depends
from sqlalchemy import Row, select, update

from src.model import User, WHTMLMetadata

from .crud_repository import CRUDRepository


class WRepository(CRUDRepository[WHTMLMetadata, str]):
    @property
    def model(self) -> type[WHTMLMetadata]:
        return WHTMLMetadata

    def get_all_with_creator_name(self) -> Sequence[Row[Tuple[WHTMLMetadata, str]]]:
        stmt = select(WHTMLMetadata, User.name).join(
            User, WHTMLMetadata.creator == User.id
        )
        return self.session.execute(stmt).all()

    def increase_view_count(self, name: str) -> None:
        stmt = (
            update(WHTMLMetadata)
            .where(WHTMLMetadata.name == name)
            .values(view_cnt=WHTMLMetadata.view_cnt + 1)
        )
        self.session.execute(stmt)
        self.session.commit()


WRepositoryDep = Annotated[WRepository, Depends()]
