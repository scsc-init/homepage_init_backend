import jwt
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from src.core import get_settings
from src.db import SessionLocal
from src.model import User


class UserAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if not get_settings().user_check:  # for development
            with SessionLocal() as session:
                user = session.get(
                    User,
                    "12350b93cae7322f29d409e12a998a598c703780c5f00c99ddf372c38817e4f4",
                )  # exec@example.com
                if user:
                    request.state.user = user
                else:
                    request.state.user = None
            return await call_next(request)

        encoded_jwt = request.headers.get("x-jwt")
        if encoded_jwt is None:
            request.state.user = None
        else:
            try:
                decoded_jwt = jwt.decode(
                    encoded_jwt,
                    get_settings().jwt_secret,
                    algorithms=["HS256"],
                    options={"require": ["user_id", "exp"], "verify_exp": True},
                )
            except jwt.exceptions.ExpiredSignatureError:
                request.state.user = None
            except jwt.exceptions.InvalidSignatureError:
                request.state.user = None
            except jwt.exceptions.MissingRequiredClaimError:
                request.state.user = None
            except jwt.exceptions.InvalidTokenError:
                request.state.user = None
            else:
                with SessionLocal() as session:
                    user = session.get(User, decoded_jwt["user_id"])
                    if user:
                        request.state.user = user
                    else:
                        request.state.user = None

        return await call_next(request)
