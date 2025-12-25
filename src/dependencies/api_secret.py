from fastapi import HTTPException, Request

from src.core import get_settings


async def api_secret(request: Request):
    path = request.url.path
    if path not in (
        "/api/user/login",
        "/api/user/create",
    ):
        return

    x_api_secret = request.headers.get("x-api-secret")
    if x_api_secret is None:
        raise HTTPException(status_code=401, detail="No x-api-secret included")
    if x_api_secret != get_settings().api_secret:
        raise HTTPException(status_code=401, detail="Invalid x-api-secret")
