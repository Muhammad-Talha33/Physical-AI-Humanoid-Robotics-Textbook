# RAG Chatbot Backend

Retrieval-Augmented Generation (RAG) chatbot for the Physical AI & Humanoid Robotics textbook. This backend service enables readers to ask questions about book content and receive accurate, grounded answers with chapter citations.

## Features

- **Content Embedding Generation**: Automatically processes book chapters into searchable vector embeddings
- **Contextual Question Retrieval**: Answers user questions with content strictly grounded in the book
- **Multi-Turn Conversations**: Maintains conversation context for natural follow-up questions
- **Citation Tracking**: Provides chapter and section references for all responses
- **Cost Control**: Built-in rate limiting and cost monitoring (<$20/month target)
- **Production Ready**: Comprehensive logging, metrics, and error handling

## Architecture

### Tech Stack

- **Python 3.11+**: Core language
- **FastAPI**: REST API framework
- **OpenAI API**: Embeddings (text-embedding-3-small) and chat completions
- **Qdrant Cloud**: Vector database for embedding storage
- **Neon Postgres**: Relational database for query logs and metrics
- **Railway/Fly.io**: Cloud deployment platform

### Project Structure

```
rag-backend/
├── src/
│   ├── embeddings/       # Text chunking and embedding generation
│   ├── retrieval/        # Vector search and context assembly
│   ├── chat/             # Response generation and session management
│   ├── api/              # FastAPI routes and models
│   ├── monitoring/       # Logging and metrics tracking
│   └── config/           # Configuration management
├── scripts/              # Setup and ingestion scripts
├── tests/                # Unit and integration tests
└── requirements.txt      # Python dependencies
```

## Prerequisites

1. **Python 3.11+**
2. **OpenAI API Key** ([Get one here](https://platform.openai.com/api-keys))
3. **Qdrant Cloud Account** ([Free tier](https://cloud.qdrant.io))
4. **Neon Postgres Account** ([Free tier](https://neon.tech))

## Setup

### 1. Install Dependencies

```bash
cd rag-backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt  # For development
```

### 2. Configure Environment

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Edit `.env`:

```env
OPENAI_API_KEY=your_openai_api_key
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=your_qdrant_api_key
POSTGRES_HOST=your-project.neon.tech
POSTGRES_DB=rag_chatbot
POSTGRES_USER=your_user
POSTGRES_PASSWORD=your_password
```

### 3. Initialize Qdrant Collection

```bash
python scripts/setup_qdrant.py
```

### 4. Initialize Postgres Schema

```bash
python scripts/setup_postgres.py
```

### 5. Ingest Book Content

```bash
# Ingest all chapters from docs directory
python scripts/run_ingestion.py --docs-dir ../docs

# Ingest a single file
python scripts/run_ingestion.py --single-file ../docs/module1/chapter1.md

# Force re-ingestion (deletes existing embeddings)
python scripts/run_ingestion.py --docs-dir ../docs --force
```

## Running the API

### Development Mode

```bash
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode

```bash
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Endpoints

### POST /api/v1/chat/query

Submit a question and receive a grounded answer.

**Request:**
```json
{
  "session_id": null,
  "query": "What is ROS 2?",
  "user_identifier": "user@example.com"
}
```

**Response:**
```json
{
  "session_id": "123e4567-e89b-12d3-a456-426614174000",
  "query_id": "987fcdeb-51a2-43f7-b123-9876543210ab",
  "response": "ROS 2 is the next generation Robot Operating System...",
  "citations": [
    {
      "chapter": "module1/chapter1-intro-to-ros2.md",
      "section": "What is ROS 2?",
      "chunk_id": "abc123..."
    }
  ],
  "processing_time_ms": 1456,
  "grounding_status": "grounded"
}
```

### GET /api/v1/health

Check service health and dependencies.

### GET /api/v1/metrics

View metrics dashboard (admin endpoint).

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/unit/test_chunker.py
```

### Code Quality

```bash
# Format code
black src/

# Lint
flake8 src/

# Type checking
mypy src/
```

## Monitoring

### Logs

Structured JSON logs with correlation IDs for request tracing.

### Metrics

- Query latency (p50, p95, p99)
- Retrieval quality (avg similarity score)
- Error rates by type
- API costs (embeddings + queries)

### Cost Control

- Rate limiting: 50 queries/user/hour
- Monthly cost target: <$20
- Cost alerts at $50/month

## Deployment

### Railway

```bash
# Install Railway CLI
npm install -g @railway/cli

# Deploy
railway up
```

### Fly.io

```bash
# Install Fly CLI
curl -L https://fly.io/install.sh | sh

# Deploy
fly deploy
```

## Troubleshooting

### Qdrant Connection Errors

- Verify `QDRANT_URL` and `QDRANT_API_KEY` in `.env`
- Run `python scripts/setup_qdrant.py` to recreate collection

### OpenAI Rate Limits

- Check your API quota at [OpenAI dashboard](https://platform.openai.com/usage)
- Reduce `max_concurrent` in ingestion script

### Postgres Connection Issues

- Verify Neon credentials in `.env`
- Ensure `sslmode=require` for Neon connections

### No Results from Queries

- Check `SIMILARITY_THRESHOLD` setting (default: 0.72)
- Lower threshold for more results: `SIMILARITY_THRESHOLD=0.65`
- Verify embeddings were generated: Check Qdrant collection

## License

MIT License - See LICENSE file for details

## Support

For issues or questions, please open an issue on GitHub.
