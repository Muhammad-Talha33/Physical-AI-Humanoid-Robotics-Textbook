# RAG Chatbot - Developer Quickstart Guide

Complete guide to set up, run, and deploy the RAG chatbot backend for Physical AI & Humanoid Robotics book content.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Environment Setup](#environment-setup)
- [Database Initialization](#database-initialization)
- [Content Ingestion](#content-ingestion)
- [Running the API Server](#running-the-api-server)
- [Testing](#testing)
- [Monitoring](#monitoring)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software

- **Python 3.11+** (required for latest async features)
- **pip** (Python package manager)
- **Git** (for cloning repository)

### Required Cloud Services

1. **OpenAI Account**
   - Sign up at https://platform.openai.com
   - Create an API key
   - Ensure billing is enabled (embeddings + chat models)

2. **Qdrant Cloud Account**
   - Sign up at https://cloud.qdrant.io
   - Create a free cluster
   - Note your cluster URL and API key

3. **Neon Postgres Account**
   - Sign up at https://neon.tech
   - Create a new project/database
   - Note connection details (host, database, user, password)

---

## Environment Setup

### 1. Clone the Repository

```bash
cd rag-backend
```

### 2. Create Virtual Environment

```bash
python -m venv venv
```

**Activate the virtual environment:**

- Windows:
  ```bash
  venv\Scripts\activate
  ```

- macOS/Linux:
  ```bash
  source venv/bin/activate
  ```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` with your actual credentials:

```env
# OpenAI Configuration
OPENAI_API_KEY=sk-proj-...your-key-here...
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
OPENAI_CHAT_MODEL=gpt-3.5-turbo

# Qdrant Configuration
QDRANT_URL=https://your-cluster.europe-west3-0.gcp.cloud.qdrant.io
QDRANT_API_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6...your-key-here...
QDRANT_COLLECTION_NAME=book-embeddings

# Neon Postgres Configuration
POSTGRES_HOST=ep-your-project.us-east-1.aws.neon.tech
POSTGRES_PORT=5432
POSTGRES_DB=neondb
POSTGRES_USER=neondb_owner
POSTGRES_PASSWORD=your_password_here
POSTGRES_SSLMODE=require

# Application Configuration
ENVIRONMENT=development
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=INFO

# RAG Configuration (Optimized values)
SIMILARITY_THRESHOLD=0.60
TOP_K_RESULTS=5
CHUNK_SIZE_MIN=300
CHUNK_SIZE_MAX=600
CHUNK_OVERLAP_PERCENT=25

# Security (Production only)
ADMIN_API_KEY=  # Leave empty for development
```

**Important Notes:**
- **Development**: Leave `ADMIN_API_KEY` empty to allow unauthenticated access to `/metrics`
- **Production**: Generate a secure key:
  ```bash
  python -c "import secrets; print(secrets.token_urlsafe(32))"
  ```

---

## Database Initialization

### 1. Initialize Qdrant Vector Database

Create the `book-embeddings` collection:

```bash
python scripts/setup_qdrant.py
```

**Expected output:**
```
Collection 'book-embeddings' initialized successfully
Vector size: 1536 dimensions
Distance metric: Cosine
```

**Troubleshooting:**
- If collection already exists, script will report it
- To recreate: delete collection in Qdrant dashboard first

### 2. Initialize Postgres Schema

Create all required tables:

```bash
python scripts/setup_postgres.py
```

**Expected output:**
```
Creating tables...
Tables created successfully:
  - queries
  - retrieved_contexts
  - conversation_sessions
  - responses
  - rate_limit_tracker
  - metrics
```

**Tables created:**
- `queries`: All user queries with timestamps
- `retrieved_contexts`: Chunks retrieved for each query
- `conversation_sessions`: Multi-turn conversation state
- `responses`: Generated responses with grounding status
- `rate_limit_tracker`: Rate limiting enforcement
- `metrics`: Performance and cost tracking

---

## Content Ingestion

### 1. Verify Book Content

Ensure `/docs` directory contains your markdown chapter files:

```bash
ls ../docs/
```

Expected structure:
```
docs/
├── module1_ros2/
│   ├── chapter1.md
│   ├── chapter2.md
│   └── ...
├── module2_digital_twin/
│   ├── chapter6.md
│   └── ...
├── module3_ai_brain/
│   └── ...
└── module4_vla/
    └── ...
```

### 2. Run Ingestion Pipeline

Process all book chapters and generate embeddings:

```bash
python scripts/run_ingestion.py
```

**Expected output:**
```
Processing chapter: /docs/module1_ros2/chapter1.md
  ✓ Chunked into 3 segments
  ✓ Generated 3 embeddings
  ✓ Stored in Qdrant

Processing chapter: /docs/module1_ros2/chapter2.md
  ✓ Chunked into 2 segments
  ✓ Generated 2 embeddings
  ✓ Stored in Qdrant

...

Ingestion complete: 52 embeddings created from 21 chapters
```

**Performance:**
- ~10-30 seconds per chapter (depending on OpenAI API rate limits)
- Total time for 21 chapters: ~5-10 minutes
- Cost: ~$0.10-0.20 for full book ingestion

---

## Running the API Server

### 1. Start the Server

```bash
python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000
```

**Expected output:**
```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 2. Verify Server Health

Open another terminal and test the health endpoint:

```bash
curl http://localhost:8000/api/v1/health
```

**Expected response:**
```json
{
  "status": "healthy",
  "services": {
    "postgres": "healthy",
    "qdrant": "healthy",
    "openai": "healthy"
  },
  "metrics": {
    "total_queries": 0,
    "total_embeddings": 52
  }
}
```

### 3. Test Query Endpoint

```bash
curl -X POST http://localhost:8000/api/v1/chat/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is ROS 2?"}'
```

**Expected response:**
```json
{
  "response": "ROS 2 (Robot Operating System 2) is...",
  "grounding_status": "grounded",
  "citations": [
    {
      "chapter_name": "Introduction to ROS 2",
      "section_title": "What is ROS 2?",
      "text_snippet": "ROS 2 is a middleware framework..."
    }
  ],
  "session_id": "uuid-here"
}
```

---

## Testing

### 1. Latency Validation

Test query response times:

```bash
cd rag-backend
python -c "
import time
import requests

query = 'What is ROS 2?'
start = time.time()
response = requests.post(
    'http://localhost:8000/api/v1/chat/query',
    json={'query': query}
)
elapsed_ms = int((time.time() - start) * 1000)

print(f'Latency: {elapsed_ms}ms')
print(f'Status: {response.json().get(\"grounding_status\")}')"
```

**Expected:**
- First query (cold start): 5-25 seconds
- Subsequent queries: 2-10 seconds
- p95 target: <2000ms (after warmup)

### 2. Hallucination Validation

Run comprehensive hallucination tests:

```bash
python test_hallucinations.py
```

**Expected output:**
```
T069: HALLUCINATION VALIDATION - 21 DIVERSE QUERIES
======================================================================

1. [GROUNDED] What is ROS 2?
   Citations: 3 source(s)
   Answer: ROS 2 is a middleware framework for robotics...

...

21. [INSUFFICIENT] What is the capital of France?
   Answer: I cannot find information about this in the book content

======================================================================
VALIDATION RESULTS
======================================================================
Total queries: 21
Grounded responses: 11
Insufficient context: 10
Hallucinations detected: 0

PASS: Zero hallucinations detected
```

---

## Monitoring

### 1. View Metrics Endpoint

**Development (no auth):**
```bash
curl http://localhost:8000/api/v1/metrics
```

**Production (with API key):**
```bash
curl http://localhost:8000/api/v1/metrics \
  -H "X-API-Key: your_admin_api_key_here"
```

**Response:**
```json
{
  "time_range": "last_24h",
  "query_latency": {
    "p50": 2500,
    "p95": 8500,
    "p99": 15000
  },
  "retrieval_quality": {
    "avg_similarity_score": 0.75
  },
  "error_rates": {
    "openai_error": 0,
    "qdrant_error": 0,
    "rate_limit": 2
  },
  "api_costs": {
    "embedding_generation_usd": 0.15,
    "query_processing_usd": 0.32,
    "total_month_to_date_usd": 0.47
  }
}
```

### 2. View Server Logs

Logs are written to `server.log` in JSON format:

```bash
tail -f server.log | python -m json.tool
```

**Log entries include:**
- `correlation_id`: Trace requests end-to-end
- `query_preview`: Snippet of user query
- `grounding_status`: grounded | insufficient_context
- `processing_time_ms`: Latency metrics

---

## Deployment

### Option 1: Railway

1. Install Railway CLI:
   ```bash
   npm install -g @railway/cli
   ```

2. Login and initialize:
   ```bash
   railway login
   railway init
   ```

3. Set environment variables:
   ```bash
   railway variables set OPENAI_API_KEY=sk-proj-...
   railway variables set QDRANT_URL=https://...
   railway variables set POSTGRES_HOST=ep-...
   # Set all other variables from .env
   ```

4. Deploy:
   ```bash
   railway up
   ```

### Option 2: Fly.io

1. Install Fly CLI:
   ```bash
   curl -L https://fly.io/install.sh | sh
   ```

2. Launch app:
   ```bash
   fly launch
   ```

3. Set secrets:
   ```bash
   fly secrets set OPENAI_API_KEY=sk-proj-...
   fly secrets set QDRANT_URL=https://...
   # Set all other variables
   ```

4. Deploy:
   ```bash
   fly deploy
   ```

### Production Checklist

- [ ] Set `ENVIRONMENT=production` in environment variables
- [ ] Generate and set secure `ADMIN_API_KEY`
- [ ] Configure CORS allowed origins in `src/api/main.py`
- [ ] Set up monitoring/alerting for error rates
- [ ] Configure monthly cost limits
- [ ] Enable HTTPS (handled by Railway/Fly.io)

---

## Troubleshooting

### Issue: "Insufficient context" for all queries

**Symptoms:**
- All queries return `grounding_status: "insufficient_context"`
- No citations returned

**Causes & Solutions:**

1. **No embeddings in Qdrant**
   ```bash
   python scripts/setup_qdrant.py  # Reinitialize
   python scripts/run_ingestion.py  # Re-ingest content
   ```

2. **Similarity threshold too high**
   - Check `.env`: `SIMILARITY_THRESHOLD=0.60` (not 0.72)
   - Restart server to pick up changes

3. **Wrong collection name**
   - Verify `.env`: `QDRANT_COLLECTION_NAME=book-embeddings`

### Issue: High latency (>10s per query)

**Causes & Solutions:**

1. **Cold start** (first query)
   - Expected: 5-25s for first query
   - Subsequent queries should be faster

2. **OpenAI API rate limits**
   - Check your OpenAI tier (free vs paid)
   - Upgrade to paid tier for better performance

3. **Postgres connection pooling**
   - Check `db_pool` configuration in `src/api/main.py`
   - Increase pool size if needed

### Issue: Authentication errors (401)

**Symptoms:**
- `/api/v1/metrics` returns 401 Unauthorized

**Solutions:**

1. **Development mode:**
   - Ensure `.env` has `ENVIRONMENT=development`
   - Leave `ADMIN_API_KEY` empty or unset

2. **Production mode:**
   - Generate API key: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
   - Set in `.env`: `ADMIN_API_KEY=generated_key_here`
   - Include header in requests: `-H "X-API-Key: your_key"`

### Issue: Postgres connection failures

**Symptoms:**
- Error: `could not connect to server`
- Health endpoint shows postgres: "unhealthy"

**Solutions:**

1. **Verify connection string**
   ```bash
   python -c "from src.config.settings import settings; print(settings.postgres_dsn)"
   ```

2. **Check Neon project status**
   - Login to https://console.neon.tech
   - Verify project is active (not suspended)

3. **Test connection directly**
   ```bash
   pip install psycopg2-binary
   python -c "
   import psycopg2
   from src.config.settings import settings
   conn = psycopg2.connect(settings.postgres_dsn)
   print('Connected successfully')
   conn.close()"
   ```

### Issue: Rate limit exceeded (429)

**Symptoms:**
- Error: `Rate limit exceeded`
- Response: `retry_after_seconds: 1800`

**Solutions:**

1. **Wait for cooldown period** (~1 hour)

2. **Increase rate limit** (`.env`):
   ```env
   RATE_LIMIT_QUERIES_PER_HOUR=100
   ```

3. **Clear rate limit** (Postgres):
   ```sql
   DELETE FROM rate_limit_tracker WHERE user_identifier = 'anonymous';
   ```

### Getting Help

- Check logs: `tail -f server.log`
- Review configuration: `python -c "from src.config.settings import settings; print(settings)"`
- Test individual components in isolation
- Check cloud service dashboards (OpenAI, Qdrant, Neon)

---

## Next Steps

Once your RAG chatbot backend is running:

1. **Integrate with Frontend**
   - Build a web UI (React, Vue, etc.)
   - Call `/api/v1/chat/query` endpoint
   - Display responses with citations

2. **Optimize Performance**
   - Add caching layer (Redis)
   - Implement connection pooling
   - Pre-warm server on deployment

3. **Enhance Features**
   - Add user authentication
   - Implement conversation history UI
   - Add feedback/rating system

4. **Scale for Production**
   - Set up load balancing
   - Configure auto-scaling
   - Add CDN for static assets
