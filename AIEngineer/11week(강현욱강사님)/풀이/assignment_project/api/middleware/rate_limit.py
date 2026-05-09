"""slowapi Limiter + 429 커스텀 핸들러."""

from __future__ import annotations

from fastapi import Request
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from core.config import get_settings


_settings = get_settings()

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[_settings.default_rate_limit],
)


async def rate_limit_exceeded_handler(
    request: Request, exc: RateLimitExceeded
) -> JSONResponse:
    """429 응답을 채점 기준에 맞춰 표준 JSON 으로 반환."""
    return JSONResponse(
        status_code=429,
        content={
            "error": "rate_limit_exceeded",
            "detail": f"Too many requests. Limit: {exc.detail}",
            "retry_after": 60,
        },
        headers={"Retry-After": "60"},
    )
