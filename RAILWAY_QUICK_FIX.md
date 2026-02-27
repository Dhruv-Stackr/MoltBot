# Quick Railway Deployment Fix

## The Issue on Railway
You're seeing `OPTIONS 400` errors on Railway because it's running old code without the fixes.

## The Solution

### Step 1: Add Environment Variables in Railway

In your Railway **backend service**, add these variables:

```
NOCODB_URL=https://app.nocodb.com/api/v2/tables/mofz1f3ftcxtks5/records
NOCODB_TOKEN=bnxELWAHG5z41N8JTGDjRBp4k8r8q41cMh_abecn
```

### Step 2: Verify Railway Configuration

Make sure your `railway.toml` files are correct:

**Backend** (`/app/backend/railway.toml`):
```toml
[build]
builder = "nixpacks"

[deploy]
startCommand = "uvicorn server:app --host 0.0.0.0 --port $PORT"
```

**Frontend** (`/app/frontend/railway.toml`):
```toml
[build]
builder = "nixpacks"

[deploy]
startCommand = "yarn start"
```

### Step 3: Deploy to Railway

**Option A - Auto Deploy (Recommended):**
If you connected Railway to GitHub:
1. Push your code: `git push origin main`
2. Railway will auto-deploy

**Option B - Manual Deploy:**
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Link project
railway link

# Deploy
railway up
```

### Step 4: Check Deployment Status

Visit: `https://your-backend-url.railway.app/api/`

Should return: `{"message":"OpenClaw Hosting API"}`

---

## Why Railway Has Issues

| Issue | Cause | Fix |
|-------|-------|-----|
| OPTIONS 400 | Old code without OPTIONS handler | Deploy updated code |
| Login loop | Missing NOCODB_URL/TOKEN | Add env variables |
| 500 errors | Database connection fails | Add NOCODB credentials |

---

## After Deployment

Test on Railway:
1. Visit your frontend URL
2. Login with Google
3. Start OpenClaw
4. Everything should work like in Emergent preview!

---

## Need to Download Code?

Use Emergent's "Download Code" feature to get all files, then:
```bash
cd your-project
git init
git add .
git commit -m "NocoDB migration complete"
git push railway main
```

The code in `/app/` is production-ready! ✅
