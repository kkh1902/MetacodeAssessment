"""API Key 생성/해싱/검증 유틸 (Q6 Colab 구현을 그대로 이식)."""

from __future__ import annotations

import hashlib
import hmac
import secrets


def generate_api_key() -> str:
    """secrets.token_urlsafe(32)로 평문 API Key 생성."""
    return secrets.token_urlsafe(32)


def hash_api_key(plain_key: str) -> str:
    """SHA-256 해싱 → 64자 hex digest 반환."""
    return hashlib.sha256(plain_key.encode("utf-8")).hexdigest()


def verify_api_key(plain_key: str, stored_hash: str) -> bool:
    """타이밍 공격 방어를 위해 hmac.compare_digest 로 비교."""
    return hmac.compare_digest(hash_api_key(plain_key), stored_hash)
