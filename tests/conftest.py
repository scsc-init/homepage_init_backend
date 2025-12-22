import io
import os
import shutil
from pathlib import Path
from typing import Any, Dict

import pytest
from fastapi.testclient import TestClient

from src.db import DBSessionFactory
from src.dependencies.user_auth import user_auth as user_auth_dependency
from src.model import User
from tests import factories


def _ensure_directory(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def _clean_directory(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    for entry in path.iterdir():
        if entry.is_file():
            entry.unlink()
        else:
            shutil.rmtree(entry)


@pytest.fixture(scope="session")
def test_environment(tmp_path_factory) -> Dict[str, Any]:
    base_dir = tmp_path_factory.mktemp("api-tests")
    db_path = base_dir / "test.db"
    file_dir = _ensure_directory(base_dir / "files")
    image_dir = _ensure_directory(base_dir / "images")
    article_dir = _ensure_directory(base_dir / "articles")
    w_dir = _ensure_directory(base_dir / "w-html")

    env_map = {
        "API_SECRET": "test-api-secret",
        "JWT_SECRET": "test-jwt-secret",
        "JWT_VALID_SECONDS": "3600",
        "SQLITE_FILENAME": str(db_path),
        "IMAGE_DIR": str(image_dir),
        "FILE_DIR": str(file_dir),
        "FILE_MAX_SIZE": "10485760",
        "ARTICLE_DIR": str(article_dir),
        "USER_CHECK": "FALSE",
        "ENROLLMENT_FEE": "0",
        "CORS_ALL_ACCEPT": "FALSE",
        "RABBITMQ_HOST": "test-rabbitmq",
        "BOT_HOST": "test-bot",
        "REPLY_QUEUE": "reply",
        "DISCORD_RECEIVE_QUEUE": "discord",
        "NOTICE_CHANNEL_ID": "0",
        "GRANT_CHANNEL_ID": "0",
        "W_HTML_DIR": str(w_dir),
    }
    for key, value in env_map.items():
        os.environ[key] = value

    from src.core.config import get_settings

    get_settings.cache_clear()
    settings = get_settings()

    yield {"base_dir": base_dir, "db_path": db_path, "settings": settings}

    from src.db import DBSessionFactory

    DBSessionFactory().teardown()
    get_settings.cache_clear()
    if db_path.exists():
        db_path.unlink()


@pytest.fixture(autouse=True)
def prepare_database(test_environment):
    from src.core.config import get_settings
    from src.db import Base, DBSessionFactory
    from src.util import get_user_role_level
    from tests import factories

    engine = DBSessionFactory().get_engine()
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    get_user_role_level.cache_clear()

    session = DBSessionFactory().make_session()
    try:
        factories.seed_user_roles(session)
        major = factories.create_major(
            session, college="Test College", major_name="Test Major"
        )
        factories.create_scsc_global_status(session)
        factories.create_user(
            session,
            user_id=factories.DEFAULT_EXEC_USER_ID,
            role_level=factories.DEFAULT_ROLE_LEVELS["executive"],
            major=major,
        )
    finally:
        session.close()

    settings = get_settings()
    for directory in (
        Path(settings.file_dir),
        Path(settings.image_dir),
        Path(settings.article_dir),
        Path(settings.w_html_dir),
    ):
        _clean_directory(directory)

    yield


@pytest.fixture(scope="session")
def app(test_environment):
    from main import app as fastapi_app

    return fastapi_app


@pytest.fixture
def client(app):
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def api_headers():
    return {"x-api-secret": os.environ["API_SECRET"]}


@pytest.fixture
def set_current_user(app):
    overrides = app.dependency_overrides

    def _set(user):
        async def override(request, session):
            request.state.user = user

        overrides[user_auth_dependency] = override

    try:
        yield _set
    finally:
        overrides.pop(user_auth_dependency, None)


@pytest.fixture
def doc_file():
    return io.BytesIO(b"%PDF-1.4 test content"), "document.pdf", "application/pdf"


@pytest.fixture
def image_file():
    return io.BytesIO(b"binary image"), "image.png", "image/png"


@pytest.fixture(autouse=True)
def stub_discord(monkeypatch):
    async def _no_reply(*args, **kwargs):
        return None

    async def _reply(*args, **kwargs):
        return True

    monkeypatch.setattr(
        "src.services.scsc.send_discord_bot_request_no_reply", _no_reply
    )
    monkeypatch.setattr("src.services.scsc.send_discord_bot_request", _reply)


@pytest.fixture(autouse=True)
def default_request_user(app, prepare_database):
    session = DBSessionFactory().make_session()
    try:
        user = session.get(User, factories.DEFAULT_EXEC_USER_ID)
    finally:
        session.close()

    if user is None:
        yield
        return

    async def override(request, session):
        request.state.user = user

    app.dependency_overrides[user_auth_dependency] = override
    try:
        yield
    finally:
        app.dependency_overrides.pop(user_auth_dependency, None)
