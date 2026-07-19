from __future__ import annotations
import httpx


class MCPClient:
    """MCP 协议客户端 — 调用外部 MCP Server"""

    def __init__(self, server_url: str = ""):
        self.server_url = server_url
        self._session: httpx.AsyncClient = None

    async def connect(self):
        self._session = httpx.AsyncClient(timeout=300)

    async def call_tool(self, tool_name: str, arguments: dict = None) -> dict:
        if not self._session:
            await self.connect()
        payload = {"method": "tools/call", "params": {"name": tool_name, "arguments": arguments or {}}}
        resp = await self._session.post(f"{self.server_url}/mcp", json=payload)
        return resp.json()

    async def list_tools(self) -> list[dict]:
        if not self._session:
            await self.connect()
        resp = await self._session.post(f"{self.server_url}/mcp", json={"method": "tools/list"})
        return resp.json().get("tools", [])

    async def close(self):
        if self._session:
            await self._session.aclose()
