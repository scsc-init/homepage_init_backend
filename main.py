import logging.config
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Mount Static Files
from fastapi.staticfiles import StaticFiles

# Middleware
from src.core import get_settings

# Dependencies
from src.dependencies import check_user_status, user_auth
from src.middleware import (
    AssertPermissionMiddleware,
    HTTPLoggerMiddleware,
)

# Route
from src.routes import root_router

# Logger
from src.util import LOGGING_CONFIG

logging.config.dictConfig(LOGGING_CONFIG)

# RabbitMQ
from src.amqp import mq_client
from src.core import logger


# Lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    if not get_settings().rabbitmq_required:
        logger.warning(
            "Startup Warning: RabbitMQ connection is not enabled via environment variable RABBITMQ_REQUIRED. "
            "The application will start, but amqp features will be unavailable."
        )
    else:
        try:
            await mq_client.connect()

        except Exception:
            logger.error("Startup Failed: RabbitMQ is required but could not connect.")
            raise

    yield

    await mq_client.close()


app = FastAPI(
    dependencies=[
        Depends(user_auth),
        Depends(check_user_status),
    ],
    lifespan=lifespan,
)

# CORS must be first
if get_settings().cors_all_accept:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Custom middleware follows
# NOTE: Starlette executes middlewares in reverse order of addition.
# Request flow (outer -> inner): HTTPLogger -> AssertPermission
app.add_middleware(AssertPermissionMiddleware)
app.add_middleware(HTTPLoggerMiddleware)

app.include_router(root_router)

app.mount("/static", StaticFiles(directory="static"), name="static")
