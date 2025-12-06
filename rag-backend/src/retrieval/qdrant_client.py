"""Qdrant vector database operations for embedding storage and retrieval."""
import uuid
from typing import List, Dict, Optional
from datetime import datetime
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, Filter, FieldCondition, MatchValue
from ..monitoring.logger import get_logger
from ..config.settings import settings

logger = get_logger(__name__)


class QdrantVectorStore:
    """
    Manages vector storage and retrieval using Qdrant.

    Operations:
    - Insert embeddings with metadata
    - Delete by chapter
    - Health check
    """

    def __init__(
        self,
        url: str = None,
        api_key: str = None,
        collection_name: str = None
    ):
        self.client = QdrantClient(
            url=url or settings.qdrant_url,
            api_key=api_key or settings.qdrant_api_key
        )
        self.collection_name = collection_name or settings.qdrant_collection_name

        logger.info(
            "QdrantVectorStore initialized",
            collection=self.collection_name
        )

    async def insert_embeddings(
        self,
        embeddings: List[List[float]],
        metadata_list: List[Dict],
        chunk_ids: Optional[List[uuid.UUID]] = None
    ) -> List[uuid.UUID]:
        """
        Insert embeddings with metadata into Qdrant.

        Args:
            embeddings: List of embedding vectors
            metadata_list: List of metadata dicts for each embedding
            chunk_ids: Optional list of chunk IDs (auto-generated if None)

        Returns:
            List of chunk IDs
        """
        if not chunk_ids:
            chunk_ids = [uuid.uuid4() for _ in embeddings]

        # Create points
        points = []
        for chunk_id, embedding, metadata in zip(chunk_ids, embeddings, metadata_list):
            # Ensure metadata has required fields
            payload = {
                "chunk_id": str(chunk_id),
                "chapter_file_path": metadata.get("chapter_file_path", ""),
                "section_title": metadata.get("section_title", ""),
                "text_snippet": metadata.get("text_snippet", ""),
                "token_count": metadata.get("token_count", 0),
                "created_at": metadata.get("created_at", datetime.utcnow().isoformat())
            }

            points.append(PointStruct(
                id=str(chunk_id),
                vector=embedding,
                payload=payload
            ))

        # Insert into Qdrant
        try:
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )

            logger.info(
                "Embeddings inserted successfully",
                count=len(points),
                collection=self.collection_name
            )

            return chunk_ids

        except Exception as e:
            logger.error(
                "Failed to insert embeddings",
                error=str(e),
                count=len(points)
            )
            raise

    async def delete_by_chapter(self, chapter_file_path: str) -> int:
        """
        Delete all embeddings for a specific chapter.

        Args:
            chapter_file_path: Path to chapter file

        Returns:
            Number of points deleted
        """
        try:
            # Get points matching the chapter
            search_result = self.client.scroll(
                collection_name=self.collection_name,
                scroll_filter=Filter(
                    must=[
                        FieldCondition(
                            key="chapter_file_path",
                            match=MatchValue(value=chapter_file_path)
                        )
                    ]
                ),
                limit=10000
            )

            point_ids = [point.id for point in search_result[0]]

            if point_ids:
                self.client.delete(
                    collection_name=self.collection_name,
                    points_selector=point_ids
                )

            logger.info(
                "Chapter embeddings deleted",
                chapter=chapter_file_path,
                count=len(point_ids)
            )

            return len(point_ids)

        except Exception as e:
            logger.error(
                "Failed to delete chapter embeddings",
                error=str(e),
                chapter=chapter_file_path
            )
            raise

    def health_check(self) -> bool:
        """
        Check if Qdrant is accessible and collection exists.

        Returns:
            True if healthy, False otherwise
        """
        try:
            collections = self.client.get_collections().collections
            collection_exists = any(c.name == self.collection_name for c in collections)

            if not collection_exists:
                logger.warning(
                    "Collection does not exist",
                    collection=self.collection_name
                )
                return False

            # Try to get collection info
            info = self.client.get_collection(self.collection_name)

            logger.info(
                "Qdrant health check passed",
                collection=self.collection_name,
                vectors_count=info.points_count,
                status=info.status
            )

            return True

        except Exception as e:
            logger.error(
                "Qdrant health check failed",
                error=str(e)
            )
            return False

    def get_collection_info(self) -> Dict:
        """Get information about the collection."""
        try:
            info = self.client.get_collection(self.collection_name)

            return {
                "name": self.collection_name,
                "vectors_count": info.points_count,
                "status": info.status,
                "vector_size": info.config.params.vectors.size
            }

        except Exception as e:
            logger.error("Failed to get collection info", error=str(e))
            return {}
