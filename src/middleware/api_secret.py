from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from ..core.config import check_api_secret


class APISecretMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if not request.url.path.startswith('/api'):
            return await call_next(request)
        x_api_secret = request.headers.get('x-api-secret')
        if x_api_secret is None:
            return JSONResponse({"detail": "No x-api-secret included"}, 401)
        if not check_api_secret(x_api_secret):
            return JSONResponse({"detail": "Invalid x-api-secret"}, 401)
        return await call_next(request)
