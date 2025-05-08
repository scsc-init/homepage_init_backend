from sqlmodel import SQLModel, Field, UniqueConstraint
from typing import Optional

class Major(SQLModel, table=True):
    __tablename__ = "major"
    __table_args__ = (
        UniqueConstraint("college", "major_name", name="uq_college_major"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    college: str = Field(nullable=False)
    major_name: str = Field(nullable=False)
