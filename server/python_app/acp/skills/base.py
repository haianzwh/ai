from __future__ import annotations
import abc
from typing import Any


class Skill(abc.ABC):
    """Skill 抽象基类 — 所有技能必须实现"""

    @property
    @abc.abstractmethod
    def name(self) -> str:
        ...

    @property
    def description(self) -> str:
        return ""

    @property
    def parameters(self) -> dict:
        return {}

    @abc.abstractmethod
    async def execute(self, **kwargs) -> dict:
        ...

    def to_tool_def(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters,
        }
