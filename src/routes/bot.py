from fastapi import APIRouter

from src.services import (
    BodySendDeveloperContact,
    BodySendMessageToID,
    BotServiceDep,
)

bot_router = APIRouter(tags=["bot"])


@bot_router.get("/bot/discord/general/get_invite")
async def get_discord_invite(bot_service: BotServiceDep):
    return await bot_service.get_discord_invite()


@bot_router.post("/bot/discord/general/send_message_to_id", status_code=201)
async def send_message_to_id(body: BodySendMessageToID, bot_service: BotServiceDep):
    await bot_service.send_message_to_id(body=body)


@bot_router.post("/bot/discord/developer/contact", status_code=201)
async def send_developer_contact(
    body: BodySendDeveloperContact,
    bot_service: BotServiceDep,
):
    await bot_service.send_developer_contact(body=body)


@bot_router.get("/bot/discord/status", status_code=200)
async def get_status(bot_service: BotServiceDep):
    return await bot_service.get_status()


@bot_router.post("/bot/discord/login", status_code=204)
async def login_without_permission(bot_service: BotServiceDep):
    await bot_service.login_without_permission()
