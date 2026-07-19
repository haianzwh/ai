from __future__ import annotations
from .base import Plugin


class ResponseFormatterPlugin(Plugin):
    """统一响应格式 — 确保所有响应都包含 success 字段"""
    name = "response_formatter"
    priority = 200

    async def on_response(self, method: str, params: dict, result):
        if isinstance(result, dict) and "success" not in result:
            result["success"] = not result.get("error")
        return result
