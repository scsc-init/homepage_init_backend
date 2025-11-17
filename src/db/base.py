from typing import Annotated

from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass, mapped_column


class Base(MappedAsDataclass, DeclarativeBase):
    """subclasses will be converted to dataclasses"""


intpk = Annotated[int, mapped_column(primary_key=True, autoincrement=True, init=False)]
