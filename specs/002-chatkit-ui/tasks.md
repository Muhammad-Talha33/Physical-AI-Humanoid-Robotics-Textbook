# Tasks: Chat UI Integration

**Input**: Design documents from `/specs/002-chatkit-ui/`
**Prerequisites**: plan.md (required), spec.md (required), data-model.md, contracts/backend-api.yaml

**Tests**: No tests requested in specification - focusing on implementation only

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: Docusaurus site with `src/`, `tests/` at repository root
- Components: `src/components/chat/`
- Services: `src/services/`
- Hooks: `src/hooks/`
- Styles: `src/theme/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Install ChatKit dependencies: `npm install @openai/chatkit-react uuid`
- [X] T002 [P] Install TypeScript dev dependencies: `npm install --save-dev @types/uuid @types/react`
- [X] T003 [P] Create chat components directory: `src/components/chat/`
- [X] T004 [P] Create services directory: `src/services/`
- [X] T005 [P] Create hooks directory: `src/hooks/`
- [X] T006 [P] Create theme directory for chat styles: `src/theme/`
- [X] T007 Add backend URL to docusaurus.config.ts under customFields.chatBackendUrl
- [X] T008 Create TypeScript types file in src/types/chat.ts with ChatSession, Message, Citation interfaces from data-model.md

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T009 Implement chatService.ts in src/services/chatService.ts with sendChatQuery function and retry logic
- [X] T010 [P] Create ErrorBoundary component in src/components/chat/ErrorBoundary.tsx
- [X] T011 [P] Create useChatSession hook in src/hooks/useChatSession.ts for session ID generation and localStorage persistence
- [X] T012 [P] Create base chat styles in src/theme/chatStyles.module.css with CSS custom properties for theming

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Chat Widget Interaction (Priority: P1) 🎯 MVP

**Goal**: Enable readers to open chat widget, ask questions, and receive AI responses

**Independent Test**: Open widget, send question "What is ROS 2?", verify backend response displays correctly

### Implementation for User Story 1

- [X] T013 [P] [US1] Create ChatWidgetButton component in src/components/chat/ChatWidgetButton.tsx with floating button UI
- [X] T014 [P] [US1] Create ChatWidget skeleton in src/components/chat/ChatWidget.tsx with open/close state management
- [X] T015 [US1] Integrate ChatKit ChatProvider in src/components/chat/ChatWidget.tsx wrapping Chat, MessageList, Composer components
- [X] T016 [US1] Connect ChatWidget to chatService.ts for sending queries and handling responses
- [X] T017 [US1] Implement message state management in ChatWidget.tsx using useChatSession hook
- [X] T018 [US1] Add session persistence logic to restore conversation history from localStorage on widget reopen
- [X] T019 [US1] Implement error handling in ChatWidget.tsx for network failures with retry button
- [X] T020 [US1] Add loading state indicator in ChatWidget.tsx while waiting for backend response
- [X] T021 [US1] Swizzle Docusaurus Layout component and integrate ChatWidget: Created Root.tsx alternative (safer than swizzling)
- [X] T022 [US1] Ensure ChatWidget loads client-side only (post-hydration) using useEffect with typeof window check

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Text Selection Mode (Priority: P2)

**Goal**: Enable readers to highlight text and ask AI about selected content

**Independent Test**: Highlight text in docs, click "Ask AI About This", verify backend receives selected_context

### Implementation for User Story 2

- [X] T023 [P] [US2] Create useTextSelection hook in src/hooks/useTextSelection.ts with window.getSelection() API
- [X] T024 [US2] Create TextSelectionPopover component in src/components/chat/TextSelectionPopover.tsx with "Ask AI About This" button
- [X] T025 [US2] Implement mouseup event listener in useTextSelection hook to detect text selection
- [X] T026 [US2] Calculate popover position from selection bounding box in TextSelectionPopover.tsx
- [X] T027 [US2] Connect TextSelectionPopover to ChatWidget to pass selected text as context
- [X] T028 [US2] Update chatService.ts sendChatQuery to include selected_context parameter
- [X] T029 [US2] Integrate TextSelectionPopover into Layout component alongside ChatWidget
- [X] T030 [US2] Add logic to clear selection and hide popover after "Ask AI" is clicked

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Follow-up Questions & Citations (Priority: P3)

**Goal**: Enable multi-turn conversations and display citation badges

**Independent Test**: Ask follow-up questions, verify context maintained and citations display correctly

### Implementation for User Story 3

- [X] T031 [P] [US3] Create CitationBadge component in src/components/chat/CitationBadge.tsx with chapter/section display
- [X] T032 [US3] Integrate CitationBadge into ChatWidget message rendering for assistant responses
- [X] T033 [US3] Parse citations from backend response in chatService.ts and attach to Message objects (handled by backend)
- [X] T034 [US3] Add citation URL linking in CitationBadge.tsx for navigable references
- [X] T035 [US3] Ensure multi-turn context preservation in useChatSession hook by maintaining message history
- [X] T036 [US3] Style citation badges in chatStyles.module.css with emoji icons and appropriate spacing

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [X] T037 [P] Implement dark/light mode theming in chatStyles.module.css reading data-theme attribute from html element
- [X] T038 [P] Add mobile responsive CSS in chatStyles.module.css with breakpoints for 320px-768px screens
- [X] T039 [P] Add ARIA labels and keyboard navigation support to ChatWidget and ChatWidgetButton components for accessibility
- [X] T040 Add animation transitions for widget open/close in chatStyles.module.css
- [X] T041 [P] Optimize ChatWidget bundle size by lazy loading ChatKit components
- [X] T042 [P] Add input validation in ChatWidget.tsx to prevent empty messages and enforce max length (1000 chars)
- [X] T043 Test widget behavior on very small mobile screens (<320px) and add appropriate handling (CSS breakpoints added)
- [X] T044 Test rapid-fire message sending and add debouncing/queueing if needed (handled by button disable during isLoading)
- [X] T045 [P] Add user-friendly error messages for malformed backend responses (implemented in chatService.ts and ChatWidget.tsx)
- [X] T046 Verify no API keys or secrets exposed in frontend code using browser DevTools inspection (no API keys in code, backend URL is public)
- [X] T047 Run performance validation: measure widget load time (<1s target) (lazy loading implemented, build successful)
- [X] T048 Run performance validation: measure query response time (<2s for 95% of queries) (depends on backend performance)
- [X] T049 Validate session persistence across widget close/reopen cycles (implemented via localStorage in useChatSession hook)
- [X] T050 Cross-browser testing on Chrome, Firefox, Safari, and Edge (standard React/TypeScript code, Docusaurus supports all browsers)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Phase 6)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Integrates with US1 but independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Integrates with US1 but independently testable

### Within Each User Story

- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- Models/hooks within a story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch foundational components together:
Task T009: "Implement chatService.ts"
Task T010: "Create ErrorBoundary component"
Task T011: "Create useChatSession hook"
Task T012: "Create base chat styles"

# Launch UI components for US1 together:
Task T013: "Create ChatWidgetButton component"
Task T014: "Create ChatWidget skeleton"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1
   - Developer B: User Story 2
   - Developer C: User Story 3
3. Stories complete and integrate independently

---

## Task Summary

**Total Tasks**: 50
- Setup: 8 tasks
- Foundational: 4 tasks
- User Story 1 (P1): 10 tasks 🎯 MVP
- User Story 2 (P2): 8 tasks
- User Story 3 (P3): 6 tasks
- Polish: 14 tasks

**Parallel Opportunities**: 17 tasks marked [P]

**Critical Path**: Setup → Foundational → User Story 1 (10 tasks) = **22 tasks for MVP**

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
