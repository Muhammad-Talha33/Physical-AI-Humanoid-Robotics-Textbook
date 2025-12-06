"""Metrics tracking for query latency, retrieval quality, errors, and costs."""
import asyncio
import uuid
from datetime import datetime
from typing import Dict, List, Optional
import asyncpg
from .logger import get_logger
from ..config.settings import settings

logger = get_logger(__name__)


class MetricsTracker:
    """Track and store application metrics."""

    def __init__(self, postgres_pool: Optional[asyncpg.Pool] = None):
        """Initialize metrics tracker."""
        self.pool = postgres_pool
        self._metrics_buffer: List[Dict] = []

    async def track_query_latency(
        self,
        latency_ms: int,
        percentile: Optional[str] = None
    ) -> None:
        """Track query processing latency."""
        await self._record_metric(
            metric_type="query_latency",
            value=float(latency_ms),
            metadata={"percentile": percentile} if percentile else {}
        )

    async def track_retrieval_quality(
        self,
        avg_similarity_score: float,
        results_count: int
    ) -> None:
        """Track retrieval quality metrics."""
        await self._record_metric(
            metric_type="retrieval_quality",
            value=avg_similarity_score,
            metadata={"results_count": results_count}
        )

    async def track_error(
        self,
        error_type: str,
        error_message: Optional[str] = None
    ) -> None:
        """Track error occurrences."""
        await self._record_metric(
            metric_type="error_rate",
            value=1.0,
            metadata={
                "error_type": error_type,
                "error_message": error_message or ""
            }
        )

    async def track_api_cost(
        self,
        cost_usd: float,
        cost_type: str,
        tokens_used: int = 0
    ) -> None:
        """Track API costs."""
        await self._record_metric(
            metric_type="api_cost",
            value=cost_usd,
            metadata={
                "cost_type": cost_type,
                "tokens_used": tokens_used
            }
        )

    async def _record_metric(
        self,
        metric_type: str,
        value: float,
        metadata: Dict
    ) -> None:
        """Record a metric to the database."""
        if not self.pool:
            # Buffer metrics if pool not initialized
            self._metrics_buffer.append({
                "metric_type": metric_type,
                "value": value,
                "metadata": metadata,
                "timestamp": datetime.utcnow()
            })
            return

        try:
            import json
            async with self.pool.acquire() as conn:
                await conn.execute(
                    """
                    INSERT INTO metrics (metric_id, timestamp, metric_type, value, metadata)
                    VALUES ($1, $2, $3, $4, $5)
                    """,
                    uuid.uuid4(),
                    datetime.utcnow(),
                    metric_type,
                    value,
                    json.dumps(metadata)
                )
        except Exception as e:
            logger.error("Failed to record metric", error=str(e), metric_type=metric_type)

    async def get_metrics_summary(
        self,
        time_range: str = "last_24h"
    ) -> Dict:
        """Get aggregated metrics summary."""
        if not self.pool:
            return {}

        try:
            async with self.pool.acquire() as conn:
                # Query latency percentiles
                latency_result = await conn.fetch(
                    """
                    SELECT
                        PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY value) as p50,
                        PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY value) as p95,
                        PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY value) as p99
                    FROM metrics
                    WHERE metric_type = 'query_latency'
                    AND timestamp > NOW() - INTERVAL '24 hours'
                    """
                )

                # Retrieval quality
                retrieval_result = await conn.fetchrow(
                    """
                    SELECT AVG(value) as avg_similarity
                    FROM metrics
                    WHERE metric_type = 'retrieval_quality'
                    AND timestamp > NOW() - INTERVAL '24 hours'
                    """
                )

                # Error rates
                error_result = await conn.fetch(
                    """
                    SELECT
                        metadata->>'error_type' as error_type,
                        COUNT(*) as count
                    FROM metrics
                    WHERE metric_type = 'error_rate'
                    AND timestamp > NOW() - INTERVAL '24 hours'
                    GROUP BY metadata->>'error_type'
                    """
                )

                # API costs
                cost_result = await conn.fetchrow(
                    """
                    SELECT
                        SUM(CASE WHEN metadata->>'cost_type' = 'embedding' THEN value ELSE 0 END) as embedding_cost,
                        SUM(CASE WHEN metadata->>'cost_type' = 'query' THEN value ELSE 0 END) as query_cost,
                        SUM(value) as total_cost
                    FROM metrics
                    WHERE metric_type = 'api_cost'
                    AND timestamp > NOW() - INTERVAL '30 days'
                    """
                )

                return {
                    "time_range": time_range,
                    "query_latency": {
                        "p50": int(latency_result[0]["p50"] or 0),
                        "p95": int(latency_result[0]["p95"] or 0),
                        "p99": int(latency_result[0]["p99"] or 0)
                    },
                    "retrieval_quality": {
                        "avg_similarity_score": float(retrieval_result["avg_similarity"] or 0.0)
                    },
                    "error_rates": {
                        row["error_type"]: row["count"]
                        for row in error_result
                    },
                    "api_costs": {
                        "embedding_generation_usd": float(cost_result["embedding_cost"] or 0.0),
                        "query_processing_usd": float(cost_result["query_cost"] or 0.0),
                        "total_month_to_date_usd": float(cost_result["total_cost"] or 0.0)
                    }
                }

        except Exception as e:
            logger.error("Failed to get metrics summary", error=str(e))
            return {}


# Global metrics tracker instance
metrics_tracker = MetricsTracker()
