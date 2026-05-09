"""API Key 인증 의존성 — DEV_MODE=true 일 때 스킵."""

from __future__ import annotations

from fastapi import Header, HTTPException, status

from core.config import get_settings
from utils.api_key import verify_api_key


async def require_api_key(
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
) -> str:
    """X-API-Key 헤더를 검증하고 인증된 키를 반환한다.

    DEV_MODE=true 인 경우 검증을 스킵하여 'dev' 식별자를 반환.
    """
    settings = get_settings()
    if settings.dev_mode:
        return "dev"

    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="X-API-Key header is required",
        )
    if not settings.api_key_hash:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="API_KEY_HASH not configured",
        )
    if not verify_api_key(x_api_key, settings.api_key_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )
    return x_api_key
