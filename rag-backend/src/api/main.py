"""FastAPI application setup and configuration."""
import asyncpg
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from ..config.settings import settings
from ..monitoring.logger import get_logger
from ..monitoring.metrics import metrics_tracker

logger = get_logger(__name__)

# Global database pool
db_pool: asyncpg.Pool = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan events."""
    global db_pool

    # Startup
    logger.info("Starting RAG backend API...")

    try:
        # Initialize database connection pool
        db_pool = await asyncpg.create_pool(
            host=settings.postgres_host,
            port=settings.postgres_port,
            database=settings.postgres_db,
            user=settings.postgres_user,
            password=settings.postgres_password,
            ssl="require" if settings.postgres_sslmode == "require" else None,
            min_size=2,
            max_size=10
        )

        # Initialize metrics tracker with pool
        metrics_tracker.pool = db_pool

        logger.info("Database connection pool initialized")

    except Exception as e:
        logger.error("Failed to initialize database pool", error=str(e))
        raise

    yield

    # Shutdown
    logger.info("Shutting down RAG backend API...")

    if db_pool:
        await db_pool.close()
        logger.info("Database connection pool closed")


# Create FastAPI application
app = FastAPI(
    title="RAG Chatbot API",
    description="Retrieval-Augmented Generation API for Physical AI & Humanoid Robotics Book",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure based on deployment domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and include routes
from .routes import router
app.include_router(router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "RAG Chatbot API",
        "version": "1.0.0",
        "status": "running"
    }


# db_pool is accessed directly by routes module to avoid circular import
