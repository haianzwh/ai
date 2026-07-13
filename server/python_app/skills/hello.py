"""
=============================================================================
  Skill: Hello World 示例技能
  演示如何创建一个技能插件
  
  后期可以新建 skill_ppt.py, skill_agent.py 等
=============================================================================
"""
from fastapi import FastAPI, APIRouter
from .base import BaseSkill


class HelloSkill(BaseSkill):
    """示例技能：演示技能插件机制"""
    name = "hello_world"
    description = "Hello World 示例技能"

    async def on_register(self, app: FastAPI) -> None:
        router = APIRouter(prefix="/api/skills/hello", tags=["技能示例"])

        @router.get("")
        async def hello():
            return {"message": "Hello from skill plugin!", "skill": self.name}

        app.include_router(router)
