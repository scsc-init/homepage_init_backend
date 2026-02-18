import asyncio
import json
import uuid
from typing import Any

import aio_pika

from src.core import get_settings, logger


class RabbitMQClient:
    def __init__(self):
        self.connection = None
        self.channel = None
        self.callback_queue = None
        self.consumer_tag = None
        self.futures: dict[str, asyncio.Future[Any]] = {}
        self._lock = asyncio.Lock()

    async def connect(self, retries: int = 5, delay: int = 5):
        """Initializes connection, channel, and the callback consumer."""
        async with self._lock:
            if self.connection and not self.connection.is_closed:
                return
            # NOTE(`guest` and `guest` are each the username and password; for more security these should be moved to configurable env variables)
            dsn = f"amqp://guest:guest@{get_settings().rabbitmq_host}/"

            for attempt in range(retries):
                try:
                    self.connection = await aio_pika.connect_robust(dsn)
                    self.channel = await self.connection.channel()

                    self.callback_queue = await self.channel.declare_queue(
                        "", exclusive=True, auto_delete=True
                    )

                    self.consumer_tag = await self.callback_queue.consume(
                        self.on_response, no_ack=True
                    )

                    logger.info(
                        f"Connected to RabbitMQ on attempt {attempt + 1}. RPC Queue: {self.callback_queue.name}"
                    )
                    return

                except (
                    ConnectionRefusedError,
                    aio_pika.exceptions.AMQPConnectionError,
                ) as e:
                    if attempt < retries - 1:
                        logger.warning(
                            f"RabbitMQ not ready (Attempt {attempt + 1}/{retries}). Retrying in {delay}s..."
                        )
                        await asyncio.sleep(delay)
                    else:
                        logger.critical(
                            "Could not connect to RabbitMQ after multiple attempts."
                        )
                        raise e
                except Exception as e:
                    logger.critical(f"Unexpected error connecting to RabbitMQ: {e}")
                    raise e

    async def close(self):
        async with self._lock:
            if self.futures:
                logger.warning(f"Cancelling {len(self.futures)} pending RPC requests.")
                for correlation_id, future in self.futures.items():
                    if not future.done():
                        future.set_exception(
                            RuntimeError("RabbitMQ connection closing")
                        )
                self.futures.clear()

            if self.channel and not self.channel.is_closed:
                await self.channel.close()

            if self.connection and not self.connection.is_closed:
                await self.connection.close()

            self.connection = None
            self.channel = None
            self.callback_queue = None
            self.consumer_tag = None
            logger.info("RabbitMQ connection closed.")

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
            if future.done():
                return
            try:
                body_str = message.body.decode("utf-8")
                payload = json.loads(body_str)
                future.set_result(payload)
            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                logger.error(f"Failed to decode response for {correlation_id}: {e}")
                future.set_exception(e)
            except Exception as e:
                logger.exception(
                    f"Unexpected error processing response {correlation_id}"
                )
                future.set_exception(e)

    async def send_discord_bot_request(
        self, action_code: int, body: dict | None = None, timeout: int = 5
    ) -> Any:
        """
        RPC: Sends request to bot server through rabbitmq, returns reply from bot server.
        Raises TimeoutError if bot fails to respond in time.
        """
        if (
            not self.connection
            or self.connection.is_closed
            or not self.channel
            or not self.callback_queue
        ):
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
