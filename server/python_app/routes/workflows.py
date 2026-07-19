"""
=============================================================================
  工作流路由
=============================================================================
"""
from fastapi import APIRouter, Depends
from ..auth import get_current_user

router = APIRouter(prefix="/api/workflows", tags=["工作流"])

_workflow_engine = None

def set_workflow_engine(e):
    global _workflow_engine
    _workflow_engine = e


@router.get("/")
async def list_workflows(user: dict = Depends(get_current_user)):
    if not _workflow_engine:
        return {"success": True, "workflows": []}
    return {"success": True, "workflows": list(_workflow_engine._workflows.keys())}


@router.post("/{name}/execute")
async def execute_workflow(name: str, body: dict, user: dict = Depends(get_current_user)):
    if not _workflow_engine:
        return {"success": False, "error": "Workflow engine not initialized"}
    result = await _workflow_engine.execute(name, **body.get("args", {}))
    return result
