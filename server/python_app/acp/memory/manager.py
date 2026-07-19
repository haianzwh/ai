from __future__ import annotations
import abc
import time
import json
from typing import Any
from collections import OrderedDict


class BaseMemory(abc.ABC):
    @abc.abstractmethod
    async def add(self, key: str, value: Any, ttl: int = 0):
        ...

    @abc.abstractmethod
    async def get(self, key: str) -> Any:
        ...

    @abc.abstractmethod
    async def delete(self, key: str):
        ...

    @abc.abstractmethod
    async def clear(self):
        ...

    @abc.abstractmethod
    async def list_keys(self, prefix: str = "") -> list[str]:
        ...


class ShortTermMemory(BaseMemory):
    """短期记忆 — LRU + TTL 过期"""

    def __init__(self, max_size: int = 200, default_ttl: int = 3600):
        self._store: OrderedDict[str, tuple[Any, float]] = OrderedDict()
        self._max = max_size
        self._default_ttl = default_ttl

    async def add(self, key: str, value: Any, ttl: int = 0):
        self._evict_expired()
        ttl = ttl or self._default_ttl
        if key in self._store:
            self._store.move_to_end(key)
        elif len(self._store) >= self._max:
            self._store.popitem(last=False)
        self._store[key] = (value, time.time() + ttl)

    async def get(self, key: str) -> Any | None:
        self._evict_expired()
        entry = self._store.get(key)
        if entry:
            self._store.move_to_end(key)
            return entry[0]
        return None

    async def delete(self, key: str):
        self._store.pop(key, None)

    async def clear(self):
        self._store.clear()

    async def list_keys(self, prefix: str = "") -> list[str]:
        self._evict_expired()
        if prefix:
            return [k for k in self._store if k.startswith(prefix)]
        return list(self._store.keys())

    async def get_all_by_prefix(self, prefix: str) -> dict[str, Any]:
        self._evict_expired()
        return {k: v[0] for k, v in self._store.items() if k.startswith(prefix)}

    def _evict_expired(self):
        now = time.time()
        expired = [k for k, v in self._store.items() if v[1] < now]
        for k in expired:
            del self._store[k]


class LongTermMemory(BaseMemory):
    """长期记忆 — JSON 文件持久化 + TTL"""

    def __init__(self, storage_path: str = "/tmp/acp_ltm.json"):
        self._path = storage_path
        self._store: dict[str, tuple[Any, float]] = {}
        self._load()

    async def add(self, key: str, value: Any, ttl: int = 0):
        exp = time.time() + (ttl or 86400 * 30)
        self._store[key] = (value, exp)
        self._flush()

    async def get(self, key: str) -> Any | None:
        entry = self._store.get(key)
        if entry and entry[1] > time.time():
            return entry[0]
        if entry:
            del self._store[key]
            self._flush()
        return None

    async def delete(self, key: str):
        self._store.pop(key, None)
        self._flush()

    async def clear(self):
        self._store.clear()
        self._flush()

    async def list_keys(self, prefix: str = "") -> list[str]:
        if prefix:
            return [k for k in self._store if k.startswith(prefix) and self._store[k][1] > time.time()]
        return [k for k, v in self._store.items() if v[1] > time.time()]

    async def get_all_by_prefix(self, prefix: str) -> dict[str, Any]:
        return {k: v[0] for k, v in self._store.items()
                if k.startswith(prefix) and v[1] > time.time()}

    def _load(self):
        try:
            with open(self._path) as f:
                raw = json.load(f)
                self._store = {k: (v["val"], v["exp"]) for k, v in raw.items()}
        except:
            self._store = {}

    def _flush(self):
        raw = {k: {"val": v[0], "exp": v[1]} for k, v in self._store.items()}
        with open(self._path, "w") as f:
            json.dump(raw, f, ensure_ascii=False)


class WorkingMemory(BaseMemory):
    """工作记忆 — 单请求生命周期"""

    def __init__(self):
        self._store: dict[str, Any] = {}

    async def add(self, key: str, value: Any, ttl: int = 0):
        self._store[key] = value

    async def get(self, key: str) -> Any:
        return self._store.get(key)

    async def delete(self, key: str):
        self._store.pop(key, None)

    async def clear(self):
        self._store.clear()

    async def list_keys(self, prefix: str = "") -> list[str]:
        if prefix:
            return [k for k in self._store if k.startswith(prefix)]
        return list(self._store.keys())

    async def get_all_by_prefix(self, prefix: str) -> dict[str, Any]:
        return {k: v for k, v in self._store.items() if k.startswith(prefix)}


class MemoryManager:
    """统一记忆管理器 — 三层存储 + 命名空间隔离"""

    def __init__(self):
        self.short_term = ShortTermMemory()
        self.long_term = LongTermMemory()
        self.working = WorkingMemory()

    async def remember(self, key: str, value: Any, scope: str = "working", ttl: int = 0):
        mem = getattr(self, scope, self.working)
        await mem.add(key, value, ttl)

    async def recall(self, key: str, scope: str = "working") -> Any:
        mem = getattr(self, scope, self.working)
        return await mem.get(key)

    async def forget(self, key: str, scope: str = "working"):
        mem = getattr(self, scope, self.working)
        await mem.delete(key)

    async def list_user_memories(self, user_id: str, scope: str = "short_term") -> list[dict]:
        mem = getattr(self, scope, self.short_term)
        prefix = f"user:{user_id}:"
        keys = await mem.list_keys(prefix)
        result = []
        for k in keys:
            val = await mem.get(k)
            label = k[len(prefix):]
            result.append({"key": label, "value": val, "scope": scope})
        return result

    async def clear_user_memories(self, user_id: str, scope: str = "short_term"):
        mem = getattr(self, scope, self.short_term)
        prefix = f"user:{user_id}:"
        keys = await mem.list_keys(prefix)
        for k in keys:
            await mem.delete(k)

    # ── 全局记忆 ────────────────────────────────────────────

    async def set_global(self, key: str, value: Any, ttl: int = 0):
        """设置全局记忆（所有用户共享）"""
        await self.long_term.add(f"global:{key}", value, ttl or 86400 * 30)

    async def get_global(self, key: str) -> Any | None:
        return await self.long_term.get(f"global:{key}")

    async def delete_global(self, key: str):
        await self.long_term.delete(f"global:{key}")

    async def list_global(self) -> list[dict]:
        keys = await self.long_term.list_keys("global:")
        result = []
        for k in keys:
            val = await self.long_term.get(k)
            result.append({"key": k[7:], "value": val})
        return result

    async def clear_global(self):
        keys = await self.long_term.list_keys("global:")
        for k in keys:
            await self.long_term.delete(k)
