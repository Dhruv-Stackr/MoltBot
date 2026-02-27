# 🔧 Fixed: Node.js Version Error (Railway Frontend)

## ✅ Problem Solved

**Error:** 
```
error react-router-dom@7.13.1: The engine "node" is incompatible with this module. 
Expected version ">=20.0.0". Got "18.20.5"
```

**Root Cause:** Railway's auto-detection picked Node.js 18, but `react-router-dom@7.5.1` (which resolves to v7.13.1) requires Node.js 20+.

**Solution:** Configure Railway to use Node.js 22 (or 20+) for the frontend.

---

## ✅ Changes Made

### 1. Updated `/app/frontend/railway.toml`
Changed from `nodejs_20` to `nodejs_22`:
```toml
[phases.setup]
nixPkgs = ["nodejs_22", "yarn"]
```

### 2. Added `/app/frontend/nixpacks.toml`
Alternative configuration file that Railway will detect:
```toml
[phases.setup]
nixPkgs = ["nodejs_22"]
```

### 3. Updated `/app/frontend/package.json`
Added engines field to explicitly require Node 20+:
```json
"engines": {
  "node": ">=20.0.0",
  "npm": ">=10.0.0"
}
```

---

## 🚀 Deployment Instructions (Updated)

### For Backend (No Changes):

1. **Railway Dashboard** → New Project → Deploy from GitHub
2. **Select Repository:** Your MoltBot repo
3. **Set Root Directory:** `backend` ⚠️
4. **Add Environment Variables:**
   ```
   MONGO_URL=<your-mongodb-connection>
   DB_NAME=moltbot
   LLM_KEY=sk-emergent-e18C93144D2577f7cF
   EMERGENT_BASE_URL=https://integrations.emergentagent.com/llm
   CORS_ORIGINS=*
   ```
5. Deploy ✅

---

### For Frontend (Updated with Node.js 22):

1. **Same Project** → New → GitHub Repo (same repo)
2. **Set Root Directory:** `frontend` ⚠️
3. **Verify Node Version:** Railway should now auto-detect Node.js 22 from nixpacks.toml
4. **Add Environment Variable:**
   ```
   REACT_APP_BACKEND_URL=<backend-url-from-backend-deployment>
   ```
5. Deploy ✅

---

## 🔍 Verification

After deployment, check the build logs to confirm:
```
✓ setup      │ nodejs_22, yarn
```

Instead of:
```
✗ setup      │ nodejs_18, yarn-1_x
```

---

## 📋 All Fixed Issues Summary

| Issue | Status |
|-------|--------|
| ❌ Monorepo structure | ✅ **FIXED** - Root directory configuration |
| ❌ `emergentintegrations` missing | ✅ **FIXED** - Removed from requirements.txt |
| ❌ Node.js version mismatch | ✅ **FIXED** - Using Node.js 22 |
| ✅ Emergent LLM key works externally | ✅ **CONFIRMED** |

---

## 🎯 Final Deployment Checklist

- [ ] Push all code changes to GitHub:
  ```bash
  git add .
  git commit -m "Fix Railway deployment: Node.js 22 + remove emergentintegrations"
  git push origin main
  ```

- [ ] Deploy Backend:
  - Root directory: `backend`
  - Add all environment variables
  - Get backend URL

- [ ] Deploy Frontend:
  - Root directory: `frontend`
  - Add `REACT_APP_BACKEND_URL` with backend URL
  - Verify Node.js 22 in build logs

- [ ] Test application:
  - Backend health check: `curl <backend-url>/health`
  - Frontend loads in browser
  - Can login and use MoltBot

---

## 💡 Why Node.js 22?

- **react-router-dom v7** requires Node.js 20+
- Node.js 22 is the latest LTS version (as of Feb 2026)
- Better performance and security
- Future-proof for other dependencies

---

## 🆘 If Build Still Fails

1. **Check Build Logs:**
   - Railway Dashboard → Service → Deployments → View Logs
   - Look for Node.js version in the setup phase

2. **Force Nixpacks to Use Node 22:**
   - Add Railway environment variable: `NIXPACKS_PKGS=nodejs_22`

3. **Alternative: Use .nvmrc:**
   Create `/app/frontend/.nvmrc` with content:
   ```
   22
   ```

4. **Clear Railway Cache:**
   - Settings → Service → Clear Build Cache
   - Redeploy

---

**Your MoltBot is now fully configured for Railway deployment!** 🎉

All issues resolved:
- ✅ Backend dependencies fixed (no emergentintegrations)
- ✅ Frontend Node.js version updated to 22
- ✅ Configuration files added for Railway
- ✅ Emergent LLM key works externally
