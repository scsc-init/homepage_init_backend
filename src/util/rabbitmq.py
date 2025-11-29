import asyncio
import json
import uuid

import aio_pika

from src.core import get_settings


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
    try:
        channel = await connection.channel()

        reply_queue = await channel.declare_queue(
            get_settings().reply_queue, durable=True
        )

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

        async def _consume_reply():
            async with reply_queue.iterator() as queue_iter:
                async for msg in queue_iter:
                    async with msg.process():
                        payload = json.loads(msg.body)
                        if payload.get("correlation_id") == correlation_id:
                            return payload.get("result")

        try:
            return await asyncio.wait_for(_consume_reply(), timeout=timeout)
        except asyncio.TimeoutError:
            raise TimeoutError("Bot response timed out") from None

    finally:
        await connection.close()


async def send_discord_bot_request_no_reply(action_code: int, body: dict | None = None):
    """
    Sends request to bot server through rabbitmq.
    Handles requests that do not expect a response from the bot server.
    No return value.
    """
    connection = await aio_pika.connect_robust(
        f"amqp://guest:guest@{get_settings().rabbitmq_host}/"
    )
    try:
        channel = await connection.channel()

        message = aio_pika.Message(
            body=json.dumps({"action_code": action_code, "body": body or {}}).encode()
        )

        await channel.default_exchange.publish(
            message, routing_key=get_settings().discord_receive_queue
        )
    finally:
        await connection.close()
