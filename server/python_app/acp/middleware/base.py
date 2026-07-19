from __future__ import annotations
import abc
from typing import Any


class Plugin(abc.ABC):
    """ACP 中间件插件基类"""

    name: str = "base"
    priority: int = 100

    async def on_request(self, method: str, params: dict) -> dict | None:
        return None

    async def on_response(self, method: str, params: dict, result: Any) -> Any:
        return result

    async def setup(self):
        pass

    async def teardown(self):
        pass
