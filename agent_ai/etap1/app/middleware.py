import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.perf_counter()

        try:
            response = await call_next(request)
        except Exception as error:
            process_time = time.perf_counter() - start_time

            print(
                f"{request.method} {request.url.path} -> ERROR "
                f"({process_time:.4f}s): {error}"
            )

            raise

        process_time = time.perf_counter() - start_time

        print(
            f"{request.method} {request.url.path} -> "
            f"{response.status_code} ({process_time:.4f}s)"
        )

        return response