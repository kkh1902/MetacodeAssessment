"""RAG 스트리밍 오케스트레이션 — SSE 4종 이벤트를 yield 한다."""

from __future__ import annotations

import asyncio
import time
from typing import AsyncGenerator

from core.sse import format_sse
from schemas.stream import DoneEvent, SourceEvent, StatusEvent, TokenEvent


async def stream_search_and_generate(
    query: str,
    *,
    use_real_pipeline: bool = False,
) -> AsyncGenerator[str, None]:
    """검색 → 토큰 스트림 → 출처 → 완료 순서로 SSE 이벤트를 흘려보낸다.

    use_real_pipeline=True 면 RAGPipeline을 사용하고,
    False (기본) 면 mock 스트림으로 동작 — Q4 단독 테스트용.
    """
    t0 = time.perf_counter()

    # 1) status: 검색 시작
    yield format_sse(
        "status",
        StatusEvent(stage="searching", message=f"query='{query}' 검색 시작").model_dump(),
    )

    if use_real_pipeline:
        # Q9 통합 경로: 실제 RAG 파이프라인 호출
        from rag.rag_pipeline import RAGPipeline

        pipeline = RAGPipeline()
        result = await asyncio.to_thread(pipeline.query, query)

        yield format_sse(
            "status",
            StatusEvent(stage="generating", message="LLM 답변 생성 중").model_dump(),
        )

        for token in result["answer"].split():
            yield format_sse("token", TokenEvent(content=token + " ").model_dump())
            await asyncio.sleep(0.01)

        for source in result["sources"]:
            yield format_sse(
                "source",
                SourceEvent(
                    title=source.get("title", "unknown"),
                    score=float(source.get("score", 0.0)),
                    snippet=source.get("snippet", "")[:120],
                ).model_dump(),
            )

        latency_ms = (time.perf_counter() - t0) * 1000
        yield format_sse(
            "done",
            DoneEvent(
                total_tokens=len(result["answer"].split()),
                latency_ms=latency_ms,
            ).model_dump(),
        )
        return

    # 2) mock 토큰 스트림 — Q4 단독 검증용
    yield format_sse(
        "status",
        StatusEvent(stage="generating", message="LLM 답변 생성 중").model_dump(),
    )

    mock_answer = "Hello world this is a mock RAG response"
    tokens = mock_answer.split()
    for token in tokens:
        yield format_sse("token", TokenEvent(content=token + " ").model_dump())
        await asyncio.sleep(0.05)

    # 3) source 이벤트 (mock 문서 1건)
    yield format_sse(
        "source",
        SourceEvent(
            title="mock_document.txt",
            score=0.92,
            snippet="이 문서는 SSE 스트리밍 테스트용 mock 데이터입니다.",
        ).model_dump(),
    )

    # 4) done 이벤트
    latency_ms = (time.perf_counter() - t0) * 1000
    yield format_sse(
        "done",
        DoneEvent(total_tokens=len(tokens), latency_ms=latency_ms).model_dump(),
    )
