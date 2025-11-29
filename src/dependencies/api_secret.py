from fastapi import HTTPException, Request

from src.core import get_settings

from .user_auth import NullableUserDep


async def api_secret(request: Request, current_user: NullableUserDep):
    if not request.url.path.startswith("/api") or request.method not in (
        "GET",
        "POST",
    ):
        return
    if current_user is not None:
        return
    else:
        x_api_secret = request.headers.get("x-api-secret")
        if x_api_secret is None:
            raise HTTPException(status_code=401, detail="No x-api-secret included")
        if x_api_secret != get_settings().api_secret:
            raise HTTPException(status_code=401, detail="Invalid x-api-secret")
        return
