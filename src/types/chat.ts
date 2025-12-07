/**
 * TypeScript type definitions for Chat UI
 * Based on data-model.md from specs/002-chatkit-ui/
 */

export interface ChatSession {
  sessionId: string;        // UUID v4 identifier
  messages: Message[];      // Conversation history
  createdAt: Date;          // Session start timestamp
  lastActivityAt: Date;     // Last message timestamp
}

export interface Message {
  id: string;               // Unique message ID
  role: 'user' | 'assistant'; // Message sender
  content: string;          // Message text
  timestamp: Date;          // When message was created
  citations?: Citation[];   // Optional source references
  selectedContext?: string; // Optional highlighted text context
}

export interface Citation {
  chapter: string;      // Chapter name/title
  section: string;      // Section name/title
  url?: string;         // Optional link to chapter/section
}

export interface SelectedContext {
  text: string;         // Selected text content
  startOffset: number;  // Start position in document
  endOffset: number;    // End position in document
}

/**
 * Backend API Request/Response Types
 * Based on contracts/backend-api.yaml
 */

export interface ChatQueryRequest {
  query: string;            // User's question (1-1000 chars)
  sessionId: string;        // UUID v4 session identifier
  selected_context?: string; // Optional selected text (max 2000 chars)
}

export interface ChatQueryResponse {
  answer: string;           // AI-generated response
  citations?: Citation[];   // Optional source citations
}

export interface ChatErrorResponse {
  error: string;            // Human-readable error message
  code: number;             // HTTP status code
}

/**
 * localStorage Schema
 */

export interface StoredSession {
  sessionId: string;
  messages: Array<{
    id: string;
    role: 'user' | 'assistant';
    content: string;
    timestamp: string;      // ISO 8601 format
    citations?: Citation[];
  }>;
  createdAt: string;        // ISO 8601 format
  lastActivityAt: string;   // ISO 8601 format
}
