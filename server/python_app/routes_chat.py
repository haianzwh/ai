"""
=============================================================================
  聊天路由 — 基于 opencode web 作为 AI 引擎
=============================================================================
"""
import json, uuid, asyncio, logging, httpx
from fastapi import APIRouter, HTTPException, Depends, Query, Body
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from .database import execute, execute_write, execute_one
from .auth import get_current_user
from .ai_client import create_opencode_session, send_prompt, poll_response, OPENCODE_URL


class SendReq(BaseModel):
    content: str

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/chat", tags=["聊天"])

# 发送锁：每个会话同时只允许一个发送请求
_send_locks: dict[str, asyncio.Lock] = {}

# 内存中缓存：chat_session_id → opencode_session_id
# 重启丢失，聊天会话需重建
_oc_cache: dict[str, str] = {}


@router.get("/models")
async def list_models(user: dict = Depends(get_current_user)):
    """从 opencode 获取可用模型列表"""
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{OPENCODE_URL}/api/model")
            data = resp.json()
            models = [
                {"id": m["id"], "name": m.get("name", m["id"]), "provider": m.get("providerID", "")}
                for m in data.get("data", [])
                if m.get("status") == "active"
            ]
        return {"success": True, "models": models}
    except Exception as e:
        return {"success": False, "models": [], "error": str(e)}


@router.get("/sessions")
async def list_sessions(user: dict = Depends(get_current_user)):
    rows = await execute(
        "SELECT id, title, model, created_at, updated_at FROM chat_sessions WHERE username=%s ORDER BY updated_at DESC LIMIT 50",
        (user["username"],),
    )
    return {
        "success": True,
        "sessions": [
            {
                "id": r["id"], "title": r["title"], "model": r["model"],
                "created": r["created_at"].strftime("%m-%d %H:%M"),
                "updated": r["updated_at"].strftime("%m-%d %H:%M"),
            }
            for r in rows
        ],
    }


@router.post("/sessions")
async def create_session(user: dict = Depends(get_current_user)):
    sid = f"chat_{uuid.uuid4().hex[:12]}"

    # 提前创建 opencode 会话（预热，后续发消息不用等）
    oc_id = ""
    try:
        oc = await create_opencode_session()
        oc_id = oc.get("id", "")
    except Exception:
        pass

    await execute_write(
        "INSERT INTO chat_sessions (id, username, title, model, oc_session_id) VALUES (%s,%s,%s,%s,%s)",
        (sid, user["username"], "新对话", "hy3-free", oc_id),
    )
    return {"success": True, "id": sid, "title": "新对话"}


@router.delete("/sessions/{sid}")
async def delete_session(sid: str, user: dict = Depends(get_current_user)):
    await execute_write("DELETE FROM chat_messages WHERE session_id=%s", (sid,))
    await execute_write("DELETE FROM chat_sessions WHERE id=%s AND username=%s", (sid, user["username"]))
    return {"success": True}


@router.get("/sessions/{sid}/messages")
async def get_messages(sid: str, user: dict = Depends(get_current_user)):
    rows = await execute(
        "SELECT id, role, content, thinking, tokens_input, tokens_output, created_at FROM chat_messages WHERE session_id=%s ORDER BY id ASC LIMIT 100",
        (sid,),
    )
    return {
        "success": True,
        "messages": [
            {
                "id": r["id"], "role": r["role"],
                "content": r["content"], "thinking": r.get("thinking"),
                "time": r["created_at"].strftime("%H:%M"),
            }
            for r in rows
        ],
    }


@router.post("/sessions/{sid}/send")
async def send_message(
    sid: str,
    req: SendReq,
    user: dict = Depends(get_current_user),
):
    """发送消息，同步等待 AI 回复"""
    content = req.content
    
    # 保存用户消息
    await execute_write(
        "INSERT INTO chat_messages (session_id, role, content) VALUES (%s,%s,%s)",
        (sid, "user", content),
    )

    # 获取或创建 opencode 会话
    session = await execute_one("SELECT oc_session_id FROM chat_sessions WHERE id=%s", (sid,))
    oc_id = session["oc_session_id"] if session else ""
    if not oc_id:
        oc = await create_opencode_session()
        oc_id = oc.get("id", "")
        await execute_write("UPDATE chat_sessions SET oc_session_id=%s WHERE id=%s", (oc_id, sid))

    # 首次发消息更新标题
    count_rows = await execute(
        "SELECT COUNT(*) as c FROM chat_messages WHERE session_id=%s AND role='user'",
        (sid,),
    )
    if count_rows and count_rows[0]["c"] == 1:
        title = content[:30] + ("..." if len(content) > 30 else "")
        await execute_write("UPDATE chat_sessions SET title=%s WHERE id=%s", (title, sid))

    # 检测思考模式：消息开头有 <think> 标签时切换模型
    is_think = content.startswith("<think>")
    if is_think:
        content = content.replace("<think>","").replace("</think>","")
        content = (
            "\n\n请按以下格式输出：\n"
            "<think>\n你的推理过程\n</think>\n"
            "你的最终答案\n\n"
            "问题：" + content
        )

    # 发送 prompt 前记录已有消息 ID（防重复取旧回复）
    import httpx
    try:
        r = httpx.get(f"{OPENCODE_URL}/api/session/{oc_id}/message", params={"from": 0, "to": 50}, timeout=5)
        existing_ids = {m["id"] for m in r.json().get("data", []) if m.get("id")}
    except:
        existing_ids = set()

    # 发送 prompt 并等待 AI 回复
    full_text = ""
    for retry in range(2):
        try:
            await send_prompt(oc_id, content)
            async for chunk in poll_response(oc_id, existing_ids=existing_ids, timeout=120):
                if chunk.get("done"):
                    break
                if chunk.get("content"):
                    full_text += chunk["content"]
            break
        except Exception as e:
            # 请求体过大时重建会话（清除上下文）
            if "TooLarge" in str(e) or "max bytes" in str(e):
                oc = await create_opencode_session()
                oc_id = oc.get("id", "")
                await execute_write("UPDATE chat_sessions SET oc_session_id=%s WHERE id=%s", (oc_id, sid))
                await send_prompt(oc_id, content)
                async for chunk in poll_response(oc_id, existing_ids=set(), timeout=120):
                    if chunk.get("done"):
                        break
                    if chunk.get("content"):
                        full_text += chunk["content"]
                break
            else:
                return {"success": False, "error": str(e)}

    # 保存 AI 回复
    if full_text:
        await execute_write(
            "INSERT INTO chat_messages (session_id, role, content) VALUES (%s,%s,%s)",
            (sid, "assistant", full_text),
        )

    return {"success": True, "content": full_text}

