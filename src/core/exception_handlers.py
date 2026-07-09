from typing import Optional

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from .config import get_settings
from .logger import logger


def cors_headers_for_origin(origin: Optional[str]) -> dict[str, str]:
    if not origin:
        return {}
    settings = get_settings()
    is_allowed = settings.cors_all_accept or origin in settings.cors_whitelist_origins
    if not is_allowed:
        return {}
    return {
        "Access-Control-Allow-Origin": origin,
        "Access-Control-Allow-Credentials": "true",
        "Vary": "Origin",
    }


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception(
        "info_type=unhandled_exception ; method=%s ; path=%s",
        request.method,
        request.url.path,
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error"},
        headers=cors_headers_for_origin(request.headers.get("origin")),
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(Exception, unhandled_exception_handler)
