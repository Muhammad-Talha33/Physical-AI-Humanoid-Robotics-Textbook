"""Conversation session management with sliding window context."""
import uuid
import asyncpg
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from ..monitoring.logger import get_logger
from ..config.settings import settings

logger = get_logger(__name__)


class ConversationSession:
    """
    Manages multi-turn conversation sessions.

    Features:
    - Session persistence in Postgres
    - Conversation history tracking
    - Sliding window (last 5-10 turns)
    - Auto-expiration of inactive sessions
    """

    def __init__(self, db_pool: asyncpg.Pool):
        self.db_pool = db_pool
        self.max_turns = settings.max_conversation_turns

        logger.info("ConversationSession initialized", max_turns=self.max_turns)

    async def create_session(
        self,
        user_identifier: str = "anonymous"
    ) -> uuid.UUID:
        """
        Create a new conversation session.

        Args:
            user_identifier: User identifier for the session

        Returns:
            Session ID
        """
        session_id = uuid.uuid4()

        async with self.db_pool.acquire() as conn:
            import json
            await conn.execute(
                """
                INSERT INTO conversation_sessions (session_id, user_identifier, conversation_history)
                VALUES ($1, $2, $3)
                """,
                session_id,
                user_identifier,
                json.dumps([])
            )

        logger.info("Session created", session_id=str(session_id))

        return session_id

    async def get_session(
        self,
        session_id: uuid.UUID
    ) -> Optional[Dict]:
        """
        Retrieve session data.

        Args:
            session_id: Session ID to retrieve

        Returns:
            Session data dict or None if not found
        """
        async with self.db_pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT session_id, user_identifier, created_at, last_activity_at,
                       query_count, is_active, conversation_history
                FROM conversation_sessions
                WHERE session_id = $1
                """,
                session_id
            )

        if not row:
            logger.warning("Session not found", session_id=str(session_id))
            return None

        import json
        # Parse conversation_history from JSON string
        conversation_history = row["conversation_history"]
        if isinstance(conversation_history, str):
            conversation_history = json.loads(conversation_history)

        return {
            "session_id": row["session_id"],
            "user_identifier": row["user_identifier"],
            "created_at": row["created_at"],
            "last_activity_at": row["last_activity_at"],
            "query_count": row["query_count"],
            "is_active": row["is_active"],
            "conversation_history": conversation_history
        }

    async def update_session(
        self,
        session_id: uuid.UUID,
        query: str,
        response: str
    ) -> None:
        """
        Update session with new conversation turn.

        Args:
            session_id: Session ID to update
            query: User's query
            response: Assistant's response
        """
        async with self.db_pool.acquire() as conn:
            # Get current history
            row = await conn.fetchrow(
                """
                SELECT conversation_history, query_count
                FROM conversation_sessions
                WHERE session_id = $1
                """,
                session_id
            )

            if not row:
                logger.error("Session not found for update", session_id=str(session_id))
                return

            import json
            # Parse conversation_history from JSON string
            history = row["conversation_history"]
            if isinstance(history, str):
                history = json.loads(history)
            history = history or []

            query_count = row["query_count"] or 0

            # Add new turn to history
            history.append({
                "role": "user",
                "content": query,
                "timestamp": datetime.utcnow().isoformat()
            })
            history.append({
                "role": "assistant",
                "content": response,
                "timestamp": datetime.utcnow().isoformat()
            })

            # Apply sliding window (keep last N turns)
            max_messages = self.max_turns * 2  # Each turn has user + assistant message
            if len(history) > max_messages:
                history = history[-max_messages:]

            # Update session
            import json
            await conn.execute(
                """
                UPDATE conversation_sessions
                SET conversation_history = $1,
                    query_count = $2,
                    last_activity_at = $3
                WHERE session_id = $4
                """,
                json.dumps(history),
                query_count + 1,
                datetime.utcnow(),
                session_id
            )

        logger.info(
            "Session updated",
            session_id=str(session_id),
            turns=len(history) // 2
        )

    async def get_conversation_history(
        self,
        session_id: uuid.UUID
    ) -> List[Dict]:
        """
        Get conversation history for a session.

        Args:
            session_id: Session ID

        Returns:
            List of conversation turns
        """
        session = await self.get_session(session_id)

        if not session:
            return []

        return session["conversation_history"] or []

    async def expire_inactive_sessions(
        self,
        inactive_hours: int = 24
    ) -> int:
        """
        Mark inactive sessions as inactive.

        Args:
            inactive_hours: Hours of inactivity before expiration

        Returns:
            Number of sessions expired
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=inactive_hours)

        async with self.db_pool.acquire() as conn:
            result = await conn.execute(
                """
                UPDATE conversation_sessions
                SET is_active = false
                WHERE last_activity_at < $1
                AND is_active = true
                """,
                cutoff_time
            )

        # Parse result to get count
        count = int(result.split()[-1]) if result else 0

        logger.info("Expired inactive sessions", count=count, cutoff_hours=inactive_hours)

        return count

    async def delete_session(
        self,
        session_id: uuid.UUID
    ) -> bool:
        """
        Delete a session.

        Args:
            session_id: Session ID to delete

        Returns:
            True if deleted, False if not found
        """
        async with self.db_pool.acquire() as conn:
            result = await conn.execute(
                """
                DELETE FROM conversation_sessions
                WHERE session_id = $1
                """,
                session_id
            )

        deleted = result.split()[-1] == "1" if result else False

        if deleted:
            logger.info("Session deleted", session_id=str(session_id))
        else:
            logger.warning("Session not found for deletion", session_id=str(session_id))

        return deleted
