from fastapi import HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware

from src.db import SessionDep, get_session
from src.dependencies import resolve_request_user
from src.util import get_user_role_level


class AssertPermissionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if not request.url.path.startswith("/api") or request.method not in (
            "GET",
            "POST",
        ):
            return await call_next(request)

        if request.url.path.startswith("/api/executive"):
            dependency = get_session()
            try:
                session: SessionDep = next(dependency)
            except StopIteration as exc:
                raise RuntimeError(
                    "get_session dependency did not yield a session"
                ) from exc
            try:
                user = self._resolve_user(request, session)
            except Exception as exc:
                try:
                    dependency.throw(exc)
                except StopIteration:
                    pass
                raise
            else:
                try:
                    next(dependency)
                except StopIteration:
                    pass
            request.state.user = user
            if user is None:
                raise HTTPException(status_code=401, detail="Not authenticated")
            if user.role < get_user_role_level("executive"):
                raise HTTPException(
                    status_code=403,
                    detail="Permission denied: at least executive role required",
                )

        return await call_next(request)

    def _resolve_user(self, request: Request, session: SessionDep):
        return resolve_request_user(request, session)
