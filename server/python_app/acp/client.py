from __future__ import annotations
from typing import Optional
from .protocol import ACPRequest, ACPResponse, ACPMethod
from .server import ACPServer


class ACPClient:
    """ACP 客户端 — Process 层通过它调用 ACP Server"""

    def __init__(self, server: ACPServer = None):
        self._server = server
        self._counter = 0

    @property
    def server(self) -> Optional[ACPServer]:
        return self._server

    @server.setter
    def server(self, s: ACPServer):
        self._server = s

    async def call(self, method: str, params: dict) -> dict:
        self._counter += 1
        req = ACPRequest(method=method, params=params, id=self._counter)
        if not self._server:
            return {"success": False, "error": "ACP Server not initialized"}
        resp: ACPResponse = await self._server.route_request(req)
        if resp.error:
            return {"success": False, "error": resp.error.get("message", "ACP error")}
        result = resp.result
        if isinstance(result, dict):
            return result
        return {"success": True, "result": result}
