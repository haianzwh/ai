from __future__ import annotations
import httpx
import asyncio

from .base import Provider, ProviderModel, SendResult
from ..config import OPENCODE_BASE_URL

DEFAULT_MODEL = "deepseek-v4-flash-free"


class OpenCodeProvider(Provider):
    """通过 opencode web API 调用模型的 Provider"""

    @property
    def provider_id(self) -> str:
        return "opencode"

    async def create_session(self) -> dict:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(f"{OPENCODE_BASE_URL}/api/session", json={})
            return resp.json().get("data", {})

    async def set_model(self, session_id: str, model: str = DEFAULT_MODEL):
        async with httpx.AsyncClient(timeout=10) as client:
            await client.post(
                f"{OPENCODE_BASE_URL}/api/session/{session_id}/model",
                json={"model": {"id": model, "providerID": "opencode"}},
            )

    async def send_prompt(self, session_id: str, text: str, model_name: str = "") -> str:
        if model_name:
            text = f'[System note: You are powered by the model named "{model_name}".]\n\n{text}'
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                f"{OPENCODE_BASE_URL}/api/session/{session_id}/prompt",
                json={"prompt": {"text": text}},
            )
            return resp.json().get("data", {}).get("id", "")

    async def poll_response(self, session_id: str, existing_ids: set[str] = None, timeout: int = 20):
        start = asyncio.get_event_loop().time()
        seen: set[str] = set(existing_ids) if existing_ids else set()
        full_text = ""

        async with httpx.AsyncClient(timeout=30) as client:
            while True:
                elapsed = asyncio.get_event_loop().time() - start
                if elapsed > timeout:
                    yield {"content": full_text, "done": True}
                    return

                try:
                    resp = await client.get(
                        f"{OPENCODE_BASE_URL}/api/session/{session_id}/message",
                        params={"from": 0, "to": 100},
                    )
                    messages = resp.json().get("data", [])
                except Exception:
                    await asyncio.sleep(1)
                    continue

                new_messages = [m for m in messages if m.get("id") not in seen]
                for msg in new_messages:
                    mid = msg.get("id", "")
                    mtype = msg.get("type", "")
                    if mtype == "user":
                        continue
                    if mtype == "assistant":
                        if msg.get("finish") == "error":
                            continue
                        has_content = False
                        for block in msg.get("content", []):
                            text = block.get("text", "") if isinstance(block, dict) else str(block)
                            if text:
                                has_content = True
                                if text != full_text:
                                    delta = text[len(full_text):] if text.startswith(full_text) else text
                                    full_text = text
                                    yield {"content": delta, "done": False}
                        if not has_content:
                            continue
                        if msg.get("finish") == "stop":
                            seen.add(mid)
                            yield {"content": "", "done": True}
                            return
                        seen.discard(mid)

                await asyncio.sleep(0.5)

    async def fetch_models(self) -> list[ProviderModel]:
        models = []
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(f"{OPENCODE_BASE_URL}/api/model")
                data = resp.json()
                raw = [
                    {"id": m["id"], "name": m.get("name", m["id"]), "status": m.get("status", "")}
                    for m in data.get("data", [])
                ]
                free_active = [m for m in raw if "free" in m["id"] and m["status"] == "active"]
                free_rest = [m for m in raw if "free" in m["id"] and m["status"] != "active"]
                other = [m for m in raw if "free" not in m["id"]]
                for m in free_active + free_rest + other:
                    models.append(ProviderModel(id=m["id"], name=m["name"], provider_id="opencode"))
        except Exception:
            pass
        return models

    async def send(self, model, messages, user_content, api_key="", sub_key="", **kwargs) -> SendResult:
        oc_id = kwargs.get("oc_session_id", "")
        if not oc_id:
            oc = await self.create_session()
            oc_id = oc.get("id", "")
            if oc_id:
                await self.set_model(oc_id, model)
            kwargs["set_oc_id"] = oc_id  # 让调用方保存

        # 发送 prompt
        import httpx as _hx
        try:
            r = _hx.get(f"{OPENCODE_BASE_URL}/api/session/{oc_id}/message", params={"from": 0, "to": 50}, timeout=5)
            existing_ids = {m["id"] for m in r.json().get("data", []) if m.get("id")}
        except:
            existing_ids = set()

        await self.send_prompt(oc_id, user_content, model)

        full_text = ""
        for retry in range(2):
            try:
                async for chunk in self.poll_response(oc_id, existing_ids=existing_ids, timeout=120):
                    if chunk.get("done"):
                        break
                    if chunk.get("content"):
                        full_text += chunk["content"]
                break
            except Exception as e:
                if "TooLarge" in str(e) or "max bytes" in str(e):
                    oc = await self.create_session()
                    oc_id = oc.get("id", "")
                    if oc_id:
                        await self.set_model(oc_id, model)
                    kwargs["set_oc_id"] = oc_id
                    await self.send_prompt(oc_id, user_content, model)
                    async for chunk in self.poll_response(oc_id, timeout=120):
                        if chunk.get("done"):
                            break
                        if chunk.get("content"):
                            full_text += chunk["content"]
                    break
                else:
                    return SendResult(error=str(e))

        if not full_text:
            return SendResult(error="Empty response")

        import re as _re
        tm = _re.search(r"<think>(.*?)</think>", full_text, _re.DOTALL)
        if tm:
            before = full_text[:full_text.index("<think>")].strip()
            after = full_text[full_text.index("</think>") + 8:].strip()
            tc = tm.group(1).strip()
            if before and tc.startswith(before):
                tc = tc[len(before):].strip()
            thinking_part = (before + "\n\n" + tc).strip()
            clean_text = after
        else:
            thinking_part = ""
            clean_text = full_text.strip()

        return SendResult(content=clean_text, thinking=thinking_part)
