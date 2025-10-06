import logging

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from src.core import get_settings
from src.util import send_discord_bot_request, send_discord_bot_request_no_reply

logger = logging.getLogger("app")

bot_router = APIRouter(tags=["bot"])


@bot_router.get("/bot/discord/general/get_invite")
async def get_discord_invite():
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


class BodySendMessageToID(BaseModel):
    id: int
    content: str = Field(..., min_length=1, max_length=2000)


@bot_router.post("/bot/discord/general/send_message_to_id", status_code=201)
async def send_message_to_id(body: BodySendMessageToID):
    await send_discord_bot_request_no_reply(action_code=1002, body=body.model_dump())


@bot_router.get("/bot/discord/status", status_code=200)
async def get_status():
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(5.0, connect=2.0)) as client:
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


@bot_router.post("/bot/discord/login", status_code=204)
async def login_without_permission():
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(5.0, connect=2.0)) as client:
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
