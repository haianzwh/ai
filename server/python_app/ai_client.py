"""
=============================================================================
  AI 客户端 — 通过 opencode web API 调用模型
=============================================================================
"""
import httpx, json, asyncio
from typing import AsyncGenerator

OPENCODE_URL = "http://localhost:4096"
DEFAULT_MODEL = "deepseek-v4-flash-free"


async def create_opencode_session(model: str = DEFAULT_MODEL) -> dict:
    """在 opencode 中创建新会话，并切换到指定模型"""
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{OPENCODE_URL}/api/session", json={})
        session = resp.json().get("data", {})
        sid = session.get("id", "")
        if sid and model:
            await client.put(
                f"{OPENCODE_URL}/api/session/{sid}/model",
                json={"modelID": model},
            )
            await asyncio.sleep(1)  # 等模型切换生效
        return session


async def send_prompt(session_id: str, text: str) -> str:
    """通过 opencode 发送消息，返回 message_id"""
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{OPENCODE_URL}/api/session/{session_id}/prompt",
            json={"prompt": {"text": text}},
        )
        data = resp.json()
        return data.get("data", {}).get("id", "")


async def poll_response(session_id: str, timeout: int = 120) -> AsyncGenerator[dict, None]:
    """轮询 opencode 消息，获取 AI 回复。"""
    start = asyncio.get_event_loop().time()
    seen: set[str] = set()
    full_text = ""

    async with httpx.AsyncClient() as client:
        while True:
            elapsed = asyncio.get_event_loop().time() - start
            if elapsed > timeout:
                if full_text:
                    yield {"content": full_text, "done": True, "error": None}
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

                error = msg.get("error")
                if error:
                    seen.add(mid)
                    yield {"content": "", "done": True, "error": str(error.get("message", error))}
                    return

                if mtype == "assistant":
                    seen.add(mid)
                    if msg.get("finish") == "error":
                        continue

                    for block in msg.get("content", []):
                        btype = block.get("type", "text")
                        text = block.get("text", "") if isinstance(block, dict) else str(block)

                        if btype in ("reasoning", "thinking", "thought"):
                            if text:
                                yield {"thinking": text, "done": False}
                            continue

                        if text:
                            if text != full_text and text.startswith(full_text):
                                delta = text[len(full_text):]
                            else:
                                delta = text
                                full_text = ""
                            full_text += delta
                            yield {"content": delta, "done": False}

                    if msg.get("finish") == "stop":
                        yield {"content": "", "done": True, "error": None}
                        return

            await asyncio.sleep(0.5)