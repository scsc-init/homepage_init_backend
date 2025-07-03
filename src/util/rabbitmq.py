import aio_pika
import json
import uuid
import asyncio

from src.core import get_settings


async def send_discord_bot_request(action_code: int, body: dict|None = None, timeout=5):
    correlation_id = str(uuid.uuid4())
    body = body or {}

    connection = await aio_pika.connect_robust(f"amqp://guest:guest@{get_settings().rabbitmq_host}/")
    channel = await connection.channel()

    reply_queue = await channel.declare_queue(get_settings().reply_queue, durable=True)

    message = aio_pika.Message(
        body=json.dumps({
            "action_code": action_code,
            "body": body,
            "reply_to": get_settings().reply_queue,
            "correlation_id": correlation_id}).encode(),
        reply_to=get_settings().reply_queue,
        correlation_id=correlation_id)

    await channel.default_exchange.publish(message, routing_key=get_settings().discord_receive_queue)

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


async def send_discord_bot_request_no_reply(action_code: int, body: dict|None = None):
    connection = await aio_pika.connect_robust(f"amqp://guest:guest@{get_settings().rabbitmq_host}/")
    channel = await connection.channel()

    message = aio_pika.Message(body=json.dumps({ "action_code": action_code, "body": body or {} }).encode())

    await channel.default_exchange.publish(message, routing_key=get_settings().discord_receive_queue)
    await connection.close()