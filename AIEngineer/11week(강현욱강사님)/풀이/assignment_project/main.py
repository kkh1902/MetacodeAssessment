"""FastAPI 앱 진입점 — 미들웨어, 라우터, 헬스체크 등록."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from slowapi.errors import RateLimitExceeded

from api.middleware.rate_limit import limiter, rate_limit_exceeded_handler
from api.routes import chat as chat_routes
from api.routes import documents as document_routes
from core.cache import CacheService
from core.config import get_settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    app.state.cache = CacheService(settings.redis_url)
    yield
    await app.state.cache.close()


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="Assignment FastAPI Backend", version="1.0.0", lifespan=lifespan)

    # CORS — 화이트리스트 도메인만 허용
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allow_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Rate Limit (slowapi) 등록
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

    # 라우터 등록
    app.include_router(chat_routes.router)
    app.include_router(document_routes.router)

    # 정적 파일 (Q5 웹 UI)
    app.mount("/static", StaticFiles(directory="static"), name="static")

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/health/ready")
    async def health_ready() -> dict[str, str | bool]:
        cache_ok = await app.state.cache.ping()
        return {"status": "ok", "redis": cache_ok}

    return app


app = create_app()
