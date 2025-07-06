from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.util import send_discord_bot_request, send_discord_bot_request_no_reply


bot_router = APIRouter(tags=['bot'])


@bot_router.get('/bot/discord/general/get_invite')
async def get_discord_invite():
    try:
        result = await send_discord_bot_request(action_code=1001)
        return {"result": result}
    except TimeoutError:
        raise HTTPException(status_code=504, detail="Bot did not respond")
    

class BodySendMessageToID(BaseModel):
    id: int
    content: str

@bot_router.post('/bot/discord/general/send_message_to_id', status_code=201)
async def send_message_to_id(body: BodySendMessageToID):
    await send_discord_bot_request_no_reply(action_code=1002, body=body.model_dump())