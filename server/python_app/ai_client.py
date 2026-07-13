"""
=============================================================================
  AI 客户端 — 通过 opencode web API 调用模型
=============================================================================
"""
import httpx
import asyncio
from typing import AsyncGenerator

OPENCODE_URL = "http://localhost:4096"
DEFAULT_MODEL = "deepseek-v4-flash-free"


async def create_opencode_session(model: str = DEFAULT_MODEL) -> dict:
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{OPENCODE_URL}/api/session", json={})
        session = resp.json().get("data", {})
        sid = session.get("id", "")
        if sid and model:
            await client.put(f"{OPENCODE_URL}/api/session/{sid}/model", json={"modelID": model})
        return session


async def send_prompt(session_id: str, text: str) -> str:
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{OPENCODE_URL}/api/session/{session_id}/prompt",
            json={"prompt": {"text": text}},
        )
        return resp.json().get("data", {}).get("id", "")


async def poll_response(session_id: str, timeout: int = 120) -> AsyncGenerator[dict, None]:
    start = asyncio.get_event_loop().time()
    seen: set[str] = set()
    full_text = ""

    async with httpx.AsyncClient() as client:
        while True:
            elapsed = asyncio.get_event_loop().time() - start
            if elapsed > timeout:
                if full_text:
                    yield {"content": full_text, "done": True}
                else:
                    yield {"content": "", "done": True, "error": "超时"}
                return

            try:
                resp = await client.get(
                    f"{OPENCODE_URL}/api/session/{session_id}/message",
                    params={"from": 0, "to": 100},
                )
                messages = resp.json().get("data", [])
            except Exception:
                await asyncio.sleep(1)
                continue

            for msg in messages:
                mid = msg.get("id", "")
                if mid in seen:
                    continue
                mtype = msg.get("type", "")
                if mtype == "user":
                    seen.add(mid)
                    continue

                if mtype == "assistant":
                    seen.add(mid)
                    if msg.get("finish") == "error":
                        continue
                    for block in msg.get("content", []):
                        text = block.get("text", "") if isinstance(block, dict) else str(block)
                        if text:
                            yield {"content": text, "done": False}
                    if msg.get("finish") == "stop":
                        yield {"content": "", "done": True}
                        return

            await asyncio.sleep(0.5)
