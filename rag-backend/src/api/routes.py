"""API route definitions."""
import uuid
import asyncpg
from datetime import datetime
from fastapi import APIRouter, HTTPException, status, Depends, Header
from .models import (
    QueryRequest,
    QueryResponse,
    Citation,
    HealthResponse,
    MetricsResponse,
    ErrorResponse,
    ServiceStatus,
    HealthMetrics
)
from ..monitoring.logger import get_logger, set_correlation_id
from ..monitoring.metrics import metrics_tracker
from ..retrieval.retriever import Retriever
from ..retrieval.context_builder import ContextBuilder
from ..chat.response_generator import ResponseGenerator
from ..chat.session import ConversationSession
from ..chat.rate_limiter import RateLimiter
from ..config.settings import settings
import tiktoken

logger = get_logger(__name__)

router = APIRouter()


# Admin authentication dependency
async def verify_admin_api_key(x_api_key: str = Header(..., alias="X-API-Key")):
    """
    Verify admin API key for protected endpoints.

    Raises 401 if API key is not configured or doesn't match.
    """
    if not settings.admin_api_key:
        # If no admin key is configured, allow access in development
        if settings.environment == "development":
            logger.warning("Admin API key not configured - allowing access in development mode")
            return True
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Admin API key not configured"
            )

    if x_api_key != settings.admin_api_key:
        logger.warning("Invalid admin API key attempt")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )

    return True

# Initialize components
retriever = Retriever()
context_builder = ContextBuilder()
response_generator = ResponseGenerator()
session_manager = None  # Will be initialized with db_pool
rate_limiter = None  # Will be initialized with db_pool

# Get db pool function (to avoid circular import)
def get_db_pool():
    """Get database pool from main app."""
    from .main import db_pool
    return db_pool


@router.post(
    "/chat/query",
    response_model=QueryResponse,
    responses={
        429: {"model": ErrorResponse, "description": "Rate limit exceeded"},
        503: {"model": ErrorResponse, "description": "Service unavailable"}
    }
)
async def process_query(request: QueryRequest, db_pool: asyncpg.Pool = Depends(get_db_pool)):
    """
    Process a user query and return a grounded response with citations.

    Steps:
    1. Create or retrieve conversation session
    2. Validate query length
    3. Generate query embedding with conversation context
    4. Retrieve relevant chunks from Qdrant
    5. Build context with citations
    6. Generate grounded response using conversation history
    7. Update session with new turn
    8. Log to Postgres
    9. Track metrics
    """
    start_time = datetime.utcnow()

    # Initialize components if needed
    global session_manager, rate_limiter
    if session_manager is None:
        session_manager = ConversationSession(db_pool)
    if rate_limiter is None:
        rate_limiter = RateLimiter(db_pool)

    # Set correlation ID for request tracing
    query_id = uuid.uuid4()
    set_correlation_id(str(query_id))

    # Check rate limit
    user_id = request.user_identifier or "anonymous"
    rate_check = await rate_limiter.check_rate_limit(user_id)

    if not rate_check["allowed"]:
        logger.warning("Rate limit exceeded", user=user_id)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "error": "rate_limit_exceeded",
                "message": f"You've reached the query limit of {settings.rate_limit_queries_per_hour} questions per hour. Please try again later.",
                "retry_after_seconds": rate_check["retry_after_seconds"]
            }
        )

    # Create or use existing session
    if request.session_id:
        session_id = request.session_id
        session_data = await session_manager.get_session(session_id)
        if not session_data:
            # Session not found, create new one
            session_id = await session_manager.create_session(request.user_identifier or "anonymous")
            conversation_history = []
        else:
            conversation_history = session_data["conversation_history"] or []
    else:
        # Create new session
        session_id = await session_manager.create_session(request.user_identifier or "anonymous")
        conversation_history = []

    logger.info(
        "Processing query",
        query_id=str(query_id),
        session_id=str(session_id),
        query_preview=request.query[:100]
    )

    try:
        # Validate query length
        tokenizer = tiktoken.encoding_for_model("gpt-3.5-turbo")
        query_tokens = len(tokenizer.encode(request.query))

        if query_tokens > settings.max_query_length_tokens:
            logger.warning("Query exceeds max length", tokens=query_tokens)
            request.query = request.query[:settings.max_query_length_tokens]

        # Retrieve relevant chunks
        retrieved_chunks = await retriever.retrieve(request.query)

        # Build context
        context_data = context_builder.build_context(retrieved_chunks)

        # Generate response with conversation history
        response_data = await response_generator.generate_response(
            query=request.query,
            context=context_data["formatted_context"],
            citations=context_data["citations"],
            conversation_history=conversation_history
        )

        # Update session with new conversation turn
        await session_manager.update_session(
            session_id=session_id,
            query=request.query,
            response=response_data["response_text"]
        )

        # Calculate processing time
        processing_time_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)

        # Calculate turn number
        turn_number = (len(conversation_history) // 2) + 1

        # Log query to database
        async with db_pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO queries (query_id, session_id, user_identifier, query_text, turn_number, processing_time_ms)
                VALUES ($1, $2, $3, $4, $5, $6)
                """,
                query_id,
                session_id,
                request.user_identifier or "anonymous",
                request.query,
                turn_number,
                processing_time_ms
            )

            # Log retrieved contexts
            for chunk in retrieved_chunks:
                await conn.execute(
                    """
                    INSERT INTO retrieved_contexts (query_id, chunk_id, similarity_score, rank, was_used_in_response)
                    VALUES ($1, $2, $3, $4, $5)
                    """,
                    query_id,
                    uuid.UUID(chunk.chunk_id),
                    chunk.similarity_score,
                    chunk.rank,
                    True
                )

            # Log response
            import json
            await conn.execute(
                """
                INSERT INTO responses (query_id, response_text, source_citations, grounding_status, generation_time_ms, openai_tokens_used)
                VALUES ($1, $2, $3, $4, $5, $6)
                """,
                query_id,
                response_data["response_text"],
                json.dumps(context_data["citations"]),
                response_data["grounding_status"],
                processing_time_ms,
                response_data["tokens_used"]
            )

        # Track metrics
        await metrics_tracker.track_query_latency(processing_time_ms)

        if retrieved_chunks:
            avg_similarity = sum(c.similarity_score for c in retrieved_chunks) / len(retrieved_chunks)
            await metrics_tracker.track_retrieval_quality(avg_similarity, len(retrieved_chunks))

        # Track API cost (rough estimate)
        cost = (response_data["tokens_used"] / 1_000_000) * 0.002  # GPT-3.5-turbo pricing
        await metrics_tracker.track_api_cost(cost, "query", response_data["tokens_used"])

        # Build response
        citations_list = [
            Citation(
                chapter=c["chapter"],
                section=c["section"],
                chunk_id=uuid.UUID(c["chunk_id"])
            )
            for c in context_data["citations"]
        ]

        logger.info(
            "Query processed successfully",
            query_id=str(query_id),
            processing_time_ms=processing_time_ms,
            grounding_status=response_data["grounding_status"]
        )

        return QueryResponse(
            session_id=session_id,
            query_id=query_id,
            response=response_data["response_text"],
            citations=citations_list,
            processing_time_ms=processing_time_ms,
            grounding_status=response_data["grounding_status"]
        )

    except Exception as e:
        logger.error("Query processing failed", error=str(e), query_id=str(query_id))
        await metrics_tracker.track_error("query_processing_error", str(e))

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="I'm experiencing technical difficulties right now. Please try again in a moment."
        )


@router.get("/health", response_model=HealthResponse)
async def health_check(db_pool: asyncpg.Pool = Depends(get_db_pool)):
    """
    Check the health status of the API and its dependencies.

    Returns status of Qdrant, Postgres, and OpenAI services.
    """
    services = {}
    overall_status = "healthy"

    # Check Qdrant
    try:
        from ..retrieval.qdrant_client import QdrantVectorStore
        qdrant_store = QdrantVectorStore()
        qdrant_start = datetime.utcnow()
        is_healthy = qdrant_store.health_check()
        qdrant_latency = int((datetime.utcnow() - qdrant_start).total_seconds() * 1000)

        services["qdrant"] = ServiceStatus(
            status="up" if is_healthy else "down",
            latency_ms=qdrant_latency,
            last_check=datetime.utcnow().isoformat()
        )

        if not is_healthy:
            overall_status = "degraded"

    except Exception as e:
        logger.error("Qdrant health check failed", error=str(e))
        services["qdrant"] = ServiceStatus(
            status="down",
            latency_ms=None,
            last_check=datetime.utcnow().isoformat()
        )
        overall_status = "degraded"

    # Check Postgres
    try:
        pg_start = datetime.utcnow()
        async with db_pool.acquire() as conn:
            await conn.fetchval("SELECT 1")
        pg_latency = int((datetime.utcnow() - pg_start).total_seconds() * 1000)

        services["postgres"] = ServiceStatus(
            status="up",
            latency_ms=pg_latency,
            last_check=datetime.utcnow().isoformat()
        )

    except Exception as e:
        logger.error("Postgres health check failed", error=str(e))
        services["postgres"] = ServiceStatus(
            status="down",
            latency_ms=None,
            last_check=datetime.utcnow().isoformat()
        )
        overall_status = "unhealthy"

    # OpenAI status (no active check, just report as available)
    services["openai"] = ServiceStatus(
        status="assumed_up",
        latency_ms=None,
        last_check=datetime.utcnow().isoformat()
    )

    # Get basic metrics
    try:
        async with db_pool.acquire() as conn:
            # Queries in last hour
            queries_last_hour = await conn.fetchval(
                """
                SELECT COUNT(*)
                FROM queries
                WHERE timestamp > NOW() - INTERVAL '1 hour'
                """
            )

            # Average p95 latency
            avg_latency = await conn.fetchval(
                """
                SELECT PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY processing_time_ms)
                FROM queries
                WHERE timestamp > NOW() - INTERVAL '1 hour'
                """
            )

        metrics = HealthMetrics(
            avg_query_latency_p95_ms=int(avg_latency or 0),
            queries_last_hour=queries_last_hour or 0,
            error_rate_percent=0.0  # TODO: Calculate from error logs
        )

    except Exception as e:
        logger.error("Failed to fetch health metrics", error=str(e))
        metrics = HealthMetrics(
            avg_query_latency_p95_ms=0,
            queries_last_hour=0,
            error_rate_percent=0.0
        )

    return HealthResponse(
        status=overall_status,
        services=services,
        metrics=metrics
    )


@router.get("/metrics", response_model=MetricsResponse)
async def get_metrics(_: bool = Depends(verify_admin_api_key)):
    """
    Get aggregated metrics for monitoring and cost tracking.

    Protected admin endpoint - requires X-API-Key header with valid admin API key.
    """
    # Get metrics summary from tracker
    summary = await metrics_tracker.get_metrics_summary(time_range="last_24h")

    if not summary:
        # Return empty metrics if not available
        from .models import (
            QueryLatencyMetrics,
            RetrievalQualityMetrics,
            ApiCostMetrics
        )

        return MetricsResponse(
            time_range="last_24h",
            query_latency=QueryLatencyMetrics(p50=0, p95=0, p99=0),
            retrieval_quality=RetrievalQualityMetrics(avg_similarity_score=0.0),
            error_rates={},
            api_costs=ApiCostMetrics(
                embedding_generation_usd=0.0,
                query_processing_usd=0.0,
                total_month_to_date_usd=0.0
            )
        )

    from .models import (
        QueryLatencyMetrics,
        RetrievalQualityMetrics,
        ApiCostMetrics
    )

    return MetricsResponse(
        time_range=summary["time_range"],
        query_latency=QueryLatencyMetrics(**summary["query_latency"]),
        retrieval_quality=RetrievalQualityMetrics(**summary["retrieval_quality"]),
        error_rates=summary["error_rates"],
        api_costs=ApiCostMetrics(**summary["api_costs"])
    )
