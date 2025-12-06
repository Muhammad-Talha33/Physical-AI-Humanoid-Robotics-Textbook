"""Assemble retrieved chunks with source citations."""
from typing import List, Dict
from .retriever import RetrievedChunk
from ..monitoring.logger import get_logger

logger = get_logger(__name__)


class ContextBuilder:
    """
    Builds context from retrieved chunks with citations.

    Features:
    - Formats chunks for LLM consumption
    - Generates source citations
    - Handles deduplication
    """

    def __init__(self, max_context_length: int = 4000):
        self.max_context_length = max_context_length
        logger.info("ContextBuilder initialized", max_length=max_context_length)

    def build_context(
        self,
        retrieved_chunks: List[RetrievedChunk]
    ) -> Dict:
        """
        Build formatted context from retrieved chunks.

        Args:
            retrieved_chunks: List of RetrievedChunk objects

        Returns:
            Dict with formatted_context and citations
        """
        if not retrieved_chunks:
            return {
                "formatted_context": "",
                "citations": [],
                "has_context": False
            }

        # Sort by rank (already sorted, but explicit)
        chunks = sorted(retrieved_chunks, key=lambda x: x.rank)

        # Build context text with citations
        context_parts = []
        citations = []
        current_length = 0

        for chunk in chunks:
            # Create citation
            citation = {
                "chapter": chunk.chapter,
                "section": chunk.section,
                "chunk_id": chunk.chunk_id,
                "similarity_score": chunk.similarity_score
            }

            # Format chunk with citation marker
            chunk_text = f"[Source {chunk.rank}: {chunk.section}]\n{chunk.text}\n"

            # Check if adding this chunk would exceed max length
            if current_length + len(chunk_text) > self.max_context_length:
                logger.warning(
                    "Context length limit reached",
                    chunks_included=len(context_parts),
                    total_chunks=len(chunks)
                )
                break

            context_parts.append(chunk_text)
            citations.append(citation)
            current_length += len(chunk_text)

        formatted_context = "\n".join(context_parts)

        logger.info(
            "Context built",
            chunks_count=len(context_parts),
            context_length=len(formatted_context),
            citations_count=len(citations)
        )

        return {
            "formatted_context": formatted_context,
            "citations": citations,
            "has_context": len(context_parts) > 0
        }

    def build_citations_text(self, citations: List[Dict]) -> str:
        """
        Format citations for display in response.

        Args:
            citations: List of citation dicts

        Returns:
            Formatted citations text
        """
        if not citations:
            return ""

        citation_lines = ["\n\n**Sources:**"]
        seen_chapters = set()

        for citation in citations:
            chapter = citation["chapter"]
            section = citation["section"]

            # Deduplicate by chapter
            if chapter not in seen_chapters:
                citation_lines.append(f"- {chapter} ({section})")
                seen_chapters.add(chapter)

        return "\n".join(citation_lines)
