from typing import Annotated

import httpx
from fastapi import Depends, HTTPException
from pydantic import BaseModel, Field

from src.core import get_settings, logger
from src.util import send_discord_bot_request, send_discord_bot_request_no_reply


class BodySendMessageToID(BaseModel):
    id: int
    content: str = Field(..., min_length=1, max_length=2000)


class BotService:
    def __init__(
        self,
    ) -> None: ...

    async def get_discord_invite(self):
        try:
            result = await send_discord_bot_request(action_code=1001)
            return {"result": result}
        except TimeoutError:
            logger.error("err_type=bot_discord_get_invite ; err_code=504 ; msg=timeout")
            raise HTTPException(status_code=504, detail="Bot did not respond")
        except Exception as e:
            logger.error(
                f"err_type=bot_discord_get_invite ; err_code=500 ; msg=unexpected error: {e}"
            )
            raise HTTPException(status_code=500, detail="Unexpected error")

    async def send_message_to_id(self, body: BodySendMessageToID):
        await send_discord_bot_request_no_reply(
            action_code=1002, body=body.model_dump()
        )

    async def get_status(self):
        try:
            async with httpx.AsyncClient(
                timeout=httpx.Timeout(5.0, connect=2.0)
            ) as client:
                res = await client.get(f"http://{get_settings().bot_host}:8081/status")
        except httpx.TimeoutException:
            logger.error("err_type=bot_discord_status ; err_code=504 ; msg=timeout")
            raise HTTPException(504, "Bot did not respond")
        except httpx.RequestError as e:
            logger.error(
                f"err_type=bot_discord_status ; err_code=400 ; msg=request error: {e}"
            )
            raise HTTPException(400, str(e))
        if res.status_code != 200:
            logger.error(
                f"err_type=bot_discord_status ; err_code=400 ; msg=fetch failed: {res.text}"
            )
            raise HTTPException(400, res.text)
        return res.json()

    async def login_without_permission(self):
        try:
            async with httpx.AsyncClient(
                timeout=httpx.Timeout(5.0, connect=2.0)
            ) as client:
                res = await client.post(f"http://{get_settings().bot_host}:8081/login")
        except httpx.TimeoutException:
            logger.error("err_type=bot_discord_login ; err_code=504 ; msg=timeout")
            raise HTTPException(504, "Bot did not respond")
        except httpx.RequestError as e:
            logger.error(
                f"err_type=bot_discord_login ; err_code=400 ; msg=request error: {e}"
            )
            raise HTTPException(400, str(e))
        if res.status_code != 204:
            logger.error(
                f"err_type=bot_discord_login ; err_code=400 ; msg=login failed: {res.text}"
            )
            raise HTTPException(400, res.text)
        return


BotServiceDep = Annotated[BotService, Depends()]
