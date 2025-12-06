"""Vector similarity search with configurable threshold filtering."""
from typing import List, Dict, Optional
from qdrant_client import QdrantClient
from qdrant_client.models import SearchRequest, Filter
from ..monitoring.logger import get_logger
from ..config.settings import settings
from ..embeddings.generator import EmbeddingGenerator

logger = get_logger(__name__)


class RetrievedChunk:
    """Represents a retrieved chunk with metadata."""

    def __init__(
        self,
        chunk_id: str,
        text: str,
        similarity_score: float,
        chapter: str,
        section: str,
        rank: int
    ):
        self.chunk_id = chunk_id
        self.text = text
        self.similarity_score = similarity_score
        self.chapter = chapter
        self.section = section
        self.rank = rank


class Retriever:
    """
    Performs vector similarity search with threshold filtering.

    Features:
    - Configurable similarity threshold (0.70-0.75)
    - Top-K results retrieval
    - Query embedding generation
    """

    def __init__(
        self,
        qdrant_client: Optional[QdrantClient] = None,
        embedding_generator: Optional[EmbeddingGenerator] = None,
        similarity_threshold: float = None,
        top_k: int = None
    ):
        self.qdrant_client = qdrant_client or QdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key
        )
        self.embedding_generator = embedding_generator or EmbeddingGenerator()
        self.similarity_threshold = similarity_threshold or settings.similarity_threshold
        self.top_k = top_k or settings.top_k_results
        self.collection_name = settings.qdrant_collection_name

        logger.info(
            "Retriever initialized",
            threshold=self.similarity_threshold,
            top_k=self.top_k
        )

    async def retrieve(
        self,
        query: str,
        filter_params: Optional[Dict] = None
    ) -> List[RetrievedChunk]:
        """
        Retrieve relevant chunks for a query.

        Args:
            query: User's question text
            filter_params: Optional metadata filters (e.g., specific chapter)

        Returns:
            List of RetrievedChunk objects above similarity threshold
        """
        # Generate query embedding
        logger.info("Generating query embedding", query_preview=query[:100])
        query_embedding = await self.embedding_generator.generate_embedding(query)

        # Perform vector search
        search_results = self.qdrant_client.query_points(
            collection_name=self.collection_name,
            query=query_embedding,
            limit=self.top_k,
            score_threshold=self.similarity_threshold
        ).points

        # Convert to RetrievedChunk objects
        retrieved_chunks = []
        for rank, result in enumerate(search_results, start=1):
            chunk = RetrievedChunk(
                chunk_id=result.id,
                text=result.payload.get("text_snippet", ""),
                similarity_score=result.score,
                chapter=result.payload.get("chapter_file_path", ""),
                section=result.payload.get("section_title", ""),
                rank=rank
            )
            retrieved_chunks.append(chunk)

        logger.info(
            "Retrieval completed",
            query_preview=query[:100],
            results_count=len(retrieved_chunks),
            avg_similarity=sum(c.similarity_score for c in retrieved_chunks) / len(retrieved_chunks) if retrieved_chunks else 0.0
        )

        return retrieved_chunks

    async def retrieve_with_full_text(
        self,
        query: str,
        filter_params: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Retrieve chunks with full text content (not just snippet).

        Args:
            query: User's question text
            filter_params: Optional metadata filters

        Returns:
            List of dicts with full chunk data
        """
        # Generate query embedding
        query_embedding = await self.embedding_generator.generate_embedding(query)

        # Perform vector search with full payload
        search_results = self.qdrant_client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            limit=self.top_k,
            score_threshold=self.similarity_threshold,
            with_payload=True
        )

        # Extract full results
        results = []
        for rank, result in enumerate(search_results, start=1):
            results.append({
                "chunk_id": result.id,
                "score": result.score,
                "rank": rank,
                "payload": result.payload
            })

        return results
