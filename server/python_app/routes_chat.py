"""
=============================================================================
  ACP 架构 — Process 层路由
  负责 HTTP 路由委派，不直接调用 AI 引擎
=============================================================================
"""
import json
from fastapi import APIRouter, HTTPException, Depends, Body
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from .database import execute_write
from .auth import get_current_user

# Agent 层
from .agent.registry import registry as provider_registry
from .agent.base import ProviderModel

# Control 层
from .control.auth import get_user_api_keys, mask_key, save_user_api_key

# Process 层
from .process.chat import (
    list_sessions, create_session, delete_session, get_messages,
    update_session_model, update_session_title, toggle_pin, send_message,
)


class SendReq(BaseModel):
    content: str


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


logger = __import__("logging").getLogger(__name__)
router = APIRouter(prefix="/api/chat", tags=["聊天"])


# ── Provider 列表 ─────────────────────────────────────

@router.get("/providers")
async def list_providers(user: dict = Depends(get_current_user)):
    return {"success": True, "providers": provider_registry.list_provider_info()}


# ── 模型列表 ──────────────────────────────────────────

@router.get("/models")
async def list_models(user: dict = Depends(get_current_user)):
    user_keys = await get_user_api_keys(user["id"])
    models = await provider_registry.list_models(user_keys)
    return {"success": True, "models": models}


# ── API Key 管理 ──────────────────────────────────────

@router.get("/user/deepseek-key")
async def get_deepseek_key(user: dict = Depends(get_current_user)):
    keys = await get_user_api_keys(user["id"])
    return {
        "success": True,
        "hasGOKey": "deepseek" in keys,
        "maskedGOKey": mask_key(keys.get("deepseek", "")),
        "hasZenKey": "zen" in keys,
        "maskedZenKey": mask_key(keys.get("zen", "")),
    }


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


# ── 会话管理 ──────────────────────────────────────────

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


# ── 发送消息 ──────────────────────────────────────────

@router.post("/sessions/{sid}/send")
async def send_to_ai(sid: str, req: SendReq, user: dict = Depends(get_current_user)):
    """Process 层核心入口：编排发送→重试→保存"""
    result = await send_message(sid, user["id"], user["username"], req.content)
    return result
