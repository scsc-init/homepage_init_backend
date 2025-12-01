import os
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Callable, Optional

import jwt
import pytest
from fastapi.testclient import TestClient

# Configure SQLite path for tests before importing FastAPI app
TEST_DB_PATH = Path(__file__).resolve().parent / "test.sqlite3"
TEST_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("SQLITE_FILENAME", str(TEST_DB_PATH))

import src.model
from main import app
from src.core import get_settings
from src.db import Base, DBSessionFactory
from src.db.engine import engine
from src.model import (
    CheckUserStatusRule,
    HTTPMethod,
    Major,
    User,
    UserRole,
    UserStatus,
)
from src.util.get_from_db import get_user_role_level

ROLE_DATA = [
    (0, "lowest", "lowest_kor"),
    (100, "dormant", "dormant_kor"),
    (200, "newcomer", "newcomer_kor"),
    (300, "member", "member_kor"),
    (400, "oldboy", "oldboy_kor"),
    (500, "executive", "executive_kor"),
    (1000, "president", "president_kor"),
]


@pytest.fixture(scope="session", autouse=True)
def manage_test_database():
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()
    yield
    DBSessionFactory().teardown()
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()


@pytest.fixture(autouse=True)
def reset_db_schema():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    session = DBSessionFactory().make_session()
    try:
        session.add_all(
            [
                UserRole(level=level, name=name, kor_name=kor)
                for level, name, kor in ROLE_DATA
            ]
        )
        session.commit()
    finally:
        session.close()
    get_user_role_level.cache_clear()


@pytest.fixture
def db_session():
    session = DBSessionFactory().make_session()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def create_major(db_session) -> Callable[..., Major]:
    def _create_major(
        *,
        college: str = "Engineering",
        major_name: Optional[str] = None,
    ) -> Major:
        name = major_name or f"Major-{uuid.uuid4().hex[:6]}"
        major = Major(college=college, major_name=name)
        db_session.add(major)
        db_session.commit()
        db_session.refresh(major)
        return major

    return _create_major


@pytest.fixture
def create_user(
    db_session, create_major, make_jwt_token
) -> Callable[..., tuple[User, Optional[str]]]:
    def _create_user(
        *,
        role_level: int = 300,
        status: UserStatus = UserStatus.active,
        major: Optional[Major] = None,
        issue_token: bool = True,
    ) -> tuple[User, Optional[str]]:
        assigned_major = major or create_major()
        unique = uuid.uuid4().hex[:8]
        user = User(
            id=f"user-{uuid.uuid4().hex}",
            email=f"{unique}@example.com",
            name=f"User-{unique}",
            phone=f"010{uuid.uuid4().int % 10**8:08d}",
            student_id=f"2020{uuid.uuid4().int % 100000:05d}",
            role=role_level,
            major_id=assigned_major.id,
            status=status,
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        token = make_jwt_token(user.id) if issue_token else None
        return user, token

    return _create_user


@pytest.fixture
def create_status_rule(db_session) -> Callable[..., CheckUserStatusRule]:
    def _create_rule(
        *,
        user_status: UserStatus,
        method: HTTPMethod = HTTPMethod.GET,
        path: str = "/api/majors",
    ) -> CheckUserStatusRule:
        rule = CheckUserStatusRule(user_status=user_status, method=method, path=path)
        db_session.add(rule)
        db_session.commit()
        db_session.refresh(rule)
        return rule

    return _create_rule


@pytest.fixture
def make_jwt_token():
    settings = get_settings()

    def _issue(user_id: str, *, expires_in: int = 3600) -> str:
        payload = {
            "user_id": user_id,
            "exp": datetime.now(timezone.utc) + timedelta(seconds=expires_in),
        }
        return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")

    return _issue


@pytest.fixture
def build_headers():
    settings = get_settings()

    def _headers(token: Optional[str] = None) -> dict[str, str]:
        headers: dict[str, str] = {"x-api-secret": settings.api_secret}
        if token:
            headers["x-jwt"] = token
        return headers

    return _headers


@pytest.fixture
def api_client():
    with TestClient(app) as test_client:
        yield test_client
