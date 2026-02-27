# Railway Backend - Add CORS Middleware

## The Issue
Railway backend is running but doesn't have CORS headers, blocking frontend requests.

## Quick Fix

Add this to your `server.py` at the top (after imports, before creating the `app`):

```python
from starlette.middleware.cors import CORSMiddleware

# ... your other imports ...

app = FastAPI()

# Add CORS middleware - MUST be added early
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for now
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ... rest of your code ...
```

## Already in Code?

If CORS middleware is already in your `server.py`, check:

1. **Line placement**: CORS middleware must be added **immediately after** creating the `app` object
2. **Origins**: Should be `["*"]` or include your frontend URL

## After Adding

1. Commit and push to Railway
2. Wait for redeploy (2-3 mins)
3. Test again

## Verify CORS is Working

```bash
curl -I -X OPTIONS \
  https://moltbot-production-2586.up.railway.app/api/auth/session \
  -H "Origin: https://imaginative-success-production.up.railway.app" \
  -H "Access-Control-Request-Method: POST"
```

Should see:
```
access-control-allow-origin: *
access-control-allow-methods: DELETE, GET, HEAD, OPTIONS, PATCH, POST, PUT
```

If you see these headers → CORS is working!
If you don't see them → Code not deployed yet or CORS not configured.
