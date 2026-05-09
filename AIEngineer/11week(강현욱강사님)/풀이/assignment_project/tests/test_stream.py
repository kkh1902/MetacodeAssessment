"""Q4 검증 — SSE 4종 이벤트(status / token / source / done) 모두 수신."""

from __future__ import annotations

import os

import httpx
import pytest

# DEV_MODE 강제 — 인증 스킵
os.environ.setdefault("DEV_MODE", "true")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")

from main import app  # noqa: E402  (env 세팅 후 import)


def _parse_event_types(raw: str) -> set[str]:
    types: set[str] = set()
    for line in raw.splitlines():
        if line.startswith("event:"):
            types.add(line.split(":", 1)[1].strip())
    return types


@pytest.mark.asyncio
async def test_stream_emits_four_event_types() -> None:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        async with client.stream(
            "POST",
            "/api/v1/chat/stream",
            json={"query": "What is RAG?"},
            headers={"X-API-Key": "dev"},
        ) as response:
            assert response.status_code == 200
            chunks: list[str] = []
            async for chunk in response.aiter_text():
                chunks.append(chunk)

    payload = "".join(chunks)
    print("\n=== SSE Stream ===")
    print(payload)
    print("==================")

    received = _parse_event_types(payload)
    expected = {"status", "token", "source", "done"}
    missing = expected - received
    assert not missing, f"Missing event types: {missing}\nReceived: {received}"
