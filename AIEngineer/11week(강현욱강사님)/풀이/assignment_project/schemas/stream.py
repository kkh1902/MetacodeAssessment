"""SSE 4종 이벤트 Pydantic 스키마."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class StatusEvent(BaseModel):
    """파이프라인 단계 상태 알림 (예: searching, generating)."""

    type: Literal["status"] = "status"
    stage: str = Field(..., description="searching | generating | done")
    message: str = ""


class TokenEvent(BaseModel):
    """LLM 토큰 단위 스트리밍 청크."""

    type: Literal["token"] = "token"
    content: str


class SourceEvent(BaseModel):
    """검색에 사용된 문서 출처 정보."""

    type: Literal["source"] = "source"
    title: str
    score: float = 0.0
    snippet: str = ""


class DoneEvent(BaseModel):
    """스트림 종료 마커 — 토큰/소스 수집 완료를 알린다."""

    type: Literal["done"] = "done"
    total_tokens: int = 0
    latency_ms: float = 0.0
