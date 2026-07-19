from __future__ import annotations
import time
import asyncio
from typing import Any


class ACPEvent:
    """ACP 事件定义"""
    def __init__(self, name: str, data: dict = None):
        self.name = name
        self.data = data or {}
        self.timestamp = time.time()


class EventEmitter:
    """事件发射器 — 发布/订阅模式"""

    def __init__(self):
        self._handlers: dict[str, list] = {}

    def on(self, event: str, handler):
        self._handlers.setdefault(event, []).append(handler)

    async def emit(self, event: ACPEvent):
        for handler in self._handlers.get(event.name, []):
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(event)
                else:
                    handler(event)
            except Exception as e:
                print(f"[Event] handler error: {e}")

    async def emit_sync(self, name: str, data: dict = None):
        await self.emit(ACPEvent(name, data))
