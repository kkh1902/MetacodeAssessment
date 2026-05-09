"""POST /api/v1/chat/stream — SSE 스트리밍 엔드포인트."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field, field_validator

from api.middleware.auth import require_api_key
from api.middleware.rate_limit import limiter
from services.rag_service import stream_search_and_generate

router = APIRouter(prefix="/api/v1/chat", tags=["chat"])


class ChatStreamRequest(BaseModel):
    query: str = Field(..., description="사용자 질문")
    use_real_pipeline: bool = False

    @field_validator("query")
    @classmethod
    def _not_blank(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("query must not be empty")
        return v


@router.post("/stream")
@limiter.limit("5/minute")
async def chat_stream(
    request: Request,
    body: ChatStreamRequest,
    _api_key: Annotated[str, Depends(require_api_key)],
) -> StreamingResponse:
    """SSE 4종 이벤트(status / token / source / done) 를 흘려보낸다."""
    generator = stream_search_and_generate(
        body.query,
        use_real_pipeline=body.use_real_pipeline,
    )
    return StreamingResponse(
        generator,
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
