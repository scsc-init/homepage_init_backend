from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from src.util import get_user, get_user_role_level


class AssertPermissionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if not request.url.path.startswith("/api") or request.method not in (
            "GET",
            "POST",
        ):
            return await call_next(request)
        if request.url.path.startswith("/api/executive"):
            try:
                current_user = get_user(request)
            except HTTPException as e:
                return JSONResponse({"detail": e.detail}, e.status_code)
            if current_user.role < get_user_role_level("executive"):
                return JSONResponse(
                    {"detail": "permission denied: at least executive role required"},
                    403,
                )
        return await call_next(request)
