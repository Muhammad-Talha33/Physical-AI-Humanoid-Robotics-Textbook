"""OpenAI embedding generation with exponential backoff retry logic."""
from typing import List
import asyncio
from openai import AsyncOpenAI
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)
from ..monitoring.logger import get_logger
from ..config.settings import settings

logger = get_logger(__name__)


class EmbeddingGenerator:
    """
    Generate embeddings using OpenAI API with retry logic.

    Implements:
    - Exponential backoff retry (3 attempts, 1s/2s/4s delays)
    - Batch processing support
    - Cost tracking
    """

    def __init__(self, api_key: str = None, model: str = None):
        self.client = AsyncOpenAI(api_key=api_key or settings.openai_api_key)
        self.model = model or settings.openai_embedding_model

        logger.info("EmbeddingGenerator initialized", model=self.model)

    @retry(
        stop=stop_after_attempt(settings.max_retries),
        wait=wait_exponential(
            multiplier=settings.retry_backoff_seconds,
            min=settings.retry_backoff_seconds,
            max=settings.retry_backoff_seconds * 4
        ),
        retry=retry_if_exception_type((Exception,)),
        reraise=True
    )
    async def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text string.

        Args:
            text: Input text to embed

        Returns:
            Embedding vector as list of floats

        Raises:
            Exception: If all retry attempts fail
        """
        try:
            response = await self.client.embeddings.create(
                input=text,
                model=self.model
            )

            embedding = response.data[0].embedding

            logger.debug(
                "Embedding generated",
                text_length=len(text),
                embedding_dim=len(embedding),
                model=self.model
            )

            return embedding

        except Exception as e:
            logger.error(
                "Failed to generate embedding",
                error=str(e),
                text_preview=text[:100]
            )
            raise

    async def generate_embeddings_batch(
        self,
        texts: List[str],
        batch_size: int = 100
    ) -> List[List[float]]:
        """
        Generate embeddings for multiple texts in batches.

        Args:
            texts: List of text strings to embed
            batch_size: Number of texts to process per API call

        Returns:
            List of embedding vectors
        """
        embeddings = []

        # Process in batches to respect API limits
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]

            try:
                response = await self.client.embeddings.create(
                    input=batch,
                    model=self.model
                )

                batch_embeddings = [item.embedding for item in response.data]
                embeddings.extend(batch_embeddings)

                logger.info(
                    "Batch embeddings generated",
                    batch_num=i // batch_size + 1,
                    batch_size=len(batch),
                    total_processed=len(embeddings)
                )

                # Small delay to avoid rate limiting
                if i + batch_size < len(texts):
                    await asyncio.sleep(0.5)

            except Exception as e:
                logger.error(
                    "Failed to generate batch embeddings",
                    error=str(e),
                    batch_num=i // batch_size + 1
                )
                raise

        return embeddings

    def estimate_cost(
        self,
        total_tokens: int,
        cost_per_million_tokens: float = 0.02
    ) -> float:
        """
        Estimate cost for embedding generation.

        Default cost is for text-embedding-3-small at $0.02 per 1M tokens.

        Args:
            total_tokens: Total number of tokens to embed
            cost_per_million_tokens: Cost per 1 million tokens (USD)

        Returns:
            Estimated cost in USD
        """
        return (total_tokens / 1_000_000) * cost_per_million_tokens
