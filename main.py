from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

from src.core.config import get_session_secret
from src.middleware.assert_permission import AssertPermissionMiddleware
from src.routes.major import major_router
from src.routes.user import user_router

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

app.include_router(major_router, prefix='/api')
app.include_router(user_router, prefix='/api')