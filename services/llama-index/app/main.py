import logging
from contextlib import asynccontextmanager
import time
import random
import asyncio
from concurrent.futures import ThreadPoolExecutor

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import sentry_sdk
from prometheus_client import make_asgi_app

from app.api.router import api_router
from app.core.config import settings
from app.core.logging import setup_logging

logger = logging.getLogger(__name__)

# Configure Sentry for error tracking if enabled
if settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=settings.ENVIRONMENT,
        traces_sample_rate=0.1,
    )

# Setup logging
setup_logging()

# Create a thread pool for background tasks
executor = ThreadPoolExecutor(max_workers=1)


async def index_tables_background():
    """Background task to index tables"""
    try:
        from app.core.index_manager import IndexManager

        logger.info("Starting background indexing...")
        index_manager = IndexManager.get_instance()

        # Index tables with delay between each
        for table in settings.TABLES_TO_INDEX:
            try:
                logger.info(f"Indexing table: {table}")
                result = index_manager.index_table(table)
                if result["success"]:
                    logger.info(f"Successfully indexed table: {table}")
                else:
                    logger.error(
                        f"Failed to index table {table}: {result.get('error')}"
                    )

                # Add a random delay between tables (5-15 seconds)
                if table != settings.TABLES_TO_INDEX[-1]:
                    delay = random.uniform(
                        settings.MIN_TABLE_DELAY, settings.MAX_TABLE_DELAY
                    )
                    logger.info(f"Waiting {delay:.2f} seconds before next table...")
                    await asyncio.sleep(delay)

            except Exception as e:
                logger.error(f"Error indexing table {table}: {e}", exc_info=True)
                continue

        logger.info("Background indexing completed")
    except Exception as e:
        logger.error(f"Error in background indexing: {e}", exc_info=True)


# Startup and shutdown event handlers
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup tasks
    logger.info("Starting up Llama Index RAG API")

    # Start background indexing if enabled
    if settings.PRELOAD_INDEXES:
        # Start indexing in the background
        asyncio.create_task(index_tables_background())
        logger.info("Started background indexing")

    yield

    # Shutdown tasks
    logger.info("Shutting down Llama Index RAG API")
    # Cancel any running background tasks
    for task in asyncio.all_tasks():
        if task is not asyncio.current_task():
            task.cancel()


# Create FastAPI app
app = FastAPI(
    title="Manufacturing MES RAG API",
    description="API for querying manufacturing data using RAG",
    version="1.0.0",
    lifespan=lifespan,
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add Prometheus metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

# Include API routes
app.include_router(api_router, prefix=settings.API_V1_STR)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected error occurred. Please try again later."},
    )


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8080, reload=True)
