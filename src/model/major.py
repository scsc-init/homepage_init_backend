from sqlalchemy import Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.db import Base


class Major(Base):
    __tablename__ = "major"
    __table_args__ = (
        UniqueConstraint("college", "major_name", name="uq_college_major"),
    )

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, init=False
    )
    college: Mapped[str] = mapped_column(nullable=False)
    major_name: Mapped[str] = mapped_column(nullable=False)
