"""ChromaDB Ephemeral (인메모리) 벡터 스토어 래퍼."""

from __future__ import annotations

from typing import Any

import chromadb


_DEFAULT_COLLECTION = "assignment_rag"


class VectorDB:
    """프로세스 수명 동안만 유지되는 인메모리 ChromaDB."""

    _client: chromadb.api.ClientAPI | None = None

    def __init__(self, collection_name: str = _DEFAULT_COLLECTION) -> None:
        if VectorDB._client is None:
            VectorDB._client = chromadb.EphemeralClient()
        self.collection = VectorDB._client.get_or_create_collection(name=collection_name)

    def add(
        self,
        *,
        ids: list[str],
        embeddings: list[list[float]],
        documents: list[str],
        metadatas: list[dict[str, Any]],
    ) -> None:
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
        )

    def query(
        self, *, query_embedding: list[float], top_k: int = 3
    ) -> list[dict[str, Any]]:
        result = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
        )
        docs = (result.get("documents") or [[]])[0]
        metas = (result.get("metadatas") or [[]])[0]
        dists = (result.get("distances") or [[]])[0]

        hits: list[dict[str, Any]] = []
        for doc, meta, dist in zip(docs, metas, dists):
            hits.append(
                {
                    "title": (meta or {}).get("source", "unknown"),
                    "snippet": doc,
                    "score": float(1.0 - dist) if dist is not None else 0.0,
                    "metadata": meta or {},
                }
            )
        return hits

    def count(self) -> int:
        return int(self.collection.count())
