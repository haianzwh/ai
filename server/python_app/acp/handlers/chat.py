from __future__ import annotations
from typing import Optional
from ..protocol import ACPResponse, ACPErrorCode
from ...agent.registry import registry
from ...agent.base import SendResult
from ...control.auth import get_user_api_keys


class ChatHandler:
    """处理 chat.completions 方法"""

    def __init__(self, external_gateway=None):
        self.external_gateway = external_gateway

    async def __call__(self, params: dict) -> ACPResponse:
        provider_name = params.get("provider", "")
        if not provider_name:
            return ACPResponse.fail(ACPErrorCode.INVALID_PARAMS, "provider is required")

        provider_inst = registry.get(provider_name)
        if not provider_inst:
            return ACPResponse.fail(ACPErrorCode.PROVIDER_ERROR, f"Provider not found: {provider_name}")

        model = params.get("model", "")
        messages = params.get("messages", [])
        user_content = params.get("user_content", "")
        api_key = params.get("api_key", "")
        sub_key = params.get("sub_key", "")
        oc_session_id = params.get("oc_session_id", "")
        user_id = params.get("user_id", "")

        if not model:
            return ACPResponse.fail(ACPErrorCode.INVALID_PARAMS, "model is required")

        try:
            result: SendResult = await provider_inst.send(
                model=model,
                messages=messages,
                user_content=user_content,
                api_key=api_key,
                sub_key=sub_key,
                oc_session_id=oc_session_id,
            )
            return ACPResponse.success({
                "content": result.content,
                "thinking": result.thinking,
                "ok": result.ok,
                "error": result.error,
            })
        except Exception as e:
            return ACPResponse.fail(ACPErrorCode.INTERNAL_ERROR, str(e))
