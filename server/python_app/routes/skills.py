"""
=============================================================================
  技能路由
=============================================================================
"""
from fastapi import APIRouter, Depends
from ..auth import get_current_user
from ..acp.skills.registry import skill_registry

router = APIRouter(prefix="/api/skills", tags=["技能"])


@router.get("/")
async def list_skills(user: dict = Depends(get_current_user)):
    return {"success": True, "skills": skill_registry.list_all()}


@router.post("/{name}/execute")
async def execute_skill(name: str, body: dict, user: dict = Depends(get_current_user)):
    result = await skill_registry.execute(name, **body.get("args", {}))
    return result
