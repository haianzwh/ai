from __future__ import annotations
from .base import Plugin


class PluginRegistry:
    """插件注册中心 — 支持从 YAML 热加载"""

    def __init__(self):
        self._plugins: list[Plugin] = []

    def register(self, plugin: Plugin):
        self._plugins.append(plugin)
        self._plugins.sort(key=lambda p: p.priority)

    async def run_on_request(self, method: str, params: dict) -> dict | None:
        for p in self._plugins:
            result = await p.on_request(method, params)
            if result is not None:
                return result
        return None

    async def run_on_response(self, method: str, params: dict, result):
        r = result
        for p in self._plugins:
            r = await p.on_response(method, params, r)
        return r

    async def setup_all(self):
        for p in self._plugins:
            await p.setup()

    async def teardown_all(self):
        for p in self._plugins:
            await p.teardown()

    def list(self) -> list[dict]:
        return [{"name": p.name, "priority": p.priority} for p in self._plugins]


plugin_registry = PluginRegistry()
