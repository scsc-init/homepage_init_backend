"""/main.py"""

# Dependency
import logging.config

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Mount Static Files
from fastapi.staticfiles import StaticFiles

# Middleware
from src.core import get_settings
from src.middleware import (
    APISecretMiddleware,
    AssertPermissionMiddleware,
    CheckUserStatusMiddleware,
    HTTPLoggerMiddleware,
    UserAuthMiddleware,
)

# Route
from src.routes import root_router

# Logger
from src.util import LOGGING_CONFIG

logging.config.dictConfig(LOGGING_CONFIG)

app = FastAPI()

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
# Request flow (outer → inner): APISecret → UserAuth → HTTPLogger → AssertPermission → CheckUserStatus
app.add_middleware(CheckUserStatusMiddleware)
app.add_middleware(AssertPermissionMiddleware)
app.add_middleware(HTTPLoggerMiddleware)
app.add_middleware(UserAuthMiddleware)
app.add_middleware(APISecretMiddleware)

app.include_router(root_router)

app.mount("/static", StaticFiles(directory="static"), name="static")
