from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

from src.middleware.api_secret import APISecretMiddleware
from src.core.config import get_session_secret
from src.middleware.assert_permission import AssertPermissionMiddleware
from src.routes.root import root_router

app = FastAPI()

app.add_middleware(AssertPermissionMiddleware)
app.add_middleware(
    SessionMiddleware,
    secret_key=get_session_secret(),
    session_cookie="session_id",
    max_age=1800, # seconds
    # same_site="strict",
    https_only=True,
)
app.add_middleware(APISecretMiddleware)

app.include_router(root_router)