"""Answer generation with grounding validation using OpenAI."""
from typing import Dict, List, Optional
from openai import AsyncOpenAI
from ..monitoring.logger import get_logger
from ..config.settings import settings

logger = get_logger(__name__)


class ResponseGenerator:
    """
    Generates grounded responses using OpenAI chat completions.

    Features:
    - Strict grounding to retrieved context
    - Citation enforcement
    - Insufficient context detection
    """

    def __init__(self, api_key: str = None, model: str = None):
        self.client = AsyncOpenAI(api_key=api_key or settings.openai_api_key)
        self.model = model or settings.openai_chat_model
        logger.info("ResponseGenerator initialized", model=self.model)

    async def generate_response(
        self,
        query: str,
        context: str,
        citations: List[Dict],
        conversation_history: Optional[List[Dict]] = None
    ) -> Dict:
        """
        Generate a grounded response to the query.

        Args:
            query: User's question
            context: Retrieved context from book chapters
            citations: List of source citations
            conversation_history: Optional previous conversation turns

        Returns:
            Dict with response_text, grounding_status, and token usage
        """
        # Check if we have sufficient context
        # Reduced minimum from 50 to 20 chars to handle shorter but valid contexts
        if not context or len(context.strip()) < 20:
            logger.warning("Insufficient context", context_length=len(context.strip()) if context else 0)
            return {
                "response_text": self._insufficient_context_message(),
                "grounding_status": "insufficient_context",
                "tokens_used": 0
            }

        # Build system prompt with grounding instructions
        system_prompt = self._build_system_prompt()

        # Build user message with context and query
        user_message = self._build_user_message(query, context)

        # Construct messages
        messages = [{"role": "system", "content": system_prompt}]

        # Add conversation history if available
        if conversation_history:
            messages.extend(conversation_history[-10:])  # Last 10 turns

        messages.append({"role": "user", "content": user_message})

        try:
            # Generate response
            logger.info("Generating response", query_preview=query[:100])

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.3,  # Lower temperature for more factual responses
                max_tokens=500
            )

            response_text = response.choices[0].message.content
            tokens_used = response.usage.total_tokens

            # Validate grounding
            grounding_status = self._validate_grounding(response_text, context)

            logger.info(
                "Response generated",
                grounding_status=grounding_status,
                tokens_used=tokens_used,
                response_length=len(response_text)
            )

            return {
                "response_text": response_text,
                "grounding_status": grounding_status,
                "tokens_used": tokens_used
            }

        except Exception as e:
            logger.error("Failed to generate response", error=str(e))
            return {
                "response_text": self._error_message(),
                "grounding_status": "error",
                "tokens_used": 0
            }

    def _build_system_prompt(self) -> str:
        """Build system prompt with grounding instructions."""
        return """You are a helpful assistant for the Physical AI & Humanoid Robotics textbook.

CRITICAL RULES:
1. Answer ONLY based on the provided context from the book
2. If you can answer even partially from the context, provide that answer
3. Only say "I cannot find information about this" if the context is truly irrelevant
4. Always cite the source sections when providing information (use Source 1, Source 2, etc.)
5. Do not make assumptions or add information not present in the context
6. Be concise and direct in your answers
7. Use technical terms accurately as they appear in the book
8. If the question uses different wording than the book (e.g., "ros2" vs "ROS 2"), still answer if the meaning is clear

Your goal is to help readers understand the book content, not to provide general knowledge about robotics."""

    def _build_user_message(self, query: str, context: str) -> str:
        """Build user message with context and query."""
        # Normalize the query to improve matching
        query_normalized = query.strip()

        return f"""Context from the book (numbered sources):

{context}

---

Question: {query_normalized}

Instructions:
- Answer based on the context above
- Cite sources using (Source 1), (Source 2), etc.
- If the question uses informal language (like "ros2" for "ROS 2"), answer based on the technical content
- Only say you cannot find information if the context is truly unrelated to the question"""

    def _validate_grounding(self, response: str, context: str) -> str:
        """
        Validate that response is grounded in context.

        Simple heuristic: check if response contains key phrases
        indicating lack of information.

        Args:
            response: Generated response
            context: Retrieved context

        Returns:
            Grounding status: "grounded", "insufficient_context", or "error"
        """
        insufficient_phrases = [
            "cannot find information",
            "don't have information",
            "not mentioned in the context",
            "doesn't contain",
            "not in the provided context"
        ]

        response_lower = response.lower()

        for phrase in insufficient_phrases:
            if phrase in response_lower:
                return "insufficient_context"

        # If response is very short, might be insufficient
        if len(response.strip()) < 20:
            return "insufficient_context"

        # Otherwise assume grounded
        return "grounded"

    def _insufficient_context_message(self) -> str:
        """Standard message for insufficient context."""
        return (
            "I cannot find information about this in the book content. "
            "Please try rephrasing your question or ask about topics covered in the "
            "Physical AI & Humanoid Robotics textbook."
        )

    def _error_message(self) -> str:
        """Standard error message."""
        return (
            "I'm experiencing technical difficulties right now. "
            "Please try again in a moment."
        )
