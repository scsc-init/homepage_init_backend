from datetime import datetime, timezone
from enum import Enum

from sqlmodel import Field, SQLModel


class UserStatus(str, Enum):
    active = "active"
    pending = "pending"
    standby = "standby"
    banned = "banned"


class UserRole(SQLModel, table=True):
    __tablename__ = "user_role"  # type: ignore

    level: int = Field(primary_key=True)

    name: str = Field(nullable=False, unique=True)
    kor_name: str = Field(nullable=False, unique=True)


class User(SQLModel, table=True):
    __tablename__ = "user"  # type: ignore

    id: str = Field(primary_key=True)

    email: str = Field(nullable=False, unique=True)
    name: str = Field(nullable=False)
    phone: str = Field(nullable=False, unique=True)
    student_id: str = Field(nullable=False, unique=True)

    role: int = Field(foreign_key="user_role.level", nullable=False)
    status: UserStatus = Field(default=UserStatus.pending, nullable=False)

    last_login: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False)

    major_id: int = Field(foreign_key="major.id", nullable=False)


class StandbyReqTbl(SQLModel, table=True):
    __tablename__ = "standby_req_tbl"  # type: ignore
    
    standby_user_id: str = Field(default=None, primary_key=True)
    
    user_name: str = Field(nullable=False)
    deposit_name: str = Field(nullable=False)
    deposit_time: datetime = Field()
    is_checked: bool = Field(default=False, nullable=False)
    
    
class OldboyApplicant(SQLModel, table=True):
    __tablename__ = "oldboy_applicant"  # type: ignore

    id: str = Field(foreign_key="user.id", primary_key=True)
    processed: bool = Field(default=False, nullable=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False)