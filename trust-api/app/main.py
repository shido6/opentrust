import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from .config import LOG_LEVEL
from .routers import decision, health


@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.basicConfig(level=LOG_LEVEL.upper())
    logger = logging.getLogger("trust-api")
    logger.info("OpenTrust SIP Trust API starting")
    yield
    logger.info("OpenTrust SIP Trust API shutting down")


app = FastAPI(
    title="OpenTrust SIP Trust API",
    version="0.1.0",
    description="Carrier-grade SIP trust scoring engine — Policy + Evidence + Analytics",
    lifespan=lifespan,
)

app.include_router(health.router)
app.include_router(decision.router)
