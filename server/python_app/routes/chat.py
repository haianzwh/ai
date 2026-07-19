"""
=============================================================================
  聊天路由 — 委派给 process/chat.py
=============================================================================
"""
import json, os, shutil, uuid
from fastapi import APIRouter, HTTPException, Depends, Body, Request, UploadFile, File
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel

from ..database import execute_write, execute_one
from ..auth import get_current_user
from ..agent.registry import registry as provider_registry
from ..control.auth import get_user_api_keys, mask_key, save_user_api_key
from ..process.chat import (
    list_sessions, create_session, delete_session, get_messages,
    update_session_model, update_session_title, toggle_pin, send_message,
)
from ..acp.protocol import ACPRequest, ACPResponse
from ..config import OPENCODE_BASE_URL

router = APIRouter(prefix="/api/chat", tags=["聊天"])

UPLOAD_BASE = "/tmp/opencode/ai-chat/server/uploads"

_acp_server = None

def set_acp_server(s):
    global _acp_server
    _acp_server = s

class SendReq(BaseModel):
    content: str = ""

class CreateSessionReq(BaseModel):
    model: str = ""

class ModelReq(BaseModel):
    model: str

class TitleReq(BaseModel):
    title: str

class ApiKeyReq(BaseModel):
    api_key: str

class ZenKeyReq(BaseModel):
    api_key: str


@router.get("/providers")
async def list_providers(user: dict = Depends(get_current_user)):
    return {"success": True, "providers": provider_registry.list_provider_info()}

@router.get("/models")
async def list_models(user: dict = Depends(get_current_user)):
    user_keys = await get_user_api_keys(user["id"])
    models = await provider_registry.list_models(user_keys)
    return {"success": True, "models": models}

@router.get("/user/deepseek-key")
async def get_deepseek_key(user: dict = Depends(get_current_user)):
    keys = await get_user_api_keys(user["id"])
    return {"success": True, "hasGOKey": "deepseek" in keys, "maskedGOKey": mask_key(keys.get("deepseek", "")),
            "hasZenKey": "zen" in keys, "maskedZenKey": mask_key(keys.get("zen", ""))}

@router.put("/user/deepseek-key")
async def set_deepseek_key(req: ApiKeyReq, user: dict = Depends(get_current_user)):
    if req.api_key and not req.api_key.startswith("sk-"):
        raise HTTPException(status_code=400, detail={"error": "API key must start with sk-"})
    ok = await save_user_api_key(user["id"], "deepseek", req.api_key or "")
    return {"success": ok}

@router.put("/user/zen-key")
async def set_zen_key(req: ZenKeyReq, user: dict = Depends(get_current_user)):
    if req.api_key and not req.api_key.startswith("sk-"):
        raise HTTPException(status_code=400, detail={"error": "API key must start with sk-"})
    ok = await save_user_api_key(user["id"], "zen", req.api_key or "")
    return {"success": ok}

@router.get("/sessions")
async def get_sessions(user: dict = Depends(get_current_user)):
    sessions = await list_sessions(user["username"])
    return {"success": True, "sessions": sessions}

@router.post("/sessions")
async def new_session(req: CreateSessionReq = Body(default=None), user: dict = Depends(get_current_user)):
    model = req.model if req and req.model else ""
    result = await create_session(user["username"], model)
    return {"success": True, "id": result["id"], "title": result["title"], "model": result["model"]}

@router.delete("/sessions/{sid}")
async def remove_session(sid: str, user: dict = Depends(get_current_user)):
    await delete_session(sid, user["username"])
    return {"success": True}

@router.put("/sessions/{sid}")
async def rename_session(sid: str, req: TitleReq, user: dict = Depends(get_current_user)):
    await update_session_title(sid, user["username"], req.title)
    return {"success": True}

@router.put("/sessions/{sid}/model")
async def change_session_model(sid: str, req: ModelReq, user: dict = Depends(get_current_user)):
    await update_session_model(sid, user["username"], req.model)
    return {"success": True}

@router.put("/sessions/{sid}/pin")
async def pin_session(sid: str, user: dict = Depends(get_current_user)):
    new_val = await toggle_pin(sid, user["username"])
    return {"success": True, "pinned": new_val}

@router.get("/sessions/{sid}/messages")
async def get_session_messages(sid: str, user: dict = Depends(get_current_user)):
    data = await get_messages(sid, user["username"])
    return {"success": True, **data}

@router.post("/upload")
async def upload_file(file: UploadFile = File(...), user: dict = Depends(get_current_user)):
    user_dir = os.path.join(UPLOAD_BASE, user["username"])
    os.makedirs(user_dir, exist_ok=True)
    ext = os.path.splitext(file.filename or "file")[1]
    safe_name = f"{uuid.uuid4().hex[:12]}{ext}"
    dest = os.path.join(user_dir, safe_name)
    with open(dest, "wb") as f:
        shutil.copyfileobj(file.file, f)
    size = os.path.getsize(dest)
    url = f"/uploads/{user['username']}/{safe_name}"
    return {"success": True, "url": url, "path": dest, "name": file.filename, "size": size}

@router.post("/sessions/{sid}/send")
async def send_to_ai(sid: str, req: SendReq, user: dict = Depends(get_current_user)):
    result = await send_message(sid, user["id"], user["username"], content=req.content)
    return result

@router.get("/sessions/{sid}/stream")
async def stream_ai_response(sid: str, user: dict = Depends(get_current_user)):
    """SSE 流式返回 AI 的实时思考与回复"""
    import asyncio, httpx

    async def event_generator():
        # 等 oc_id 就绪
        oc_id = ""
        for _ in range(30):
            s = await execute_one("SELECT oc_session_id FROM chat_sessions WHERE id=%s", (sid,))
            oc_id = s["oc_session_id"] if s else ""
            if oc_id: break
            await asyncio.sleep(1)
        if not oc_id:
            yield f"data: {json.dumps({'type':'error','message':'会话未就绪'})}\n\n"
            return

        poll_start = asyncio.get_event_loop().time()
        last_text = ""

        async with httpx.AsyncClient(timeout=None) as client:
            try:
                async with client.stream("GET", f"{OPENCODE_BASE_URL}/api/session/{oc_id}/event") as resp:
                    async for line in resp.aiter_lines():
                        if asyncio.get_event_loop().time() - poll_start > 600:
                            break
                        if not line.startswith("data: "):
                            continue
                        try:
                            evt = json.loads(line[6:])
                        except Exception:
                            continue

                        evt_type = evt.get("type", "")
                        data = evt.get("data", {})

                        # 推理过程（reasoning 结束时携带完整推理文本）
                        if evt_type == "session.next.reasoning.ended":
                            t = data.get("text", "")
                            if t:
                                yield f"data: {json.dumps({'type':'thinking','text':t[:1000]})}\n\n"

                        # 文本回复（text 结束时携带完整回复文本）
                        elif evt_type == "session.next.text.ended":
                            t = data.get("text", "")
                            if t:
                                last_text = t
                                yield f"data: {json.dumps({'type':'delta','text':t})}\n\n"

                        # 工具调用
                        elif evt_type == "session.next.tool.called":
                            name = data.get("name", "")
                            if name:
                                yield f"data: {json.dumps({'type':'tool','name':name})}\n\n"

                        # 步骤结束（含 finish 状态）
                        elif evt_type == "session.next.step.ended":
                            finish = data.get("finish", "")
                            if finish in ("stop", "error"):
                                yield f"data: {json.dumps({'type':'done','content':last_text or '(empty)'})}\n\n"
                                return

            except Exception:
                pass

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@router.post("/acp/rpc")
async def acp_rpc(req: Request):
    if not _acp_server:
        return {"jsonrpc": "2.0", "error": {"code": -32603, "message": "ACP Server not ready"}, "id": None}
    body = await req.json()
    acp_req = ACPRequest(method=body.get("method", ""), params=body.get("params", {}), id=body.get("id"))
    resp = await _acp_server.route_request(acp_req)
    return {"jsonrpc": resp.jsonrpc, "result": resp.result, "error": resp.error, "id": resp.id}


@router.post("/acp/chat/completions")
async def acp_chat_completions(req: Request):
    """ACP chat.completions — 支持 stream: true 实现 SSE 流式输出"""
    body = await req.json()
    params = body.get("params", {})
    stream = body.get("stream", params.get("stream", False))

    if not stream:
        return await acp_rpc(req)

    # Streaming 模式
    provider_name = params.get("provider", "opencode")
    model = params.get("model", "deepseek-v4-flash-free")
    messages = params.get("messages", [])
    user_content = params.get("user_content", "")
    user_id = params.get("user_id", "")
    session_id = params.get("session_id", "")

    from ..agent.registry import registry
    provider = registry.get(provider_name)
    if not provider:
        return JSONResponse({"error": f"Provider not found: {provider_name}"}, status_code=400)

    # 从 messages 最后一条提取 user content
    if not user_content:
        for m in reversed(messages):
            if m.get("role") == "user":
                parts = m.get("content", [])
                if isinstance(parts, str):
                    user_content = parts
                elif isinstance(parts, list):
                    user_content = "".join(p.get("text", "") for p in parts if isinstance(p, dict))
                break

    if not user_content:
        return JSONResponse({"error": "user_content required"}, status_code=400)

    # 注入 + 提取记忆上下文
    try:
        user = await get_current_user(req)
        if user and user.get("username"):
            from ..process.chat import _inject_memory_context, _extract_and_store_memories
            user_content = await _inject_memory_context(user["username"], user_content, session_id)
            await _extract_and_store_memories(user["username"], user_content, session_id)
            try:
                from ..process.chat import _memory_mgr
                if _memory_mgr:
                    pref = "回答必须包含：每步标号+✅完成标记、创建的文件列表、步骤摘要"
                    await _memory_mgr.set_global("output_format", pref)
            except Exception:
                pass
    except Exception:
        pass

    async def event_generator():
        finished = False
        # 先发一个空行让浏览器收到 headers
        yield ":\n\n"
        try:
            async for evt in provider.send_stream(model=model, user_content=user_content, oc_session_id=session_id):
                et = evt["type"]
                ed = evt["data"]

                if et == "session.ready":
                    oc_id = ed.get("oc_id", "")
                    if oc_id:
                        yield f"event: session_ready\ndata: {json.dumps({'oc_id': oc_id})}\n\n"

                if et == "session.next.reasoning.ended":
                    t = ed.get("text", "")
                    if t:
                        yield f"event: reasoning\ndata: {json.dumps({'text': t[:1000]})}\n\n"
                elif et == "session.next.text.ended":
                    t = ed.get("text", "")
                    if t:
                        yield f"event: delta\ndata: {json.dumps({'text': t})}\n\n"
                elif et == "session.next.tool.called":
                    name = ed.get("name", "")
                    inp = ed.get("input", ed.get("arguments", ""))
                    if isinstance(inp, (dict, list)):
                        inp = json.dumps(inp, ensure_ascii=False)[:200]
                    if name:
                        yield f"event: tool_call\ndata: {json.dumps({'name': name, 'input': str(inp)[:200]})}\n\n"
                elif et == "session.next.step.ended":
                    finish = ed.get("finish", "")
                    if finish in ("stop", "error"):
                        finished = True
                        yield f"event: done\ndata: {json.dumps({'finish': finish})}\n\n"
                        return
                elif et == "timeout":
                    yield f"event: done\ndata: {json.dumps({'finish': 'timeout'})}\n\n"
                    return
            # 流自然结束但未发送 done → 补充 done
            if not finished:
                yield f"event: done\ndata: {json.dumps({'finish': 'stop'})}\n\n"
        except Exception as e:
            yield f"event: error\ndata: {json.dumps({'message': str(e)})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
