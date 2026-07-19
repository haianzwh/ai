from __future__ import annotations
from ..protocol import ACPResponse, ACPErrorCode
from ...agent.registry import registry


class ModelsHandler:
    """处理 models.list 方法"""

    async def __call__(self, params: dict) -> ACPResponse:
        provider_name = params.get("provider")
        user_keys = params.get("user_keys", {})

        if provider_name:
            provider_inst = registry.get(provider_name)
            if not provider_inst:
                return ACPResponse.fail(ACPErrorCode.PROVIDER_ERROR, f"Provider not found: {provider_name}")
            try:
                models = await provider_inst.fetch_models()
                result = [{"id": m.id, "name": m.name, "provider": m.provider_id, "sub_key": m.sub_key} for m in models]
                return ACPResponse.success(result)
            except Exception as e:
                return ACPResponse.fail(ACPErrorCode.INTERNAL_ERROR, str(e))

        models = await registry.list_models(user_keys)
        return ACPResponse.success(models)
