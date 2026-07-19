from __future__ import annotations
from .base import Plugin


class AuthMiddleware(Plugin):
    """API Key 验证透传中间件"""
    name = "auth"
    priority = 15

    async def on_request(self, method: str, params: dict) -> dict | None:
        api_key = params.get("api_key", "")
        if api_key and not api_key.startswith("sk-"):
            return {"error": "Invalid API key format"}
        return None
