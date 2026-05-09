"""Gemini gemini-embedding-001 임베딩 서비스 (google-generativeai SDK)."""

from __future__ import annotations

import os
from typing import Sequence

import google.generativeai as genai

from core.config import get_settings


class EmbeddingService:
    """gemini-embedding-001 모델로 텍스트 임베딩을 생성한다."""

    def __init__(self, model: str | None = None) -> None:
        settings = get_settings()
        api_key = settings.gemini_api_key or os.getenv("GEMINI_API_KEY", "")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY 환경 변수가 설정되어 있지 않습니다.")
        genai.configure(api_key=api_key)
        self.model = model or settings.embedding_model

    def embed(self, text: str, *, task_type: str = "retrieval_document") -> list[float]:
        result = genai.embed_content(
            model=self.model,
            content=text,
            task_type=task_type,
        )
        return list(result["embedding"])

    def embed_batch(
        self, texts: Sequence[str], *, task_type: str = "retrieval_document"
    ) -> list[list[float]]:
        return [self.embed(t, task_type=task_type) for t in texts]

    def embed_query(self, query: str) -> list[float]:
        return self.embed(query, task_type="retrieval_query")
