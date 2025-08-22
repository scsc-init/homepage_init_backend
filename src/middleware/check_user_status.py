from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from sqlalchemy import text
from starlette.middleware.base import BaseHTTPMiddleware

from src.db import SessionLocal
from src.util import get_user


class CheckUserStatusMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        with SessionLocal() as session:
            raw_sql = """
                SELECT *
                FROM check_user_status_rule
                WHERE method = :method AND :path LIKE path
            """
            blacklist_rules = session.exec(text(raw_sql).bindparams(method=request.method, path=request.url.path)).all()  # type: ignore

        if blacklist_rules:
            try:
                current_user = get_user(request)
            except HTTPException as e:
                return JSONResponse({"detail": e.detail}, e.status_code)
            for rule in blacklist_rules:
                if rule.user_status == current_user.status: return JSONResponse({"detail": f"cannot access path={request.url.path} with user status={current_user.status}"}, 403)

        return await call_next(request)
