from __future__ import annotations
from .base import Plugin


class PromptInjectorPlugin(Plugin):
    """在用户消息前注入系统提示词"""
    name = "prompt_injector"
    priority = 50

    def __init__(self, system_prompt: str = ""):
        self.system_prompt = system_prompt or "You are a helpful assistant."

    async def on_request(self, method: str, params: dict) -> dict | None:
        if method == "chat.completions":
            messages = params.get("messages", [])
            if messages and messages[0].get("role") != "system":
                messages.insert(0, {"role": "system", "content": self.system_prompt})
            params["messages"] = messages
        return None
