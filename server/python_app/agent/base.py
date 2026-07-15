from __future__ import annotations
import abc
from typing import Optional


class ProviderModel:
    """Provider 提供的单个模型"""
    def __init__(self, id: str, name: str, provider_id: str, sub_key: str = ""):
        self.id = id
        self.name = name
        self.provider_id = provider_id   # e.g. "opencode", "deepseek"
        self.sub_key = sub_key            # e.g. "go", "zen" (for providers with variants)


class SendResult:
    """AI 发送消息的结果"""
    def __init__(self, content: str = "", thinking: str = "", error: str = ""):
        self.content = content
        self.thinking = thinking
        self.error = error

    @property
    def ok(self) -> bool:
        return not self.error and bool(self.content)


class Provider(abc.ABC):
    """AI Provider 抽象基类。所有 AI 引擎都必须实现此类"""

    @property
    @abc.abstractmethod
    def provider_id(self) -> str:
        """唯一标识符，如 opencode / deepseek"""
        ...

    @abc.abstractmethod
    async def fetch_models(self) -> list[ProviderModel]:
        """获取该 provider 当前可用的模型列表"""
        ...

    @abc.abstractmethod
    async def send(
        self,
        model: str,
        messages: list[dict],
        user_content: str,
        api_key: str = "",
        sub_key: str = "",
        **kwargs,
    ) -> SendResult:
        """发送消息并获取回复"""
        ...

    async def validate_key(self, api_key: str) -> bool:
        """校验 API Key 是否有效（默认返回 True）"""
        return True
