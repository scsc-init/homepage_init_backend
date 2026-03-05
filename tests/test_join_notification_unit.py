import os
from types import SimpleNamespace

os.environ.setdefault("API_SECRET", "test-api-secret")
os.environ.setdefault("JWT_SECRET", "test-jwt-secret")
os.environ.setdefault("JWT_VALID_SECONDS", "3600")
os.environ.setdefault("NOTICE_CHANNEL_ID", "1")
os.environ.setdefault("GRANT_CHANNEL_ID", "2")
os.environ.setdefault("DB_USER", "test-user")
os.environ.setdefault("DB_PASSWORD", "test-password")

from src.services.join_notification import notify_ig_owner_join_sms


class _FakeUserRepository:
    def __init__(self, owner):
        self._owner = owner

    def get_by_id(self, _owner_id: str):
        return self._owner


def test_notify_ig_owner_join_sms_sends_message(monkeypatch):
    owner = SimpleNamespace(id="owner-1", phone="01012345678")
    joined_user = SimpleNamespace(id="join-1", name="Tester")
    repository = _FakeUserRepository(owner)
    calls = []

    async def fake_send_sms(*, to: str, content: str):
        calls.append({"to": to, "content": content})

    monkeypatch.setattr(
        "src.services.join_notification.send_sms",
        fake_send_sms,
    )

    import asyncio

    asyncio.run(
        notify_ig_owner_join_sms(
            ig_type="sig",
            ig_id=1,
            ig_title="Algo SIG",
            owner_id="owner-1",
            joined_user=joined_user,
            applied_at=None,
            user_repository=repository,
        )
    )

    assert len(calls) == 1
    body = calls[0]
    assert body["to"] == "01012345678"
    assert "Algo SIG" in body["content"]
    assert "Tester" in body["content"]


def test_notify_ig_owner_join_sms_ignores_missing_owner(monkeypatch):
    repository = _FakeUserRepository(None)
    joined_user = SimpleNamespace(id="join-1", name="Tester")
    calls = []

    async def fake_send_sms(*, to: str, content: str):
        calls.append({"to": to, "content": content})

    monkeypatch.setattr(
        "src.services.join_notification.send_sms",
        fake_send_sms,
    )

    import asyncio

    asyncio.run(
        notify_ig_owner_join_sms(
            ig_type="pig",
            ig_id=2,
            ig_title="Web PIG",
            owner_id="owner-x",
            joined_user=joined_user,
            applied_at=None,
            user_repository=repository,
        )
    )

    assert calls == []


def test_notify_ig_owner_join_sms_swallows_send_error(monkeypatch):
    owner = SimpleNamespace(id="owner-1", phone="01012345678")
    joined_user = SimpleNamespace(id="join-1", name="Tester")
    repository = _FakeUserRepository(owner)

    async def failing_send_sms(*, to: str, content: str):
        raise RuntimeError("mq down")

    monkeypatch.setattr(
        "src.services.join_notification.send_sms",
        failing_send_sms,
    )

    import asyncio

    asyncio.run(
        notify_ig_owner_join_sms(
            ig_type="sig",
            ig_id=1,
            ig_title="Algo SIG",
            owner_id="owner-1",
            joined_user=joined_user,
            applied_at=None,
            user_repository=repository,
        )
    )
