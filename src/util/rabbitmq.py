import asyncio
import json
import uuid

import aio_pika
from sqlmodel import select

from src.core import get_settings
from src.db import SessionDep
from src.model import UserRole


async def send_discord_bot_request(
    action_code: int, body: dict | None = None, timeout=5
):
    """
    Sends request to bot server through rabbitmq, returns reply from bot server.
    Raises TimeoutError if bot fails to respond in time.
    """
    correlation_id = str(uuid.uuid4())
    body = body or {}

    connection = await aio_pika.connect_robust(
        f"amqp://guest:guest@{get_settings().rabbitmq_host}/"
    )
    channel = await connection.channel()

    reply_queue = await channel.declare_queue(get_settings().reply_queue, durable=True)

    message = aio_pika.Message(
        body=json.dumps(
            {
                "action_code": action_code,
                "body": body,
                "reply_to": get_settings().reply_queue,
                "correlation_id": correlation_id,
            }
        ).encode(),
        reply_to=get_settings().reply_queue,
        correlation_id=correlation_id,
    )

    await channel.default_exchange.publish(
        message, routing_key=get_settings().discord_receive_queue
    )

    future = asyncio.get_event_loop().create_future()

    async with reply_queue.iterator() as queue_iter:
        async for msg in queue_iter:
            async with msg.process():
                payload = json.loads(msg.body)
                if payload.get("correlation_id") == correlation_id:
                    future.set_result(payload.get("result"))
                    break

    try:
        result = await asyncio.wait_for(future, timeout=timeout)
    except asyncio.TimeoutError:
        raise TimeoutError("Bot response timed out")

    await connection.close()
    return result


async def send_discord_bot_request_no_reply(action_code: int, body: dict | None = None):
    """
    Sends request to bot server through rabbitmq.
    Handles requests that do not expect a response from the bot server.
    No return value.
    """
    connection = await aio_pika.connect_robust(
        f"amqp://guest:guest@{get_settings().rabbitmq_host}/"
    )
    channel = await connection.channel()

    message = aio_pika.Message(
        body=json.dumps({"action_code": action_code, "body": body or {}}).encode()
    )

    await channel.default_exchange.publish(
        message, routing_key=get_settings().discord_receive_queue
    )
    await connection.close()


async def change_discord_role(
    session: SessionDep, discord_id: int, to_role_name: str
) -> None:
    """
    Change role of user by removing all possible roles and adding new one.
    """
    for role in session.scalars(select(UserRole)).all():
        await send_discord_bot_request_no_reply(
            action_code=2002, body={"user_id": discord_id, "role_name": role.name}
        )
    await send_discord_bot_request_no_reply(
        action_code=2001, body={"user_id": discord_id, "role_name": to_role_name}
    )
