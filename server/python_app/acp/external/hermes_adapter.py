from __future__ import annotations
import asyncio
import httpx
from typing import Optional


class HermesAdapter:
    """适配外部 ACP Agent（如 hermes acp）"""

    def __init__(self, command: list = None, server_url: str = ""):
        self.command = command or []
        self.server_url = server_url or "http://localhost:8080"
        self._process: Optional[asyncio.subprocess.Process] = None
        self._session: Optional[httpx.AsyncClient] = None

    async def start(self) -> Optional[asyncio.subprocess.Process]:
        if self.command:
            self._process = await asyncio.create_subprocess_exec(
                *self.command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            await asyncio.sleep(1)
        self._session = httpx.AsyncClient(timeout=120)
        return self._process

    async def call(self, method: str, params: dict) -> dict:
        if not self._session:
            self._session = httpx.AsyncClient(timeout=120)
        payload = {"jsonrpc": "2.0", "method": method, "params": params, "id": 1}
        resp = await self._session.post(f"{self.server_url}/rpc", json=payload)
        data = resp.json()
        return data.get("result", {})

    async def close(self):
        if self._session:
            await self._session.aclose()
        if self._process:
            self._process.terminate()
            await self._process.wait()
