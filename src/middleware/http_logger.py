import logging
import time
import uuid

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from src.util import request_id_var

http_logger = logging.getLogger("http_access")


class HTTPLoggerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        request_id_var.set(request_id)

        start_time = time.time()

        http_logger.info(f"Request: {request.method} {request.url.path}")

        response = await call_next(request)

        process_time = (time.time() - start_time) * 1000
        formatted_process_time = "{0:.2f}".format(process_time)

        http_logger.info(
            f"Response: status_code={response.status_code} duration={formatted_process_time}ms"
        )

        return response
