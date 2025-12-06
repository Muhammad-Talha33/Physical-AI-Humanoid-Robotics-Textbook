# Implementation Plan: RAG Chatbot with Embeddings

**Branch**: `001-rag-chatbot-embeddings` | **Date**: 2025-12-06 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-rag-chatbot-embeddings/spec.md`

**Note**: This plan implements the embedding generation and RAG retrieval system for the Physical AI & Humanoid Robotics book.

## Summary

This feature enables readers to interact with book content through natural language questions by implementing a Retrieval-Augmented Generation (RAG) system. The system chunks book chapters into semantically meaningful segments (500-1000 tokens with sentence-boundary awareness), generates embeddings using OpenAI's embedding API, stores them in Qdrant Cloud vector database, and retrieves relevant context for answering reader queries. The implementation prioritizes zero-hallucination responses through strict grounding, <2s latency, cost control (<$20/month), and comprehensive observability.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**:
- OpenAI Python SDK (embeddings: text-embedding-ada-002 or text-embedding-3-small)
- Qdrant Client (Python SDK for vector operations)
- FastAPI 0.104+ (REST API for chat endpoints)
- tiktoken (OpenAI tokenizer for accurate chunking)
- pydantic 2.x (data validation)
- python-dotenv (configuration management)

**Storage**:
- Qdrant Cloud (vector embeddings with metadata)
- Neon Serverless Postgres (query logs, metrics, rate limit tracking, session management)
- File system (markdown book content in `/docs`)

**Testing**: pytest with pytest-asyncio, httpx (API testing), pytest-cov (coverage)

**Target Platform**: Linux server / Docker container (deployment), cross-platform development (Windows/macOS/Linux)

**Project Type**: Backend API service (single project with CLI tools for embedding generation)

**Performance Goals**:
- Query response: <2s p95 latency end-to-end
- Embedding generation: ~100-200 chunks/minute (parallel processing)
- Vector search: <200ms for top-5 similarity search
- API throughput: 50 concurrent users without degradation

**Constraints**:
- Cost: <$20/month total (OpenAI embeddings + API calls)
- Rate limiting: 50 queries/user/hour
- Similarity threshold: 0.70-0.75 (configurable)
- Chunk size: 500-1000 tokens with 20-30% overlap, ±50 tokens for sentence boundaries
- Retry logic: 3 attempts with exponential backoff (1s, 2s, 4s)

**Scale/Scope**:
- Content: 20-40 book chapters (~500-1000 text chunks total)
- Users: 50 concurrent readers
- Conversation history: 5-10 turns per session
- Metrics retention: 30 days minimum

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### RAG Chatbot Standards (from Constitution)

- [x] **Grounding**: System answers ONLY using book content - implemented via similarity threshold filtering and explicit "no information" responses
- [x] **Retrieval Quality**: High-quality embeddings (OpenAI text-embedding-3 or ada-002) with sentence-boundary aware chunking
- [x] **Hallucination Prevention**: Strict grounding enforced - similarity threshold 0.70-0.75, explicit rejection when below threshold
- [x] **Transparency**: Complete logging of queries, retrieved chunks, responses, and core metrics
- [x] **User Experience**: Multi-turn conversation support with context retention, chapter/section citations in responses
- [x] **Performance**: <2s latency requirement (p95) for standard queries

### Technical Accuracy & Quality

- [x] **Tested & Runnable**: All code components tested (unit + integration tests for chunking, embedding, retrieval, API)
- [x] **Error Handling**: Exponential backoff retry logic for OpenAI API failures (FR-016)
- [x] **Observability**: Core metrics tracked (latency p50/p95/p99, similarity scores, error rates, API costs) - FR-010

### Infrastructure Constraints

- [x] **Cost Efficiency**: System operates within free-tier/low-cost limits (<$20/month)
- [x] **Security**: Rate limiting (50 queries/user/hour), API key protection, input sanitization
- [x] **Reliability**: 99% uptime target with graceful degradation when external services unavailable

### Compliance Notes

No constitution violations. Implementation aligns with:
- Intelligent Interactivity principle (RAG chatbot integration)
- RAG Chatbot Technology Stack (OpenAI, FastAPI, Qdrant, Neon Postgres)
- All RAG Chatbot Success Criteria (accuracy, performance, coverage, logging, integration, reliability, cost)

## Project Structure

### Documentation (this feature)

```text
specs/001-rag-chatbot-embeddings/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output - technology choices and best practices
├── data-model.md        # Phase 1 output - entity schemas and relationships
├── quickstart.md        # Phase 1 output - developer setup and usage guide
├── contracts/           # Phase 1 output - API endpoint specifications
│   └── chat-api.yaml    # OpenAPI spec for chat endpoints
└── spec.md              # Feature specification (input)
```

### Source Code (repository root)

```text
rag-backend/
├── src/
│   ├── embeddings/
│   │   ├── __init__.py
│   │   ├── chunker.py          # Sentence-boundary aware text chunking
│   │   ├── generator.py        # OpenAI embedding generation with retry logic
│   │   └── ingestion.py        # Batch processing for book chapters
│   ├── retrieval/
│   │   ├── __init__.py
│   │   ├── qdrant_client.py    # Qdrant vector database operations
│   │   ├── retriever.py        # Similarity search with threshold filtering
│   │   └── context_builder.py  # Retrieved context assembly with citations
│   ├── chat/
│   │   ├── __init__.py
│   │   ├── session.py          # Conversation session management
│   │   ├── rate_limiter.py     # 50 queries/user/hour enforcement
│   │   └── response_generator.py # Answer generation with grounding validation
│   ├── api/
│   │   ├── __init__.py
│   │   ├── main.py             # FastAPI application setup
│   │   ├── routes.py           # Chat and health check endpoints
│   │   └── models.py           # Pydantic request/response models
│   ├── monitoring/
│   │   ├── __init__.py
│   │   ├── metrics.py          # Latency, similarity, error tracking
│   │   └── logger.py           # Structured logging with metadata
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py         # Environment-based configuration
│   └── cli/
│       ├── __init__.py
│       └── ingest.py           # CLI tool for manual embedding generation
├── tests/
│   ├── unit/
│   │   ├── test_chunker.py
│   │   ├── test_generator.py
│   │   ├── test_retriever.py
│   │   └── test_rate_limiter.py
│   ├── integration/
│   │   ├── test_embedding_pipeline.py
│   │   ├── test_retrieval_accuracy.py
│   │   └── test_chat_api.py
│   └── fixtures/
│       └── sample_chapter.md   # Test data
├── scripts/
│   ├── setup_qdrant.py         # Initialize Qdrant collection
│   ├── setup_postgres.py       # Initialize Neon Postgres tables
│   └── run_ingestion.py        # Batch process all /docs chapters
├── requirements.txt
├── requirements-dev.txt
├── .env.example
├── railway.toml                # Railway deployment config (or fly.toml for Fly.io)
└── README.md

docs/                           # Book content (existing structure)
└── module*/*.md                # Chapter markdown files to be embedded
```

**Structure Decision**: Single backend project structure chosen because:
- RAG system is primarily a backend service (no complex frontend in this feature)
- Clear separation of concerns: embeddings, retrieval, chat, API, monitoring
- CLI tools for administrative tasks (ingestion) alongside API service
- Modular design allows independent testing of each component
- Simple deployment as single Docker container

## Complexity Tracking

No constitution violations requiring justification. System design follows established patterns for RAG implementations with appropriate complexity for the requirements.

---

## Phase 0: Research & Technology Validation

### Research Tasks

1. **Embedding Model Selection**
   - Compare OpenAI text-embedding-ada-002 vs text-embedding-3-small/large
   - Evaluate: cost per 1K tokens, vector dimensions, retrieval quality
   - Decision criteria: balance cost (<$20/month for ~500-1000 chunks) with accuracy

2. **Text Chunking Strategies**
   - Research sentence boundary detection libraries (nltk, spaCy, regex patterns)
   - Evaluate overlap strategies for semantic continuity
   - Validate 500-1000 token range with markdown content (code blocks, lists, headers)

3. **Qdrant Client Best Practices**
   - Collection configuration (vector size, distance metric: cosine vs dot product)
   - Indexing strategies for <200ms search latency
   - Metadata schema design for efficient filtering

4. **Rate Limiting Implementations**
   - Token bucket vs sliding window algorithms
   - Storage options: in-memory (Redis) vs database (Postgres)
   - Decision: Postgres for persistence across restarts

5. **OpenAI API Resilience Patterns**
   - Exponential backoff implementation (tenacity library vs custom)
   - Error classification: retryable (rate limit, timeout) vs non-retryable (auth error)
   - Circuit breaker patterns for cascading failures

**Output**: research.md documenting technology choices with rationale

---

## Phase 1: Data Model & API Design

### Data Model Entities

**File**: `data-model.md`

#### 1. BookChapter (File System)
```python
# Represents markdown files in /docs
- file_path: str (absolute path)
- chapter_number: int
- title: str (extracted from markdown # heading)
- module: str (e.g., "module1-ros2")
- content: str (full markdown text)
- last_modified: datetime
- word_count: int
- embedding_status: Enum[pending, processing, completed, failed]
```

#### 2. TextChunk (Qdrant + Postgres)
```python
# Stored in Qdrant as vector + payload, tracked in Postgres
- chunk_id: UUID (primary key)
- chapter_file_path: str (foreign key concept)
- section_title: str (nearest markdown heading)
- text_content: str (500-1000 tokens, sentence-boundary aligned)
- token_count: int
- chunk_index: int (position within chapter, 0-indexed)
- overlap_start_chunk_id: UUID | None (chunk this overlaps with at start)
- overlap_end_chunk_id: UUID | None (chunk this overlaps with at end)
- created_at: datetime
- embedding_model: str (e.g., "text-embedding-3-small")
```

#### 3. Embedding (Qdrant Vector)
```python
# Stored in Qdrant collection "book-embeddings"
- id: UUID (matches chunk_id)
- vector: List[float] (768 or 1536 dimensions depending on model)
- payload: {
    "chunk_id": UUID,
    "chapter_file_path": str,
    "section_title": str,
    "text_snippet": str (first 200 chars for preview),
    "token_count": int,
    "created_at": ISO timestamp
  }
```

#### 4. Query (Postgres Logs)
```python
- query_id: UUID (primary key)
- session_id: UUID (groups related queries)
- user_identifier: str (IP hash or user ID if auth added later)
- query_text: str
- timestamp: datetime
- turn_number: int (within session)
- processing_time_ms: int
```

#### 5. RetrievedContext (Postgres Logs)
```python
- retrieval_id: UUID (primary key)
- query_id: UUID (foreign key)
- chunk_id: UUID (chunk that was retrieved)
- similarity_score: float (0.0-1.0)
- rank: int (1-5 for top-5 results)
- was_used_in_response: bool
```

#### 6. ConversationSession (Postgres)
```python
- session_id: UUID (primary key)
- user_identifier: str
- created_at: datetime
- last_activity_at: datetime
- query_count: int
- is_active: bool
- conversation_history: JSONB (last 5-10 turns: [{role, content, timestamp}])
```

#### 7. Response (Postgres Logs)
```python
- response_id: UUID (primary key)
- query_id: UUID (foreign key)
- response_text: str
- source_citations: JSONB (list of {chapter, section, chunk_id})
- grounding_status: Enum[grounded, insufficient_context, error]
- generation_time_ms: int
- openai_tokens_used: int (for cost tracking)
```

#### 8. RateLimitTracker (Postgres)
```python
- user_identifier: str (primary key, composite with window_start)
- window_start: datetime (hourly window)
- query_count: int
- last_query_at: datetime
- is_blocked: bool
```

#### 9. Metrics (Postgres Time-Series)
```python
- metric_id: UUID (primary key)
- timestamp: datetime
- metric_type: Enum[query_latency, retrieval_quality, error_rate, api_cost]
- value: float
- metadata: JSONB (e.g., {percentile: "p95", error_type: "openai_timeout"})
```

### API Contracts

**File**: `contracts/chat-api.yaml` (OpenAPI 3.0 spec)

#### POST /api/v1/chat/query
Request:
```json
{
  "session_id": "UUID | null",  // null for new session
  "query": "string (max 1000 tokens)",
  "user_identifier": "string (optional, for rate limiting)"
}
```

Response (200 OK):
```json
{
  "session_id": "UUID",
  "query_id": "UUID",
  "response": "string",
  "citations": [
    {
      "chapter": "module1-ros2/chapter1-introduction-to-ros2.md",
      "section": "What is ROS 2?",
      "chunk_id": "UUID"
    }
  ],
  "processing_time_ms": 1234,
  "grounding_status": "grounded | insufficient_context"
}
```

Response (429 Too Many Requests):
```json
{
  "error": "rate_limit_exceeded",
  "message": "You've reached the query limit of 50 questions per hour. Please try again later.",
  "retry_after_seconds": 1800
}
```

Response (503 Service Unavailable):
```json
{
  "error": "external_service_unavailable",
  "message": "I'm experiencing technical difficulties right now. Please try again in a moment.",
  "service": "qdrant | openai | postgres"
}
```

#### GET /api/v1/health
Response (200 OK):
```json
{
  "status": "healthy",
  "services": {
    "qdrant": {"status": "up", "latency_ms": 45},
    "postgres": {"status": "up", "latency_ms": 12},
    "openai": {"status": "up", "last_check": "2025-12-06T10:30:00Z"}
  },
  "metrics": {
    "avg_query_latency_p95_ms": 1456,
    "queries_last_hour": 234,
    "error_rate_percent": 0.5
  }
}
```

#### GET /api/v1/metrics (Admin endpoint)
Response (200 OK):
```json
{
  "time_range": "last_24h",
  "query_latency": {
    "p50": 890,
    "p95": 1567,
    "p99": 2103
  },
  "retrieval_quality": {
    "avg_similarity_score": 0.78,
    "queries_with_results_percent": 92
  },
  "error_rates": {
    "total_errors": 12,
    "openai_api_errors": 5,
    "qdrant_errors": 3,
    "rate_limit_hits": 4
  },
  "api_costs": {
    "embedding_generation_usd": 2.34,
    "query_processing_usd": 5.67,
    "total_month_to_date_usd": 14.23
  }
}
```

### Quickstart Guide

**File**: `quickstart.md`

Content outline:
1. Prerequisites (Python 3.11+, Docker, OpenAI API key, Qdrant Cloud account, Neon Postgres account)
2. Environment setup (.env configuration with API keys and endpoints)
3. Qdrant collection initialization (`python scripts/setup_qdrant.py`)
4. Postgres schema creation (`python scripts/setup_postgres.py`)
5. Initial embedding generation (`python scripts/run_ingestion.py --docs-dir /docs`)
6. Running API server (`uvicorn src.api.main:app --reload`)
7. Testing query endpoint (curl examples)
8. Monitoring metrics (health endpoint, Postgres queries)
9. Troubleshooting common issues (API rate limits, vector search errors)

---

## Phase 1 Completion Checklist

- [ ] research.md created with all technology decisions documented
- [ ] data-model.md created with 9 entity schemas defined
- [ ] contracts/chat-api.yaml created with OpenAPI specification
- [ ] quickstart.md created with developer onboarding guide
- [ ] Constitution Check re-evaluated (no violations introduced)
- [ ] All "NEEDS CLARIFICATION" items from Technical Context resolved

**Next Command**: `/sp.tasks` to generate detailed implementation tasks

---

## Architecture Decisions Summary

### Why Python?
- Dominant ecosystem for ML/AI (OpenAI SDK, embedding models)
- Excellent async support (FastAPI, async Qdrant client)
- Rich text processing libraries (tiktoken, sentence boundary detection)
- Team familiarity and rapid development

### Why FastAPI?
- Native async/await for concurrent request handling
- Automatic OpenAPI documentation generation
- Pydantic integration for request validation
- High performance (<10ms overhead per request)

### Why Qdrant Cloud Free Tier?
- Managed service eliminates infrastructure overhead
- Free tier sufficient for 500-1000 vectors
- Sub-200ms search latency
- Built-in filtering and metadata support

### Why Neon Serverless Postgres?
- Free tier covers low-volume logging/metrics
- Serverless autoscaling (pay only for usage)
- Full Postgres compatibility (JSONB, time-series queries)
- Better for relational data (sessions, rate limits) than vector store

### Why OpenAI Embeddings (not open-source)?
- Superior retrieval quality (proven in RAG benchmarks)
- text-embedding-3-small: best cost/performance ratio ($0.02 per 1M tokens)
- Official Python SDK with built-in retry logic
- Consistent with OpenAI Agents SDK for future integration

### Why Sentence-Boundary Chunking?
- Prevents mid-sentence splits that confuse embedding models
- Improves human readability of retrieved chunks
- Minimal overhead (±50 tokens gives sufficient flexibility)
- Standard practice in production RAG systems

### Why 50 Queries/User/Hour?
- Conservative limit prevents abuse
- ~1 query per minute allows active learning
- Aligns with <$20/month cost constraint
- Can be relaxed later based on actual usage patterns

---

## Non-Functional Requirements Implementation

### Performance (FR-009: <2s p95 latency)
- Async I/O throughout (FastAPI, async Qdrant client, async OpenAI client)
- Connection pooling for Postgres
- Qdrant index optimization (HNSW with m=16, ef=100)
- Caching session context in memory (avoid Postgres roundtrips)

### Reliability (FR-016: Retry logic)
- Exponential backoff for OpenAI API (tenacity library: wait_exponential, stop_after_attempt=3)
- Circuit breaker for Qdrant (fail fast after 3 consecutive errors)
- Graceful degradation (return cached error message if all retries fail)

### Observability (FR-010: Metrics tracking)
- Structured logging with correlation IDs (query_id traces full request lifecycle)
- Prometheus-compatible metrics export (/metrics endpoint)
- Query latency histograms (p50, p95, p99)
- Error rate counters by type (openai_error, qdrant_error, rate_limit)
- Cost tracking (cumulative API token usage → USD conversion)

### Security
- API key authentication for admin endpoints (/metrics)
- Rate limiting enforced at middleware level (before processing)
- Input sanitization (max query length, SQL injection prevention)
- CORS configuration (restrict to book domain)
- No PII stored (user_identifier is hashed IP)

### Cost Control
- Embedding generation: ~$0.02 per 1M tokens (500-1000 chunks × 750 avg tokens = ~$0.015 one-time)
- Query processing: text-embedding-3-small for query embedding (~$0.0002 per query)
- Rate limiting caps max queries: 50 queries/user/hour × 50 users × 24h × 30 days = 1.8M queries/month → ~$360/month if unconstrained → rate limit brings to <$5/month
- Target: $2 embedding generation + $5-10 query processing = $7-12/month average

---

## Risk Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| OpenAI API cost overrun | High | Rate limiting (50 queries/user/hour), cost monitoring dashboard, kill switch at $50/month |
| Qdrant free tier exceeded | Medium | Monitor vector count, implement archival strategy for old embeddings, upgrade plan if needed ($25/month) |
| Poor retrieval quality (low similarity scores) | High | Tunable threshold (0.70-0.75), A/B testing, human evaluation of top queries, chunk size optimization |
| Latency > 2s | Medium | Async architecture, Qdrant index tuning, caching frequent queries, profiling bottlenecks |
| Hallucinations (responses without grounding) | Critical | Strict similarity threshold enforcement, citation verification, manual review of edge cases |
| Book content updates breaking embeddings | Low | Incremental re-embedding (detect changed files), versioning strategy, blue-green deployment |

---

## Deployment Strategy

1. **Local Development**: Python virtual environment (venv) with uvicorn for FastAPI, connect to Qdrant Cloud and Neon Postgres
2. **Staging**: Railway or Fly.io (free tier for testing, direct Python deployment)
3. **Production**: Same platform as staging, separate Qdrant collection and Neon Postgres database
4. **CI/CD**: GitHub Actions (run tests, deploy Python app on merge to main)

---

## Success Validation

Before marking this feature complete, verify:
- [ ] All 16 functional requirements (FR-001 to FR-016) implemented and tested
- [ ] 8 success criteria (SC-001 to SC-008) measured and passing
- [ ] Zero hallucinations in validation test set (20+ diverse queries)
- [ ] p95 latency <2s (load test with 50 concurrent users)
- [ ] Cost tracking shows <$20/month projection
- [ ] Rate limiting prevents >50 queries/user/hour
- [ ] All edge cases handled with appropriate error messages
- [ ] Documentation complete (README, API docs, deployment guide)
