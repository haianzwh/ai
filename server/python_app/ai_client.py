"""
=============================================================================
  AI 客户端 — 通过 opencode web API 调用模型
  opencode 管理模型选择、API key、流式输出
=============================================================================
"""
import httpx, json, asyncio
from typing import AsyncGenerator

OPENCODE_URL = "http://localhost:4096"


async def create_opencode_session() -> dict:
    """在 opencode 中创建新会话"""
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{OPENCODE_URL}/api/session", json={})
        return resp.json().get("data", {})


async def send_prompt(session_id: str, text: str) -> str:
    """通过 opencode 发送消息，返回 message_id"""
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{OPENCODE_URL}/api/session/{session_id}/prompt",
            json={"prompt": {"text": text}},
        )
        data = resp.json()
        return data.get("data", {}).get("id", "")


async def poll_response(session_id: str, after_seq: int = 0, timeout: int = 120) -> AsyncGenerator[dict, None]:
    """
    轮询 opencode 消息，获取 AI 回复。
    返回 AsyncGenerator，逐条 yield 消息增量。
    """
    start = asyncio.get_event_loop().time()
    last_seq = after_seq
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

            # 找新增的 assistant 消息
            new_messages = [m for m in messages if m.get("seq", 0) > last_seq]
            if not new_messages:
                await asyncio.sleep(0.5)
                continue

            for msg in new_messages:
                last_seq = max(last_seq, msg.get("seq", 0))

                if msg.get("role") == "assistant" or msg.get("type") == "text":
                    content = msg.get("text", "") or msg.get("content", "")
                    if isinstance(content, dict):
                        content = content.get("text", "")
                    if not content:
                        continue

                    # 增量返回（避免重复）
                    if content != full_text and content.startswith(full_text):
                        delta = content[len(full_text):]
                        full_text = content
                        yield {"content": delta, "done": False}
                    elif content != full_text:
                        full_text = content
                        yield {"content": content, "done": False}

                elif msg.get("type") == "error" or msg.get("error"):
                    yield {"content": "", "done": True, "error": str(msg.get("error", "未知错误"))}
                    return

            if any(m.get("complete") for m in new_messages if m.get("role") == "assistant"):
                yield {"content": "", "done": True, "error": None}
                return

            await asyncio.sleep(0.3)


async def get_session_messages(session_id: str) -> list[dict]:
    """获取 opencode 会话的所有消息"""
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{OPENCODE_URL}/api/session/{session_id}/message",
            params={"from": 0, "to": 200},
        )
        data = resp.json()
        msgs = []
        for m in data.get("data", []):
            role = m.get("role", "user")
            content = m.get("text", "") or m.get("content", "")
            if isinstance(content, dict):
                content = content.get("text", "")
            if content:
                msgs.append({
                    "role": "user" if role == "user" else "assistant",
                    "content": str(content),
                    "thinking": m.get("thinking", ""),
                    "tokens": m.get("tokens", {}),
                })
        return msgs
