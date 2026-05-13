import time

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.logger import logger


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.perf_counter()

        response = await call_next(request)

        process_time = time.perf_counter() - start_time

        logger.info(
            f"{request.method} {request.url.path} -> "
            f"{response.status_code} ({process_time:.4f}s)"
        )

        return response