---
id: 002
title: Create implementation plan for ChatKit UI
stage: plan
date: 2025-12-07
surface: agent
model: claude-sonnet-4-5-20250929
feature: 002-chatkit-ui
branch: 002-chatkit-ui
user: user
command: /sp.plan
labels: ["plan", "chatkit-ui", "architecture", "design", "frontend"]
links:
  spec: specs/002-chatkit-ui/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/002-chatkit-ui/plan.md
  - specs/002-chatkit-ui/research.md
  - specs/002-chatkit-ui/data-model.md
  - specs/002-chatkit-ui/contracts/backend-api.yaml
  - specs/002-chatkit-ui/quickstart.md
tests:
  - N/A (planning artifacts)
---

## Prompt

```text
Plan: Chat UI Integration for Physical AI & Humanoid Robotics Book

Feature Branch: 002-chatkit-ui
Created: 2025-12-07
Backend Endpoint: https://physical-ai-humanoid-robotics-textbook-production-3516.up.railway.app/chat/query
Chat UI Framework: OpenAI ChatKit
ChatKit Docs: https://platform.openai.com/docs/guides/chatkit

Goal: Integrate a modern, interactive Chat UI using OpenAI ChatKit into the Docusaurus book. The widget should communicate with the deployed RAG backend, support text selection, follow-ups, citations, multi-turn conversations, and provide a seamless reader experience.

[Complete user input with implementation phases and technical details]
```

## Response snapshot

Successfully created comprehensive implementation plan for Chat UI Integration (002-chatkit-ui).

**Planning Artifacts Created**:
1. **plan.md**: Complete implementation plan with technical context, constitution check, project structure, Phase 0 (Research), and Phase 1 (Design)
2. **research.md**: 8 research decisions covering ChatKit integration, session management, text selection, backend communication, error handling, theming, and citations
3. **data-model.md**: TypeScript interfaces for ChatSession, Message, Citation, SelectedContext, API contracts, and storage schemas
4. **contracts/backend-api.yaml**: OpenAPI 3.0 spec for backend `/chat/query` endpoint with request/response schemas and examples
5. **quickstart.md**: Developer onboarding guide with setup steps, code examples, and troubleshooting

**Technical Stack**:
- TypeScript 5.x + React 18.x
- OpenAI ChatKit SDK
- Docusaurus 3.x
- UUID for session management
- localStorage for persistence
- fetch API with retry logic

**Constitution Compliance**: ✅ ALL GATES PASSED
- OpenAI ChatKit usage (mandated)
- Floating widget design
- Dark/light mode support
- Client-side only rendering
- Text selection feature
- Citation display
- Session management
- Error handling
- No API key exposure

**Key Architectural Decisions**:
1. Client-side rendering with useEffect (post-hydration)
2. ChatKit provider pattern with nested components
3. UUID v4 session IDs in localStorage
4. window.getSelection() for text detection
5. fetch API with 3-retry exponential backoff
6. React Error Boundary + try/catch layered error handling
7. CSS custom properties for theming
8. Inline citation badges with chapter links

**Risk Analysis**:
- Top risk: ChatKit bundle size (mitigation: lazy loading)
- Medium risk: Backend API changes (mitigation: defensive parsing)
- Medium risk: Browser compatibility (mitigation: cross-browser testing)

**Next Phase**: Ready for `/sp.tasks` to generate implementation task list

## Outcome

- ✅ Impact: Complete implementation plan with research, design, contracts, and quickstart guide
- 🧪 Tests: N/A (planning artifacts - no code tests)
- 📁 Files: plan.md, research.md, data-model.md, contracts/backend-api.yaml, quickstart.md
- 🔁 Next prompts: Run `/sp.tasks` to generate actionable task list from plan
- 🧠 Reflection: Plan successfully balances constitution requirements (ChatKit, theming, security) with practical implementation considerations (SSR conflicts, error handling, mobile responsiveness). All gates passed, no violations.

## Evaluation notes (flywheel)

- Failure modes observed: None - all constitution gates passed
- Graders run and results (PASS/FAIL): Constitution Check - ALL PASS (Pre-design & Post-design)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
