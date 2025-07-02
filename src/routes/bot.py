from os import path
import uuid
import json
import aio_pika
import asyncio

from fastapi import APIRouter, HTTPException, Request, UploadFile, File
from fastapi.responses import FileResponse

from src.core import get_settings
from src.db import SessionDep
from src.model import FileMetadata

bot_router = APIRouter(tags=['bot'])


@bot_router.get('/bot/general/get_invite', status_code=200)
async def get_discord_invite():
    connection = await aio_pika.connect_robust("amqp://guest:guest@rabbitmq/")
    channel = await connection.channel()

    reply_queue_name = "main_response_queue"
    reply_queue = await channel.declare_queue(reply_queue_name, durable=True)

    correlation_id = str(uuid.uuid4())

    # Send request to bot
    message_body = {
        "action_code": 1001,  # example: get_invite
        "reply_to": reply_queue_name,
        "correlation_id": correlation_id
    }

    message = aio_pika.Message(
        body=json.dumps(message_body).encode(),
        reply_to=reply_queue_name,
        correlation_id=correlation_id
    )

    await channel.default_exchange.publish(
        message, routing_key="bot_queue"
    )

    # Wait for bot's response
    future = asyncio.get_event_loop().create_future()

    async with reply_queue.iterator() as queue_iter:
        async for msg in queue_iter:
            async with msg.process():
                data = json.loads(msg.body)
                if data["correlation_id"] == correlation_id:
                    future.set_result(data["result"])
                    break

    result = await future
    await connection.close()
    return {"result": result}