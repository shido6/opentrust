import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from .config import LOG_LEVEL
from .telemetry import setup_telemetry
from .middleware.auth import APIKeyMiddleware
from .routers import health, decision, dno, policies, feedback, redress, calls


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_telemetry(app)
    logger = logging.getLogger("trust-api")
    logger.info("OpenTrust SIP Trust API starting", extra={"version": "0.2.0"})
    yield
    logger.info("OpenTrust SIP Trust API shutting down")


app = FastAPI(
    title="OpenTrust SIP Trust API",
    version="0.2.0",
    description="Carrier-grade SIP trust scoring engine — Policy + Evidence + Analytics",
    lifespan=lifespan,
)

# Auth middleware (applied to all routes except /health, /metrics)
app.add_middleware(APIKeyMiddleware)

# Routers
app.include_router(health.router)
app.include_router(decision.router)
app.include_router(dno.router)
app.include_router(policies.router)
app.include_router(feedback.router)
app.include_router(redress.router)
app.include_router(calls.router)
