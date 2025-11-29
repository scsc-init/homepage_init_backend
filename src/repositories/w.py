from typing import Annotated, Sequence, Tuple

from fastapi import Depends
from sqlalchemy import Row, select

from src.model import User, WHTMLMetadata

from .dao import CRUDRepository


class WRepository(CRUDRepository[WHTMLMetadata, str]):
    @property
    def model(self) -> type[WHTMLMetadata]:
        return WHTMLMetadata

    def get_all_with_creator_name(self) -> Sequence[Row[Tuple[WHTMLMetadata, str]]]:
        stmt = select(WHTMLMetadata, User.name).join(
            User, WHTMLMetadata.creator == User.id
        )
        return self.session.execute(stmt).all()


WRepositoryDep = Annotated[WRepository, Depends()]
