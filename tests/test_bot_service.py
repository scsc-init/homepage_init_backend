import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

import src.services.bot as bot_module


def test_send_developer_contact_to_configured_channel(monkeypatch):
    mq_client = SimpleNamespace(
        send_discord_bot_request_no_reply=AsyncMock(),
    )
    settings = SimpleNamespace(developer_contact_channel_id=123456789)

    monkeypatch.setattr(bot_module, "mq_client", mq_client)
    monkeypatch.setattr(bot_module, "get_settings", lambda: settings)

    body = bot_module.BodySendDeveloperContact(
        name="홍길동",
        email="example@snu.ac.kr",
        title="문의 제목",
        content="문의 내용",
    )

    asyncio.run(bot_module.BotService().send_developer_contact(body))

    mq_client.send_discord_bot_request_no_reply.assert_awaited_once_with(
        action_code=1002,
        body={
            "channel_id": 123456789,
            "content": "새로운 개발자 문의가 도착했습니다.",
            "embed": {
                "title": "문의 제목",
                "description": "문의 내용",
                "color": 0x5865F2,
                "fields": [
                    {
                        "name": "문의자",
                        "value": "홍길동",
                        "inline": True,
                    },
                    {
                        "name": "회신 이메일",
                        "value": "example@snu.ac.kr",
                        "inline": True,
                    },
                ],
            },
        },
    )
