from __future__ import annotations
from .base import Skill


class SkillRegistry:
    """Skill 注册中心"""

    def __init__(self):
        self._skills: dict[str, Skill] = {}

    def register(self, skill: Skill):
        self._skills[skill.name] = skill
        print(f"[Skill] 注册: {skill.name}")

    def get(self, name: str) -> Skill | None:
        return self._skills.get(name)

    def list_all(self) -> list[dict]:
        return [s.to_tool_def() for s in self._skills.values()]

    async def execute(self, name: str, **kwargs) -> dict:
        skill = self._skills.get(name)
        if not skill:
            return {"success": False, "error": f"Skill not found: {name}"}
        try:
            result = await skill.execute(**kwargs)
            return {"success": True, "result": result}
        except Exception as e:
            return {"success": False, "error": str(e)}


skill_registry = SkillRegistry()
