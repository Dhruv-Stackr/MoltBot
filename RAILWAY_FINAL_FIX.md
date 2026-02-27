# DEFINITIVE Railway Deployment Fix - Step by Step

## ⏱️ Total Time: ~15 minutes

Follow EXACTLY in order. Verify each step before moving to next.

---

## 🎯 STEP 1: Backend Environment Variables (3 mins)

### 1.1 Go to Railway Backend Service
- Open Railway dashboard
- Select your **backend** service
- Go to **Variables** tab

### 1.2 Add These EXACT Variables

**Copy-paste these EXACTLY:**

```
NOCODB_URL=https://app.nocodb.com/api/v2/tables/mofz1f3ftcxtks5/records
```

```
NOCODB_TOKEN=bnxELWAHG5z41N8JTGDjRBp4k8r8q41cMh_abecn
```

```
CORS_ORIGINS=*
```

```
EMERGENT_API_KEY=sk-emergent-e18C93144D2577f7cF
```

```
EMERGENT_BASE_URL=https://integrations.emergentagent.com/llm
```

### 1.3 VERIFY Backend Variables
- Click "Save"
- Railway will redeploy backend automatically
- Wait 2-3 minutes for deployment to complete

### 1.4 TEST Backend
Open this URL in browser (replace with YOUR backend URL):
```
https://YOUR-BACKEND.railway.app/api/
```

✅ **Expected Result:** `{"message":"OpenClaw Hosting API"}`
❌ **If you see error:** Backend not deployed yet. Wait 2 more minutes.

---

## 🎯 STEP 2: Frontend Environment Variable (2 mins)

### 2.1 Get Your Railway Backend URL
From Railway dashboard, copy your backend service's public URL.
Example: `https://moltbot-backend-production.railway.app`

### 2.2 Set Frontend Variable
Go to Railway **frontend** service → Variables tab

Add this variable (replace with YOUR backend URL):
```
REACT_APP_BACKEND_URL=https://YOUR-BACKEND.railway.app
```

⚠️ **CRITICAL:** 
- Use YOUR Railway backend URL, not Emergent preview URL
- Must be HTTPS
- NO trailing slash

### 2.3 VERIFY Frontend Variable
- Click "Save"
- Wait 2-3 minutes for frontend redeploy

---

## 🎯 STEP 3: Test Complete Flow (5 mins)

### 3.1 Open Railway Frontend URL
Visit: `https://YOUR-FRONTEND.railway.app`

### 3.2 Open Browser Console
- Press F12
- Go to Console tab
- Go to Network tab

### 3.3 Click "Sign in with Google"

**Watch Network Tab:**

✅ **Success Signs:**
- See request to `/api/auth/session` → Status 200
- Redirects to Google login
- After login, returns to your app
- You see OpenClaw setup page

❌ **Failure Signs:**
- Request to `/api/auth/session` → Status 400/401/500
- CORS error in console
- Login loop

### 3.4 If You See Errors

**Error: "OPTIONS 400"**
→ Backend code not updated. Deploy latest code.

**Error: "CORS policy"**  
→ Backend not running or wrong backend URL in frontend.

**Error: "401 Unauthorized"**
→ NocoDB credentials missing in backend env vars.

**Error: Login loop**
→ Frontend REACT_APP_BACKEND_URL is wrong.

---

## 🎯 STEP 4: If Still Not Working (5 mins)

### Collect This Information:

1. **Backend URL:** https://_____.railway.app
2. **Frontend URL:** https://_____.railway.app
3. **Test Backend:**
   ```bash
   curl https://YOUR-BACKEND.railway.app/api/
   ```
   Result: _____

4. **Check Backend Logs:**
   - Go to Railway backend service
   - Click "Deployments"
   - Click latest deployment
   - Click "View Logs"
   - Copy last 50 lines

5. **Browser Console Errors:**
   - Open F12 → Console tab
   - Try to login
   - Screenshot any red errors

---

## 🚨 NUCLEAR OPTION: If Nothing Works

### Option A: Use Different Railway Account
Sometimes Railway accounts have issues. Try:
1. Create new Railway account
2. Create new project
3. Deploy fresh

### Option B: Try Different Platform

**Vercel (Easier):**
1. Deploy backend to Render.com (free tier)
2. Deploy frontend to Vercel
3. Usually works first try

**Render.com (Simpler):**
1. Both services on Render
2. Simpler configuration
3. More reliable

### Option C: Use Emergent Native Deployment
- Emergent has one-click deployment
- Everything already works in preview
- Just deploy from Emergent dashboard

---

## 📞 Last Resort

If NOTHING works after trying all above:

**Send me:**
1. Railway backend URL
2. Railway frontend URL  
3. Backend logs (last 50 lines)
4. Browser console screenshot

I'll diagnose the exact issue.

---

## ✅ Success Criteria

You know it's working when:
1. Backend API responds at `/api/`
2. Frontend loads without console errors
3. Google login redirects properly
4. After login, you see "OpenClaw Setup" page
5. Clicking "Start OpenClaw" works

If ALL these work → SUCCESS! 🎉
If ANY fail → Collect info above and we'll fix it.
