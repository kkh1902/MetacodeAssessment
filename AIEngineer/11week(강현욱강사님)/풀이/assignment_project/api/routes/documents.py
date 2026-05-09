"""POST /api/v1/documents — 파일 업로드·인덱싱 엔드포인트."""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, File, UploadFile

from api.middleware.auth import require_api_key
from services.document_service import index_document

router = APIRouter(prefix="/api/v1/documents", tags=["documents"])


@router.post("")
async def upload_document(
    file: Annotated[UploadFile, File(...)],
    _api_key: Annotated[str, Depends(require_api_key)],
) -> dict[str, Any]:
    """텍스트 파일 1건을 받아 청킹·임베딩·인덱싱한 결과를 반환한다."""
    return await index_document(file)
