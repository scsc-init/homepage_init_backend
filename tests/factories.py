from __future__ import annotations

import uuid
from typing import Iterable, Sequence

from sqlalchemy.orm import Session

from tests.types import (
    Major,
    SCSCGlobalStatus,
    SCSCStatus,
    User,
    UserRole,
    UserStatus,
)

DEFAULT_ROLE_DEFINITIONS: Sequence[tuple[str, int, str]] = (
    ("lowest", 0, "최저권한"),
    ("dormant", 100, "휴회원"),
    ("newcomer", 200, "준회원"),
    ("member", 300, "정회원"),
    ("oldboy", 400, "졸업생"),
    ("executive", 500, "운영영진"),
    ("president", 1000, "회장"),
)

DEFAULT_ROLE_LEVELS = {name: level for name, level, _ in DEFAULT_ROLE_DEFINITIONS}
DEFAULT_EXEC_USER_ID = (
    "a44946fbf09c326520c2ca0a324b19100381911c9afe5af06a90b636d8f35dd5"
)


def seed_user_roles(
    session: Session,
    definitions: Iterable[tuple[str, int, str]] = DEFAULT_ROLE_DEFINITIONS,
) -> None:
    for name, level, kor_name in definitions:
        if session.get(UserRole, level):
            continue
        session.add(UserRole(level=level, name=name, kor_name=kor_name))
    session.commit()


def create_major(
    session: Session, *, college: str = "Engineering", major_name: str | None = None
) -> Major:
    major = Major(
        college=college,
        major_name=major_name or f"Major-{uuid.uuid4().hex[:6]}",
    )
    session.add(major)
    session.commit()
    session.refresh(major)
    return major


def create_user(
    session: Session,
    *,
    user_id: str | None = None,
    role_level: int | None = None,
    major: Major | None = None,
    status: UserStatus = UserStatus.active,
) -> User:
    major = major or create_major(session)
    role_level = role_level or DEFAULT_ROLE_LEVELS["member"]
    suffix = uuid.uuid4().hex
    user = User(
        id=user_id or suffix,
        email=f"{suffix}@example.com",
        name="Test User",
        phone=f"010{uuid.uuid4().int % 10**8:08d}",
        student_id=f"{uuid.uuid4().int % 10**8:08d}",
        role=role_level,
        major_id=major.id,
        status=status,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def create_scsc_global_status(
    session: Session,
    *,
    status: SCSCStatus = SCSCStatus.recruiting,
    year: int = 2025,
    semester: int = 1,
) -> SCSCGlobalStatus:
    existing = session.get(SCSCGlobalStatus, 1)
    if existing:
        existing.status = status
        existing.year = year
        existing.semester = semester
        obj = existing
    else:
        obj = SCSCGlobalStatus(id=1, status=status, year=year, semester=semester)
        session.add(obj)
    session.commit()
    session.refresh(obj)
    return obj
