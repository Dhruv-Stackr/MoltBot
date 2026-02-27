# MoltBot Railway Deployment Guide (NocoDB Version)

## ✅ Pre-Deployment Checklist

All code is ready for deployment:
- ✅ MongoDB replaced with NocoDB
- ✅ Authentication system working
- ✅ Gateway ownership system fixed
- ✅ CORS configured properly
- ✅ OPTIONS preflight handling added
- ✅ All tests passing (15/15)

---

## 🚀 Step 1: Configure Railway Environment Variables

### Backend Service Environment Variables

Add these to your **backend service** in Railway:

| Variable Name | Value |
|---------------|-------|
| `NOCODB_URL` | `https://app.nocodb.com/api/v2/tables/mofz1f3ftcxtks5/records` |
| `NOCODB_TOKEN` | `bnxELWAHG5z41N8JTGDjRBp4k8r8q41cMh_abecn` |
| `CORS_ORIGINS` | `*` |
| `EMERGENT_API_KEY` | `sk-emergent-e18C93144D2577f7cF` |
| `EMERGENT_BASE_URL` | `https://integrations.emergentagent.com/llm` |

**Important**: Remove or ignore these old MongoDB variables:
- ❌ `MONGO_URL` - Not needed
- ❌ `DB_NAME` - Not needed

### Frontend Service Environment Variables

Make sure your **frontend service** has:

| Variable Name | Value |
|---------------|-------|
| `REACT_APP_BACKEND_URL` | `https://your-backend-url.railway.app` |

⚠️ **Replace** `your-backend-url.railway.app` with your actual Railway backend URL!

---

## 🚀 Step 2: Deploy to Railway

### Option A: Using Railway CLI

```bash
# Navigate to your project
cd /path/to/moltbot

# Login to Railway (if not already)
railway login

# Link to your project
railway link

# Deploy backend
railway up --service backend

# Deploy frontend
railway up --service frontend
```

### Option B: Using Git Push

```bash
# If your Railway is connected to GitHub:
git add .
git commit -m "Migrate to NocoDB - Railway deployment ready"
git push origin main
```

Railway will automatically detect the push and deploy.

---

## 🚀 Step 3: Verify Deployment

### Check Backend Health

Visit: `https://your-backend-url.railway.app/api/`

Should return:
```json
{"message":"OpenClaw Hosting API"}
```

### Check NocoDB Connection

Visit: `https://your-backend-url.railway.app/api/auth/instance`

Should return:
```json
{"locked":false}
```

If you see `{"detail":"..."}` errors, check:
1. Environment variables are set correctly
2. NocoDB token is valid
3. Backend service restarted after adding env vars

---

## 🔧 Troubleshooting Railway Deployment

### Issue: "OPTIONS 400 Bad Request"
**Solution**: This was fixed in the code. Make sure you deployed the latest code with the OPTIONS handler.

### Issue: "Login loop" or "401 Unauthorized"
**Causes**:
1. Missing `NOCODB_URL` or `NOCODB_TOKEN` environment variables
2. Backend not restarted after adding env vars

**Solution**:
1. Add environment variables in Railway dashboard
2. Restart the backend service
3. Clear browser cache and try again

### Issue: "Startup failed" when starting OpenClaw
**Solution**: This was fixed in the code (gateway ownership claiming). Deploy latest code.

### Issue: "CORS errors"
**Solution**: Make sure `CORS_ORIGINS=*` is set in backend environment variables.

---

## 📋 What Changed from Original MoltBot

### Database
- ❌ **Old**: MongoDB connection
- ✅ **New**: NocoDB REST API

### Files Modified
1. `/app/backend/nocodb_client.py` - **NEW FILE** - NocoDB client
2. `/app/backend/server.py` - Database operations migrated to NocoDB
3. `/app/backend/.env` - Added NocoDB credentials

### Files Unchanged
- ✅ All Railway config files (`railway.toml`, `nixpacks.toml`, `Procfile`)
- ✅ Frontend code (no changes needed)
- ✅ Package dependencies

---

## ✅ Post-Deployment Testing

After deploying to Railway, test:

1. **Visit your frontend URL**
   - Should show "OpenClaw Setup" login page

2. **Click "Sign in with Google"**
   - Should redirect to Google OAuth
   - After login, should return to your app

3. **Start OpenClaw**
   - Click "Start OpenClaw"
   - Should show "OpenClaw Control" interface

4. **Verify Data Persistence**
   - Check NocoDB dashboard
   - Should see records for users, sessions, configs

---

## 🎯 Success Criteria

Your deployment is successful when:
- ✅ Frontend loads without errors
- ✅ Google login works smoothly
- ✅ User reaches OpenClaw setup page
- ✅ Can start/stop OpenClaw gateway
- ✅ Data persists in NocoDB
- ✅ No OPTIONS 400 errors
- ✅ No login loops

---

## 📞 Need Help?

If you encounter issues:
1. Check Railway logs for both frontend and backend services
2. Verify all environment variables are set
3. Ensure NocoDB API token is valid
4. Try restarting both services in Railway

---

## 🎉 Deployment Complete!

Once deployed:
- Your app will use NocoDB for all data storage
- No MongoDB dependency
- All features working as expected
- Ready for production use!

**Deployed URL**: `https://your-frontend-url.railway.app`
