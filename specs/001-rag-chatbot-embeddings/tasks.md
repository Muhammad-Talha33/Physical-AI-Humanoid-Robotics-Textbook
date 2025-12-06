# Tasks: RAG Chatbot with Embeddings for Book Content

**Input**: Design documents from `/specs/001-rag-chatbot-embeddings/`
**Prerequisites**: plan.md (required), spec.md (required for user stories)

**Tests**: Not explicitly requested in the feature specification - tests are OPTIONAL and excluded from this task list.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create rag-backend/ project structure with src/, tests/, scripts/, docs/ directories
- [X] T002 Initialize Python 3.11+ project with requirements.txt (FastAPI, OpenAI Agents SDK, Qdrant Client, tiktoken, pydantic, python-dotenv)
- [X] T003 Create requirements-dev.txt with pytest, pytest-asyncio, pytest-cov, httpx
- [X] T004 [P] Create .env.example with OpenAI API key, Qdrant URL/API key, Neon Postgres connection string placeholders
- [X] T005 [P] Create railway.toml or fly.toml for cloud platform deployment configuration
- [X] T006 [P] Configure project-level .gitignore for Python (.env, __pycache__, venv/, .pytest_cache/)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T007 Create src/config/__init__.py and src/config/settings.py with environment-based configuration (OpenAI API key, Qdrant config, Postgres connection, rate limit settings)
- [X] T008 Create scripts/setup_qdrant.py to initialize Qdrant collection "book-embeddings" with appropriate vector dimensions and distance metric
- [X] T009 Create scripts/setup_postgres.py to create schema for Query, RetrievedContext, ConversationSession, Response, RateLimitTracker, Metrics tables
- [X] T010 [P] Create src/monitoring/__init__.py and src/monitoring/logger.py with structured logging using correlation IDs
- [X] T011 [P] Create src/monitoring/metrics.py for tracking query latency, retrieval quality, error rates, and API costs
- [X] T012 [P] Create src/api/__init__.py and src/api/models.py with Pydantic request/response models (QueryRequest, QueryResponse, HealthResponse, MetricsResponse)
- [X] T013 Create src/api/main.py with FastAPI application setup, CORS configuration, and middleware registration
- [X] T014 Create src/api/routes.py with placeholder endpoints for /api/v1/chat/query, /api/v1/health, /api/v1/metrics

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Content Embedding Generation (Priority: P1) 🎯 MVP

**Goal**: Convert all finalized book chapters into searchable embeddings and store in Qdrant vector database with metadata

**Independent Test**: Ingest a sample chapter, verify embeddings are generated and stored in the vector database with correct metadata (chapter name, section title, text snippet), and perform a manual vector similarity search to confirm retrieval works

### Implementation for User Story 1

- [X] T015 [P] [US1] Create src/embeddings/__init__.py
- [X] T016 [P] [US1] Create src/embeddings/chunker.py with sentence-boundary aware text chunking (500-1000 tokens, 20-30% overlap, ±50 tokens for sentence alignment)
- [X] T017 [P] [US1] Create src/embeddings/generator.py with OpenAI embedding generation using text-embedding-3-small or text-embedding-ada-002 with exponential backoff retry logic (3 attempts, 1s/2s/4s delays)
- [X] T018 [US1] Create src/embeddings/ingestion.py with batch processing for book chapters (concurrent embedding generation, incremental processing, chapter update handling)
- [X] T019 [P] [US1] Create src/retrieval/__init__.py
- [X] T020 [P] [US1] Create src/retrieval/qdrant_client.py with Qdrant vector database operations (insert embeddings with metadata, delete by chapter, health check)
- [X] T021 [US1] Implement chapter ingestion pipeline in scripts/run_ingestion.py that processes /docs markdown files, chunks content, generates embeddings, and stores in Qdrant
- [X] T022 [US1] Add error handling for embedding generation failures (log chapter identifier, skip failed chapters, continue processing, alert administrators)
- [X] T023 [US1] Add markdown metadata extraction (chapter number, title from # heading, module/section organization)
- [X] T024 [US1] Add validation for chunk token counts and overlap percentages
- [X] T025 [US1] Add logging for ingestion pipeline (chunks processed, embeddings generated, storage confirmations, failures)

**Checkpoint**: At this point, User Story 1 should be fully functional - sample chapter can be ingested, embeddings stored, and manual vector search retrieves results

---

## Phase 4: User Story 2 - Contextual Question Retrieval (Priority: P2)

**Goal**: Enable readers to ask questions and receive answers grounded strictly in book content with chapter/section citations

**Independent Test**: Submit a variety of questions about book topics (e.g., "What is ROS 2?"), verify retrieved context comes from correct chapters/sections, confirm answers are accurate and grounded in retrieved text, and verify "no information" responses when context is insufficient

### Implementation for User Story 2

- [X] T026 [P] [US2] Create src/retrieval/retriever.py with vector similarity search using configurable threshold (0.70-0.75), retrieving top 3-5 chunks
- [X] T027 [P] [US2] Create src/retrieval/context_builder.py to assemble retrieved chunks with source citations (chapter name, section title, chunk IDs)
- [X] T028 [P] [US2] Create src/chat/__init__.py
- [X] T029 [P] [US2] Create src/chat/response_generator.py with OpenAI completion API integration for answer generation using retrieved context
- [X] T030 [US2] Implement grounding validation in src/chat/response_generator.py to ensure responses reference only retrieved context
- [X] T031 [US2] Add citation formatting in response text (chapter + section references)
- [X] T032 [US2] Add "insufficient context" detection and appropriate response ("I cannot find information about this in the book content")
- [X] T033 [US2] Implement query embedding generation in src/retrieval/retriever.py using same OpenAI model as content embeddings
- [X] T034 [US2] Add validation for query length (max 1000 tokens, truncate with warning if exceeded)
- [X] T035 [US2] Implement POST /api/v1/chat/query endpoint in src/api/routes.py with query processing, retrieval, response generation
- [X] T036 [US2] Add error responses for external service failures (Qdrant unavailable, OpenAI API errors) with retry logic
- [X] T037 [US2] Add query logging to Postgres (Query table: query_id, query_text, timestamp, processing_time_ms)
- [X] T038 [US2] Add retrieval logging to Postgres (RetrievedContext table: chunk_id, similarity_score, rank, was_used_in_response)
- [X] T039 [US2] Add response logging to Postgres (Response table: response_text, source_citations, grounding_status, generation_time_ms, openai_tokens_used)
- [X] T040 [US2] Add metrics tracking for query latency (p50, p95, p99) and retrieval quality (average similarity score)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - questions can be asked via API, relevant context retrieved, and grounded answers returned with citations

---

## Phase 5: User Story 3 - Multi-Turn Conversation Handling (Priority: P3)

**Goal**: Enable readers to ask follow-up questions that build on previous answers for natural, contextual conversations

**Independent Test**: Conduct a multi-turn conversation (e.g., ask about ROS 2, then "What are its core concepts?", then "How do I implement this in Python?"), verify context is retained across turns, confirm answers remain grounded in book content, and validate sliding window keeps token limits in check

### Implementation for User Story 3

- [X] T041 [P] [US3] Create src/chat/session.py with ConversationSession management (session creation, history tracking, sliding window of last 5-10 turns)
- [X] T042 [US3] Implement session persistence in Postgres (ConversationSession table: session_id, user_identifier, conversation_history JSONB, query_count)
- [X] T043 [US3] Add session ID handling in POST /api/v1/chat/query endpoint (accept session_id in request, create new session if null)
- [X] T044 [US3] Implement conversation context integration in src/chat/response_generator.py (include previous turns when generating embeddings and responses)
- [X] T045 [US3] Add coreference resolution for follow-up questions (e.g., "it" refers to previously mentioned topic)
- [X] T046 [US3] Implement sliding window logic to maintain last 5-10 conversation turns and prevent token limit overflow
- [X] T047 [US3] Add session activity tracking (last_activity_at timestamp, auto-expire inactive sessions)
- [X] T048 [US3] Add conversation history to response logging (track turn_number in Query table)
- [X] T049 [US3] Update session state after each query (increment query_count, update conversation_history, set last_activity_at)

**Checkpoint**: All user stories should now be independently functional - multi-turn conversations work with context retention, and each story (US1, US2, US3) can be tested and validated separately

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and production readiness

- [X] T050 [P] Create src/chat/rate_limiter.py with 50 queries/user/hour enforcement using Postgres RateLimitTracker table
- [X] T051 [P] Add rate limiting middleware to FastAPI application in src/api/main.py
- [X] T052 [P] Implement 429 Too Many Requests response with retry_after_seconds in src/api/routes.py
- [X] T053 [P] Implement GET /api/v1/health endpoint in src/api/routes.py with Qdrant/Postgres/OpenAI service status checks
- [X] T054 [P] Implement GET /api/v1/metrics endpoint in src/api/routes.py with query latency, retrieval quality, error rates, API costs
- [X] T055 [P] Add API key authentication for admin endpoints (/api/v1/metrics)
- [X] T056 [P] Add input sanitization for query text (prevent injection attacks, validate length)
- [ ] T057 [P] Create src/cli/__init__.py and src/cli/ingest.py with CLI tool for manual embedding generation
- [X] T058 [P] Add cost tracking calculation (OpenAI token usage → USD conversion) in src/monitoring/metrics.py
- [X] T059 [P] Add error rate counters by type (openai_error, qdrant_error, rate_limit) in src/monitoring/metrics.py
- [X] T060 [P] Create README.md for rag-backend with project overview, setup instructions, API documentation
- [X] T061 [P] Create tests/fixtures/sample_chapter.md with representative book content for testing
- [X] T062 [P] Add markdown formatting preservation in retrieved text snippets (code blocks, lists, emphasis)
- [X] T063 Add edge case handling for questions outside book scope ("I can only answer questions based on the Physical AI & Humanoid Robotics book content")
- [X] T064 Add edge case handling for extremely long questions (>1000 tokens truncation with warning)
- [ ] T065 Add edge case handling for contradictory context from multiple chapters (present both perspectives with citations)
- [X] T066 [P] Update quickstart.md with complete developer onboarding guide (prerequisites, environment setup, Qdrant initialization, Postgres schema, ingestion, API server, testing, monitoring, troubleshooting)
- [X] T067 Run complete ingestion pipeline with all /docs chapters and validate embeddings
- [X] T068 Validate query response latency meets <2s p95 requirement with sample queries
- [X] T069 Validate zero hallucinations with 20+ diverse test queries and manual review

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3, 4, 5)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Phase 6)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Requires US1 embeddings to exist for retrieval testing
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Builds on US2 query/response functionality

### Within Each User Story

**User Story 1 (Content Embedding)**:
- T015, T016, T017, T019, T020 can run in parallel (different files)
- T018 depends on T016, T017 (chunker + generator)
- T021 depends on T018, T020 (ingestion uses chunker/generator/Qdrant client)
- T022-T025 depend on T021 (enhancements to ingestion pipeline)

**User Story 2 (Contextual Retrieval)**:
- T026, T027, T028, T029 can run in parallel (different files)
- T030-T032 depend on T029 (enhancements to response generator)
- T033 depends on T026 (query embedding in retriever)
- T035 depends on T026, T027, T029 (API endpoint uses retriever, context builder, response generator)
- T036-T040 depend on T035 (error handling, logging, metrics for API endpoint)

**User Story 3 (Multi-Turn Conversation)**:
- T041 can start independently (session management)
- T042-T043 depend on T041 (session persistence and API integration)
- T044-T046 depend on T043 (conversation context integration)
- T047-T049 depend on T044 (session tracking enhancements)

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel (T004, T005)
- All Foundational tasks marked [P] can run in parallel within Phase 2 (T010, T011, T012)
- Once Foundational phase completes, User Story 1 tasks can start (T015-T020 in parallel)
- Once US1 embeddings exist, User Story 2 can start (T026-T029 in parallel)
- Once US2 query/response works, User Story 3 can start (T041 independently)
- All Polish tasks marked [P] can run in parallel (T050-T062)

---

## Parallel Example: User Story 1

```bash
# Launch all foundational components for User Story 1 together:
Task T015: "Create src/embeddings/__init__.py"
Task T016: "Create src/embeddings/chunker.py with sentence-boundary aware chunking"
Task T017: "Create src/embeddings/generator.py with OpenAI embedding generation and retry logic"
Task T019: "Create src/retrieval/__init__.py"
Task T020: "Create src/retrieval/qdrant_client.py with vector database operations"

# Then launch ingestion pipeline after foundational components complete:
Task T021: "Implement chapter ingestion pipeline in scripts/run_ingestion.py"
```

---

## Parallel Example: User Story 2

```bash
# Launch all foundational components for User Story 2 together:
Task T026: "Create src/retrieval/retriever.py with vector similarity search"
Task T027: "Create src/retrieval/context_builder.py with citation assembly"
Task T028: "Create src/chat/__init__.py"
Task T029: "Create src/chat/response_generator.py with OpenAI completion API"

# Then integrate into API endpoint:
Task T035: "Implement POST /api/v1/chat/query endpoint"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Content Embedding Generation)
4. **STOP and VALIDATE**: Test User Story 1 independently
   - Ingest sample chapter
   - Verify embeddings in Qdrant
   - Perform manual vector search
5. Optional: Add T068 (full ingestion) and validate

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Embeddings ready (MVP backend!)
3. Add User Story 2 → Test independently → Query/Response working (Functional MVP!)
4. Add User Story 3 → Test independently → Multi-turn conversations enabled (Enhanced UX!)
5. Add Polish tasks → Production ready (Rate limiting, monitoring, error handling)
6. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (T016-T026)
   - Developer B: User Story 2 (T027-T041) - starts after US1 has some embeddings
   - Developer C: User Story 3 (T042-T050) - starts after US2 query/response works
3. Stories complete and integrate independently

---

## Task Summary

- **Total Tasks**: 69
- **Setup (Phase 1)**: 6 tasks
- **Foundational (Phase 2)**: 8 tasks (CRITICAL - blocks all user stories)
- **User Story 1 (P1)**: 11 tasks (T015-T025)
- **User Story 2 (P2)**: 15 tasks (T026-T040)
- **User Story 3 (P3)**: 9 tasks (T041-T049)
- **Polish (Phase 6)**: 20 tasks (T050-T069)

**Parallel Opportunities Identified**:
- 3 tasks in Setup
- 3 tasks in Foundational
- 5 tasks in User Story 1
- 4 tasks in User Story 2
- 13 tasks in Polish

**Suggested MVP Scope**: Phase 1 + Phase 2 + Phase 3 (User Story 1) = 25 tasks
**Functional MVP**: Add Phase 4 (User Story 2) = 40 tasks
**Enhanced MVP**: Add Phase 5 (User Story 3) = 49 tasks
**Production Ready**: Add Phase 6 (Polish) = 69 tasks

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
- Tests are OPTIONAL (not included) - can be added later if TDD approach is requested
