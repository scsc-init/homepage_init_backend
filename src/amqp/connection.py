import asyncio
import json
import uuid
from typing import Any

import aio_pika

from src.core import get_settings


class RabbitMQClient:
    def __init__(self):
        self.connection = None
        self.channel = None
        self.callback_queue = None
        self.futures: dict[str, asyncio.Future[Any]] = {}

    async def connect(self):
        """Initializes connection, channel, and the callback consumer."""
        self.connection = await aio_pika.connect_robust(
            f"amqp://guest:guest@{get_settings().rabbitmq_host}/"
        )
        self.channel = await self.connection.channel()
        self.callback_queue = await self.channel.declare_queue(
            "", exclusive=True, auto_delete=True
        )

        await self.callback_queue.consume(self.on_response, no_ack=True)

    async def close(self):
        if self.connection:
            await self.connection.close()

    async def on_response(self, message: aio_pika.abc.AbstractIncomingMessage):
        """
        Background listener. When a message comes back:
        1. Check the correlation_id.
        2. Find the waiting Future in self.futures.
        3. Set the result so the waiting function can proceed.
        """
        correlation_id = message.correlation_id
        if correlation_id is None:
            return
        future = self.futures.pop(correlation_id, None)

        if future:
            try:
                payload = json.loads(message.body)
                future.set_result(payload)
            except Exception as e:
                future.set_exception(e)

    async def send_discord_bot_request(
        self, action_code: int, body: dict | None = None, timeout: int = 5
    ) -> Any:
        """
        RPC: Sends request to bot server through rabbitmq, returns reply from bot server.
        Raises TimeoutError if bot fails to respond in time.
        """
        if not self.channel or not self.callback_queue:
            raise RuntimeError(
                "Connection not established with bot server. Call connect() first."
            )

        correlation_id = str(uuid.uuid4())
        loop = asyncio.get_running_loop()

        future = loop.create_future()
        self.futures[correlation_id] = future

        message = aio_pika.Message(
            body=json.dumps(
                {
                    "action_code": action_code,
                    "body": body or {},
                    "reply_to": self.callback_queue.name,
                    "correlation_id": correlation_id,
                }
            ).encode(),
            reply_to=self.callback_queue.name,
            correlation_id=correlation_id,
        )

        await self.channel.default_exchange.publish(
            message, routing_key=get_settings().discord_receive_queue
        )

        try:
            response = await asyncio.wait_for(future, timeout=timeout)
            return response.get("result")

        except asyncio.TimeoutError:
            self.futures.pop(correlation_id, None)
            raise TimeoutError("Bot response timed out")

    async def send_discord_bot_request_no_reply(
        self, action_code: int, body: dict | None = None
    ):
        """
        Fire-and-Forget: Sends request to bot server through rabbitmq.
        Handles requests that do not expect a response from the bot server.
        No return value.
        """
        if not self.channel:
            raise RuntimeError("RabbitMQ client is not connected.")

        message = aio_pika.Message(
            body=json.dumps({"action_code": action_code, "body": body or {}}).encode()
        )

        await self.channel.default_exchange.publish(
            message, routing_key=get_settings().discord_receive_queue
        )


mq_client = RabbitMQClient()
