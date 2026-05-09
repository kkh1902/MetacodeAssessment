"""환경 변수 로딩 및 전역 설정."""

from __future__ import annotations

import os
from functools import lru_cache

from dotenv import load_dotenv

load_dotenv()


class Settings:
    """프로세스 전역 설정 — 환경 변수에서 읽어 들인다."""

    def __init__(self) -> None:
        self.gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
        self.api_key_hash: str = os.getenv("API_KEY_HASH", "")
        self.dev_mode: bool = os.getenv("DEV_MODE", "false").lower() == "true"
        self.redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.cors_allow_origins: list[str] = [
            origin.strip()
            for origin in os.getenv(
                "CORS_ALLOW_ORIGINS", "http://localhost:3000"
            ).split(",")
            if origin.strip()
        ]
        self.default_rate_limit: str = os.getenv("DEFAULT_RATE_LIMIT", "10/minute")
        self.chat_rate_limit: str = os.getenv("CHAT_RATE_LIMIT", "5/minute")
        self.llm_model: str = "gemini/gemini-3.1-flash-lite-preview"
        self.embedding_model: str = "gemini-embedding-001"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
