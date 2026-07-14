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


async def create_opencode_session() -> dict:
    """在 opencode 中创建会话（模型需后续通过 set_session_model 设置）"""
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{OPENCODE_URL}/api/session",
            json={},
        )
        return resp.json().get("data", {})


async def set_session_model(session_id: str, model: str = DEFAULT_MODEL):
    """设置 opencode 会话使用的模型"""
    async with httpx.AsyncClient() as client:
        await client.post(
            f"{OPENCODE_URL}/api/session/{session_id}/model",
            json={"model": {"id": model, "providerID": "opencode"}},
        )


async def send_prompt(session_id: str, text: str) -> str:
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{OPENCODE_URL}/api/session/{session_id}/prompt",
            json={"prompt": {"text": text}},
        )
        return resp.json().get("data", {}).get("id", "")


async def poll_response(session_id: str, existing_ids: set[str] = None, timeout: int = 120) -> AsyncGenerator[dict, None]:
    """轮询 opencode 消息，获取 AI 回复。
    
    Args:
        session_id: opencode 会话 ID
        existing_ids: 发送前已有的消息 ID 集合，只返回之后的新消息
        timeout: 超时秒数
    """
    start = asyncio.get_event_loop().time()
    seen: set[str] = set(existing_ids) if existing_ids else set()
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

            # 只处理新消息
            new_messages = [m for m in messages if m.get("id") not in seen]
            
            for msg in new_messages:
                mid = msg.get("id", "")
                mtype = msg.get("type", "")

                if mtype == "user":
                    continue

                if mtype == "assistant":
                    if msg.get("finish") == "error":
                        continue

                    # 提取当前内容（含部分生成的文本）
                    has_content = False
                    for block in msg.get("content", []):
                        text = block.get("text", "") if isinstance(block, dict) else str(block)
                        if text:
                            has_content = True
                            if text != full_text:  # 新内容或增量
                                delta = text[len(full_text):] if text.startswith(full_text) else text
                                full_text = text
                                yield {"content": delta, "done": False}

                    # 无内容 → 跳过，后续轮询继续等
                    if not has_content:
                        continue

                    # 完成 → 加入 seen 避免重复
                    if msg.get("finish") == "stop":
                        seen.add(mid)
                        yield {"content": "", "done": True}
                        return
                    # 未完成 → 不加 seen，下次轮询继续读取增量
                    seen.discard(mid)

            await asyncio.sleep(0.5)
