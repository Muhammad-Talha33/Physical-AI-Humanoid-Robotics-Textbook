# Data Model: Chat UI Integration

**Feature**: 002-chatkit-ui
**Date**: 2025-12-07
**Purpose**: Define frontend data structures for chat session management, messages, citations, and text selection

---

## Overview

This document defines the TypeScript interfaces and types used in the Chat UI frontend. All data models are client-side only; backend logging is handled by the backend service.

---

## Core Entities

### 1. ChatSession

Represents a user's conversation within a single page visit.

```typescript
interface ChatSession {
  sessionId: string;        // UUID v4 identifier
  messages: Message[];      // Conversation history
  createdAt: Date;          // Session start timestamp
  lastActivityAt: Date;     // Last message timestamp
}
```

**Fields**:
- `sessionId`: Unique identifier generated on first widget open (UUID v4)
- `messages`: Array of user and assistant messages in chronological order
- `createdAt`: Timestamp when session was created (widget first opened)
- `lastActivityAt`: Timestamp of most recent message (user or assistant)

**Storage**:
- React state: Current active session
- localStorage: Persisted session for widget reopen (key: `chatbot-session-${pageId}`)

**Lifecycle**:
- Created: On first widget open
- Updated: On each message send/receive
- Persisted: On every state change
- Restored: On widget reopen within same page
- Cleared: On page navigation (localStorage scoped to page)

---

### 2. Message

Individual query or response in conversation.

```typescript
interface Message {
  id: string;               // Unique message ID
  role: 'user' | 'assistant'; // Message sender
  content: string;          // Message text
  timestamp: Date;          // When message was created
  citations?: Citation[];   // Optional source references (assistant only)
  selectedContext?: string; // Optional context (user messages with text selection)
}
```

**Fields**:
- `id`: UUID v4 for message identification
- `role`: `'user'` for user queries, `'assistant'` for AI responses
- `content`: Text content of message
- `timestamp`: When message was created (client-side time)
- `citations`: Array of citations (only for assistant messages, optional)
- `selectedContext`: Text that was selected when user sent message (optional)

**Validation Rules**:
- `content` must not be empty string
- `role` must be either `'user'` or `'assistant'`
- `citations` only valid for `role === 'assistant'`
- `selectedContext` only valid for `role === 'user'`

**Example**:
```typescript
{
  id: "550e8400-e29b-41d4-a716-446655440000",
  role: "user",
  content: "What is ROS 2?",
  timestamp: new Date("2025-12-07T10:30:00Z"),
  selectedContext: "Robot Operating System (ROS) is..."
}
```

---

### 3. Citation

Reference to book content source.

```typescript
interface Citation {
  chapter: string;      // Chapter name/title
  section: string;      // Section name/title
  url?: string;         // Optional link to chapter/section
}
```

**Fields**:
- `chapter`: Human-readable chapter name (e.g., "Introduction to Physical AI")
- `section`: Human-readable section name (e.g., "What is ROS 2?")
- `url`: Optional URL to navigate to cited content (relative or absolute)

**Rendering**:
- Displayed as inline badges in assistant messages
- Format: `[📖 Chapter: Section]`
- Clickable if `url` is provided

**Example**:
```typescript
{
  chapter: "Introduction to Physical AI",
  section: "What is ROS 2?",
  url: "/docs/intro/what-is-ros2"
}
```

---

### 4. SelectedContext

Text highlighted by user for focused AI responses.

```typescript
interface SelectedContext {
  text: string;         // Selected text content
  source: string;       // Page/chapter where selection occurred
  timestamp: Date;      // When selection was made
}
```

**Fields**:
- `text`: The actual text that was highlighted
- `source`: Source identifier (e.g., current page URL or chapter title)
- `timestamp`: When selection was captured

**Usage**:
- Created when user highlights text and clicks "Ask AI About This"
- Passed to backend in `selected_context` field
- Backend prioritizes this text over vector search

**Example**:
```typescript
{
  text: "Robot Operating System (ROS) is a flexible framework...",
  source: "/docs/intro/what-is-ros2",
  timestamp: new Date("2025-12-07T10:29:55Z")
}
```

---

## API Request/Response Types

### ChatQueryRequest

Request payload sent to backend `/chat/query` endpoint.

```typescript
interface ChatQueryRequest {
  query: string;              // User's question
  sessionId: string;          // UUID for session tracking
  selected_context?: string;  // Optional highlighted text
}
```

**Validation**:
- `query`: Required, min length 1, max length 1000
- `sessionId`: Required, must be valid UUID v4
- `selected_context`: Optional, max length 2000

---

### ChatQueryResponse

Response payload from backend `/chat/query` endpoint.

```typescript
interface ChatQueryResponse {
  answer: string;             // AI-generated response
  citations?: Citation[];     // Optional source references
}
```

**Fields**:
- `answer`: The AI's response text
- `citations`: Optional array of citations (may be empty or undefined)

---

### ChatErrorResponse

Error response from backend.

```typescript
interface ChatErrorResponse {
  error: string;              // Error message
  code: number;               // HTTP status code
}
```

**Error Codes**:
- `400`: Bad request (invalid query, sessionId, etc.)
- `500`: Internal server error
- `503`: Service unavailable (backend offline)

---

## Frontend State Management

### ChatWidgetState

React state for ChatWidget component.

```typescript
interface ChatWidgetState {
  isOpen: boolean;            // Widget visibility
  session: ChatSession | null; // Current session
  isLoading: boolean;         // Loading indicator
  error: string | null;       // Error message
}
```

**State Transitions**:
- `isOpen`: Toggle on button click
- `session`: Created on first open, restored from localStorage
- `isLoading`: True during API request, false on response/error
- `error`: Set on API error, cleared on new message

---

### TextSelectionState

React state for text selection feature.

```typescript
interface TextSelectionState {
  selectedText: string | null;  // Currently selected text
  position: { x: number; y: number } | null; // Popover position
  isVisible: boolean;           // Popover visibility
}
```

**State Transitions**:
- `selectedText`: Set on mouseup with valid selection
- `position`: Calculated from selection bounding box
- `isVisible`: True if selectedText is non-empty, false on click outside

---

## Storage Schema

### localStorage Schema

**Key**: `chatbot-session-${pageId}`

**Value** (JSON serialized):
```typescript
{
  sessionId: string;
  messages: Array<{
    id: string;
    role: 'user' | 'assistant';
    content: string;
    timestamp: string; // ISO 8601
    citations?: Citation[];
    selectedContext?: string;
  }>;
  createdAt: string; // ISO 8601
  lastActivityAt: string; // ISO 8601
}
```

**Max Size**: ~5MB (browser localStorage limit)
**Expiration**: Cleared on page navigation (scoped to page URL)

---

## Type Guards and Utilities

### Type Guards

```typescript
function isChatQueryResponse(obj: any): obj is ChatQueryResponse {
  return typeof obj?.answer === 'string';
}

function isChatErrorResponse(obj: any): obj is ChatErrorResponse {
  return typeof obj?.error === 'string' && typeof obj?.code === 'number';
}
```

### Utilities

```typescript
// Serialize session for localStorage
function serializeSession(session: ChatSession): string {
  return JSON.stringify({
    ...session,
    createdAt: session.createdAt.toISOString(),
    lastActivityAt: session.lastActivityAt.toISOString(),
    messages: session.messages.map(m => ({
      ...m,
      timestamp: m.timestamp.toISOString()
    }))
  });
}

// Deserialize session from localStorage
function deserializeSession(json: string): ChatSession {
  const data = JSON.parse(json);
  return {
    ...data,
    createdAt: new Date(data.createdAt),
    lastActivityAt: new Date(data.lastActivityAt),
    messages: data.messages.map((m: any) => ({
      ...m,
      timestamp: new Date(m.timestamp)
    }))
  };
}
```

---

## Validation Rules

### Message Content
- Min length: 1 character
- Max length: 1000 characters
- Must not be only whitespace

### Session ID
- Must be valid UUID v4 format
- Generated using `uuid` library

### Selected Context
- Max length: 2000 characters
- Trimmed of leading/trailing whitespace
- Empty strings converted to undefined

---

## Data Flow Diagram

```
User Input
    ↓
ChatWidget (React State)
    ↓
chatService.ts (API Client)
    ↓
Backend /chat/query
    ↓
ChatQueryResponse
    ↓
ChatWidget (Update State)
    ↓
localStorage (Persist)
    ↓
ChatKit UI (Render)
```

---

## Notes

- All timestamps use client-side time (user's browser timezone)
- Backend logging uses server-side timestamps (stored in Neon Postgres)
- Session persistence is page-scoped (new session per page)
- No cross-page or cross-device session sync
