from __future__ import annotations
import uuid
import asyncio
from typing import Optional

from ..database import execute, execute_write, execute_one, get_pool
from ..agent.registry import registry
from ..agent.base import SendResult
from ..control.auth import get_user_api_keys


_send_locks: dict[str, asyncio.Lock] = {}
_oc_cache: dict[str, str] = {}


async def list_sessions(username: str) -> list[dict]:
    rows = await execute(
        """SELECT id, title, model, pinned, created_at, updated_at
           FROM chat_sessions WHERE username=%s
           ORDER BY pinned DESC, updated_at DESC LIMIT 50""",
        (username,),
    )
    return [
        {
            "id": r["id"], "title": r["title"], "model": r["model"],
            "pinned": r["pinned"],
            "created": r["created_at"].strftime("%m-%d %H:%M"),
            "updated": r["updated_at"].isoformat(),
        }
        for r in rows
    ]


async def create_session(username: str, model: str = "") -> dict:
    """创建新会话"""
    sid = f"chat_{uuid.uuid4().hex[:12]}"
    provider_inst = _get_provider_for_model(model)
    oc_id = ""

    if provider_inst and provider_inst.provider_id == "opencode":
        try:
            oc = await provider_inst.create_session()
            oc_id = oc.get("id", "")
            if oc_id:
                await provider_inst.set_model(oc_id, model)
        except Exception:
            pass

    await execute_write(
        "INSERT INTO chat_sessions (id, username, title, model, oc_session_id) VALUES (%s,%s,%s,%s,%s)",
        (sid, username, "新对话", model, oc_id),
    )
    return {"id": sid, "title": "新对话", "model": model, "oc_session_id": oc_id}


async def delete_session(sid: str, username: str):
    await execute_write("DELETE FROM chat_messages WHERE session_id=%s", (sid,))
    await execute_write("DELETE FROM chat_sessions WHERE id=%s AND username=%s", (sid, username))


async def get_messages(sid: str, username: str) -> dict:
    rows = await execute(
        """SELECT id, role, content, thinking, created_at
           FROM chat_messages WHERE session_id=%s ORDER BY id ASC LIMIT 100""",
        (sid,),
    )
    session = await execute_one("SELECT model FROM chat_sessions WHERE id=%s", (sid,))
    return {
        "username": username,
        "model": session["model"] if session else "",
        "messages": [
            {
                "id": r["id"], "role": r["role"],
                "content": r["content"], "thinking": r.get("thinking"),
                "time": r["created_at"].strftime("%Y/%-m/%-d %H:%M:%S"),
            }
            for r in rows
        ],
    }


async def update_session_title(sid: str, username: str, title: str):
    await execute_write(
        "UPDATE chat_sessions SET title=%s WHERE id=%s AND username=%s",
        (title, sid, username),
    )


async def update_session_model(sid: str, username: str, model: str):
    await execute_write(
        "UPDATE chat_sessions SET model=%s, oc_session_id='' WHERE id=%s AND username=%s",
        (model, sid, username),
    )


async def toggle_pin(sid: str, username: str) -> int:
    pool = await get_pool()
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "SELECT pinned FROM chat_sessions WHERE id=%s AND username=%s FOR UPDATE",
                (sid, username),
            )
            row = await cur.fetchone()
            new_val = None
            if row:
                new_val = 0 if row[0] else 1
                if new_val == 1:
                    await cur.execute(
                        "UPDATE chat_sessions SET pinned=0 WHERE username=%s AND id!=%s",
                        (username, sid),
                    )
                    await cur.execute(
                        "UPDATE chat_sessions SET pinned=1, updated_at=NOW() WHERE id=%s AND username=%s",
                        (sid, username),
                    )
                else:
                    await cur.execute(
                        "UPDATE chat_sessions SET pinned=0 WHERE id=%s AND username=%s",
                        (sid, username),
                    )
            await conn.commit()
    return new_val if row else 0


async def send_message(sid: str, user_id: str, username: str, content: str) -> dict:
    """发送消息并等待 AI 回复（Process 层的核心编排）"""
    # 保存用户消息
    await execute_write(
        "INSERT INTO chat_messages (session_id, role, content) VALUES (%s,%s,%s)",
        (sid, "user", content),
    )

    # 获取会话信息
    session = await execute_one(
        "SELECT oc_session_id, model FROM chat_sessions WHERE id=%s", (sid,),
    )
    oc_id = session["oc_session_id"] if session else ""
    session_model = session["model"] if session else ""

    if not session_model:
        return {"success": False, "error": "No model selected"}

    # 首次消息自动设置标题
    count = await execute(
        "SELECT COUNT(*) as c FROM chat_messages WHERE session_id=%s AND role='user'", (sid,),
    )
    if count and count[0]["c"] == 1:
        title = content[:30] + ("..." if len(content) > 30 else "")
        await update_session_title(sid, username, title)

    # 思考模式
    is_think = content.startswith("<think>")
    if is_think:
        content = content.replace("<think>", "").replace("</think>", "")
        content = (
            "\n\n请按以下格式输出：\n"
            "<think>\n你的推理过程\n</think>\n"
            "你的最终答案\n\n"
            "问题：" + content
        )

    # 确定使用哪个 provider
    provider_inst = _get_provider_for_model(session_model)
    if not provider_inst:
        return {"success": False, "error": f"Unknown provider for model: {session_model}"}

    # 获取历史消息
    prev = await execute(
        """SELECT role, content FROM chat_messages
           WHERE session_id=%s AND id < (SELECT MAX(id) FROM chat_messages WHERE session_id=%s)
           ORDER BY id ASC""",
        (sid, sid),
    )

    # 获取 API Key（如果需要）
    api_key = ""
    sub_key = ""
    cfg = registry.get_config(provider_inst.provider_id)
    if cfg.get("requires_key"):
        user_keys = await get_user_api_keys(user_id)
        # 判断模型对应的 sub_key
        subs = cfg.get("sub_providers", {})
        for sk in subs:
            if any(m.get("sub_key", "") == sk for m in [{"sub_key": ""}]):
                pass
        # 尝试各 sub_key
        for sk, sv in subs.items():
            kt = sv.get("key_type", sk)
            if user_keys.get(kt):
                api_key = user_keys[kt]
                sub_key = sk
                break
        if not api_key:
            return {"success": False, "error": "API key not configured"}

    # 检测模型是否走 opencode 通道
    if provider_inst.provider_id == "opencode":
        if not oc_id:
            oc = await provider_inst.create_session()
            oc_id = oc.get("id", "")
            if oc_id:
                await provider_inst.set_model(oc_id, session_model)
            await execute_write(
                "UPDATE chat_sessions SET oc_session_id=%s WHERE id=%s", (oc_id, sid),
            )

    # 发送到 provider
    lock = _send_locks.setdefault(sid, asyncio.Lock())
    async with lock:
        result: SendResult = await provider_inst.send(
            model=session_model,
            messages=prev if prev else [],
            user_content=content,
            api_key=api_key,
            sub_key=sub_key,
            oc_session_id=oc_id,
        )

    # 保存 opencode session id（如果有更新）
    if provider_inst.provider_id == "opencode":
        new_oc = getattr(result, "_oc_id", None) or oc_id
        if new_oc != oc_id:
            await execute_write(
                "UPDATE chat_sessions SET oc_session_id=%s WHERE id=%s", (new_oc, sid),
            )

    if not result.ok:
        return {"success": False, "error": result.error}

    # 保存 AI 回复
    await execute_write(
        "INSERT INTO chat_messages (session_id, role, content, thinking) VALUES (%s,%s,%s,%s)",
        (sid, "assistant", result.content, result.thinking),
    )

    return {"success": True, "content": result.content, "thinking": result.thinking}


def _get_provider_for_model(model_id: str):
    """根据模型 ID 找到对应的 provider 实例"""
    # 检查已知模型的前缀映射
    for pid, inst in registry.list():
        if model_id in [m.id for m in registry.get_config(pid).get("models", [])]:
            return inst
        # 尝试通过 provider 自己获取所有模型来匹配
        try:
            cfg = registry.get_config(pid)
            for m in cfg.get("models", []):
                if m["id"] == model_id:
                    return inst
        except Exception:
            pass
    # fallback: opencode 兜底
    return registry.get("opencode")
