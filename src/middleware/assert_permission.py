from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from src.db import DBSessionFactory
from src.dependencies import resolve_request_user
from src.repositories import get_user_role_level


class AssertPermissionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if not request.url.path.startswith("/api") or request.method not in (
            "GET",
            "POST",
        ):
            return await call_next(request)

        if request.url.path.startswith("/api/executive"):
            session = DBSessionFactory().make_session()
            try:
                user = self._resolve_user(request, session)
            finally:
                session.close()
            request.state.user = user
            if user is None:
                return JSONResponse(
                    status_code=401, content={"detail": "Not authenticated"}
                )
            if user.role < get_user_role_level("executive"):
                return JSONResponse(
                    status_code=403,
                    content={
                        "detail": "Permission denied: at least executive role required"
                    },
                )

        return await call_next(request)

    def _resolve_user(self, request: Request, session):
        return resolve_request_user(request, session)
