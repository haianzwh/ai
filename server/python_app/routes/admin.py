"""
=============================================================================
  管理后台路由
=============================================================================
"""
from fastapi import APIRouter, Depends, Request
from fastapi.responses import FileResponse
from ..auth import get_current_user

router = APIRouter(prefix="/api/admin", tags=["管理"])

PDF_PATH = "/tmp/opencode/acp_architecture.pdf"
_memory_mgr = None


def set_memory_manager(mgr):
    global _memory_mgr
    _memory_mgr = mgr


@router.get("/health")
async def health_check():
    return {"success": True, "status": "ok", "version": "2.1.0"}


@router.get("/stats")
async def stats(user: dict = Depends(get_current_user)):
    from ..acp.middleware.registry import plugin_registry
    from ..acp.skills.registry import skill_registry
    return {
        "success": True,
        "plugins": len(plugin_registry.list()),
        "skills": len(skill_registry.list_all()),
    }


@router.get("/download/architecture")
async def download_architecture():
    """下载 ACP 架构文档 PDF"""
    import os
    if not os.path.exists(PDF_PATH):
        return {"success": False, "error": "PDF not found"}
    return FileResponse(PDF_PATH, media_type="application/pdf", filename="acp_architecture.pdf")


@router.get("/memory/{user_id}")
async def list_user_memories(user_id: str):
    if not _memory_mgr:
        return {"success": False, "error": "Memory manager not available"}
    memories = []
    for scope in ("short_term", "long_term"):
        items = await _memory_mgr.list_user_memories(user_id, scope)
        memories.extend(items)
    return {"success": True, "memories": memories, "user_id": user_id}


@router.delete("/memory/{user_id}")
async def clear_user_memories(user_id: str):
    if not _memory_mgr:
        return {"success": False, "error": "Memory manager not available"}
    for scope in ("short_term", "long_term"):
        await _memory_mgr.clear_user_memories(user_id, scope)
    return {"success": True, "message": f"已清除用户 {user_id} 的记忆"}


@router.get("/global-memory")
async def list_global_memories():
    if not _memory_mgr:
        return {"success": False, "error": "Memory manager not available"}
    items = await _memory_mgr.list_global()
    return {"success": True, "memories": items}


@router.put("/global-memory")
async def set_global_memory(req: Request):
    if not _memory_mgr:
        return {"success": False, "error": "Memory manager not available"}
    body = await req.json()
    key = body.get("key", "")
    value = body.get("value", "")
    if not key or not value:
        return {"success": False, "error": "key and value required"}
    await _memory_mgr.set_global(key, value)
    return {"success": True, "message": f"已设置全局记忆: {key}"}


@router.delete("/global-memory/{key}")
async def delete_global_memory(key: str):
    if not _memory_mgr:
        return {"success": False, "error": "Memory manager not available"}
    await _memory_mgr.delete_global(key)
    return {"success": True, "message": f"已删除全局记忆: {key}"}
