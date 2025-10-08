from sqlmodel import Field, SQLModel, UniqueConstraint


class Major(SQLModel, table=True):
    __tablename__ = "major"  # type: ignore
    __table_args__ = (
        UniqueConstraint("college", "major_name", name="uq_college_major"),
    )

    id: int = Field(default=None, primary_key=True)  # default=None because of autoincrement
    college: str = Field(nullable=False)
    major_name: str = Field(nullable=False)
