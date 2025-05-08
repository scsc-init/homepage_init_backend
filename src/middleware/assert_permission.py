from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from ..db.engine import SessionLocal
from ..auth.login import get_current_user
from ..model.user import UserRole


class AssertPermissionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path.startswith("/api/executive"):
            try:
                with SessionLocal() as session:
                    current_user = get_current_user(request, session)
            except HTTPException as e:
                return JSONResponse({"detail":e.detail}, e.status_code)
            if current_user.role not in (UserRole.executive, UserRole.president):
                return JSONResponse({"detail":"permission denied: at least executive role required"}, 403)
        return await call_next(request)