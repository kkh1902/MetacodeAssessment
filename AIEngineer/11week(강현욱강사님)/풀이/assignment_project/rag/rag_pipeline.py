"""검색 → 컨텍스트 조립 → LLM 호출까지 묶는 동기 파이프라인."""

from __future__ import annotations

import time
from typing import Any

import litellm

from core.config import get_settings
from rag.embedding_service import EmbeddingService
from rag.vector_db import VectorDB


_PROMPT_TEMPLATE = (
    "다음 컨텍스트를 참고해 사용자 질문에 답하라.\n"
    "컨텍스트에 없는 사실은 추론하지 말고 모른다고 답하라.\n\n"
    "[Context]\n{context}\n\n"
    "[Question] {question}\n[Answer]"
)


class RAGPipeline:
    """gemini-embedding-001 + ChromaDB + gemini-3.1-flash-lite-preview 통합."""

    def __init__(self, top_k: int = 3) -> None:
        self.embedder = EmbeddingService()
        self.vector_db = VectorDB()
        self.top_k = top_k
        self.model = get_settings().llm_model

    def query(self, question: str) -> dict[str, Any]:
        t0 = time.perf_counter()

        query_emb = self.embedder.embed_query(question)
        hits = self.vector_db.query(query_embedding=query_emb, top_k=self.top_k)

        if not hits:
            return {
                "answer": "관련된 문서를 찾지 못했습니다.",
                "sources": [],
                "latency_ms": (time.perf_counter() - t0) * 1000,
            }

        context = "\n---\n".join(h["snippet"] for h in hits)
        prompt = _PROMPT_TEMPLATE.format(context=context, question=question)

        response = litellm.completion(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )
        answer = response.choices[0].message.content

        latency_ms = (time.perf_counter() - t0) * 1000
        sources = [
            {"title": h["title"], "score": h["score"], "snippet": h["snippet"][:200]}
            for h in hits
        ]
        return {"answer": answer, "sources": sources, "latency_ms": latency_ms}
