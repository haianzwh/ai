from __future__ import annotations
from ..protocol import ACPResponse, ACPErrorCode
from ..skills.registry import skill_registry


class SkillsHandler:
    """处理 skills.list / skills.execute 方法"""

    async def __call__(self, params: dict) -> ACPResponse:
        action = params.get("action", "list")
        if action == "list":
            return ACPResponse.success(skill_registry.list_all())
        elif action == "execute":
            name = params.get("skill", "")
            if not name:
                return ACPResponse.fail(ACPErrorCode.INVALID_PARAMS, "skill name required")
            result = await skill_registry.execute(name, **params.get("args", {}))
            return ACPResponse.success(result)
        return ACPResponse.fail(ACPErrorCode.METHOD_NOT_FOUND, f"Unknown action: {action}")
