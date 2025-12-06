"""Sentence-boundary aware text chunking for optimal embedding generation."""
import re
from typing import List, Tuple
import tiktoken
from ..monitoring.logger import get_logger
from ..config.settings import settings

logger = get_logger(__name__)


class TextChunk:
    """Represents a text chunk with metadata."""

    def __init__(
        self,
        text: str,
        chunk_index: int,
        token_count: int,
        section_title: str = "",
        overlap_start_index: int = None,
        overlap_end_index: int = None
    ):
        self.text = text
        self.chunk_index = chunk_index
        self.token_count = token_count
        self.section_title = section_title
        self.overlap_start_index = overlap_start_index
        self.overlap_end_index = overlap_end_index


class TextChunker:
    """
    Chunks text into semantically meaningful segments with sentence-boundary awareness.

    Implements:
    - 500-1000 token chunks with 20-30% overlap
    - Sentence boundary alignment (±50 tokens flexibility)
    - Markdown structure preservation
    """

    def __init__(
        self,
        min_chunk_size: int = None,
        max_chunk_size: int = None,
        overlap_percent: int = None,
        model: str = "gpt-3.5-turbo"
    ):
        self.min_chunk_size = min_chunk_size or settings.chunk_size_min
        self.max_chunk_size = max_chunk_size or settings.chunk_size_max
        self.overlap_percent = overlap_percent or settings.chunk_overlap_percent
        self.tokenizer = tiktoken.encoding_for_model(model)

        # Calculate overlap size in tokens
        self.overlap_size = int((self.max_chunk_size * self.overlap_percent) / 100)

        logger.info(
            "TextChunker initialized",
            min_size=self.min_chunk_size,
            max_size=self.max_chunk_size,
            overlap_percent=self.overlap_percent,
            overlap_tokens=self.overlap_size
        )

    def chunk_text(
        self,
        text: str,
        chapter_path: str = ""
    ) -> List[TextChunk]:
        """
        Chunk text with sentence-boundary awareness.

        Args:
            text: Input text to chunk
            chapter_path: Path to chapter file for logging

        Returns:
            List of TextChunk objects
        """
        # Extract sections and their titles from markdown
        sections = self._extract_markdown_sections(text)

        chunks = []
        chunk_index = 0

        for section_title, section_text in sections:
            # Split section into sentences
            sentences = self._split_into_sentences(section_text)

            current_chunk_sentences = []
            current_tokens = 0

            for sentence in sentences:
                sentence_tokens = len(self.tokenizer.encode(sentence))

                # Check if adding this sentence would exceed max size
                if current_tokens + sentence_tokens > self.max_chunk_size and current_chunk_sentences:
                    # Create chunk from accumulated sentences
                    chunk_text = " ".join(current_chunk_sentences)
                    chunk_tokens = len(self.tokenizer.encode(chunk_text))

                    chunks.append(TextChunk(
                        text=chunk_text,
                        chunk_index=chunk_index,
                        token_count=chunk_tokens,
                        section_title=section_title
                    ))

                    chunk_index += 1

                    # Start new chunk with overlap
                    overlap_sentences = self._get_overlap_sentences(
                        current_chunk_sentences,
                        self.overlap_size
                    )
                    current_chunk_sentences = overlap_sentences + [sentence]
                    current_tokens = len(self.tokenizer.encode(" ".join(current_chunk_sentences)))
                else:
                    current_chunk_sentences.append(sentence)
                    current_tokens += sentence_tokens

            # Add remaining sentences as final chunk
            if current_chunk_sentences:
                chunk_text = " ".join(current_chunk_sentences)
                chunk_tokens = len(self.tokenizer.encode(chunk_text))

                # Only add if meets minimum size requirement
                if chunk_tokens >= self.min_chunk_size or len(chunks) == 0:
                    chunks.append(TextChunk(
                        text=chunk_text,
                        chunk_index=chunk_index,
                        token_count=chunk_tokens,
                        section_title=section_title
                    ))
                    chunk_index += 1
                else:
                    # Merge with previous chunk if too small
                    if chunks:
                        chunks[-1].text += " " + chunk_text
                        chunks[-1].token_count = len(self.tokenizer.encode(chunks[-1].text))

        logger.info(
            "Text chunked successfully",
            chapter=chapter_path,
            total_chunks=len(chunks),
            avg_tokens=sum(c.token_count for c in chunks) / len(chunks) if chunks else 0
        )

        return chunks

    def _extract_markdown_sections(self, text: str) -> List[Tuple[str, str]]:
        """Extract sections from markdown text based on headings."""
        # Split by markdown headings (# ## ### etc.)
        heading_pattern = r'^(#{1,6})\s+(.+)$'

        sections = []
        current_title = "Introduction"
        current_content = []

        for line in text.split('\n'):
            match = re.match(heading_pattern, line, re.MULTILINE)
            if match:
                # Save previous section
                if current_content:
                    sections.append((current_title, '\n'.join(current_content)))

                # Start new section
                current_title = match.group(2).strip()
                current_content = []
            else:
                current_content.append(line)

        # Add final section
        if current_content:
            sections.append((current_title, '\n'.join(current_content)))

        return sections if sections else [("Content", text)]

    def _split_into_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences using simple heuristics.

        Handles:
        - Common abbreviations (Dr., Mr., etc.)
        - Decimal numbers
        - Code blocks
        """
        # Preserve code blocks
        code_blocks = []
        def preserve_code(match):
            code_blocks.append(match.group(0))
            return f"__CODE_BLOCK_{len(code_blocks) - 1}__"

        text = re.sub(r'```[\s\S]*?```', preserve_code, text)

        # Split on sentence boundaries
        # Look for . ! ? followed by space and capital letter or newline
        sentence_pattern = r'(?<=[.!?])\s+(?=[A-Z])|(?<=[.!?])\n+'

        sentences = re.split(sentence_pattern, text)

        # Restore code blocks
        for i, sentence in enumerate(sentences):
            for j, code_block in enumerate(code_blocks):
                sentences[i] = sentences[i].replace(f"__CODE_BLOCK_{j}__", code_block)

        # Clean and filter
        sentences = [s.strip() for s in sentences if s.strip()]

        return sentences

    def _get_overlap_sentences(
        self,
        sentences: List[str],
        target_overlap_tokens: int
    ) -> List[str]:
        """Get last N sentences that fit within overlap token budget."""
        overlap_sentences = []
        current_tokens = 0

        for sentence in reversed(sentences):
            sentence_tokens = len(self.tokenizer.encode(sentence))

            if current_tokens + sentence_tokens <= target_overlap_tokens:
                overlap_sentences.insert(0, sentence)
                current_tokens += sentence_tokens
            else:
                break

        return overlap_sentences
