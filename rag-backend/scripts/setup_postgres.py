"""Initialize Postgres schema for RAG chatbot."""
import sys
import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.config.settings import settings


# SQL schema definitions
SCHEMA_SQL = """
-- Query tracking table
CREATE TABLE IF NOT EXISTS queries (
    query_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID,
    user_identifier VARCHAR(255),
    query_text TEXT NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    turn_number INTEGER DEFAULT 1,
    processing_time_ms INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Retrieved context tracking
CREATE TABLE IF NOT EXISTS retrieved_contexts (
    retrieval_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    query_id UUID REFERENCES queries(query_id) ON DELETE CASCADE,
    chunk_id UUID NOT NULL,
    similarity_score FLOAT NOT NULL,
    rank INTEGER NOT NULL,
    was_used_in_response BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Conversation session management
CREATE TABLE IF NOT EXISTS conversation_sessions (
    session_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_identifier VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_activity_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    query_count INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    conversation_history JSONB DEFAULT '[]'::jsonb
);

-- Response tracking
CREATE TABLE IF NOT EXISTS responses (
    response_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    query_id UUID REFERENCES queries(query_id) ON DELETE CASCADE,
    response_text TEXT NOT NULL,
    source_citations JSONB,
    grounding_status VARCHAR(50) NOT NULL,
    generation_time_ms INTEGER,
    openai_tokens_used INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Rate limiting tracker
CREATE TABLE IF NOT EXISTS rate_limit_trackers (
    user_identifier VARCHAR(255) NOT NULL,
    window_start TIMESTAMP WITH TIME ZONE NOT NULL,
    query_count INTEGER DEFAULT 0,
    last_query_at TIMESTAMP WITH TIME ZONE,
    is_blocked BOOLEAN DEFAULT false,
    PRIMARY KEY (user_identifier, window_start)
);

-- Metrics tracking
CREATE TABLE IF NOT EXISTS metrics (
    metric_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metric_type VARCHAR(100) NOT NULL,
    value FLOAT NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_queries_session_id ON queries(session_id);
CREATE INDEX IF NOT EXISTS idx_queries_timestamp ON queries(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_retrieved_contexts_query_id ON retrieved_contexts(query_id);
CREATE INDEX IF NOT EXISTS idx_conversation_sessions_user ON conversation_sessions(user_identifier);
CREATE INDEX IF NOT EXISTS idx_conversation_sessions_last_activity ON conversation_sessions(last_activity_at DESC);
CREATE INDEX IF NOT EXISTS idx_responses_query_id ON responses(query_id);
CREATE INDEX IF NOT EXISTS idx_rate_limit_trackers_user ON rate_limit_trackers(user_identifier);
CREATE INDEX IF NOT EXISTS idx_metrics_timestamp ON metrics(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_metrics_type ON metrics(metric_type);
"""


def setup_postgres():
    """Create database schema for RAG chatbot."""
    print(f"Connecting to Postgres at {settings.postgres_host}...")

    try:
        # Connect to database
        conn = psycopg2.connect(
            host=settings.postgres_host,
            port=settings.postgres_port,
            dbname=settings.postgres_db,
            user=settings.postgres_user,
            password=settings.postgres_password,
            sslmode=settings.postgres_sslmode
        )

        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        print("Creating schema...")

        # Execute schema creation
        cursor.execute(SCHEMA_SQL)

        print("Schema created successfully!")

        # Verify tables
        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_type = 'BASE TABLE'
            ORDER BY table_name;
        """)

        tables = cursor.fetchall()
        print(f"\nCreated tables:")
        for table in tables:
            print(f"  - {table[0]}")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"Error setting up Postgres: {e}")
        sys.exit(1)


if __name__ == "__main__":
    setup_postgres()
