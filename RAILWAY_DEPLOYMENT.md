# MoltBot Railway Deployment Guide

## 🚂 Deploy to Railway - Step by Step

This guide will help you deploy MoltBot (a monorepo with separate backend and frontend) to Railway.

---

## ⚠️ Important: Monorepo Structure

MoltBot has a **monorepo structure**:
```
/app/
├── backend/     # FastAPI backend
├── frontend/    # React frontend
└── ...
```

Railway requires **two separate services** for this setup.

---

## 🎯 Deployment Steps

### **Option A: Deploy Using Root Directory Settings** (Recommended)

1. **Create Backend Service**
   - Go to Railway dashboard
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your MoltBot repository
   - **Important:** Set **Root Directory** to `backend`
   - Railway will auto-detect Python and use `railway.toml` or `Procfile`

2. **Create Frontend Service**
   - In the same project, click "New" → "GitHub Repo"
   - Select the same MoltBot repository again
   - **Important:** Set **Root Directory** to `frontend`
   - Railway will auto-detect Node.js and build the React app

3. **Add MongoDB**
   - Click "New" → "Database" → "Add MongoDB"
   - Or use MongoDB Atlas (free tier)

4. **Configure Environment Variables**

   **Backend Service Variables:**
   ```
   MONGO_URL=<your-mongodb-connection-string>
   DB_NAME=moltbot
   LLM_KEY=sk-emergent-e18C93144D2577f7cF
   CORS_ORIGINS=*
   PORT=8001
   ```

   **Frontend Service Variables:**
   ```
   REACT_APP_BACKEND_URL=<your-backend-service-url>
   PORT=3000
   ```

5. **Deploy!**
   - Both services will auto-deploy
   - Update `REACT_APP_BACKEND_URL` with the actual backend URL
   - Redeploy frontend

---

### **Option B: Deploy Using Separate Repositories** (Alternative)

If Option A doesn't work:

1. Create two separate GitHub repos:
   - `moltbot-backend` (copy `/app/backend/` contents)
   - `moltbot-frontend` (copy `/app/frontend/` contents)

2. Deploy each as a separate Railway service

---

## 📋 Configuration Files Included

The following files have been added to help Railway understand the project structure:

### Root Level:
- **`railway.toml`** - Indicates this is a monorepo

### Backend (`/app/backend/`):
- **`railway.toml`** - Backend build/start configuration
- **`Procfile`** - Alternative start command
- **`requirements.txt`** - Python dependencies

### Frontend (`/app/frontend/`):
- **`railway.toml`** - Frontend build/start configuration
- **`Procfile`** - Alternative start command
- **`package.json`** - Node.js dependencies

---

## 🔧 Troubleshooting

### Error: "Script start.sh not found"
**Solution:** Deploy backend and frontend as **separate services** with different root directories.

### Error: "Could not determine how to build"
**Solution:** Ensure you've set the **Root Directory** in Railway service settings:
- Backend service: `backend`
- Frontend service: `frontend`

### Error: "Module not found"
**Solution:** Check that all dependencies are in:
- `backend/requirements.txt` (Python)
- `frontend/package.json` (Node.js)

### Frontend can't connect to backend
**Solution:** Update `REACT_APP_BACKEND_URL` in frontend service with actual backend URL from Railway.

---

## 💰 Estimated Costs

**Free Tier:**
- $5 free credit/month
- Good for testing

**Paid Plans:**
- ~$5-10/month for both services
- MongoDB Atlas free tier (512MB)

---

## 🎯 Quick Checklist

- [ ] Create backend service (root dir: `backend`)
- [ ] Create frontend service (root dir: `frontend`)
- [ ] Add MongoDB (Railway or Atlas)
- [ ] Set backend environment variables
- [ ] Deploy backend and get URL
- [ ] Set frontend environment variables with backend URL
- [ ] Deploy frontend
- [ ] Test the application

---

## 📞 Need Help?

If you encounter issues:
1. Check Railway build logs
2. Verify root directory settings
3. Ensure environment variables are set correctly
4. Check that MongoDB connection is working

---

## 🚀 After Deployment

Your MoltBot will be live at:
- **Frontend:** `https://your-frontend.railway.app`
- **Backend API:** `https://your-backend.railway.app`

Configure ClawBot skills and settings through the admin interface!
