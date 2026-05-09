"""Redis 기반 비동기 캐시 서비스."""

from __future__ import annotations

import hashlib
import json
from typing import Any

import redis.asyncio as redis_async


class CacheService:
    """질문/응답 캐시 — 동일 query 재호출 방지용."""

    def __init__(self, redis_url: str) -> None:
        self._client: redis_async.Redis = redis_async.from_url(
            redis_url, encoding="utf-8", decode_responses=True
        )

    @staticmethod
    def make_key(prefix: str, *args: Any) -> str:
        """접두어 + 인자 직렬화 해시로 결정적 키 생성."""
        raw = json.dumps(args, ensure_ascii=False, sort_keys=True, default=str)
        digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()
        return f"{prefix}:{digest}"

    async def get(self, key: str) -> Any | None:
        value = await self._client.get(key)
        if value is None:
            return None
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value

    async def set(self, key: str, value: Any, ttl_seconds: int = 300) -> None:
        payload = json.dumps(value, ensure_ascii=False, default=str)
        await self._client.set(key, payload, ex=ttl_seconds)

    async def delete(self, key: str) -> None:
        await self._client.delete(key)

    async def ping(self) -> bool:
        try:
            return bool(await self._client.ping())
        except Exception:
            return False

    async def close(self) -> None:
        await self._client.aclose()
