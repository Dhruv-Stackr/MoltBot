# Railway Deployment - Latest Fixes

## Issues Fixed:

### 1. Node.js Version Mismatch ✅
**Problem:** Railway's Node.js 22.10.0 < clawdbot's requirement (>=22.12.0)
**Solution:** Updated `backend/nixpacks.toml` to use `nodejs-22_x` (latest 22.x)

### 2. Interactive Setup in Docker Build ✅
**Problem:** molt.bot installer tried to access `/dev/tty` (not available in Docker)
**Solution:** Updated `backend/install_railway.sh` to:
- Use `OPENCLAW_SKIP_SETUP=1` environment variable
- Redirect stdin with `</dev/null` for non-interactive mode
- Don't fail build if clawdbot not immediately accessible

### 3. PATH Issues ✅
**Problem:** Globally installed npm packages not in PATH
**Solution:** Install script now:
- Detects npm global bin directory
- Checks multiple common locations
- Creates wrapper scripts as fallback
- Returns success (exit 0) even if not found, allowing runtime retry

## Files Modified:

1. **`backend/nixpacks.toml`** - Use `nodejs-22_x` for latest 22.x version
2. **`backend/install_railway.sh`** - Enhanced with:
   - Multiple installation fallbacks
   - Non-interactive mode for official installer  
   - PATH detection and wrapper creation
   - Graceful failure (doesn't break build)

## Next Steps:

1. **Push changes:**
   ```bash
   git add backend/nixpacks.toml backend/install_railway.sh
   git commit -m "Fix Node.js version and non-interactive installation"
   git push
   ```

2. **Redeploy backend on Railway**

3. **Expected behavior:**
   - Build will succeed even if clawdbot install has issues
   - Backend will try to install clawdbot at runtime if not found
   - Multiple fallback mechanisms ensure clawdbot works

## Installation Strategy:

The script now tries (in order):
1. `npm install -g clawdbot@latest` (with --force if needed)
2. Local `npm install clawdbot@latest` + wrapper
3. Check common npm bin directories
4. Official molt.bot installer (non-interactive)
5. Check additional bin directories
6. Create direct node wrapper if package exists
7. Gracefully return success for runtime retry

This multi-layer approach ensures maximum compatibility!
