from datetime import datetime, timezone
from enum import Enum

from sqlmodel import Field, SQLModel


class UserRole(str, Enum):
    user = "user"
    executive = "executive"
    president = "president"

    def __lt__(self, other: "UserRole", tbl={user: 0, executive: 1, president: 2}) -> bool:
        if isinstance(other, UserRole):
            return tbl[self] < tbl[other]
        return NotImplemented

    def __le__(self, other: "UserRole"):
        return self < other or self == other

    def __ne__(self, other: "UserRole"):
        return not self == other

    def __gt__(self, other: "UserRole"):
        return not (self < other or self == other)

    def __ge__(self, other: "UserRole"):
        return not self < other


class UserStatus(str, Enum):
    active = "active"
    pending = "pending"
    banned = "banned"


class User(SQLModel, table=True):
    __tablename__ = "user"  # type: ignore

    id: str = Field(default=None, primary_key=True)

    email: str = Field(nullable=False, unique=True)
    name: str = Field(nullable=False)
    phone: str = Field(nullable=False, unique=True)
    student_id: str = Field(nullable=False, unique=True)

    role: UserRole = Field(default=UserRole.user, nullable=False)
    status: UserStatus = Field(default=UserStatus.pending, nullable=False)

    last_login: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), nullable=False)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), nullable=False)

    major_id: int = Field(foreign_key="major.id", nullable=False)
