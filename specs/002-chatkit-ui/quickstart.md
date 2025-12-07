# Quickstart Guide: Chat UI Integration

**Feature**: 002-chatkit-ui
**Date**: 2025-12-07
**Purpose**: Step-by-step guide to set up local development environment for ChatKit UI integration

---

## Prerequisites

- Node.js 18.x or later
- npm 9.x or later
- Git
- Code editor (VS Code recommended)
- Modern browser (Chrome, Firefox, Safari, or Edge)

---

## 1. Environment Setup

### Clone Repository

```bash
git clone https://github.com/Muhammad-Talha33/Physical-AI-Humanoid-Robotics-Textbook.git
cd Physical-AI-Humanoid-Robotics-Textbook
```

### Switch to Feature Branch

```bash
git checkout 002-chatkit-ui
```

### Install Dependencies

```bash
npm install
```

### Install ChatKit Dependencies

```bash
npm install @openai/chatkit-react uuid
npm install --save-dev @types/uuid
```

---

## 2. Configuration

### Add Backend URL to Docusaurus Config

Edit `docusaurus.config.ts`:

```typescript
const config: Config = {
  // ... existing config

  customFields: {
    chatBackendUrl: 'https://physical-ai-humanoid-robotics-textbook-production-3516.up.railway.app',
  },

  // ... rest of config
};
```

### Create Directory Structure

```bash
mkdir -p src/components/chat
mkdir -p src/services
mkdir -p src/hooks
mkdir -p tests/components/chat
mkdir -p tests/e2e
```

---

## 3. Create Core Components

### ChatWidget Component Skeleton

Create `src/components/chat/ChatWidget.tsx`:

```typescript
import React, { useEffect, useState } from 'react';
import { v4 as uuidv4 } from 'uuid';

export default function ChatWidget() {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [isOpen, setIsOpen] = useState(false);

  useEffect(() => {
    // Generate or restore session ID
    const storedSessionId = localStorage.getItem('chatbot-session-id');
    if (storedSessionId) {
      setSessionId(storedSessionId);
    } else {
      const newSessionId = uuidv4();
      setSessionId(newSessionId);
      localStorage.setItem('chatbot-session-id', newSessionId);
    }
  }, []);

  return (
    <div className="chat-widget">
      <button onClick={() => setIsOpen(!isOpen)}>
        {isOpen ? 'Close Chat' : 'Open Chat'}
      </button>
      {isOpen && sessionId && (
        <div className="chat-container">
          <p>Chat Widget (Session: {sessionId.substring(0, 8)}...)</p>
          {/* ChatKit components will go here */}
        </div>
      )}
    </div>
  );
}
```

### Backend Service

Create `src/services/chatService.ts`:

```typescript
interface ChatQueryRequest {
  query: string;
  sessionId: string;
  selected_context?: string;
}

interface ChatQueryResponse {
  answer: string;
  citations?: Array<{
    chapter: string;
    section: string;
    url?: string;
  }>;
}

export async function sendChatQuery(
  query: string,
  sessionId: string,
  selectedContext?: string
): Promise<ChatQueryResponse> {
  const backendUrl = (window as any).docusaurus?.siteConfig?.customFields?.chatBackendUrl;

  const response = await fetch(`${backendUrl}/chat/query`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      query,
      sessionId,
      selected_context: selectedContext,
    }),
  });

  if (!response.ok) {
    throw new Error(`Backend error: ${response.status}`);
  }

  return response.json();
}
```

---

## 4. Integrate ChatWidget into Docusaurus

### Option A: Swizzle Layout Component (Recommended)

```bash
npm run swizzle @docusaurus/theme-classic Layout -- --eject
```

Edit `src/theme/Layout/index.tsx`:

```typescript
import ChatWidget from '@site/src/components/chat/ChatWidget';

export default function Layout(props: Props): JSX.Element {
  return (
    <LayoutProvider>
      {/* ... existing layout code ... */}
      <ChatWidget />  {/* Add chat widget */}
    </LayoutProvider>
  );
}
```

### Option B: Custom Plugin (Alternative)

Create `src/plugins/chatWidget.js`:

```javascript
module.exports = function (context, options) {
  return {
    name: 'chat-widget-plugin',
    injectHtmlTags() {
      return {
        postBodyTags: [
          {
            tagName: 'div',
            attributes: {
              id: 'chat-widget-root',
            },
          },
        ],
      };
    },
  };
};
```

---

## 5. Local Development

### Start Development Server

```bash
npm start
```

The site will open at `http://localhost:3000`.

### Verify ChatWidget Loads

1. Open browser DevTools (F12)
2. Check Console for errors
3. Look for "Chat Widget" button in bottom-right corner
4. Click button to toggle widget
5. Verify session ID is generated

### Test Backend Connection

1. Open chat widget
2. Type a test question: "What is ROS 2?"
3. Check Network tab in DevTools for POST request to `/chat/query`
4. Verify response contains `answer` field

---

## 6. Development Workflow

### File Watching

Docusaurus auto-reloads on file changes. Edit components and see changes instantly.

### Component Development

1. Edit `src/components/chat/ChatWidget.tsx`
2. Save file
3. Browser auto-refreshes
4. Test changes

### Testing Backend Integration

Use `curl` or Postman to test backend manually:

```bash
curl -X POST https://physical-ai-humanoid-robotics-textbook-production-3516.up.railway.app/chat/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is ROS 2?",
    "sessionId": "550e8400-e29b-41d4-a716-446655440000"
  }'
```

---

## 7. Running Tests

### Component Tests

```bash
npm test -- --watchAll=false
```

### E2E Tests (Playwright)

```bash
npm run test:e2e
```

---

## 8. Build for Production

### Create Production Build

```bash
npm run build
```

### Serve Production Build Locally

```bash
npm run serve
```

Visit `http://localhost:3000` to test production build.

---

## 9. Debugging Tips

### ChatWidget Not Appearing

- **Check**: Is `ChatWidget` imported in Layout component?
- **Check**: Are there console errors in DevTools?
- **Fix**: Verify React 18.x is installed

### Backend Connection Fails

- **Check**: Is backend URL correct in `docusaurus.config.ts`?
- **Check**: Is backend online? (Visit backend URL in browser)
- **Fix**: Check CORS settings on backend

### Session ID Not Persisting

- **Check**: Is localStorage enabled in browser?
- **Check**: Is session ID being saved/restored in `useEffect`?
- **Fix**: Check browser's Application tab → localStorage

### Dark Mode Not Working

- **Check**: Is `data-theme` attribute on `<html>` element?
- **Check**: Are CSS custom properties defined?
- **Fix**: Verify Docusaurus theme toggle is working

---

## 10. Common Issues

### Issue: "Module not found: @openai/chatkit-react"

**Solution**: Run `npm install @openai/chatkit-react`

### Issue: TypeScript errors for `uuid`

**Solution**: Run `npm install --save-dev @types/uuid`

### Issue: Docusaurus build fails with "window is not defined"

**Solution**: Wrap ChatWidget loading in `useEffect` with `typeof window !== 'undefined'` check

### Issue: Backend returns 400 "Invalid sessionId"

**Solution**: Verify sessionId is valid UUID v4 format

---

## 11. Next Steps

1. ✅ Environment setup complete
2. ✅ ChatWidget skeleton created
3. ✅ Backend integration tested
4. ⏸️ Integrate OpenAI ChatKit components
5. ⏸️ Implement text selection feature
6. ⏸️ Add citation display
7. ⏸️ Implement error handling
8. ⏸️ Add dark/light mode support
9. ⏸️ Write unit tests
10. ⏸️ Write E2E tests

---

## Resources

- [Docusaurus Documentation](https://docusaurus.io/docs)
- [OpenAI ChatKit Docs](https://platform.openai.com/docs/guides/chatkit)
- [React Documentation](https://react.dev)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/intro.html)

---

## Support

- **Backend Issues**: Check Railway deployment logs
- **Frontend Issues**: Check browser DevTools console
- **Build Issues**: Check npm logs and Docusaurus build output

---

**Last Updated**: 2025-12-07
