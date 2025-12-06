# Deploy to Railway - Web Interface (5 Minutes)

**Easiest method - No CLI needed!**

## Your Admin API Key
```
EEoJM4T4MIHGqnHPB_6CAao7J1h2LXqmhnpb7qRBf_Q
```

---

## Step 1: Push Code to GitHub (2 minutes)

Open a terminal and run:

```bash
cd "C:\Users\Samreen Computer\Desktop\New Folder (5)"

# Add rag-backend to staging
git add rag-backend/

# Commit the backend code
git commit -m "Add RAG chatbot backend - production ready

- 68/69 tasks complete
- Zero hallucinations validated
- Admin API authentication enabled
- 52 embeddings from 21 chapters
- Production configuration ready"

# Push to GitHub
git push origin 001-rag-chatbot-embeddings
```

**If you don't have a GitHub repo yet:**
1. Go to https://github.com/new
2. Create new repository (name: `physical-ai-rag-chatbot`)
3. Follow GitHub's instructions to push

---

## Step 2: Deploy on Railway (3 minutes)

### 2.1 Sign Up / Login
1. Go to https://railway.app
2. Click **"Start a New Project"**
3. Sign in with GitHub

### 2.2 Create New Project
1. Click **"Deploy from GitHub repo"**
2. Select your repository
3. Railway will detect it's a Python project automatically

### 2.3 Configure Root Directory
Since your backend is in `rag-backend/` subdirectory:

1. Click on your service
2. Go to **Settings**
3. Find **"Root Directory"**
4. Set to: `rag-backend`
5. Click **Save**

### 2.4 Set Environment Variables

Click **"Variables"** tab, then add all these:

**OpenAI:**
```
OPENAI_API_KEY=your_openai_api_key_from_env_file
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
OPENAI_CHAT_MODEL=gpt-3.5-turbo
```

**Qdrant:**
```
QDRANT_URL=your_qdrant_url_from_env_file
QDRANT_API_KEY=your_qdrant_api_key_from_env_file
QDRANT_COLLECTION_NAME=book-embeddings
```

**Postgres:**
```
POSTGRES_HOST=your_postgres_host_from_env_file
POSTGRES_PORT=5432
POSTGRES_DB=neondb
POSTGRES_USER=neondb_owner
POSTGRES_PASSWORD=your_postgres_password_from_env_file
POSTGRES_SSLMODE=require
```

**NOTE:** Copy the actual values from your `.env` file when setting these in Railway.

**Application:**
```
ENVIRONMENT=production
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=INFO
```

**RAG Config:**
```
SIMILARITY_THRESHOLD=0.60
TOP_K_RESULTS=5
CHUNK_SIZE_MIN=300
CHUNK_SIZE_MAX=600
CHUNK_OVERLAP_PERCENT=25
MAX_CONVERSATION_TURNS=10
MAX_QUERY_LENGTH_TOKENS=1000
RATE_LIMIT_QUERIES_PER_HOUR=50
```

**Other:**
```
MAX_RETRIES=3
RETRY_BACKOFF_SECONDS=1
MONTHLY_COST_LIMIT_USD=20.0
```

**Security (IMPORTANT!):**
```
ADMIN_API_KEY=EEoJM4T4MIHGqnHPB_6CAao7J1h2LXqmhnpb7qRBf_Q
```

### 2.5 Deploy

1. Click **"Deploy"** button
2. Wait 2-3 minutes for build
3. Railway will show deployment status

---

## Step 3: Get Your URL

1. Go to **"Settings"** tab
2. Scroll to **"Domains"**
3. Click **"Generate Domain"**
4. Your URL will look like: `https://rag-chatbot-backend-production.up.railway.app`

**Copy this URL - you'll need it for testing!**

---

## Step 4: Test Your Deployment

### Test Health Endpoint

Replace `YOUR-URL` with your Railway domain:

```bash
curl https://YOUR-URL.railway.app/api/v1/health
```

**Expected:**
```json
{
  "status": "healthy",
  "services": {
    "postgres": "healthy",
    "qdrant": "healthy",
    "openai": "healthy"
  }
}
```

### Test Query Endpoint

```bash
curl -X POST https://YOUR-URL.railway.app/api/v1/chat/query \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"What is ROS 2?\"}"
```

**Expected:**
```json
{
  "response": "ROS 2 is...",
  "grounding_status": "grounded",
  "citations": [...]
}
```

### Test Protected Metrics (with your admin key)

```bash
curl https://YOUR-URL.railway.app/api/v1/metrics \
  -H "X-API-Key: EEoJM4T4MIHGqnHPB_6CAao7J1h2LXqmhnpb7qRBf_Q"
```

---

## Troubleshooting

### Deployment Failing?

**Check build logs:**
1. Click on your service
2. Go to **"Deployments"** tab
3. Click latest deployment
4. View logs

**Common issues:**
- Wrong root directory (should be `rag-backend`)
- Missing environment variables
- Python version (Railway auto-detects from `runtime.txt` or uses latest)

### App Crashing After Deploy?

**Check runtime logs:**
1. Go to **"Logs"** tab in Railway dashboard
2. Look for errors

**Common fixes:**
- Database connection errors → Check Postgres credentials
- Qdrant errors → Check Qdrant URL and API key
- Port errors → Railway automatically sets $PORT, should work with railway.toml

### Need Help?

View logs in real-time:
1. Railway Dashboard → Your Service → **Logs** tab
2. Filter by error level

---

## What's Next?

### Your Deployed API:
- **Public URL**: `https://your-app.railway.app`
- **Health**: `/api/v1/health`
- **Chat**: `/api/v1/chat/query` (POST)
- **Metrics**: `/api/v1/metrics` (requires admin API key)

### Monitor Usage:
1. Railway Dashboard → **Usage** tab
2. Track costs and resource usage

### Auto-Deploy Updates:
Railway auto-deploys when you push to GitHub!

```bash
# Make changes to your code
git add .
git commit -m "Update feature X"
git push

# Railway automatically deploys!
```

---

## Cost Estimate

**Railway:**
- Free tier: $5/month credit
- After free tier: ~$3-5/month for this app

**External Services:**
- OpenAI: ~$5-10/month (based on query volume)
- Qdrant: Free (under 1GB)
- Neon Postgres: Free (under 0.5GB)

**Total: $8-15/month**

---

## Security Reminders

- Never commit `.env` file (it's in `.gitignore`)
- Admin API key is set via Railway environment variables only
- HTTPS is automatic on Railway
- Rate limiting is enabled (50 queries/hour/user)

---

## Your Deployment is Complete!

Save your Railway URL and admin API key securely. You can now integrate this with your frontend application!

**Support:**
- Railway docs: https://docs.railway.app
- Railway Discord: https://discord.gg/railway
