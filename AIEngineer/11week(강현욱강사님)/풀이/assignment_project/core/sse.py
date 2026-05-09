"""Server-Sent Events 포맷팅 헬퍼."""

from __future__ import annotations

import json
from typing import Any


def format_sse(event: str, data: Any) -> str:
    """SSE 표준 포맷으로 한 이벤트 메시지를 직렬화한다.

    포맷:
        event: <event-name>\n
        data: <json>\n
        \n  (이벤트 종료)
    """
    payload = json.dumps(data, ensure_ascii=False)
    return f"event: {event}\ndata: {payload}\n\n"
