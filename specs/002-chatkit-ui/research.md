# Research: Chat UI Integration

**Feature**: 002-chatkit-ui
**Date**: 2025-12-07
**Purpose**: Research ChatKit integration patterns, Docusaurus compatibility, and frontend architecture decisions

---

## 1. ChatKit Integration with Docusaurus

### Decision
Use client-side rendering with `useEffect` to load ChatKit after hydration

### Rationale
- Docusaurus uses SSR/SSG for static site generation
- ChatKit requires browser APIs (DOM, localStorage, window)
- Loading post-hydration avoids SSR conflicts while maintaining Docusaurus build compatibility
- Preserves SEO benefits of Docusaurus SSG

### Alternatives Considered
1. **Custom Docusaurus plugin**
   - ✗ More complex setup
   - ✗ Unnecessary overhead for single component
   - ✓ Would provide Docusaurus lifecycle hooks

2. **BrowserOnly wrapper**
   - ✓ Simple Docusaurus utility
   - ✗ Less control over timing
   - ✗ May still trigger during build

### Implementation Pattern
```typescript
useEffect(() => {
  if (typeof window !== 'undefined') {
    // Load ChatKit after hydration
  }
}, []);
```

---

## 2. ChatKit Component Architecture

### Decision
Use `<ChatProvider>` at root with `<Chat>`, `<MessageList>`, `<Composer>` nested

### Rationale
- ChatKit's recommended architecture
- Provides state management out-of-box
- Handles message rendering, composition, and threading
- Minimal custom code required

### Alternatives Considered
1. **Custom chat UI**
   - ✗ Reinventing the wheel
   - ✗ Violates constitution requirement for ChatKit
   - ✓ Full control over UI/UX

2. **Headless ChatKit**
   - ✓ Flexibility for custom UI
   - ✗ Loses built-in UX polish
   - ✗ More implementation work

### Component Hierarchy
```
<ChatProvider>
  <Chat>
    <MessageList />
    <Composer />
    <Thread />
  </Chat>
</ChatProvider>
```

---

## 3. Session Management Strategy

### Decision
Generate UUID on component mount, store in React state + localStorage for session persistence

### Rationale
- Lightweight, client-side only
- Survives widget close/reopen within page session
- No server-side complexity
- localStorage provides persistence across widget toggles

### Alternatives Considered
1. **Server-side sessions**
   - ✗ Unnecessary complexity
   - ✗ Backend doesn't require stateful sessions
   - ✓ Would enable cross-page persistence

2. **Cookies**
   - ✗ Overkill for single-page session management
   - ✗ GDPR compliance concerns
   - ✓ Automatic persistence

### Implementation
- Generate UUID v4 on first mount
- Store in React state for current session
- Persist in localStorage with key `chatbot-session-${pageId}`
- Restore on widget reopen

---

## 4. Text Selection Detection

### Decision
Use browser `window.getSelection()` API with `mouseup` event listener

### Rationale
- Standard web API, works across all modern browsers
- No external dependencies
- Provides selected text, range, and bounding box

### Alternatives Considered
1. **Selection libraries (e.g., rangy)**
   - ✗ Adds bundle size
   - ✗ Native API sufficient for this use case
   - ✓ Cross-browser consistency

2. **Double-click triggers**
   - ✗ Less intuitive UX
   - ✗ Doesn't capture arbitrary text selections
   - ✓ Simpler implementation

### Implementation Pattern
```typescript
useEffect(() => {
  const handleSelection = () => {
    const selection = window.getSelection();
    if (selection && selection.toString().trim()) {
      // Show popover
    }
  };
  document.addEventListener('mouseup', handleSelection);
  return () => document.removeEventListener('mouseup', handleSelection);
}, []);
```

---

## 5. Backend API Communication

### Decision
Use `fetch` API with async/await, custom retry logic for network errors

### Rationale
- Native browser API, no external dependencies
- Simple error handling with try/catch
- Async/await for clean promise handling
- Custom retry logic for resilience

### Alternatives Considered
1. **Axios**
   - ✗ Adds ~13KB to bundle size
   - ✓ Built-in retry and interceptors
   - ✓ Better error handling utilities

2. **ChatKit built-in fetch**
   - ✗ May not support custom retry/error logic
   - ✗ Less control over request lifecycle
   - ✓ Integrated with ChatKit state

### Retry Strategy
- 3 attempts with exponential backoff
- Delays: 1s, 2s, 4s
- Only retry on network errors (5xx, timeout)
- Fail fast on client errors (4xx)

---

## 6. Error Handling Pattern

### Decision
React Error Boundary + try/catch in async functions + UI error states

### Rationale
- Layered approach catches different error types
- Error Boundary catches React render errors
- try/catch handles network/async errors
- UI states provide user feedback

### Alternatives Considered
1. **Global error handler**
   - ✗ Less granular control
   - ✗ Harder to show contextual messages
   - ✓ Centralized error logging

2. **Toast notifications**
   - ✓ Non-intrusive
   - ✗ May be missed by users
   - ✓ Could be added as enhancement

### Error Types
- **Render errors**: Caught by Error Boundary → show fallback UI
- **Network errors**: Caught by try/catch → show retry button
- **Backend errors**: Parsed from response → show error message

---

## 7. Dark/Light Mode Integration

### Decision
Read Docusaurus theme from `data-theme` attribute on `<html>`, apply ChatKit CSS custom properties

### Rationale
- Docusaurus exposes theme via `data-theme` attribute
- ChatKit supports CSS variable theming
- Automatic sync with user's site theme toggle
- No duplicate theme state management

### Alternatives Considered
1. **Separate light/dark ChatKit configs**
   - ✗ Duplicates code
   - ✗ Harder to maintain
   - ✓ More explicit control

2. **CSS media query `prefers-color-scheme`**
   - ✗ Doesn't respect user's site theme toggle
   - ✗ May conflict with Docusaurus theme
   - ✓ System-level preference

### Implementation
```typescript
useEffect(() => {
  const theme = document.documentElement.getAttribute('data-theme');
  // Apply ChatKit CSS variables based on theme
}, []);
```

---

## 8. Citation Display Format

### Decision
Parse backend response for citation metadata, render as inline badges with chapter/section links

### Rationale
- Non-intrusive to chat flow
- Allows users to verify sources without leaving chat
- Clickable links for direct navigation
- Visually distinct from message text

### Alternatives Considered
1. **Footnotes**
   - ✗ Breaks chat flow
   - ✗ Harder to click on mobile
   - ✓ Traditional academic format

2. **Tooltip hover**
   - ✗ Hidden unless hovered
   - ✗ Less discoverable
   - ✓ Saves space

### Citation Badge Format
```
[📖 Chapter X: Section Y]
```
- Emoji icon for visual cue
- Chapter and section names
- Link to chapter (if URL provided by backend)

---

## Key Findings

1. **ChatKit Compatibility**: ChatKit requires React 18.x (compatible with Docusaurus 3.x)
2. **Backend Contract**: `/chat/query` expects `{ query, sessionId, selected_context? }`
3. **Response Format**: `{ answer, citations?: Array<{chapter, section, url?}> }`
4. **Text Selection**: `window.getSelection()` works without polyfills in all target browsers
5. **Docusaurus Integration**: Custom components via `src/theme` swizzling or direct import

---

## Technical Decisions Locked

1. ✅ Client-side rendering with `useEffect` + `useState`
2. ✅ UUID v4 for session IDs (via `uuid` library)
3. ✅ `window.getSelection()` for text selection
4. ✅ `fetch` API with 3-retry exponential backoff
5. ✅ React Error Boundary + try/catch
6. ✅ CSS custom properties for theming
7. ✅ Inline citation badges with links

---

## Open Questions

None. All research tasks completed and decisions finalized.

---

## References

- [Docusaurus Documentation](https://docusaurus.io/docs)
- [OpenAI ChatKit Docs](https://platform.openai.com/docs/guides/chatkit)
- [Web Selection API](https://developer.mozilla.org/en-US/docs/Web/API/Selection)
- [React Error Boundaries](https://react.dev/reference/react/Component#catching-rendering-errors-with-an-error-boundary)
