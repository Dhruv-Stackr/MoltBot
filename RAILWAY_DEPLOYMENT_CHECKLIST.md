# Railway Deployment Checklist

## ✅ Pre-Deployment Checklist

- [ ] Code pushed to GitHub
- [ ] Railway account created
- [ ] MongoDB Atlas account created (or Railway MongoDB ready)
- [ ] Emergent LLM key ready: `sk-emergent-e18C93144D2577f7cF`

---

## 📝 Step-by-Step Deployment

### 1️⃣ Setup MongoDB (5 minutes)

**Option A: MongoDB Atlas (Recommended)**
1. Go to https://www.mongodb.com/cloud/atlas
2. Sign up for free account
3. Create cluster (free tier - M0)
4. Database Access → Add User (username + password)
5. Network Access → Add IP (0.0.0.0/0 for development)
6. Get connection string: `mongodb+srv://username:password@cluster.mongodb.net/`

**Option B: Railway MongoDB**
1. Railway Project → New → Database → MongoDB
2. Copy `MONGO_URL` from variables tab

---

### 2️⃣ Deploy Backend Service (10 minutes)

1. **Create Service**
   - Railway → New Project → Deploy from GitHub repo
   - Select your MoltBot repository
   - Service will start deploying

2. **Configure Root Directory**
   - Click on the service card
   - Settings tab → Root Directory → Enter: `backend`
   - Service will redeploy automatically

3. **Add Environment Variables**
   - Settings tab → Variables tab → Add variables:
   ```
   MONGO_URL=mongodb+srv://username:password@cluster.mongodb.net/
   DB_NAME=moltbot
   LLM_KEY=sk-emergent-e18C93144D2577f7cF
   EMERGENT_BASE_URL=https://integrations.emergentagent.com/llm
   CORS_ORIGINS=*
   ```

4. **Get Backend URL**
   - Settings tab → Domains
   - Copy the generated domain (e.g., `https://moltbot-backend-production.up.railway.app`)
   - Save this for frontend configuration

5. **Verify Deployment**
   - Check Deployments tab for success status
   - Test endpoint: `curl https://your-backend-url.railway.app/health`

---

### 3️⃣ Deploy Frontend Service (10 minutes)

1. **Create Service**
   - Same Railway project → New → GitHub Repo
   - Select the SAME MoltBot repository
   - Service will start deploying

2. **Configure Root Directory**
   - Click on the new service card
   - Settings tab → Root Directory → Enter: `frontend`
   - Service will redeploy automatically

3. **Add Environment Variables**
   - Settings tab → Variables tab → Add variable:
   ```
   REACT_APP_BACKEND_URL=<paste-backend-url-from-step-2>
   ```
   Example: `REACT_APP_BACKEND_URL=https://moltbot-backend-production.up.railway.app`

4. **Get Frontend URL**
   - Settings tab → Domains
   - Copy the generated domain (e.g., `https://moltbot-frontend-production.up.railway.app`)

5. **Verify Deployment**
   - Check Deployments tab for success status
   - Open frontend URL in browser
   - Test login and basic functionality

---

### 4️⃣ Post-Deployment Configuration (5 minutes)

1. **Update Backend CORS (Optional)**
   - If you want stricter CORS, update backend's `CORS_ORIGINS` variable:
   ```
   CORS_ORIGINS=https://your-frontend-url.railway.app
   ```
   - Redeploy backend

2. **Custom Domain (Optional)**
   - Settings → Domains → Add Custom Domain
   - Follow DNS configuration instructions

3. **Enable Auto-Deploy**
   - Settings → Service → GitHub → Enable auto-deploy
   - Every push to main branch will trigger deployment

---

## 🎯 Final Verification

### Backend Health Check:
```bash
curl https://your-backend.railway.app/health
```
Expected: `{"status": "healthy"}`

### Frontend Check:
Open in browser: `https://your-frontend.railway.app`

### Database Check:
Login to MoltBot → Create a bot → Verify it saves

---

## 📊 Monitor Your Deployment

### Railway Dashboard:
- **Metrics:** CPU, Memory, Network usage
- **Logs:** Real-time application logs
- **Deployments:** Deployment history and status

### View Logs:
- Service → Deployments → View Logs
- Or use Railway CLI: `railway logs`

---

## 💰 Cost Estimate

| Service | Plan | Cost |
|---------|------|------|
| Railway Backend | Starter | ~$5/month |
| Railway Frontend | Starter | ~$5/month |
| MongoDB Atlas | Free (M0) | $0 |
| Emergent LLM | Pay-per-use | Variable |
| **Total** | | **~$10/month** |

Railway free trial: $5 credit/month

---

## 🆘 Troubleshooting

### Backend build fails:
- Check Deployments → Logs for error details
- Verify Root Directory is set to `backend`
- Verify all environment variables are set

### Frontend build fails:
- Check Deployments → Logs
- Verify Root Directory is set to `frontend`
- Verify `REACT_APP_BACKEND_URL` is correct

### Frontend can't reach backend:
- Verify backend is running (check health endpoint)
- Check CORS_ORIGINS setting on backend
- Verify REACT_APP_BACKEND_URL in frontend variables

### Database connection errors:
- Test MongoDB connection string separately
- Verify IP whitelist in MongoDB Atlas (use 0.0.0.0/0)
- Check database username/password

---

## 🎓 Railway CLI (Optional)

Install Railway CLI for easier management:

```bash
# Install
npm i -g @railway/cli

# Login
railway login

# Link project
railway link

# View logs
railway logs

# Open dashboard
railway open
```

---

## 📚 Additional Resources

- **Railway Docs:** https://docs.railway.app
- **MongoDB Atlas Docs:** https://www.mongodb.com/docs/atlas/
- **MoltBot Tutorial:** https://emergent.sh/tutorial/moltbot-on-emergent
- **Detailed Fix:** See `RAILWAY_FIX_EMERGENT_INTEGRATIONS.md`

---

## ✅ Success Criteria

You've successfully deployed when:

- [ ] Backend health check returns 200 OK
- [ ] Frontend loads in browser
- [ ] Can create and save a bot
- [ ] ClawBot responds to messages
- [ ] LLM integration works (chat functionality)

---

**Congratulations! Your MoltBot is now live on Railway!** 🎉

Remember to monitor your Railway usage and Emergent LLM credits.
