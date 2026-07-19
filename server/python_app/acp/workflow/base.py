from __future__ import annotations
import abc
from typing import Any


class Workflow(abc.ABC):
    """Workflow 抽象基类"""

    @property
    @abc.abstractmethod
    def name(self) -> str:
        ...

    @abc.abstractmethod
    async def run(self, **kwargs) -> dict:
        ...
