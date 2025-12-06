"""Application settings loaded from environment variables."""
import os
from typing import Literal
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings(BaseSettings):
    """Application configuration settings."""

    # OpenAI Configuration
    openai_api_key: str
    openai_embedding_model: str = "text-embedding-3-small"
    openai_chat_model: str = "gpt-3.5-turbo"

    # Qdrant Configuration
    qdrant_url: str
    qdrant_api_key: str
    qdrant_collection_name: str = "book-embeddings"

    # Postgres Configuration
    postgres_host: str
    postgres_port: int = 5432
    postgres_db: str
    postgres_user: str
    postgres_password: str
    postgres_sslmode: str = "require"

    # Application Configuration
    environment: Literal["development", "staging", "production"] = "development"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    log_level: str = "INFO"

    # Rate Limiting
    rate_limit_queries_per_hour: int = 50

    # RAG Configuration
    similarity_threshold: float = 0.72
    top_k_results: int = 5
    chunk_size_min: int = 500
    chunk_size_max: int = 1000
    chunk_overlap_percent: int = 25
    max_conversation_turns: int = 10
    max_query_length_tokens: int = 1000

    # Retry Configuration
    max_retries: int = 3
    retry_backoff_seconds: int = 1

    # Cost Monitoring
    monthly_cost_limit_usd: float = 20.0

    # Security
    admin_api_key: str | None = None

    @property
    def postgres_dsn(self) -> str:
        """Generate PostgreSQL connection string."""
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
            f"?sslmode={self.postgres_sslmode}"
        )

    @property
    def async_postgres_dsn(self) -> str:
        """Generate async PostgreSQL connection string."""
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
            f"?sslmode={self.postgres_sslmode}"
        )

    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
