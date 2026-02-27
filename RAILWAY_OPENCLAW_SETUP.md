# Railway Deployment Guide for MoltBot with OpenClaw

## Files Added/Modified for Railway Support

### New Files Created:
1. **`frontend/nixpacks.toml`** - Railway build configuration for frontend
   - Forces yarn usage
   - Correct build and start commands

2. **`backend/nixpacks.toml`** - Railway build configuration for backend
   - Includes Python 3.12 and Node.js 22
   - Runs clawdbot installation during build
   - Starts uvicorn on dynamic port

3. **`backend/install_railway.sh`** - Railway-optimized clawdbot installer
   - Installs clawdbot using npm during build phase
   - Creates wrapper scripts for Railway environment

4. **`backend/railway_process_manager.py`** - Process manager for Railway
   - Manages clawdbot as a background subprocess
   - Replaces supervisor functionality for Railway

5. **`backend/universal_process_manager.py`** - Environment-aware process manager
   - Automatically detects Emergent vs Railway
   - Uses supervisor on Emergent, direct process on Railway

### Modified Files:
1. **`backend/server.py`**
   - Added Railway clawdbot directory to search path
   - Replaced SupervisorClient with UniversalProcessManager
   - Updated CORS to include Railway frontend URL

## Railway Service Configuration

### Backend Service:
- **Root Directory:** `backend`
- **Port:** Leave blank (uses $PORT)
- **Environment Variables Required:**
  ```
  NOCODB_URL=https://app.nocodb.com/api/v2/tables/mofz1f3ftcxtks5/records
  NOCODB_TOKEN=bnxELWAHG5z41N8JTGDjRBp4k8r8q41cMh_abecn
  ```

### Frontend Service:
- **Root Directory:** `frontend`
- **Port:** Leave blank (uses $PORT)
- **Environment Variables Required:**
  ```
  REACT_APP_BACKEND_URL=<your-railway-backend-url>
  ```

## Deployment Steps:

1. **Push all files to your Railway project**
   ```bash
   git add .
   git commit -m "Add Railway support with OpenClaw"
   git push
   ```

2. **Configure Backend Service:**
   - Set Root Directory: `backend`
   - Add NOCODB_URL and NOCODB_TOKEN environment variables
   - Deploy

3. **Configure Frontend Service:**
   - Set Root Directory: `frontend`
   - Add REACT_APP_BACKEND_URL (your backend Railway URL)
   - Deploy

4. **Test OpenClaw:**
   - Access your frontend URL
   - Login with Google
   - Click "Start Gateway"
   - Check backend logs for clawdbot installation and startup

## How It Works:

1. **Build Phase:**
   - Railway runs `nixpacks.toml` instructions
   - Node.js 22 is installed alongside Python
   - `install_railway.sh` runs and installs clawdbot globally

2. **Runtime:**
   - Backend detects Railway environment
   - Uses `UniversalProcessManager` which delegates to `RailwayProcessManager`
   - When `/api/openclaw/start` is called:
     - Checks for clawdbot installation
     - Starts clawdbot as a background subprocess
     - Manages process lifecycle (start/stop/status)

3. **Process Management:**
   - On Emergent: Uses supervisor (existing behavior)
   - On Railway: Uses background subprocess with PID tracking

## Troubleshooting:

### If clawdbot fails to install:
- Check backend build logs for npm installation errors
- Verify Node.js is available: Look for "Node version:" in logs

### If gateway fails to start:
- Check backend runtime logs for process start errors
- Verify clawdbot is found: Look for "Clawdbot found at:" message

### If getting "not installed" error:
- clawdbot installation may have failed during build
- Redeploy backend service to retry installation
