# Railway Deployment Guide

Step-by-step guide to deploy your RAG chatbot backend to Railway.

## Prerequisites

- Railway account (sign up at https://railway.app)
- Your admin API key: `EEoJM4T4MIHGqnHPB_6CAao7J1h2LXqmhnpb7qRBf_Q`
- All environment variables from `.env` file

---

## Step 1: Install Railway CLI

**Windows (PowerShell):**
```powershell
iwr https://railway.app/install.ps1 | iex
```

**macOS/Linux:**
```bash
npm install -g @railway/cli
```

**Verify installation:**
```bash
railway --version
```

---

## Step 2: Login to Railway

```bash
railway login
```

This will open your browser to authenticate.

---

## Step 3: Initialize Railway Project

Navigate to your rag-backend directory:

```bash
cd "C:\Users\Samreen Computer\Desktop\New Folder (5)\rag-backend"
```

Initialize the project:

```bash
railway init
```

When prompted:
- **Project name**: `rag-chatbot-backend` (or your preferred name)
- **Create new project**: Yes

---

## Step 4: Set Environment Variables

Copy all variables from your `.env` file to Railway:

```bash
# OpenAI Configuration (use your actual values from .env file)
railway variables set OPENAI_API_KEY="your_openai_api_key_here"
railway variables set OPENAI_EMBEDDING_MODEL="text-embedding-3-small"
railway variables set OPENAI_CHAT_MODEL="gpt-3.5-turbo"

# Qdrant Configuration (use your actual values from .env file)
railway variables set QDRANT_URL="your_qdrant_cluster_url_here"
railway variables set QDRANT_API_KEY="your_qdrant_api_key_here"
railway variables set QDRANT_COLLECTION_NAME="book-embeddings"

# Neon Postgres Configuration (use your actual values from .env file)
railway variables set POSTGRES_HOST="your_postgres_host_here"
railway variables set POSTGRES_PORT="5432"
railway variables set POSTGRES_DB="neondb"
railway variables set POSTGRES_USER="neondb_owner"
railway variables set POSTGRES_PASSWORD="your_postgres_password_here"
railway variables set POSTGRES_SSLMODE="require"

# Application Configuration
railway variables set ENVIRONMENT="production"
railway variables set API_HOST="0.0.0.0"
railway variables set API_PORT="8000"
railway variables set LOG_LEVEL="INFO"

# Rate Limiting
railway variables set RATE_LIMIT_QUERIES_PER_HOUR="50"

# RAG Configuration (Optimized)
railway variables set SIMILARITY_THRESHOLD="0.60"
railway variables set TOP_K_RESULTS="5"
railway variables set CHUNK_SIZE_MIN="300"
railway variables set CHUNK_SIZE_MAX="600"
railway variables set CHUNK_OVERLAP_PERCENT="25"
railway variables set MAX_CONVERSATION_TURNS="10"
railway variables set MAX_QUERY_LENGTH_TOKENS="1000"

# Retry Configuration
railway variables set MAX_RETRIES="3"
railway variables set RETRY_BACKOFF_SECONDS="1"

# Cost Monitoring
railway variables set MONTHLY_COST_LIMIT_USD="20.0"

# Security - YOUR ADMIN API KEY
railway variables set ADMIN_API_KEY="EEoJM4T4MIHGqnHPB_6CAao7J1h2LXqmhnpb7qRBf_Q"
```

**Verify variables are set:**
```bash
railway variables
```

---

## Step 5: Create railway.toml Configuration

The `railway.toml` file already exists in your project with the correct configuration:

```toml
[build]
builder = "nixpacks"

[deploy]
startCommand = "uvicorn src.api.main:app --host 0.0.0.0 --port $PORT"
healthcheckPath = "/api/v1/health"
healthcheckTimeout = 100
restartPolicyType = "on_failure"
restartPolicyMaxRetries = 3
```

**Note:** Railway automatically provides a `$PORT` environment variable.

---

## Step 6: Deploy to Railway

Deploy your application:

```bash
railway up
```

**Expected output:**
```
Building...
Deploying...
Deployment successful!
URL: https://your-app.railway.app
```

**Deployment process:**
1. Railway builds your app using Nixpacks
2. Installs Python dependencies from `requirements.txt`
3. Starts the server with `uvicorn`
4. Health check at `/api/v1/health`
5. Assigns a public URL

---

## Step 7: Verify Deployment

### Check Deployment Status

```bash
railway status
```

### View Logs

```bash
railway logs
```

Look for:
```
INFO:     Started server process [1]
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Get Your Public URL

```bash
railway domain
```

Or view in Railway dashboard: https://railway.app/dashboard

---

## Step 8: Test Your Deployed API

### Test Health Endpoint

```bash
curl https://your-app.railway.app/api/v1/health
```

**Expected response:**
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
curl -X POST https://your-app.railway.app/api/v1/chat/query \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"What is ROS 2?\"}"
```

### Test Protected Metrics Endpoint

**Without API key (should fail with 401):**
```bash
curl https://your-app.railway.app/api/v1/metrics
```

**With your admin API key (should succeed):**
```bash
curl https://your-app.railway.app/api/v1/metrics \
  -H "X-API-Key: EEoJM4T4MIHGqnHPB_6CAao7J1h2LXqmhnpb7qRBf_Q"
```

**Expected response:**
```json
{
  "time_range": "last_24h",
  "query_latency": {...},
  "retrieval_quality": {...},
  "api_costs": {...}
}
```

---

## Step 9: Configure Custom Domain (Optional)

### Add Custom Domain

```bash
railway domain add yourdomain.com
```

### Update DNS Records

Add CNAME record in your DNS provider:
```
Type: CNAME
Name: @ (or subdomain)
Value: your-app.railway.app
```

Railway automatically provisions SSL certificates.

---

## Monitoring & Maintenance

### View Metrics Dashboard

Visit Railway dashboard: https://railway.app/dashboard

**Available metrics:**
- CPU usage
- Memory usage
- Network traffic
- Deployment logs
- Build logs

### View Application Logs

```bash
railway logs --follow
```

### Restart Service

```bash
railway restart
```

### Redeploy

```bash
railway up
```

---

## Cost Management

### Railway Pricing

- **Free Tier**: $5 of usage per month
- **Pro Plan**: $20/month + usage

### Monitor Costs

Check in Railway dashboard:
- Go to your project
- Click "Usage" tab
- View current month spending

### Your Expected Costs

**Railway costs:**
- Compute: ~$3-5/month (minimal usage)
- Bandwidth: ~$0.50-1/month

**External service costs:**
- OpenAI API: ~$5-10/month (depending on queries)
- Qdrant Cloud: Free tier (up to 1GB)
- Neon Postgres: Free tier (up to 0.5GB)

**Total estimated: $8-16/month**

---

## Security Checklist

- [X] Environment set to `production`
- [X] Admin API key configured (`EEoJM4T4MIHGqnHPB_6CAao7J1h2LXqmhnpb7qRBf_Q`)
- [X] HTTPS enabled automatically by Railway
- [X] Rate limiting enabled (50 queries/hour/user)
- [X] Cost limit set ($20/month)
- [ ] Configure CORS allowed origins (if needed for frontend)
- [ ] Set up monitoring alerts
- [ ] Review access logs regularly

---

## Troubleshooting

### Deployment Fails

**Check build logs:**
```bash
railway logs --build
```

**Common issues:**
- Missing dependencies in `requirements.txt`
- Python version mismatch (ensure Python 3.11+)
- Invalid environment variables

### Health Check Failing

**Check application logs:**
```bash
railway logs
```

**Common issues:**
- Postgres connection failure (check credentials)
- Qdrant connection failure (check URL and API key)
- OpenAI API key invalid

### High Response Times

**Solutions:**
- Upgrade Railway plan for more resources
- Check OpenAI API tier (upgrade to paid for better performance)
- Review database query performance
- Consider adding Redis caching layer

### Out of Memory

**Railway default: 512MB RAM**

**Increase memory:**
1. Go to Railway dashboard
2. Select your service
3. Settings → Resources
4. Increase memory allocation (costs more)

---

## Next Steps

1. **Integrate Frontend**
   - Your API is now publicly accessible
   - Use the Railway URL in your frontend app
   - Include admin API key for metrics access

2. **Set Up Monitoring**
   - Configure alert webhooks in Railway
   - Set up uptime monitoring (UptimeRobot, Pingdom)
   - Monitor cost usage regularly

3. **Implement CI/CD**
   - Connect GitHub repository
   - Enable auto-deploy on push
   - Set up preview environments

4. **Scale as Needed**
   - Monitor query volume
   - Upgrade Railway plan if needed
   - Consider multi-region deployment

---

## Your Deployment Summary

**Public URL:** (Will be shown after deployment)

**Admin API Key:** `EEoJM4T4MIHGqnHPB_6CAao7J1h2LXqmhnpb7qRBf_Q`

**Endpoints:**
- Health: `https://your-app.railway.app/api/v1/health`
- Query: `https://your-app.railway.app/api/v1/chat/query`
- Metrics (protected): `https://your-app.railway.app/api/v1/metrics`

**Security:**
- HTTPS: Enabled automatically
- Rate Limiting: 50 queries/hour/user
- Admin endpoints: Protected with API key
- Cost limit: $20/month

Your RAG chatbot is ready for public use!
