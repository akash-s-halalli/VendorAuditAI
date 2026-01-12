# VendorAuditAI Deployment Guide

## Live URLs (Share With Customers)

| Service | URL | Status |
|---------|-----|--------|
| **Frontend** | https://vendor-audit-ai.netlify.app | Live |
| **Backend API** | https://vendorauditai-production.up.railway.app | Live |
| **Health Check** | https://vendorauditai-production.up.railway.app/health | Active |

**Quick Customer Demo:** Share https://vendor-audit-ai.netlify.app

---

## Deployment Options

### Option A: Current Split Deployment (Already Live)

**Architecture:**
```
[Browser] --> [Netlify CDN] --> [React Frontend]
                                     |
                                     v (API calls)
                              [Railway Backend]
                                     |
                                     v
                              [PostgreSQL DB]
```

**Pros:** CDN-cached frontend, independent scaling
**Cons:** Two services to manage

### Option B: Unified Container (Single URL)

Deploy frontend + backend as one container using the root Dockerfile.

**To Switch:**
1. In Railway dashboard, change "Root Directory" from `backend` to `/`
2. Redeploy - Railway will use the unified Dockerfile
3. Single URL serves both API and frontend

### Option C: Self-Hosted Docker

```bash
git clone https://github.com/YOUR_USERNAME/VendorAuditAI.git
cd VendorAuditAI
cp .env.example .env
# Edit .env with your API keys
docker-compose up -d
# Access at http://localhost:8000
```

---

## What's Been Done

### 1. Frontend Deployment (Complete)
- Created `frontend/netlify.toml` for SPA routing
- Deployed to Netlify successfully
- Site live at: https://vendor-audit-ai.netlify.app
- Created `frontend/.env.production` with Railway backend URL

### 2. Backend Code (Complete)
- Created `backend/Dockerfile` for Python 3.12
- Created `backend/requirements.txt` with all dependencies
- Created `backend/railway.toml` for Railway configuration
- Added Google Gemini as LLM/embedding provider option
- Fixed syntax errors and refactored LLM services with ABC pattern
- All 70 backend tests passing

### 3. Backend Deployment (Partial)
- Set environment variables on Railway:
  - `JWT_SECRET_KEY` (generated)
  - `CORS_ORIGINS` (includes Netlify domain)
  - `APP_ENV=production`
  - `DEBUG=false`
- **PENDING**: PostgreSQL database needs to be added

---

## Remaining Steps to Complete Backend Deployment

### Step 1: Add PostgreSQL Database on Railway

1. Go to https://railway.app/project/f81b16de-74b5-44dc-97bc-acd5bacef069
2. Click "+ New" > "Database" > "Add PostgreSQL"
3. Railway will automatically add `DATABASE_URL` environment variable

### Step 2: Update Database URL Format

After PostgreSQL is added, update the DATABASE_URL to use asyncpg:

```bash
# In Railway dashboard, set:
DATABASE_URL=postgresql+asyncpg://... (replace postgresql:// with postgresql+asyncpg://)
```

Or use Railway CLI:
```bash
RAILWAY_TOKEN="6df8f143-0958-417b-8f05-737939af2775" railway variables --service VendorAuditAI --set "DATABASE_URL=postgresql+asyncpg://user:pass@host:port/db"
```

### Step 3: Generate Public Domain

1. In Railway dashboard, go to your VendorAuditAI service
2. Click "Settings" > "Networking" > "Generate Domain"
3. You'll get a URL like: `vendorauditai-production.up.railway.app`

### Step 4: Redeploy Backend

```bash
cd backend
RAILWAY_TOKEN="6df8f143-0958-417b-8f05-737939af2775" railway up --service VendorAuditAI --detach
```

### Step 5: Test Backend

```bash
curl https://YOUR-RAILWAY-DOMAIN.up.railway.app/api/v1/status
```

Expected response:
```json
{"api_version":"v1","status":"operational","endpoints":{...}}
```

### Step 6: Update Frontend API URL

1. Go to Netlify Dashboard > vendor-audit-ai > Site Settings > Environment Variables
2. Add: `VITE_API_URL=https://YOUR-RAILWAY-DOMAIN.up.railway.app`
3. Trigger redeploy in Netlify

Or redeploy locally:
```bash
cd frontend
echo "VITE_API_URL=https://YOUR-RAILWAY-DOMAIN.up.railway.app" > .env.production
npm run build
netlify deploy --prod --dir=dist
```

### Step 7: Test Full Production Flow

1. Go to https://vendor-audit-ai.netlify.app
2. Register a new account
3. Login with the new account
4. Create a vendor
5. Verify all features work

---

## Useful CLI Commands

```bash
# Link to project (one-time setup)
railway link

# Check deployment status
railway status

# View build logs
railway logs --build

# View runtime logs
railway logs

# Set environment variables
railway variables --set "KEY=value"

# Deploy
railway up --detach
```

---

## Demo Credentials (Production)

| Field | Value |
|-------|-------|
| **Email** | `newdemo@vendorauditai.com` |
| **Password** | `Demo12345` |

This is the only demo account. Use it to explore all platform features.

---

## Architecture Overview

```
[Browser] --> [Netlify CDN] --> [React Frontend]
                                     |
                                     v
                              [Railway Backend]
                                     |
                                     v
                              [PostgreSQL DB]
```

## Environment Variables Reference

### Backend (Railway)

| Variable | Required | Description |
|----------|----------|-------------|
| DATABASE_URL | Yes | PostgreSQL connection string (use postgresql+asyncpg://) |
| JWT_SECRET_KEY | Yes | Secret for JWT tokens (min 32 chars) |
| CORS_ORIGINS | Yes | JSON array of allowed origins |
| APP_ENV | No | "production" or "development" |
| DEBUG | No | "true" or "false" |
| LLM_PROVIDER | No | "anthropic" or "gemini" (default: anthropic) |
| EMBEDDING_PROVIDER | No | "openai" or "gemini" (default: openai) |
| GOOGLE_API_KEY | No | For Gemini AI features |
| ANTHROPIC_API_KEY | No | For Claude AI features |
| OPENAI_API_KEY | No | For OpenAI embeddings |

### Frontend (Netlify)

| Variable | Required | Description |
|----------|----------|-------------|
| VITE_API_URL | Yes | Backend API URL (e.g., https://xxx.up.railway.app) |

---

## Troubleshooting

### Healthcheck Failing
1. Check runtime logs: `railway logs --service VendorAuditAI`
2. Ensure DATABASE_URL is set
3. Ensure JWT_SECRET_KEY is set
4. Verify the app starts on the correct PORT (Railway sets this automatically)

### CORS Errors
1. Verify CORS_ORIGINS includes your Netlify domain
2. Format must be JSON array: `["https://domain1.com","https://domain2.com"]`

### Database Connection Issues
1. Ensure DATABASE_URL uses `postgresql+asyncpg://` prefix
2. Check PostgreSQL service is running in Railway

---

## Sources

- [Railway CLI Documentation](https://docs.railway.com/guides/cli)
- [Railway Public API](https://docs.railway.com/guides/public-api)
