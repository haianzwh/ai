from __future__ import annotations
import time
from collections import defaultdict
from .base import Plugin


class RateLimitMiddleware(Plugin):
    """简单的速率限制中间件"""
    name = "rate_limit"
    priority = 20

    def __init__(self, max_per_minute: int = 60):
        super().__init__()
        self._max = max_per_minute
        self._buckets: dict[str, list[float]] = defaultdict(list)

    async def on_request(self, method: str, params: dict) -> dict | None:
        provider = params.get("provider", "default")
        now = time.time()
        bucket = self._buckets[provider]
        bucket[:] = [t for t in bucket if now - t < 60]
        bucket.append(now)
        if len(bucket) > self._max:
            return {"error": "Rate limit exceeded"}
        return None
