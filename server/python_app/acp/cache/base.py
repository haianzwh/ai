from __future__ import annotations
from typing import Any
import time


class BaseCache:
    """缓存抽象基类"""

    async def get(self, key: str) -> Any | None:
        return None

    async def set(self, key: str, value: Any, ttl: int = 3600):
        pass

    async def delete(self, key: str):
        pass


class SimpleCache(BaseCache):
    """简单内存缓存"""
    def __init__(self):
        self._store: dict[str, tuple[Any, float]] = {}

    async def get(self, key: str) -> Any | None:
        entry = self._store.get(key)
        if entry:
            value, exp = entry
            if time.time() < exp:
                return value
            del self._store[key]
        return None

    async def set(self, key: str, value: Any, ttl: int = 3600):
        self._store[key] = (value, time.time() + ttl)

    async def delete(self, key: str):
        self._store.pop(key, None)


class PromptCache(SimpleCache):
    """Prompt 缓存"""


class EmbeddingCache(SimpleCache):
    """Embedding 缓存"""


class ResultCache(SimpleCache):
    """模型响应缓存"""
