# 🚨 Quick Fix for Railway Deployment Error

## The Problem
```
⚠ Script start.sh not found
✖ Railpack could not determine how to build the app.
```

Railway is trying to deploy the entire repo as one service, but MoltBot is a **monorepo** with separate backend and frontend.

---

## ✅ The Solution

Deploy as **TWO separate services** in Railway:

### Step 1: Deploy Backend

1. Go to Railway → New Project → Deploy from GitHub
2. Select your MoltBot repo
3. **CRITICAL:** Go to Settings → **Set Root Directory to `backend`**
4. Add environment variables:
   ```
   MONGO_URL=<your-mongodb-url>
   DB_NAME=moltbot
   LLM_KEY=sk-emergent-e18C93144D2577f7cF
   CORS_ORIGINS=*
   ```
5. Deploy ✅

### Step 2: Deploy Frontend

1. In the same project → New → GitHub Repo
2. Select the same MoltBot repo
3. **CRITICAL:** Go to Settings → **Set Root Directory to `frontend`**
4. Add environment variables:
   ```
   REACT_APP_BACKEND_URL=<backend-url-from-step-1>
   ```
5. Deploy ✅

### Step 3: Add MongoDB (if needed)

1. In the same project → New → Database → MongoDB
2. Copy the connection URL
3. Update backend's `MONGO_URL` variable
4. Redeploy backend

---

## 🎯 Key Points

- **Root Directory is CRITICAL** - Railway needs to know which folder to deploy
- Deploy backend first, get its URL, then use it in frontend
- Each service needs its own environment variables
- Both services should be in the same Railway project

---

## 📸 Visual Guide

```
Railway Project: MoltBot
│
├── Service 1: Backend
│   ├── Root Directory: backend
│   ├── Detected: Python (FastAPI)
│   └── URL: https://moltbot-backend-xxx.railway.app
│
├── Service 2: Frontend  
│   ├── Root Directory: frontend
│   ├── Detected: Node.js (React)
│   └── URL: https://moltbot-frontend-xxx.railway.app
│
└── Database: MongoDB
    └── Connection: mongodb://...
```

---

## ⚡ That's It!

Your MoltBot should now deploy successfully on Railway! 🎉

For detailed instructions, see: `RAILWAY_DEPLOYMENT.md`
