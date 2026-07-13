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
        # 1. 创建会话
        resp = await client.post(f"{OPENCODE_URL}/api/session", json={})
        session = resp.json().get("data", {})
        sid = session.get("id", "")

        # 2. 切换到指定模型
        if sid and model:
            await client.put(
                f"{OPENCODE_URL}/api/session/{sid}/model",
                json={"modelID": model},
            )

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
    seen: set[str] = set()  # 已处理的消息 ID
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

            # 找没见过的消息
            for msg in messages:
                mid = msg.get("id", "")
                if mid in seen:
                    continue

                mtype = msg.get("type", "")

                # 用户消息直接标记已见
                if mtype == "user":
                    seen.add(mid)
                    continue

                # 检测错误
                error = msg.get("error")
                if error:
                    seen.add(mid)
                    yield {"content": "", "done": True, "error": str(error.get("message", error))}
                    return

                if mtype == "assistant":
                    seen.add(mid)

                    # 跳过未完成的消息
                    if msg.get("finish") == "error":
                        continue

                    # 从 content 数组中提取文本
                    content_blocks = msg.get("content", [])
                    if not content_blocks:
                        continue

                    for block in content_blocks:
                        btype = block.get("type", "text")
                        block_text = block.get("text", "") if isinstance(block, dict) else str(block)

                        # reasoning/thinking 类型
                        if btype in ("reasoning", "thinking", "thought"):
                            if block_text:
                                yield {"thinking": block_text, "done": False}
                            continue

                        # 主文本
                        if block_text:
                            if block_text != full_text and block_text.startswith(full_text):
                                delta = block_text[len(full_text):]
                            else:
                                delta = block_text
                                full_text = ""
                            full_text += delta
                            yield {"content": delta, "done": False}

                    # 消息完成后退出
                    if msg.get("finish") == "stop":
                        yield {"content": "", "done": True, "error": None}
                        return

            await asyncio.sleep(0.5)


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
