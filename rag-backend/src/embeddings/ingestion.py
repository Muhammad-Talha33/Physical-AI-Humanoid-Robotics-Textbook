"""Batch processing pipeline for book chapter ingestion."""
import asyncio
import os
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import uuid
from .chunker import TextChunker
from .generator import EmbeddingGenerator
from ..retrieval.qdrant_client import QdrantVectorStore
from ..monitoring.logger import get_logger
from ..monitoring.metrics import metrics_tracker

logger = get_logger(__name__)


class IngestionPipeline:
    """
    End-to-end pipeline for processing book chapters into embeddings.

    Steps:
    1. Load markdown files from docs directory
    2. Extract chapter metadata (number, title, module)
    3. Chunk content with sentence-boundary awareness
    4. Generate embeddings concurrently
    5. Store in Qdrant with metadata
    6. Track progress and errors
    """

    def __init__(
        self,
        chunker: Optional[TextChunker] = None,
        generator: Optional[EmbeddingGenerator] = None,
        vector_store: Optional[QdrantVectorStore] = None
    ):
        self.chunker = chunker or TextChunker()
        self.generator = generator or EmbeddingGenerator()
        self.vector_store = vector_store or QdrantVectorStore()

        self.total_chapters_processed = 0
        self.total_chunks_generated = 0
        self.total_embeddings_stored = 0
        self.failed_chapters = []

        logger.info("IngestionPipeline initialized")

    async def ingest_chapter(
        self,
        file_path: str,
        force_update: bool = False
    ) -> Dict:
        """
        Ingest a single chapter file.

        Args:
            file_path: Path to markdown file
            force_update: If True, delete existing embeddings before re-ingesting

        Returns:
            Dict with ingestion results
        """
        start_time = datetime.utcnow()

        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract metadata from file path and content
            metadata = self._extract_chapter_metadata(file_path, content)

            logger.info(
                "Starting chapter ingestion",
                chapter=metadata['chapter'],
                file=file_path
            )

            # Delete existing embeddings if force update
            if force_update:
                await self.vector_store.delete_by_chapter(file_path)

            # Chunk the content
            chunks = self.chunker.chunk_text(content, chapter_path=file_path)

            if not chunks:
                logger.warning("No chunks generated", chapter=file_path)
                return {
                    "success": False,
                    "error": "No chunks generated",
                    "chunks_count": 0
                }

            # Generate embeddings for all chunks
            chunk_texts = [chunk.text for chunk in chunks]
            embeddings = await self.generator.generate_embeddings_batch(chunk_texts)

            # Prepare metadata for each chunk
            chunk_ids = [uuid.uuid4() for _ in chunks]
            metadata_list = []

            for i, chunk in enumerate(chunks):
                chunk_metadata = {
                    "chunk_id": str(chunk_ids[i]),
                    "chapter_file_path": file_path,
                    "section_title": chunk.section_title,
                    "text_snippet": chunk.text[:200],  # First 200 chars
                    "token_count": chunk.token_count,
                    "created_at": datetime.utcnow().isoformat(),
                    "chapter_number": metadata.get("chapter_number"),
                    "chapter_title": metadata.get("title"),
                    "module": metadata.get("module")
                }
                metadata_list.append(chunk_metadata)

            # Store in Qdrant
            await self.vector_store.insert_embeddings(
                embeddings=embeddings,
                metadata_list=metadata_list,
                chunk_ids=chunk_ids
            )

            # Track metrics
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            total_tokens = sum(chunk.token_count for chunk in chunks)

            # Estimate cost
            cost = self.generator.estimate_cost(total_tokens)
            await metrics_tracker.track_api_cost(
                cost_usd=cost,
                cost_type="embedding",
                tokens_used=total_tokens
            )

            self.total_chapters_processed += 1
            self.total_chunks_generated += len(chunks)
            self.total_embeddings_stored += len(embeddings)

            logger.info(
                "Chapter ingestion completed",
                chapter=file_path,
                chunks=len(chunks),
                tokens=total_tokens,
                processing_time_ms=processing_time,
                estimated_cost_usd=cost
            )

            return {
                "success": True,
                "chapter": file_path,
                "chunks_count": len(chunks),
                "tokens_total": total_tokens,
                "processing_time_ms": processing_time,
                "estimated_cost_usd": cost
            }

        except Exception as e:
            logger.error(
                "Chapter ingestion failed",
                chapter=file_path,
                error=str(e)
            )

            self.failed_chapters.append({
                "chapter": file_path,
                "error": str(e)
            })

            await metrics_tracker.track_error(
                error_type="ingestion_error",
                error_message=str(e)
            )

            return {
                "success": False,
                "chapter": file_path,
                "error": str(e)
            }

    async def ingest_directory(
        self,
        docs_dir: str,
        pattern: str = "**/*.md",
        force_update: bool = False,
        max_concurrent: int = 5
    ) -> Dict:
        """
        Ingest all markdown files from a directory.

        Args:
            docs_dir: Path to docs directory
            pattern: Glob pattern for markdown files
            force_update: If True, re-ingest all chapters
            max_concurrent: Maximum concurrent chapter processing

        Returns:
            Summary of ingestion results
        """
        docs_path = Path(docs_dir)

        if not docs_path.exists():
            logger.error("Docs directory not found", path=docs_dir)
            return {"success": False, "error": "Directory not found"}

        # Find all markdown files
        markdown_files = list(docs_path.glob(pattern))

        logger.info(
            "Starting directory ingestion",
            docs_dir=docs_dir,
            files_found=len(markdown_files)
        )

        # Process files in batches
        semaphore = asyncio.Semaphore(max_concurrent)

        async def process_with_semaphore(file_path):
            async with semaphore:
                return await self.ingest_chapter(str(file_path), force_update)

        tasks = [process_with_semaphore(f) for f in markdown_files]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Aggregate results
        successful = sum(1 for r in results if isinstance(r, dict) and r.get("success"))
        failed = len(results) - successful

        total_cost = sum(
            r.get("estimated_cost_usd", 0)
            for r in results
            if isinstance(r, dict) and r.get("success")
        )

        summary = {
            "success": True,
            "total_files": len(markdown_files),
            "successful": successful,
            "failed": failed,
            "total_chapters_processed": self.total_chapters_processed,
            "total_chunks_generated": self.total_chunks_generated,
            "total_embeddings_stored": self.total_embeddings_stored,
            "total_cost_usd": total_cost,
            "failed_chapters": self.failed_chapters
        }

        logger.info(
            "Directory ingestion completed",
            **summary
        )

        return summary

    def _extract_chapter_metadata(self, file_path: str, content: str) -> Dict:
        """Extract metadata from chapter file."""
        path_parts = Path(file_path).parts

        # Try to extract module and chapter number from path
        module = None
        chapter_number = None

        for part in path_parts:
            if part.startswith("module"):
                module = part
            if "chapter" in part.lower():
                # Extract number from chapter filename
                import re
                match = re.search(r'chapter[_-]?(\d+)', part, re.IGNORECASE)
                if match:
                    chapter_number = int(match.group(1))

        # Extract title from first # heading
        title = None
        for line in content.split('\n'):
            if line.startswith('# '):
                title = line[2:].strip()
                break

        return {
            "chapter": file_path,
            "module": module,
            "chapter_number": chapter_number,
            "title": title or Path(file_path).stem
        }
