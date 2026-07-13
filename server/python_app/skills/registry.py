"""
=============================================================================
  技能注册表
  管理所有技能的加载和注册。
  
  使用方法:
      from .skill_registry import registry
      
      # 加载技能
      registry.register(MySkill())
      
      # 在 main.py 启动时安装所有技能
      await registry.install(app)
=============================================================================
"""
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastapi import FastAPI
    from .base import BaseSkill


class SkillRegistry:
    """
    技能注册中心。
    
    单例模式，存储所有已注册的技能并在 app 启动时安装。
    """

    def __init__(self) -> None:
        self._skills: list[BaseSkill] = []

    def register(self, skill: BaseSkill) -> None:
        """注册一个技能到注册表中"""
        self._skills.append(skill)

    async def install(self, app: FastAPI) -> None:
        """
        将所有已注册的技能安装到 FastAPI app。
        在 startup 事件中调用。
        """
        for skill in self._skills:
            try:
                await skill.on_register(app)
                print(f"[Skill] 已加载: {skill.name} - {skill.description}")
            except Exception as e:
                print(f"[Skill] 加载失败: {skill.name} - {e}")


# 全局单例
registry = SkillRegistry()
