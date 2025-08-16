from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import httpx
import logging

from src.util import send_discord_bot_request, send_discord_bot_request_no_reply
from src.core import get_settings

logger = logging.getLogger("app")

bot_router = APIRouter(tags=['bot'])


@bot_router.get('/bot/discord/general/get_invite')
async def get_discord_invite():
    try:
        result = await send_discord_bot_request(action_code=1001)
        return {"result": result}
    except TimeoutError:
        logger.error(f'\nerr_type=bot_discord_get_invite \n err_code=504 \nmsg=timeout')
        raise HTTPException(status_code=504, detail="Bot did not respond")
    except Exception as e:
        logger.error(f'\nerr_type=bot_discord_get_invite \n err_code=500 \nmsg=unexpected error: {e}')   

class BodySendMessageToID(BaseModel):
    id: int
    content: str

@bot_router.post('/bot/discord/general/send_message_to_id', status_code=201)
async def send_message_to_id(body: BodySendMessageToID):
    await send_discord_bot_request_no_reply(action_code=1002, body=body.model_dump())
    
    
@bot_router.get('/bot/discord/status', status_code=200)
async def get_status():
    async with httpx.AsyncClient() as client:
        res = await client.get(f"http://{get_settings().bot_host}:8081/status")
        if res.status_code != 200:
            logger.error(f'\nerr_type=bot_discord_status \n err_code=400 \nmsg=fetch failed: {res.text}')
            raise HTTPException(400, res.text)
        return res.json()
    
    
@bot_router.post('/executive/bot/discord/login', status_code=204)
async def login():
    async with httpx.AsyncClient() as client:
        res = await client.post(f"http://{get_settings().bot_host}:8081/login")
        if res.status_code != 204: 
            logger.error(f'\nerr_type=bot_discord_login \n err_code=400 \nmsg=login failed: {res.text}')
            raise HTTPException(400, res.text)
        return
