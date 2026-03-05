import hashlib
import hmac
import secrets
from datetime import datetime, timezone

import httpx

from src.core import get_settings


def _make_solapi_auth_header(api_key: str, api_secret: str) -> str:
    date = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    salt = secrets.token_hex(16)
    signature = hmac.new(
        api_secret.encode("utf-8"),
        f"{date}{salt}".encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return (
        "HMAC-SHA256 "
        f"apiKey={api_key}, "
        f"date={date}, "
        f"salt={salt}, "
        f"signature={signature}"
    )


async def send_sms(to: str, content: str) -> None:
    settings = get_settings()
    if not settings.sms_api_key or not settings.sms_api_secret or not settings.sms_sender:
        return

    url = settings.sms_api_url or "https://api.solapi.com/messages/v4/send-many"

    payload = {
        "messages": [
            {
                "to": to,
                "from": settings.sms_sender,
                "text": content,
                "type": "SMS",
            }
        ]
    }

    headers = {
        "Authorization": _make_solapi_auth_header(
            settings.sms_api_key, settings.sms_api_secret
        ),
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=httpx.Timeout(5.0, connect=2.0)) as client:
        res = await client.post(
            url,
            json=payload,
            headers=headers,
        )
    if res.status_code >= 400:
        raise RuntimeError(
            f"sms provider request failed with status={res.status_code}, body={res.text}"
        )
