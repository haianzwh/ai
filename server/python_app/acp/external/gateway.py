from __future__ import annotations
import asyncio
from typing import Optional
from ..protocol import ACPResponse, ACPErrorCode
from .hermes_adapter import HermesAdapter


class ExternalACPGateway:
    """管理所有外部 ACP Agent 的连接与调用"""

    def __init__(self):
        self._adapters: dict[str, HermesAdapter] = {}
        self._process_manager = None
        self._initialized = False

    async def initialize(self, providers_config: dict = None):
        if not providers_config:
            self._initialized = True
            return
        for pid, cfg in providers_config.items():
            rtype = cfg.get("type", "internal")
            if rtype == "external":
                command = cfg.get("command", [])
                if command:
                    adapter = HermesAdapter(command=command)
                    self._adapters[pid] = adapter
                    await adapter.start()
                    print(f"[ACP] 外部 Agent 已连接: {pid}")
        self._initialized = True

    async def call(self, provider_name: str, method: str, params: dict) -> ACPResponse:
        adapter = self._adapters.get(provider_name)
        if not adapter:
            return ACPResponse.fail(ACPErrorCode.PROVIDER_ERROR, f"Unknown external provider: {provider_name}")
        try:
            result = await adapter.call(method, params)
            return ACPResponse.success(result)
        except Exception as e:
            return ACPResponse.fail(ACPErrorCode.INTERNAL_ERROR, str(e))

    async def shutdown(self):
        for name, adapter in self._adapters.items():
            try:
                await adapter.close()
            except Exception:
                pass
        self._adapters.clear()
        self._initialized = False
