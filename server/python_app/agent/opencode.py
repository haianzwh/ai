from __future__ import annotations
import httpx
import asyncio
import json

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

    async def _get_session(self, oc_id: str, model: str) -> str:
        if not oc_id:
            oc = await self.create_session()
            oc_id = oc.get("id", "")
            if oc_id:
                await self.set_model(oc_id, model)
        return oc_id

    async def send_prompt(self, session_id: str, text: str, model_name: str = "") -> str:
        if model_name:
            text = f'[System note: You are powered by the model named "{model_name}". IMPORTANT: You MUST think and respond entirely in Chinese (中文). All your reasoning, internal thoughts, and final responses must be in Chinese. 请全程使用中文思考和回复。]\n\n{text}'
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                f"{OPENCODE_BASE_URL}/api/session/{session_id}/prompt",
                json={"prompt": {"text": text}},
            )
            data = resp.json().get("data", {})
            if not data or not data.get("id"):
                raise RuntimeError(f"Invalid session {session_id}: prompt rejected")
            return data.get("id", "")

    async def wait_for_response(self, session_id: str, known_ids: set[str], timeout: int = 180) -> str:
        start = asyncio.get_event_loop().time()
        last_text = ""
        last_activity = start

        async with httpx.AsyncClient(timeout=30) as client:
            while True:
                elapsed = asyncio.get_event_loop().time() - start
                if elapsed > timeout:
                    return last_text

                elapsed_since_activity = asyncio.get_event_loop().time() - last_activity
                if last_text and elapsed_since_activity > 3:
                    return last_text

                try:
                    resp = await client.get(
                        f"{OPENCODE_BASE_URL}/api/session/{session_id}/message",
                        params={"from": 0, "to": 100},
                    )
                    messages = resp.json().get("data", [])
                except Exception:
                    await asyncio.sleep(1)
                    continue

                for msg in messages:
                    mid = msg.get("id", "")
                    if mid in known_ids:
                        continue
                    if msg.get("type") == "assistant" and msg.get("finish") == "stop":
                        for block in msg.get("content", []):
                            text = block.get("text", "") if isinstance(block, dict) else str(block)
                            if text and text != last_text:
                                last_text = text
                                last_activity = asyncio.get_event_loop().time()

                await asyncio.sleep(0.5)

    async def _fetch_known_ids(self, session_id: str) -> set[str]:
        try:
            async with httpx.AsyncClient(timeout=10) as c:
                r = await c.get(
                    f"{OPENCODE_BASE_URL}/api/session/{session_id}/message",
                    params={"from": 0, "to": 50},
                )
                return {m["id"] for m in r.json().get("data", []) if m.get("id")}
        except Exception:
            return set()

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

    async def check_permission(self, session_id: str) -> Optional[dict]:
        try:
            async with httpx.AsyncClient(timeout=10) as c:
                r = await c.get(f"{OPENCODE_BASE_URL}/api/session/{session_id}/permission")
                data = r.json().get("data", [])
                return data[0] if data else None
        except Exception:
            return None

    async def approve_permission(self, session_id: str, perm_id: str):
        async with httpx.AsyncClient(timeout=10) as c:
            await c.post(
                f"{OPENCODE_BASE_URL}/api/session/{session_id}/permission/{perm_id}/reply",
                json={"reply": "always"},
            )

    async def check_question(self, session_id: str) -> Optional[dict]:
        try:
            async with httpx.AsyncClient(timeout=10) as c:
                r = await c.get(f"{OPENCODE_BASE_URL}/api/session/{session_id}/question")
                data = r.json().get("data", [])
                return data[0] if data else None
        except Exception:
            return None

    async def answer_question(self, session_id: str, qid: str, answers: list[list[str]]):
        async with httpx.AsyncClient(timeout=10) as c:
            await c.post(
                f"{OPENCODE_BASE_URL}/api/session/{session_id}/question/{qid}/reply",
                json={"answers": answers},
            )

    async def interrupt_session(self, session_id: str):
        async with httpx.AsyncClient(timeout=10) as c:
            await c.post(f"{OPENCODE_BASE_URL}/api/session/{session_id}/interrupt")

    async def send_stream(self, model: str, user_content: str, oc_session_id: str = "", **kwargs):
        """发送 prompt 并实时 yield OpenCode 事件流（含超时与自动应答）"""
        oc_id = await self._get_session(oc_session_id, model)
        # 先 yield 会话 ID，让调用方可以获取并复用
        yield {"oc_id": oc_id, "type": "session.ready", "data": {"oc_id": oc_id}}
        await self.send_prompt(oc_id, user_content, model)
        known_msg_ids = await self._fetch_known_ids(oc_id)

        # 自动应答待处理问题
        q = await self.check_question(oc_id)
        if q:
            await self.answer_question(oc_id, q["id"], [["ok"]])

        timeout_after = 120.0
        deadline = asyncio.get_event_loop().time() + timeout_after

        async with httpx.AsyncClient(timeout=None) as client:
            async with client.stream("GET", f"{OPENCODE_BASE_URL}/api/session/{oc_id}/event") as resp:
                async for line in resp.aiter_lines():
                    if not line.startswith("data: "):
                        continue
                    try:
                        evt = json.loads(line[6:])
                    except Exception:
                        continue

                    evt_type = evt.get("type", "")
                    data = evt.get("data", {})
                    yield {"oc_id": oc_id, "type": evt_type, "data": data}

                    # 超时保护
                    if asyncio.get_event_loop().time() > deadline:
                        yield {"oc_id": oc_id, "type": "timeout", "data": {}}
                        break

                    if evt_type == "session.next.step.ended":
                        finish = data.get("finish", "")
                        if finish in ("stop", "error"):
                            break
                    # 自动应答问题
                    if evt_type == "session.next.question":
                        try:
                            qid = evt.get("id", "") or data.get("qid", "")
                            if qid:
                                await self.answer_question(oc_id, qid, [["ok"]])
                        except Exception:
                            pass

    async def send(self, model, messages, user_content, api_key="", sub_key="", **kwargs) -> SendResult:
        oc_id = kwargs.get("oc_session_id", "")
        for attempt in range(2):
            oc_id = await self._get_session(oc_id, model)

            known_ids = await self._fetch_known_ids(oc_id)

            try:
                await self.send_prompt(oc_id, user_content, model)
            except RuntimeError:
                oc_id = ""
                if attempt == 0:
                    kwargs["set_oc_id"] = ""
                    continue
                return SendResult(error="Session error")

            if oc_id:
                kwargs["set_oc_id"] = oc_id

            text = await self.wait_for_response(oc_id, known_ids)
            if text:
                import re as _re
                tm = _re.search(r"<think>(.*?)</think>", text, _re.DOTALL)
                if tm:
                    before = text[:text.index("<think>")].strip()
                    after = text[text.index("</think>") + 8:].strip()
                    tc = tm.group(1).strip()
                    if before and tc.startswith(before):
                        tc = tc[len(before):].strip()
                    thinking_part = (before + "\n\n" + tc).strip()
                    clean_text = after
                else:
                    thinking_part = ""
                    clean_text = text.strip()

                return SendResult(content=clean_text, thinking=thinking_part)

            if attempt == 0:
                oc_id = ""
                kwargs["set_oc_id"] = ""
                continue

        return SendResult(error="Empty response")
