"""Rate limiting enforcement using Postgres for persistence."""
import asyncpg
from datetime import datetime, timedelta
from typing import Optional
from ..monitoring.logger import get_logger
from ..config.settings import settings

logger = get_logger(__name__)


class RateLimiter:
    """
    Enforce rate limiting using sliding window algorithm.

    Features:
    - 50 queries/user/hour (configurable)
    - Postgres-backed for persistence across restarts
    - Per-user tracking
    """

    def __init__(
        self,
        db_pool: asyncpg.Pool,
        queries_per_hour: int = None
    ):
        self.db_pool = db_pool
        self.queries_per_hour = queries_per_hour or settings.rate_limit_queries_per_hour

        logger.info("RateLimiter initialized", limit=self.queries_per_hour)

    async def check_rate_limit(
        self,
        user_identifier: str
    ) -> dict:
        """
        Check if user has exceeded rate limit.

        Args:
            user_identifier: User identifier (IP hash or user ID)

        Returns:
            Dict with:
                - allowed: bool
                - remaining: int (queries remaining in window)
                - retry_after_seconds: int (if blocked)
        """
        # Calculate current hourly window
        now = datetime.utcnow()
        window_start = now.replace(minute=0, second=0, microsecond=0)

        async with self.db_pool.acquire() as conn:
            # Get or create rate limit record
            row = await conn.fetchrow(
                """
                SELECT query_count, is_blocked, last_query_at
                FROM rate_limit_trackers
                WHERE user_identifier = $1 AND window_start = $2
                """,
                user_identifier,
                window_start
            )

            if not row:
                # First query in this window - create record
                await conn.execute(
                    """
                    INSERT INTO rate_limit_trackers (user_identifier, window_start, query_count, last_query_at)
                    VALUES ($1, $2, 1, $3)
                    """,
                    user_identifier,
                    window_start,
                    now
                )

                logger.info(
                    "Rate limit created",
                    user=user_identifier,
                    queries_remaining=self.queries_per_hour - 1
                )

                return {
                    "allowed": True,
                    "remaining": self.queries_per_hour - 1,
                    "retry_after_seconds": 0
                }

            query_count = row["query_count"]

            # Check if limit exceeded
            if query_count >= self.queries_per_hour:
                # Calculate time until next window
                next_window = window_start + timedelta(hours=1)
                retry_after = int((next_window - now).total_seconds())

                logger.warning(
                    "Rate limit exceeded",
                    user=user_identifier,
                    query_count=query_count,
                    limit=self.queries_per_hour
                )

                # Mark as blocked
                await conn.execute(
                    """
                    UPDATE rate_limit_trackers
                    SET is_blocked = true
                    WHERE user_identifier = $1 AND window_start = $2
                    """,
                    user_identifier,
                    window_start
                )

                return {
                    "allowed": False,
                    "remaining": 0,
                    "retry_after_seconds": retry_after
                }

            # Increment query count
            await conn.execute(
                """
                UPDATE rate_limit_trackers
                SET query_count = query_count + 1,
                    last_query_at = $1
                WHERE user_identifier = $2 AND window_start = $3
                """,
                now,
                user_identifier,
                window_start
            )

            remaining = self.queries_per_hour - (query_count + 1)

            logger.debug(
                "Rate limit check passed",
                user=user_identifier,
                queries_used=query_count + 1,
                remaining=remaining
            )

            return {
                "allowed": True,
                "remaining": remaining,
                "retry_after_seconds": 0
            }

    async def reset_user_limit(
        self,
        user_identifier: str
    ) -> None:
        """Reset rate limit for a user (admin function)."""
        window_start = datetime.utcnow().replace(minute=0, second=0, microsecond=0)

        async with self.db_pool.acquire() as conn:
            await conn.execute(
                """
                DELETE FROM rate_limit_trackers
                WHERE user_identifier = $1 AND window_start = $2
                """,
                user_identifier,
                window_start
            )

        logger.info("Rate limit reset", user=user_identifier)

    async def cleanup_old_windows(
        self,
        hours_old: int = 24
    ) -> int:
        """Clean up old rate limit tracking records."""
        cutoff = datetime.utcnow() - timedelta(hours=hours_old)

        async with self.db_pool.acquire() as conn:
            result = await conn.execute(
                """
                DELETE FROM rate_limit_trackers
                WHERE window_start < $1
                """,
                cutoff
            )

        count = int(result.split()[-1]) if result else 0

        logger.info("Cleaned up old rate limit records", count=count)

        return count
