from __future__ import annotations
import httpx
import json
import re as _re

from .base import Provider, ProviderModel, SendResult


class DeepSeekProvider(Provider):
    """直接调用 DeepSeek API 的 Provider (GO / ZEN 两套 endpoint)"""

    def __init__(self, config: dict = None):
        self._config = config or {}
        self._default_key = (config or {}).get("default_key", "")

    @property
    def provider_id(self) -> str:
        return "deepseek"

    def _get_key(self, api_key: str = "") -> str:
        return api_key or self._default_key

    def _get_endpoint(self, sub_key: str = "") -> str:
        subs = self._config.get("sub_providers", {})
        if sub_key:
            ep = subs.get(sub_key, {}).get("endpoint", "")
            if ep:
                return ep
        return subs.get("go", {}).get("endpoint", "https://opencode.ai/zen/go/v1/chat/completions")

    async def fetch_models(self) -> list[ProviderModel]:
        models = []
        subs = self._config.get("sub_providers", {})
        for sk in subs:
            for m in self._config.get("models", []):
                models.append(ProviderModel(
                    id=m["id"],
                    name=m["name"],
                    provider_id=self.provider_id,
                    sub_key=sk,
                ))
        return models

    async def send(
        self,
        model: str,
        messages: list[dict],
        user_content: str,
        api_key: str = "",
        sub_key: str = "",
        **kwargs,
    ) -> SendResult:
        api_key = self._get_key(api_key)
        if not api_key:
            return SendResult(error="API key not configured")

        endpoint = self._get_endpoint(sub_key)

        api_messages = []
        for m in messages:
            role = "assistant" if m["role"] == "assistant" else "user"
            api_messages.append({"role": role, "content": m["content"]})
        api_messages.append({"role": "user", "content": user_content})

        async with httpx.AsyncClient(timeout=120) as client:
            try:
                resp = await client.post(
                    endpoint,
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": model,
                        "messages": api_messages,
                        "stream": False,
                        "max_tokens": 8192,
                    },
                )
                data = resp.json()
            except Exception as e:
                return SendResult(error=str(e))

        choice = data.get("choices", [{}])[0].get("message", {})
        full_text = choice.get("content", "")
        thinking_text = choice.get("reasoning_content", "")

        if not full_text:
            return SendResult(error="No content from API")

        if thinking_text:
            return SendResult(content=full_text.strip(), thinking=thinking_text.strip())

        tm = _re.search(r"<think>(.*?)</think>", full_text, _re.DOTALL)
        if tm:
            before = full_text[:full_text.index("<think>")].strip()
            after = full_text[full_text.index("</think>") + 8:].strip()
            tc = tm.group(1).strip()
            if before and tc.startswith(before):
                tc = tc[len(before):].strip()
            return SendResult(
                content=after,
                thinking=(before + "\n\n" + tc).strip(),
            )

        return SendResult(content=full_text.strip())

    async def send_stream(self, model: str, user_content: str, **kwargs):
        """流式调用 DeepSeek API，逐 chunk 产出事件"""
        api_key = self._get_key(kwargs.get("api_key", ""))
        if not api_key:
            yield {"oc_id": "", "type": "error", "data": {"message": "API key not configured"}}
            return
        sub_key = kwargs.get("sub_key", "")
        endpoint = self._get_endpoint(sub_key)

        # 加入系统提示：中文 + 输出格式
        system_msg = {"role": "system", "content": "你是一个AI编程助手。请全程使用中文思考和回复。回答要简洁、准确、完整。按步骤输出，每步完成后标记✅。"}
        api_messages = [system_msg, {"role": "user", "content": user_content}]

        async with httpx.AsyncClient(timeout=120) as client:
            async with client.stream(
                "POST",
                endpoint,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model,
                    "messages": api_messages,
                    "stream": True,
                    "max_tokens": 8192,
                },
            ) as resp:
                async for line in resp.aiter_lines():
                    if not line.startswith("data: "):
                        continue
                    chunk = line[6:]
                    if chunk == "[DONE]":
                        break
                    try:
                        data = json.loads(chunk)
                    except Exception:
                        continue
                    choices = data.get("choices", [])
                    if not choices:
                        continue
                    delta = choices[0].get("delta", {})
                    content = delta.get("content", "")
                    reasoning = delta.get("reasoning_content", "")
                    if reasoning:
                        yield {"oc_id": "", "type": "session.next.reasoning.ended", "data": {"text": reasoning}}
                    if content:
                        yield {"oc_id": "", "type": "session.next.text.ended", "data": {"text": content}}
                yield {"oc_id": "", "type": "session.next.step.ended", "data": {"finish": "stop"}}

    async def validate_key(self, api_key: str) -> bool:
        api_key = self._get_key(api_key)
        return api_key.startswith("sk-") if api_key else False
