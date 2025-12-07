# Implementation Plan: Chat UI Integration

**Branch**: `002-chatkit-ui` | **Date**: 2025-12-07 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-chatkit-ui/spec.md`

## Summary

Integrate OpenAI ChatKit as a conversational UI for the RAG-powered chatbot in the Physical AI & Humanoid Robotics Docusaurus book. The implementation will create a floating chat widget that connects to the deployed FastAPI backend, supports text selection for context-aware responses, maintains session-based conversations, displays citations, and provides graceful error handling—all while adhering to the constitution's Chat UI Standards.

## Technical Context

**Language/Version**: TypeScript 5.x + React 18.x (Docusaurus 3.x compatible)
**Primary Dependencies**:
- `@openai/chatkit-react` (OpenAI ChatKit SDK)
- `react` and `react-dom` (18.x)
- `@docusaurus/core` (3.x)
- `uuid` (for session ID generation)

**Storage**: Browser localStorage (session persistence), Backend Neon Postgres (logging)
**Testing**: Jest + React Testing Library (component tests), Playwright (E2E tests)
**Target Platform**: Modern web browsers (Chrome, Firefox, Safari, Edge - latest 2 versions)
**Project Type**: Web frontend (Docusaurus site with React component integration)
**Performance Goals**:
- Widget load <1s
- 95% queries respond <2s (backend-dependent)
- Smooth 60fps animations for widget transitions

**Constraints**:
- No SSR rendering (client-side only, post-hydration)
- No API keys in frontend code
- Mobile responsive (320px-768px+)
- Dark/light mode support

**Scale/Scope**:
- Single chat widget component
- ~500-1000 LOC for widget + utilities
- Support for concurrent users (backend handles load)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Conversational Interface Principle
- ✅ **PASS**: Using OpenAI ChatKit as mandated
- ✅ **PASS**: Fully embedded inside Docusaurus book

### Chat UI Standards
- ✅ **PASS**: ChatKit's built-in components (`<ChatProvider>`, `<Chat>`, `<MessageList>`, `<Composer>`, `<Thread>`)
- ✅ **PASS**: Floating widget/sidebar design
- ✅ **PASS**: Dark/light mode support planned
- ✅ **PASS**: Client-side only loading (post-hydration)
- ✅ **PASS**: Text selection → "Ask AI About This"
- ✅ **PASS**: Citations display
- ✅ **PASS**: Follow-up questions with session memory
- ✅ **PASS**: Graceful error handling

### Frontend Integration Constraints
- ✅ **PASS**: Component location `/src/components/chat/ChatWidget.tsx`
- ✅ **PASS**: Backend URL `https://physical-ai-humanoid-robotics-textbook-production-3516.up.railway.app/`
- ✅ **PASS**: Environment variables via Docusaurus config
- ✅ **PASS**: No API keys exposed

### Chat UI Success Criteria
- ✅ **PASS**: Load time <1s target
- ✅ **PASS**: Smooth scrolling planned
- ✅ **PASS**: Mobile responsive design
- ✅ **PASS**: Text selection feature planned
- ✅ **PASS**: Backend logging (handled by backend)
- ✅ **PASS**: No API key exposure
- ✅ **PASS**: Graceful failure states planned

**Constitution Check Result**: ✅ ALL GATES PASSED

## Project Structure

### Documentation (this feature)

```text
specs/002-chatkit-ui/
├── plan.md              # This file
├── research.md          # Phase 0 output (ChatKit integration patterns)
├── data-model.md        # Phase 1 output (frontend state models)
├── quickstart.md        # Phase 1 output (local dev setup)
├── contracts/           # Phase 1 output (backend API contract)
│   └── backend-api.yaml # OpenAPI spec for /chat/query
└── tasks.md             # Phase 2 output (/sp.tasks command)
```

### Source Code (repository root)

```text
src/
├── components/
│   └── chat/
│       ├── ChatWidget.tsx          # Main ChatKit widget component
│       ├── ChatWidgetButton.tsx    # Floating button trigger
│       ├── TextSelectionPopover.tsx # "Ask AI About This" popover
│       └── ErrorBoundary.tsx       # Error handling wrapper
├── services/
│   └── chatService.ts              # Backend API client
├── hooks/
│   ├── useChatSession.ts           # Session management hook
│   └── useTextSelection.ts         # Text selection detection hook
└── theme/
    └── chatStyles.module.css       # Custom ChatKit theming

tests/
├── components/
│   └── chat/
│       ├── ChatWidget.test.tsx
│       └── TextSelectionPopover.test.tsx
└── e2e/
    └── chat-integration.spec.ts    # Playwright E2E tests

docusaurus.config.ts                 # Add backend URL config
```

**Structure Decision**: Docusaurus single-site project with React components in `/src/components`. ChatKit integration follows Docusaurus plugin/component patterns. Backend is already deployed separately, so this is frontend-only implementation.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations detected. All constitution requirements are met by the planned implementation.

---

## Phase 0: Research

### Research Tasks

1. **ChatKit Integration with Docusaurus**
   - **Decision**: Use client-side rendering with `useEffect` to load ChatKit after hydration
   - **Rationale**: Docusaurus uses SSR/SSG, but ChatKit requires browser APIs (DOM, localStorage). Loading post-hydration avoids SSR conflicts while maintaining Docusaurus build compatibility.
   - **Alternatives Considered**:
     - Custom Docusaurus plugin: More complex, unnecessary overhead
     - BrowserOnly wrapper: Simpler but less control over timing

2. **ChatKit Component Architecture**
   - **Decision**: Use `<ChatProvider>` at root with `<Chat>`, `<MessageList>`, `<Composer>` nested
   - **Rationale**: ChatKit's recommended architecture provides state management, message handling, and UI rendering out-of-box
   - **Alternatives Considered**:
     - Custom chat UI: Reinventing the wheel, violates constitution requirement for ChatKit
     - Headless ChatKit: Possible but loses built-in UX polish

3. **Session Management Strategy**
   - **Decision**: Generate UUID on component mount, store in React state + localStorage for session persistence
   - **Rationale**: Lightweight, client-side only, survives widget close/reopen within page session
   - **Alternatives Considered**:
     - Server-side sessions: Unnecessary complexity, backend doesn't require it
     - Cookies: Overkill for single-page session management

4. **Text Selection Detection**
   - **Decision**: Use browser `window.getSelection()` API with `mouseup` event listener
   - **Rationale**: Standard web API, works across all modern browsers, no external dependencies
   - **Alternatives Considered**:
     - Selection libraries (e.g., rangy): Adds bundle size, native API sufficient
     - Double-click triggers: Less intuitive UX

5. **Backend API Communication**
   - **Decision**: Use `fetch` API with async/await, custom retry logic for network errors
   - **Rationale**: Native browser API, no external HTTP library needed, simple error handling
   - **Alternatives Considered**:
     - Axios: Adds bundle size, fetch is sufficient for simple POST requests
     - ChatKit built-in fetch: May not support custom retry/error logic

6. **Error Handling Pattern**
   - **Decision**: React Error Boundary + try/catch in async functions + UI error states
   - **Rationale**: Layered approach catches render errors, network errors, and displays user-friendly messages
   - **Alternatives Considered**:
     - Global error handler: Less granular, harder to show contextual messages
     - Toast notifications: Possible addition, but inline errors more visible

7. **Dark/Light Mode Integration**
   - **Decision**: Read Docusaurus theme from `data-theme` attribute on `<html>`, apply ChatKit CSS custom properties
   - **Rationale**: Docusaurus exposes theme via data attribute, ChatKit supports CSS variable theming
   - **Alternatives Considered**:
     - Separate light/dark ChatKit configs: Duplicates code, harder to maintain
     - CSS media query `prefers-color-scheme`: Doesn't respect user's site theme toggle

8. **Citation Display Format**
   - **Decision**: Parse backend response for citation metadata, render as inline badges with chapter/section links
   - **Rationale**: Non-intrusive, allows users to verify sources without leaving chat
   - **Alternatives Considered**:
     - Footnotes: Breaks chat flow, harder to click
     - Tooltip hover: Hidden unless hovered, less discoverable

### Research Outputs

**Key Findings**:
- ChatKit requires `react` peer dependency 18.x (compatible with Docusaurus 3.x)
- Backend `/chat/query` endpoint expects JSON: `{ query: string, sessionId: string, selected_context?: string }`
- Backend response format: `{ answer: string, citations?: Array<{chapter: string, section: string}> }`
- Text selection API works in all target browsers without polyfills
- Docusaurus supports custom React components via `src/theme` swizzling or direct import

**Technical Decisions Locked**:
1. Client-side rendering with `useEffect` + `useState` for ChatKit lifecycle
2. UUID v4 for session IDs (via `uuid` library)
3. `window.getSelection()` for text selection detection
4. `fetch` API for backend communication with 3-retry exponential backoff
5. React Error Boundary + try/catch for error handling
6. CSS custom properties for dark/light mode theming
7. Inline citation badges with optional chapter links

---

## Phase 1: Design & Contracts

### Data Models

**See**: [data-model.md](./data-model.md)

**Key Entities**:
1. **ChatSession**: `{ sessionId: string, messages: Message[], createdAt: Date }`
2. **Message**: `{ id: string, role: 'user' | 'assistant', content: string, timestamp: Date, citations?: Citation[] }`
3. **Citation**: `{ chapter: string, section: string, url?: string }`
4. **SelectedContext**: `{ text: string, source: string }`

### API Contracts

**See**: [contracts/backend-api.yaml](./contracts/backend-api.yaml)

**Backend Endpoint**: `POST https://physical-ai-humanoid-robotics-textbook-production-3516.up.railway.app/chat/query`

**Request Schema**:
```typescript
{
  query: string;          // User's question
  sessionId: string;      // UUID for session tracking
  selected_context?: string; // Optional highlighted text
}
```

**Response Schema**:
```typescript
{
  answer: string;         // AI-generated response
  citations?: Array<{     // Optional source references
    chapter: string;
    section: string;
    url?: string;
  }>;
}
```

**Error Response**:
```typescript
{
  error: string;          // Error message
  code: number;           // HTTP status code
}
```

### Component Architecture

**Primary Components**:
1. **ChatWidgetButton**: Floating button (bottom-right corner) to toggle chat widget
2. **ChatWidget**: Main container with ChatKit `<Chat>` component
3. **ChatProvider Wrapper**: Wraps ChatKit provider with session management
4. **TextSelectionPopover**: Appears on text selection with "Ask AI About This" button
5. **CitationBadge**: Displays inline citation with optional link
6. **ErrorBoundary**: Catches render errors and shows fallback UI

**Data Flow**:
1. User clicks ChatWidgetButton → ChatWidget opens
2. User types question → sends to chatService.ts → backend API
3. Backend responds → ChatKit displays message + citations
4. User selects text → TextSelectionPopover appears → sends with `selected_context`
5. Session persists in localStorage → restores on widget reopen

### Quickstart Guide

**See**: [quickstart.md](./quickstart.md)

**Setup Steps**:
1. Install dependencies: `npm install @openai/chatkit-react uuid`
2. Add backend URL to `docusaurus.config.ts` under `customFields`
3. Create `/src/components/chat/ChatWidget.tsx`
4. Import ChatWidget in `src/theme/Layout/index.tsx` (Docusaurus theme swizzling)
5. Run `npm start` to test locally
6. Verify widget loads, connects to backend, displays responses

---

## Phase 2: Task Generation

**Next Step**: Run `/sp.tasks` to generate actionable task list from this plan.

**Expected Task Categories**:
- Setup: Install dependencies, configure Docusaurus
- UI Implementation: ChatWidget, TextSelectionPopover, CitationBadge components
- Backend Integration: chatService.ts, error handling, retry logic
- Session Management: useChatSession hook, localStorage persistence
- Theming: Dark/light mode CSS, Docusaurus theme integration
- Testing: Component tests, E2E tests, error scenarios
- QA: Performance validation, mobile responsiveness, accessibility

---

## Post-Design Constitution Re-Check

*Re-evaluate gates after Phase 1 design completion*

### Conversational Interface Principle
- ✅ **PASS**: ChatKit integration design confirmed

### Chat UI Standards
- ✅ **PASS**: All ChatKit components accounted for in architecture
- ✅ **PASS**: Floating widget design with ChatWidgetButton
- ✅ **PASS**: Dark/light mode via CSS custom properties
- ✅ **PASS**: Client-side only (useEffect post-hydration)
- ✅ **PASS**: TextSelectionPopover for text selection feature
- ✅ **PASS**: CitationBadge for citation display
- ✅ **PASS**: ErrorBoundary for graceful error handling

### Frontend Integration Constraints
- ✅ **PASS**: Component path `/src/components/chat/ChatWidget.tsx` confirmed
- ✅ **PASS**: Backend URL in Docusaurus config (no hardcoded URLs)
- ✅ **PASS**: No API keys in design

### Chat UI Success Criteria
- ✅ **PASS**: Performance targets achievable with lazy loading
- ✅ **PASS**: Mobile responsive design with CSS breakpoints
- ✅ **PASS**: All features designed (text selection, citations, errors, sessions)

**Post-Design Result**: ✅ ALL GATES PASSED

---

## Risk Analysis

**Top Risks**:
1. **ChatKit Bundle Size**: ChatKit SDK may increase page load time
   - **Mitigation**: Lazy load ChatWidget only when user clicks button
   - **Fallback**: Code-split ChatKit into separate chunk

2. **Backend API Changes**: Backend contract may change without notice
   - **Mitigation**: Defensive parsing of backend responses, strict TypeScript types
   - **Fallback**: Version API contract, negotiate with backend team

3. **Browser Compatibility**: Text selection API may behave differently across browsers
   - **Mitigation**: Test on all target browsers (Chrome, Firefox, Safari, Edge)
   - **Fallback**: Polyfill or graceful degradation for unsupported browsers

**Minor Risks**:
- Dark mode CSS conflicts with Docusaurus theme (Low: CSS custom properties are isolated)
- Session ID collisions (Very Low: UUID v4 has negligible collision probability)
- Mobile text selection UX issues (Medium: Requires extensive mobile testing)

---

## Next Steps

1. ✅ Complete Phase 0 (Research) - DONE
2. ✅ Complete Phase 1 (Design & Contracts) - DONE
3. ⏸️ Run `/sp.tasks` to generate implementation task list
4. ⏸️ Execute tasks sequentially or in parallel as marked
5. ⏸️ Run QA validation against success criteria
6. ⏸️ Deploy to production branch

**Current Status**: Planning complete, ready for task generation and implementation.
