# Railway Backend Troubleshooting

## What Railway backend URL shows

**If you see "Application Error":**
- Backend crashed after startup
- Check environment variables are set correctly

**If you see "Service Unavailable" or 502:**
- Port mapping issue
- Railway can't reach your app

**If you see "Not Found" (404):**
- Backend is running but wrong path
- Try: `https://your-backend.railway.app/api/`

**If page doesn't load at all:**
- Backend not deployed yet
- Still building

## Quick Tests

1. **Visit:** `https://your-backend-url.railway.app/api/`
   - Should show: `{"message":"OpenClaw Hosting API"}`

2. **Check Railway Dashboard:**
   - Does backend show "Active" or "Deployed"?
   - Is there a public URL shown?

3. **Check Railway Metrics:**
   - Is CPU usage > 0%?
   - Is memory being used?

## Common Issues

### Issue: No Public URL
**Fix:** In Railway backend settings, make sure:
- Service is set to "public"
- Generate domain is enabled

### Issue: 502 Bad Gateway  
**Fix:** Railway can't reach port 8080
- Add this in Railway backend settings:
- PORT environment variable should be auto-set by Railway
- Or expose port 8080 explicitly

### Issue: Health Check Failing
**Fix:** Disable health checks or add health endpoint
