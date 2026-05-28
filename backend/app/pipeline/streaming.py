"""Server-Sent Events helpers for streaming query responses."""

import json
from collections.abc import AsyncIterator
from typing import Any

from app.api.v1.schemas.query import QueryStreamEvent


async def sse_event_stream(events: AsyncIterator[QueryStreamEvent]) -> AsyncIterator[str]:
    async for event in events:
        payload: dict[str, Any] = event.model_dump(mode="json")
        yield f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"
    yield "data: [DONE]\n\n"
