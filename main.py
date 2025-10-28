from fastapi import FastAPI
from contextlib import asynccontextmanager
from prometheus_fastapi_instrumentator import Instrumentator, metrics

from app.api.main_router import api_router
from app.middleware.logging_middleware import LoggingMiddleware
from app.db.mongo_session import connect_to_mongo, close_mongo_connection
from app.utils.logger_util import logger

# Prometheus metrics setup
instrumentator = (
    Instrumentator()
    .add(metrics.latency())
    .add(metrics.request_size())
    .add(metrics.response_size())
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handles startup and shutdown events."""
    await connect_to_mongo()
    logger.info("Connected to MongoDB")

    instrumentator.expose(app)
    logger.info("Prometheus metrics exposed at /metrics")

    yield

    await close_mongo_connection()
    logger.info("Application shutdown complete.")

#  Create FastAPI app
app = FastAPI(
    title="Callify",
    description="A FastAPI app with Prometheus metrics & MongoDB request logging.",
    version="1.0.0",
    lifespan=lifespan,
)

# ✅ Add logging middleware
app.add_middleware(LoggingMiddleware)

# ✅ Attach Prometheus instrumentation
instrumentator.instrument(app)

# ✅ Include all routers
app.include_router(api_router)
