from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
import logging

logger = logging.getLogger("uvicorn")

class OperationLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Log the request
        logger.info(f"Request: {request.method} {request.url}")
        
        response = await call_next(request)
        
        # Log the response status
        logger.info(f"Response status: {response.status_code}")
        
        return response
