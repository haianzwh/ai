"""
=============================================================================
  Skill Creator — 元技能：一句话生成新技能
  传 JSON body {name: "x", description: "y"} 自动生成完整Python skill包
=============================================================================
"""
from fastapi import FastAPI, APIRouter
from pydantic import BaseModel, Field
from pathlib import Path
import re

NAME = "skill-creator"
DESC = "元技能：用自然语言描述需求，自动生成新的 skill 代码"


class GenReq(BaseModel):
    name: str = Field(..., description="技能名称，如 ppt-export")
    description: str = Field(..., description="技能描述，一句话说明功能")


class SkillCreator:
    name = NAME
    description = DESC

    async def on_register(self, app: FastAPI):
        router = APIRouter(prefix="/api/skills/creator", tags=["技能生成器"])

        @router.post("/generate")
        async def generate_skill(req: GenReq):
            safe_name = re.sub(r"[^a-z0-9_-]", "_", req.name.lower())
            class_name = self._class_name(safe_name)

            base_dir = Path("/tmp/opencode/ai-chat/server/python_app/skills")
            skill_dir = base_dir / safe_name
            skill_dir.mkdir(parents=True, exist_ok=True)

            base_py = f'''"""
{req.description}
"""
from fastapi import FastAPI, APIRouter

NAME = "{safe_name}"
DESC = "{req.description}"


class {class_name}:
    name = NAME
    description = DESC

    async def on_register(self, app: FastAPI):
        router = APIRouter(prefix="/api/skills/{safe_name}", tags=["{safe_name}"])

        @router.get("")
        async def info():
            return {{
                "skill": "{safe_name}",
                "description": "{req.description}",
            }}

        @router.get("/run")
        async def run():
            return {{"status": "ok", "message": "{safe_name} running"}}

        app.include_router(router)
'''
            (skill_dir / "base.py").write_text(base_py)

            init_py = f'''"""技能: {req.description}"""
from .base import {class_name}

__all__ = ["{class_name}"]
'''
            (skill_dir / "__init__.py").write_text(init_py)

            registry_py = f'''from .base import {class_name}
__all__ = ["{class_name}"]
'''
            (skill_dir / "registry.py").write_text(registry_py)

            skill_md = f'''---
name: {safe_name}
description: "{req.description}"
license: MIT
---

# {safe_name}

{req.description}

## API 接口
- GET /api/skills/{safe_name}/ — 技能信息
- GET /api/skills/{safe_name}/run — 执行
'''
            (skill_dir / "SKILL.md").write_text(skill_md)

            return {
                "success": True, "name": safe_name, "class": class_name,
                "dir": str(skill_dir),
                "files": ["base.py", "__init__.py", "registry.py", "SKILL.md"],
                "next": f"在 main.py 中注册: registry.register({class_name}()) 然后重启",
            }

        @router.get("/templates")
        async def templates():
            return {
                "templates": {
                    "api": {"desc": "REST API 端点", "eg": "name=todo-api&description=待办管理API"},
                    "file-process": {"desc": "文件处理", "eg": "name=pdf-merge&description=PDF合并"},
                    "ai-agent": {"desc": "AI代理", "eg": "name=translator&description=中英互译"},
                    "tool": {"desc": "工具/脚本", "eg": "name=backup&description=自动备份"},
                }
            }

        app.include_router(router)

    @staticmethod
    def _class_name(s: str) -> str:
        return "".join(w.capitalize() for w in s.replace("-", "_").split("_")) + "Skill"
