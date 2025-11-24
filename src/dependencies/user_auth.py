from typing import Annotated, Optional

import jwt
from fastapi import Depends, HTTPException, Request

from src.core import get_settings
from src.db import SessionDep
from src.model import User


async def user_auth(request: Request, session: SessionDep):
    settings = get_settings()

    if not settings.user_check:
        user = session.get(
            User,
            "a44946fbf09c326520c2ca0a324b19100381911c9afe5af06a90b636d8f35dd5",
        )  # bot@discord.com
        if user:
            request.state.user = user
        else:
            request.state.user = None
        return

    encoded_jwt = request.headers.get("x-jwt")

    if encoded_jwt is None:
        request.state.user = None
        return

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
        user = session.get(User, decoded_jwt["user_id"])
        if user:
            request.state.user = user
        else:
            request.state.user = None


def get_user(request: Request) -> User:
    """Retrieves the User object set by the authentication dependency, raises exception if no user found."""
    user = request.state.user
    if user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user


UserDep = Annotated[User, Depends(get_user)]


def get_user_optional(request: Request) -> Optional[User]:
    """Retrieves the User object set by the authentication dependency, or None."""
    return getattr(request.state, "user", None)


UserSafeDep = Annotated[Optional[User], Depends(get_user_optional)]
