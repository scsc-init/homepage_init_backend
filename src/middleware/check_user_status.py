import logging

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from sqlmodel import literal, select
from starlette.middleware.base import BaseHTTPMiddleware

from src.db import SessionLocal
from src.model import CheckUserStatusRule
from src.util import get_user

logger = logging.getLogger("app")


class CheckUserStatusMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        with SessionLocal() as session:
            query = select(CheckUserStatusRule).where(
                CheckUserStatusRule.method == request.method,
                literal(request.url.path).like(CheckUserStatusRule.path),
            )
            blacklist_rules = session.exec(query).all()

        if blacklist_rules:
            try:
                current_user = get_user(request)
            except HTTPException as e:
                return JSONResponse({"detail": e.detail}, e.status_code)
            for rule in blacklist_rules:
                if rule.user_status == current_user.status:
                    logger.info(
                        "info_type=CheckUserStatusMiddleware ; user_id=%s ; status=%s ; method=%s ; path=%s",
                        current_user.id,
                        current_user.status,
                        request.method,
                        request.url.path,
                    )
                    return JSONResponse(
                        {
                            "detail": f"cannot access path={request.url.path} with user status={current_user.status}"
                        },
                        403,
                    )

        return await call_next(request)
