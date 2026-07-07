import logging
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

from ..config import API_KEYS, API_KEY_HEADER

logger = logging.getLogger("trust-api.auth")


class APIKeyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path in ("/health", "/metrics"):
            return await call_next(request)

        api_key = request.headers.get(API_KEY_HEADER)
        if not api_key:
            logger.warning("Missing API key", extra={"path": str(request.url.path)})
            raise HTTPException(status_code=401, detail="Missing API key")

        principal = API_KEYS.get(api_key)
        if not principal:
            logger.warning("Invalid API key")
            raise HTTPException(status_code=403, detail="Invalid API key")

        request.state.tenant_id = principal.get("tenant_id", "default")
        request.state.role = principal.get("role", "operator")
        request.state.api_key_name = principal.get("name", "unnamed-key")

        return await call_next(request)
