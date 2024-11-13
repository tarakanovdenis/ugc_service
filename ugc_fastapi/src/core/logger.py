import logging

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


class RequestIDFilter(logging.Filter):
    def __init__(self, request: Request = None):
        super().__init__()
        self.request = request

    def set_request(self, request: Request):
        self.request = request

    def filter(self, record: logging.LogRecord) -> bool:
        if self.request:
            record.request_id = self.request.headers.get('x-request-id')
        else:
            record.request_id = None
        return True


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Attach the request to the log record

        request_id_filter.set_request(request)
        response = await call_next(request)
        return response


logger = logging.getLogger("uvicorn.access")

request_id_filter = RequestIDFilter()
logger.addFilter(request_id_filter)
