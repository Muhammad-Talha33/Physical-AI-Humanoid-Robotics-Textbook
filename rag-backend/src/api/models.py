"""Pydantic models for API request/response validation."""
from typing import List, Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    """Request model for chat query endpoint."""

    session_id: Optional[UUID] = Field(
        None,
        description="Session ID for multi-turn conversations. Null for new session."
    )
    query: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="User's question text"
    )
    user_identifier: Optional[str] = Field(
        None,
        description="Optional user identifier for rate limiting"
    )


class Citation(BaseModel):
    """Citation model for source references."""

    chapter: str = Field(..., description="Chapter file path")
    section: str = Field(..., description="Section title")
    chunk_id: UUID = Field(..., description="Unique chunk identifier")


class QueryResponse(BaseModel):
    """Response model for chat query endpoint."""

    session_id: UUID = Field(..., description="Session ID for this conversation")
    query_id: UUID = Field(..., description="Unique query identifier")
    response: str = Field(..., description="Generated response text")
    citations: List[Citation] = Field(
        default_factory=list,
        description="Source citations for the response"
    )
    processing_time_ms: int = Field(..., description="Processing time in milliseconds")
    grounding_status: str = Field(
        ...,
        description="Grounding status: grounded, insufficient_context, or error"
    )


class ServiceStatus(BaseModel):
    """Service health status."""

    status: str = Field(..., description="Service status: up or down")
    latency_ms: Optional[int] = Field(None, description="Latency in milliseconds")
    last_check: Optional[str] = Field(None, description="Last check timestamp (ISO format)")


class HealthMetrics(BaseModel):
    """Health check metrics."""

    avg_query_latency_p95_ms: int
    queries_last_hour: int
    error_rate_percent: float


class HealthResponse(BaseModel):
    """Response model for health check endpoint."""

    status: str = Field(..., description="Overall health status")
    services: Dict[str, ServiceStatus] = Field(
        default_factory=dict,
        description="Status of external services"
    )
    metrics: Optional[HealthMetrics] = Field(None, description="System metrics")


class QueryLatencyMetrics(BaseModel):
    """Query latency percentiles."""

    p50: int
    p95: int
    p99: int


class RetrievalQualityMetrics(BaseModel):
    """Retrieval quality metrics."""

    avg_similarity_score: float
    queries_with_results_percent: Optional[float] = None


class ErrorRateMetrics(BaseModel):
    """Error rate metrics."""

    total_errors: int
    openai_api_errors: int = 0
    qdrant_errors: int = 0
    rate_limit_hits: int = 0


class ApiCostMetrics(BaseModel):
    """API cost metrics."""

    embedding_generation_usd: float
    query_processing_usd: float
    total_month_to_date_usd: float


class MetricsResponse(BaseModel):
    """Response model for metrics endpoint."""

    time_range: str
    query_latency: QueryLatencyMetrics
    retrieval_quality: RetrievalQualityMetrics
    error_rates: Dict[str, int]
    api_costs: ApiCostMetrics


class ErrorResponse(BaseModel):
    """Error response model."""

    error: str = Field(..., description="Error code")
    message: str = Field(..., description="Human-readable error message")
    retry_after_seconds: Optional[int] = Field(None, description="Retry delay in seconds")
    service: Optional[str] = Field(None, description="Service that failed")
