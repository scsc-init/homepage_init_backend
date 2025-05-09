"""/main.py"""

# Dependency
from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

# Middleware
from src.middleware.api_secret import APISecretMiddleware
from src.middleware.assert_permission import AssertPermissionMiddleware
# Environment
from src.core.config import get_session_secret
# Route
from src.routes.root import root_router

app = FastAPI()

app.add_middleware(AssertPermissionMiddleware)
app.add_middleware(APISecretMiddleware)
app.add_middleware(
    SessionMiddleware,
    secret_key=get_session_secret(),
    session_cookie="session_id",
    max_age=1800, # 1800 sec = 30 min
    # same_site="strict",
    https_only=False,
)

app.include_router(root_router)