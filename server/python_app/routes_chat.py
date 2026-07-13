"""
=============================================================================
  聊天路由 — 基于 opencode web 作为 AI 引擎
=============================================================================
"""
import json, uuid, asyncio, logging, httpx
from fastapi import APIRouter, HTTPException, Depends, Query, Body
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from .database import execute, execute_write, execute_one
from .auth import get_current_user
from .ai_client import create_opencode_session, send_prompt, poll_response, OPENCODE_URL


class SendReq(BaseModel):
    content: str

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/chat", tags=["聊天"])

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

    # 在 opencode 中创建对应会话
    oc_id = ""
    try:
        oc = await create_opencode_session()
        oc_id = oc.get("id", "")
    except Exception:
        pass

    await execute_write(
        "INSERT INTO chat_sessions (id, username, title, model, oc_session_id) VALUES (%s,%s,%s,%s,%s)",
        (sid, user["username"], "新对话", "deepseek-v4-flash-free", oc_id),
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
    """发送消息 → SSE 流式返回 AI 回复"""
    content = req.content
    # 保存用户消息
    await execute_write(
        "INSERT INTO chat_messages (session_id, role, content) VALUES (%s,%s,%s)",
        (sid, "user", content),
    )

    # 获取或创建 opencode 会话（持久化到DB，复用上下文）
    session = await execute_one("SELECT oc_session_id FROM chat_sessions WHERE id=%s", (sid,))
    oc_id = session["oc_session_id"] if session else ""
    if not oc_id:
        try:
            oc = await create_opencode_session()
            oc_id = oc.get("id", "")
            await execute_write("UPDATE chat_sessions SET oc_session_id=%s WHERE id=%s", (oc_id, sid))
        except Exception as e:
            return StreamingResponse(
                _error_stream(f"创建AI会话: {e}"),
                media_type="text/event-stream",
            )

    # 发送 prompt 到 opencode
    try:
        msg_id = await send_prompt(oc_id, content)
    except Exception as e:
        return StreamingResponse(
            _error_stream(f"发送消息失败: {e}"),
            media_type="text/event-stream",
        )

    # 首次发消息更新标题
    count_rows = await execute("SELECT COUNT(*) as c FROM chat_messages WHERE session_id=%s AND role='user'", (sid,))
    if count_rows and count_rows[0]["c"] == 1:
        title = content[:30] + ("..." if len(content) > 30 else "")
        await execute_write("UPDATE chat_sessions SET title=%s WHERE id=%s", (title, sid))

    return StreamingResponse(
        _stream_response(sid, oc_id),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


async def _stream_response(sid: str, oc_id: str):
    full = ""
    thinking = ""
    try:
        async for chunk in poll_response(oc_id):
            if chunk.get("done"):
                if chunk.get("error"):
                    yield f"data: {json.dumps({'error': chunk['error'], 'done': True})}\n\n"
                else:
                    await execute_write(
                        "INSERT INTO chat_messages (session_id, role, content, thinking) VALUES (%s,%s,%s,%s)",
                        (sid, "assistant", full, thinking),
                    )
                    yield f"data: {json.dumps({'done': True})}\n\n"
                return

            # 思考过程
            if chunk.get("thinking"):
                delta = chunk["thinking"]
                thinking += delta
                yield f"data: {json.dumps({'thinking': delta})}\n\n"

            # 正文
            delta = chunk.get("content", "")
            if delta:
                full += delta
                yield f"data: {json.dumps({'content': delta})}\n\n"
    except Exception as e:
        if full:
            await execute_write(
                "INSERT INTO chat_messages (session_id, role, content, thinking) VALUES (%s,%s,%s,%s)",
                (sid, "assistant", full, thinking),
            )
        yield f"data: {json.dumps({'error': str(e), 'done': True})}\n\n"


async def _error_stream(msg: str):
    yield f"data: {json.dumps({'error': msg, 'done': True})}\n\n"
