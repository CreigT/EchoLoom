# Deploy EchoLoom

This is a **single-service** deploy. JSON persistence on disk. No paid cloud required.

## What production-ready means here

Safe to put on a public URL for demo and private-story intake.

Not safe yet for paid customer audio, voice cloning, public marketplace sales, or regulated family archives at scale.

## Required environment

```
APP_ENV=production
APP_SECRET=<32+ random characters>
ALLOWED_ORIGINS=https://your-domain.example
DATA_DIR=/app/data
LLM_PROVIDER=mock
REQUIRE_VOICE_CONSENT=true
```

The process refuses to start in production if APP_SECRET is still the default.

## Render

Use render.yaml. Mount a disk at /app/data. Health check /health.

## Local production mode

```bash
export APP_ENV=production
export APP_SECRET=$(python -c "import secrets; print(secrets.token_hex(24))")
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1
```

Use one worker while persistence is a JSON file.

## Checks after deploy

- GET /health
- GET /ready
- Submit a story with consent checked
- Restart and confirm the project remains
