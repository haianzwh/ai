from __future__ import annotations
from .base import Plugin


class SensitiveFilterPlugin(Plugin):
    """敏感词过滤"""
    name = "sensitive_filter"
    priority = 30

    def __init__(self, words: list[str] = None):
        self._words: set[str] = set(w.lower() for w in (words or []))

    async def on_request(self, method: str, params: dict) -> dict | None:
        if method != "chat.completions":
            return None
        for msg in params.get("messages", []):
            content = msg.get("content", "")
            if isinstance(content, str):
                for w in self._words:
                    if w in content.lower():
                        return {"error": "Content blocked by sensitive filter"}
        return None
