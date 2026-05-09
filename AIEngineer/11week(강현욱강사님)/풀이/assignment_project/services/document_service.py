"""파일 업로드 → 파싱 → 청킹 → 임베딩 → 벡터 DB 저장 파이프라인."""

from __future__ import annotations

import re
import uuid
from typing import Any

from fastapi import UploadFile

from rag.embedding_service import EmbeddingService
from rag.vector_db import VectorDB


def _split_into_chunks(text: str, max_chars: int = 800, overlap: int = 100) -> list[str]:
    """문단/문장 단위 단순 청킹 — 800자 ± overlap."""
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []
    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = min(start + max_chars, len(text))
        chunks.append(text[start:end])
        if end == len(text):
            break
        start = end - overlap
    return chunks


async def index_document(file: UploadFile) -> dict[str, Any]:
    """업로드된 텍스트 파일을 인덱싱하고 결과 메타를 반환한다."""
    raw = await file.read()
    text = raw.decode("utf-8", errors="ignore")
    chunks = _split_into_chunks(text)

    if not chunks:
        return {"filename": file.filename, "chunks": 0, "status": "empty"}

    embedder = EmbeddingService()
    vector_db = VectorDB()

    embeddings = embedder.embed_batch(chunks)
    ids = [f"{file.filename}-{uuid.uuid4().hex[:8]}-{i}" for i in range(len(chunks))]
    metadatas = [
        {"source": file.filename or "unknown", "chunk_index": i}
        for i in range(len(chunks))
    ]

    vector_db.add(ids=ids, embeddings=embeddings, documents=chunks, metadatas=metadatas)

    return {
        "filename": file.filename,
        "chunks": len(chunks),
        "status": "indexed",
    }
