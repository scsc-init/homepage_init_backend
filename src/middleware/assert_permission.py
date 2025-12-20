from fastapi import HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware

from src.db.engine import DBSessionFactory
from src.dependencies.user_auth import resolve_request_user
from src.util import get_user_role_level


class AssertPermissionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if not request.url.path.startswith("/api") or request.method not in (
            "GET",
            "POST",
        ):
            return await call_next(request)

        user = self._resolve_user(request)
        request.state.user = user

        if request.url.path.startswith("/api/executive"):
            if user is None:
                raise HTTPException(status_code=401, detail="Not authenticated")
            if user.role < get_user_role_level("executive"):
                raise HTTPException(
                    status_code=403,
                    detail="Permission denied: at least executive role required",
                )

        return await call_next(request)

    def _resolve_user(self, request: Request):
        session = DBSessionFactory().make_session()
        try:
            return resolve_request_user(request, session)
        finally:
            session.close()
