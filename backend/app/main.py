from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware

from app import __version__
from app.api.routes import router
from app.core.config import get_settings
from app.services.store import store

settings = get_settings()
FRONTEND = Path(__file__).resolve().parents[2] / "frontend"


class SecurityHeaders(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "same-origin"
        response.headers["Permissions-Policy"] = "microphone=(), camera=(), geolocation=()"
        response.headers["Cache-Control"] = "no-store"
        return response


@asynccontextmanager
async def lifespan(_: FastAPI):
    await store.load()
    yield


app = FastAPI(
    title=settings.app_name,
    version=__version__,
    description="Multi-agent studio that turns raw stories into produced audio.",
    lifespan=lifespan,
    docs_url="/docs" if not settings.is_production() else None,
    redoc_url=None,
)

origins = settings.origin_list()
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=origins != ["*"],
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)
app.add_middleware(SecurityHeaders)
app.include_router(router, prefix="/api")


@app.get("/health")
async def health() -> dict:
    return {"ok": True, "service": settings.app_name, "version": __version__, "env": settings.app_env}


@app.get("/ready")
async def ready() -> JSONResponse:
    await store.load()
    payload = {
        "ok": True,
        "persist": bool(store._persist_path),
        "projects": len(await store.all()),
        "version": __version__,
    }
    return JSONResponse(payload)


if FRONTEND.exists():
    app.mount("/assets", StaticFiles(directory=FRONTEND), name="assets")

    @app.get("/")
    async def studio() -> FileResponse:
        return FileResponse(FRONTEND / "index.html")
