import os
import re

os.environ.setdefault("API_SECRET", "test-api-secret")
os.environ.setdefault("JWT_SECRET", "test-jwt-secret")
os.environ.setdefault("JWT_VALID_SECONDS", "3600")
os.environ.setdefault("NOTICE_CHANNEL_ID", "1")
os.environ.setdefault("GRANT_CHANNEL_ID", "2")
os.environ.setdefault("DB_USER", "test-user")
os.environ.setdefault("DB_PASSWORD", "test-password")

from src.core import get_settings
from src.services.sms import send_sms


class _FakeResponse:
    def __init__(self, status_code=200, text="ok"):
        self.status_code = status_code
        self.text = text


def test_send_sms_uses_solapi_request_shape(monkeypatch):
    monkeypatch.setenv("SMS_API_KEY", "key-123")
    monkeypatch.setenv("SMS_API_SECRET", "secret-123")
    monkeypatch.setenv("SMS_SENDER", "01099998888")
    monkeypatch.delenv("SMS_API_URL", raising=False)
    get_settings.cache_clear()

    captured = {}

    class _FakeAsyncClient:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def post(self, url, json=None, headers=None):
            captured["url"] = url
            captured["json"] = json
            captured["headers"] = headers
            return _FakeResponse(200, "ok")

    monkeypatch.setattr("src.services.sms.httpx.AsyncClient", _FakeAsyncClient)

    import asyncio

    asyncio.run(send_sms("01012345678", "hello"))

    assert captured["url"] == "https://api.solapi.com/messages/v4/send-many"
    assert captured["json"]["messages"][0]["to"] == "01012345678"
    assert captured["json"]["messages"][0]["from"] == "01099998888"
    assert captured["json"]["messages"][0]["text"] == "hello"
    assert captured["json"]["messages"][0]["type"] == "SMS"
    assert captured["headers"]["Content-Type"] == "application/json"
    assert captured["headers"]["Authorization"].startswith("HMAC-SHA256 ")
    assert re.search(r"apiKey=key-123", captured["headers"]["Authorization"])
    assert re.search(r"signature=[0-9a-f]{64}", captured["headers"]["Authorization"])


def test_send_sms_is_noop_when_not_configured(monkeypatch):
    monkeypatch.delenv("SMS_API_KEY", raising=False)
    monkeypatch.delenv("SMS_API_SECRET", raising=False)
    monkeypatch.delenv("SMS_SENDER", raising=False)
    get_settings.cache_clear()

    called = {"post": False}

    class _FakeAsyncClient:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def post(self, *args, **kwargs):
            called["post"] = True
            return _FakeResponse(200, "ok")

    monkeypatch.setattr("src.services.sms.httpx.AsyncClient", _FakeAsyncClient)

    import asyncio

    asyncio.run(send_sms("01012345678", "hello"))
    assert called["post"] is False
